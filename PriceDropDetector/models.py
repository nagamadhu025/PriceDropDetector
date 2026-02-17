from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    is_verified = Column(Boolean, default=False)  # ⭐ NEW: Email verification status
    
    # Relationship
    products = relationship("Product", back_populates="owner")
    otp_records = relationship("OTP", back_populates="user")  # ⭐ NEW


class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String)
    name = Column(String)
    price = Column(Float)
    target_price = Column(Float)
    last_alerted = Column(DateTime, nullable=True)
    subscribed = Column(Boolean, default=True)
    image = Column(String, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Relationship
    owner = relationship("User", back_populates="products")


class PriceHistory(Base):
    __tablename__ = "price_history"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    price = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    product = relationship("Product")


class OTP(Base):
    """Store OTP codes for email verification"""
    __tablename__ = "otps"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    otp_code = Column(String, index=True)  # 6-digit OTP
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)  # OTP valid for 10 minutes
    is_used = Column(Boolean, default=False)
    
    # Relationship
    user = relationship("User", back_populates="otp_records")