# -*- coding: utf-8 -*-
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings

engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Re-export Base from user model to share metadata across all domain models
from app.infrastructure.models.user import Base

def get_db():
    """Generador de sesiones de base de datos para inyección de dependencias en FastAPI"""
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
