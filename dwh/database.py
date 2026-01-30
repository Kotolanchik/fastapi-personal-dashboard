import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DWH_DATABASE_URL = os.getenv("DWH_DATABASE_URL", "sqlite:///./data/dwh.db")

connect_args = {}
if DWH_DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(DWH_DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
