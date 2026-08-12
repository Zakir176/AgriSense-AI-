from pydantic import BaseModel
from typing import Dict, Optional

class FinancialSummary(BaseModel):
    batch_id: int
    total_revenue_zmw: float
    total_birds_sold: int
    avg_price_per_bird_zmw: float
    total_expenses_zmw: float
    expenses_by_category: Dict[str, float]
    gross_profit_zmw: float
    profit_margin_pct: float
    current_live_count: int

class ProfitLossReport(BaseModel):
    pass  # handled inline in router for now

class ForecastReport(BaseModel):
    pass  # handled inline in router for now
