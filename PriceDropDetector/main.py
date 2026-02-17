from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from database import engine, SessionLocal
from models import Base, Product, User, PriceHistory, OTP  # ⭐ Added OTP
from scraper import get_amazon_price
from scheduler import start_scheduler, check_prices
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt
from otp_service import generate_otp, send_otp_email, get_otp_expiry  # ⭐ NEW

app = FastAPI()

# =============================
# CONFIGURATION
# =============================
SECRET_KEY = "your-secret-key-change-this-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
security = HTTPBearer()


# =============================
# HELPER FUNCTIONS
# =============================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    
    return user


# =============================
# SCHEMAS
# =============================
class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str


class VerifyOTPRequest(BaseModel):
    email: EmailStr
    otp_code: str


class ResendOTPRequest(BaseModel):
    email: EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class ProductCreate(BaseModel):
    url: str
    target_price: float


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict


# =============================
# STARTUP
# =============================
@app.on_event("startup")
def startup_event():
    start_scheduler()


@app.get("/")
def home():
    return {"message": "Price Tracker Running"}


# =============================
# AUTH APIs WITH OTP
# =============================

@app.post("/register")
def register_user(data: RegisterRequest, db: Session = Depends(get_db)):
    """Register a new user and send OTP for verification"""
    # Check if email already exists
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        if existing.is_verified:
            raise HTTPException(status_code=400, detail="Email already registered")
        else:
            # Email exists but not verified - delete old user and OTPs
            db.query(OTP).filter(OTP.user_id == existing.id).delete()
            db.delete(existing)
            db.commit()

    # Hash password
    hashed_password = pwd_context.hash(data.password)

    # Create user (not verified yet)
    user = User(
        name=data.name,
        email=data.email,
        password=hashed_password,
        is_verified=False  # ⭐ Not verified yet
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    # Generate and save OTP
    otp_code = generate_otp()
    otp = OTP(
        user_id=user.id,
        otp_code=otp_code,
        expires_at=get_otp_expiry()
    )
    db.add(otp)
    db.commit()

    # Send OTP email
    email_sent = send_otp_email(user.email, otp_code, user.name)
    
    if not email_sent:
        # Rollback if email fails
        db.delete(otp)
        db.delete(user)
        db.commit()
        raise HTTPException(status_code=500, detail="Failed to send verification email")

    return {
        "message": "Registration successful! Please check your email for the verification code.",
        "email": user.email
    }


@app.post("/verify-otp")
def verify_otp(data: VerifyOTPRequest, db: Session = Depends(get_db)):
    """Verify OTP code and activate user account"""
    # Find user
    user = db.query(User).filter(User.email == data.email).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.is_verified:
        raise HTTPException(status_code=400, detail="Email already verified")

    # Find valid OTP
    otp = db.query(OTP).filter(
        OTP.user_id == user.id,
        OTP.otp_code == data.otp_code,
        OTP.is_used == False,
        OTP.expires_at > datetime.utcnow()
    ).first()

    if not otp:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP code")

    # Mark OTP as used
    otp.is_used = True
    
    # Verify user
    user.is_verified = True
    
    db.commit()

    return {
        "message": "Email verified successfully! You can now login.",
        "verified": True
    }


@app.post("/resend-otp")
def resend_otp(data: ResendOTPRequest, db: Session = Depends(get_db)):
    """Resend OTP verification code"""
    user = db.query(User).filter(User.email == data.email).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.is_verified:
        raise HTTPException(status_code=400, detail="Email already verified")

    # Delete old OTPs
    db.query(OTP).filter(OTP.user_id == user.id).delete()
    db.commit()

    # Generate new OTP
    otp_code = generate_otp()
    otp = OTP(
        user_id=user.id,
        otp_code=otp_code,
        expires_at=get_otp_expiry()
    )
    db.add(otp)
    db.commit()

    # Send email
    email_sent = send_otp_email(user.email, otp_code, user.name)
    
    if not email_sent:
        raise HTTPException(status_code=500, detail="Failed to send verification email")

    return {"message": "New verification code sent to your email"}


@app.post("/login", response_model=TokenResponse)
def login_user(data: LoginRequest, db: Session = Depends(get_db)):
    """Login and receive authentication token"""
    user = db.query(User).filter(User.email == data.email).first()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # ⭐ Check if email is verified
    if not user.is_verified:
        raise HTTPException(
            status_code=403, 
            detail="Please verify your email before logging in"
        )

    if not pwd_context.verify(data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Create access token
    access_token = create_access_token(data={"sub": user.email})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name
        }
    }


# =============================
# PRODUCT APIs (Protected)
# =============================

@app.get("/products")
def get_products(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    products = db.query(Product).filter(Product.user_id == current_user.id).all()
    return products


@app.post("/add-product")
def add_product(
    data: ProductCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    existing = db.query(Product).filter(
        Product.url == data.url,
        Product.user_id == current_user.id
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Product already tracked")

    product_data = get_amazon_price(data.url)

    if not product_data:
        raise HTTPException(
            status_code=503, 
            detail="Could not fetch product details. Amazon may have blocked the request."
        )

    product = Product(
        url=data.url,
        name=product_data["name"],
        price=float(product_data["price"]),
        target_price=data.target_price,
        last_alerted=None,
        subscribed=True,
        image=product_data.get("image"),
        user_id=current_user.id
    )

    db.add(product)
    db.commit()
    db.refresh(product)

    check_prices(product_id=product.id)

    return {
        "message": "Product added successfully",
        "product_id": product.id,
        "product": {
            "id": product.id,
            "name": product.name,
            "price": product.price,
            "target_price": product.target_price,
            "image": product.image
        }
    }


@app.delete("/product/{product_id}")
def delete_product(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.user_id == current_user.id
    ).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    db.delete(product)
    db.commit()

    return {"message": "Product deleted successfully"}


@app.post("/toggle-subscription/{product_id}")
def toggle_subscription(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.user_id == current_user.id
    ).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    product.subscribed = not product.subscribed
    db.commit()

    return {
        "message": "Subscription updated",
        "subscribed": product.subscribed
    }


@app.get("/product/{product_id}/price-history")
def get_price_history(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.user_id == current_user.id
    ).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    history = db.query(PriceHistory).filter(
        PriceHistory.product_id == product_id
    ).order_by(PriceHistory.timestamp.desc()).limit(30).all()
    
    return [
        {
            "price": h.price,
            "timestamp": h.timestamp.isoformat()
        }
        for h in reversed(history)
    ]


@app.get("/me")
def get_current_user_info(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email
    }