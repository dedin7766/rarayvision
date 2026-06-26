import os
import json
import uuid
import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from passlib.context import CryptContext
from backend.app.core.config import DB_USER, DB_PASS, DB_HOST, DB_NAME

SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"

engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    api_keys = relationship("ApiKey", back_populates="user", cascade="all, delete-orphan")
    faces = relationship("Face", back_populates="user", cascade="all, delete-orphan")

class ApiKey(Base):
    __tablename__ = "api_keys"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    key_string = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=True)
    status = Column(String(50), default="Active")
    expires_at = Column(DateTime, nullable=True)
    usage_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="api_keys")

class Face(Base):
    __tablename__ = "faces"

    internal_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    face_id = Column(String(100), index=True, nullable=False) # e.g. "karyawan-1"
    name = Column(String(255), nullable=False)
    embedding = Column(Text, nullable=False) # JSON encoded embedding
    image_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="faces")

# Create all tables in the engine
Base.metadata.create_all(bind=engine)

# Password hashing
import bcrypt

def get_password_hash(password: str) -> str:
    # Hash a password
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Check a password
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
