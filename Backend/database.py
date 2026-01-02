from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv
import logging

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_NAME = os.getenv("DB_NAME")
DB_HOST = os.getenv("DB_HOST", "localhost")

logger = logging.getLogger(__name__)

# Prefer explicit MySQL connection if credentials are provided, otherwise fall back to SQLite for
# local development. You can also set DATABASE_URL env var to override.
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
	if DB_USER and DB_PASS and DB_NAME:
		DATABASE_URL = f"mysql+mysqlconnector://{DB_USER}:{DB_PASS}@{DB_HOST}:3306/{DB_NAME}"
		logger.info("Using MySQL database from environment variables")
		engine = create_engine(DATABASE_URL)
	else:
		# fallback to sqlite file in project folder
		DATABASE_URL = f"sqlite:///./invoices.db"
		logger.info("DB env vars not set, falling back to SQLite at ./invoices.db")
		engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
	engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
