from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.config import settings

connect_args = {"check_same_thread": False} if "sqlite" in settings.SQLALCHEMY_DATABASE_URI else {}
engine = create_engine(settings.SQLALCHEMY_DATABASE_URI, pool_pre_ping=True, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
