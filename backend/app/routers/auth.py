from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from ..database import get_db
from ..config import settings
from ..limiter import limiter
from ..models.auth import User
from ..models.farm import Farm
from ..models.user_farm import UserFarmAssociation
from ..schemas.auth import Token, UserResponse, UserCreate

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Fix 1.2: Use bcrypt for all new hashes.
# sha256_crypt is kept as a deprecated fallback so existing hashed passwords in the
# database continue to verify correctly during the transition. Passlib will automatically
# re-hash to bcrypt on the next login if needs_update() is detected.
pwd_context = CryptContext(schemes=["bcrypt", "sha256_crypt"], deprecated=["sha256_crypt"])
# The path must align with the prefix added by the main router mount
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/token")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    # Fix 2.3 / deprecated: use timezone-aware datetime instead of deprecated utcnow()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user

# Fix 1.6: Admin-only dependency — only users with is_admin=True can reach protected endpoints
def get_admin_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator privileges required"
        )
    return current_user

async def get_login_credentials(request: Request) -> tuple[Optional[str], Optional[str]]:
    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        try:
            data = await request.json()
            if isinstance(data, dict):
                return data.get("username"), data.get("password")
        except Exception:
            pass
    try:
        form = await request.form()
        return form.get("username"), form.get("password")
    except Exception:
        pass
    return None, None

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(
    user: UserCreate,
    db: Session = Depends(get_db),
):
    try:
        # Check if user already exists
        existing = db.query(User).filter(User.username == user.username).first()
        if existing:
            raise HTTPException(status_code=400, detail="Username already registered")
            
        is_first_user = db.query(User).count() == 0

        db_user = User(
            username=user.username,
            hashed_password=get_password_hash(user.password),
            full_name=user.full_name,
            is_admin=is_first_user  # First registered user is automatically an admin
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        # Automatically associate new user to the default farm if present
        try:
            default_farm = db.query(Farm).first()
            if default_farm:
                assoc = UserFarmAssociation(user_id=db_user.id, farm_id=default_farm.id, role="owner")
                db.add(assoc)
                db.commit()
        except Exception:
            db.rollback()

        return db_user
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )

@router.post("/token", response_model=Token)
@limiter.limit("10/minute")
async def login_for_access_token(
    request: Request,
    credentials: tuple[Optional[str], Optional[str]] = Depends(get_login_credentials),
    db: Session = Depends(get_db),
):
    username, password = credentials
    if not username or not password:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Username and password are required",
        )
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Silently upgrade deprecated sha256_crypt hashes to bcrypt on first login
    if pwd_context.needs_update(user.hashed_password):
        user.hashed_password = get_password_hash(password)
        db.commit()
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

def get_user_farm(farm_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    assoc = db.query(UserFarmAssociation).filter(
        UserFarmAssociation.user_id == current_user.id,
        UserFarmAssociation.farm_id == farm_id
    ).first()
    if not assoc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this farm"
        )
    return assoc
