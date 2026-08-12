from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import date, timedelta
from ..database import get_db
from ..models.batch import Batch
from ..models.inventory import InventoryAdjustment
from ..models.expense import Expense
from ..models.growth import GrowthSample
from ..models.auth import User
from ..schemas.expense import ExpenseCreate, ExpenseResponse
from ..schemas.financial import FinancialSummary, ProfitLossReport, ForecastReport
from .auth import get_current_user, get_user_farm

router = APIRouter(prefix="/financial", tags=["Financial"])

# ── Expenses CRUD ──────────────────────────────────────────────────────────────

@router.post("/batch/{batch_id}/expenses", response_model=ExpenseResponse, status_code=201)
def create_expense(batch_id: int, expense: ExpenseCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    get_user_farm(batch.farm_id, current_user, db)
    db_exp = Expense(batch_id=batch_id, **expense.model_dump())
    db.add(db_exp)
    db.commit()
    db.refresh(db_exp)
    return db_exp

@router.get("/batch/{batch_id}/expenses", response_model=List[ExpenseResponse])
def list_expenses(batch_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    get_user_farm(batch.farm_id, current_user, db)
    return db.query(Expense).filter(Expense.batch_id == batch_id).order_by(Expense.date.desc()).all()

# ── Financial Summary ──────────────────────────────────────────────────────────

@router.get("/batch/{batch_id}/summary", response_model=FinancialSummary)
def get_financial_summary(batch_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    get_user_farm(batch.farm_id, current_user, db)

    # Revenue from sales
    sales = db.query(InventoryAdjustment).filter(
        InventoryAdjustment.batch_id == batch_id,
        InventoryAdjustment.adjustment_type == "sale"
    ).all()
    total_revenue = sum(s.total_amount_zmw or 0 for s in sales)
    total_birds_sold = sum(abs(s.quantity_delta) for s in sales)
    avg_price_per_bird = (total_revenue / total_birds_sold) if total_birds_sold > 0 else 0

    # Expenses
    expenses = db.query(Expense).filter(Expense.batch_id == batch_id).all()
    total_expenses = sum(e.amount_zmw for e in expenses)
    expenses_by_category = {}
    for e in expenses:
        expenses_by_category[e.category] = expenses_by_category.get(e.category, 0) + e.amount_zmw

    # Profit / Loss
    gross_profit = total_revenue - total_expenses
    profit_margin_pct = (gross_profit / total_revenue * 100) if total_revenue > 0 else 0

    # Current live count for forecasting
    adjustments = db.query(InventoryAdjustment).filter(InventoryAdjustment.batch_id == batch_id).all()
    net_delta = sum(a.quantity_delta for a in adjustments)
    current_live = max(0, batch.bird_count + net_delta)

    return FinancialSummary(
        batch_id=batch_id,
        total_revenue_zmw=total_revenue,
        total_birds_sold=total_birds_sold,
        avg_price_per_bird_zmw=avg_price_per_bird,
        total_expenses_zmw=total_expenses,
        expenses_by_category=expenses_by_category,
        gross_profit_zmw=gross_profit,
        profit_margin_pct=profit_margin_pct,
        current_live_count=current_live
    )

# ── Expected Income Forecast ───────────────────────────────────────────────────

@router.get("/batch/{batch_id}/forecast")
def get_income_forecast(
    batch_id: int,
    expected_price_per_bird: float,  # query param: ZMW per bird
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Forecasts expected income from remaining live birds.
    Uses current live count × user-supplied expected price per bird.
    Also factors in mortality trend to project realistic sellable birds.
    """
    batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    get_user_farm(batch.farm_id, current_user, db)

    adjustments = db.query(InventoryAdjustment).filter(InventoryAdjustment.batch_id == batch_id).all()
    net_delta = sum(a.quantity_delta for a in adjustments)
    current_live = max(0, batch.bird_count + net_delta)

    # Mortality trend: average daily mortality over last 14 days
    mortality_events = [a for a in adjustments if a.adjustment_type == "mortality"]
    total_mortality = sum(abs(a.quantity_delta) for a in mortality_events)
    days_since_start = (date.today() - batch.start_date).days or 1
    daily_mortality_rate = total_mortality / days_since_start

    # Project 30-day mortality
    projected_30d_mortality = round(daily_mortality_rate * 30)
    projected_sellable = max(0, current_live - projected_30d_mortality)

    expected_income = projected_sellable * expected_price_per_bird

    return {
        "batch_id": batch_id,
        "current_live_count": current_live,
        "projected_30d_mortality": projected_30d_mortality,
        "projected_sellable_birds": projected_sellable,
        "expected_price_per_bird_zmw": expected_price_per_bird,
        "expected_income_zmw": expected_income,
        "confidence": "estimate — based on historical mortality trend"
    }

# ── Profit & Loss Report ───────────────────────────────────────────────────────

@router.get("/batch/{batch_id}/profit-loss")
def get_profit_loss(batch_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Full P&L breakdown: revenue by sale event, expenses by category,
    net profit/loss, and per-bird profitability.
    """
    batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    get_user_farm(batch.farm_id, current_user, db)

    sales = db.query(InventoryAdjustment).filter(
        InventoryAdjustment.batch_id == batch_id,
        InventoryAdjustment.adjustment_type == "sale"
    ).order_by(InventoryAdjustment.date).all()

    expenses = db.query(Expense).filter(
        Expense.batch_id == batch_id
    ).order_by(Expense.date).all()

    total_revenue = sum(s.total_amount_zmw or 0 for s in sales)
    total_expenses = sum(e.amount_zmw for e in expenses)
    net_profit = total_revenue - total_expenses
    total_birds_sold = sum(abs(s.quantity_delta) for s in sales)
    profit_per_bird = (net_profit / total_birds_sold) if total_birds_sold > 0 else 0

    return {
        "batch_id": batch_id,
        "revenue_entries": [
            {
                "date": str(s.date),
                "birds_sold": abs(s.quantity_delta),
                "unit_price_zmw": s.unit_price_zmw,
                "total_zmw": s.total_amount_zmw,
                "buyer": s.buyer_name
            } for s in sales
        ],
        "expense_entries": [
            {
                "date": str(e.date),
                "category": e.category,
                "description": e.description,
                "amount_zmw": e.amount_zmw
            } for e in expenses
        ],
        "summary": {
            "total_revenue_zmw": total_revenue,
            "total_expenses_zmw": total_expenses,
            "net_profit_zmw": net_profit,
            "total_birds_sold": total_birds_sold,
            "profit_per_bird_zmw": round(profit_per_bird, 2),
            "is_profitable": net_profit > 0
        }
    }
