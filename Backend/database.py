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

# Database Priority:
# 1. Primary: Supabase (if SUPABASE_URL and SUPABASE_KEY are set)
# 2. Fallback: MySQL (if DB_USER, DB_PASS, DB_NAME are set)
# 3. Final Fallback: SQLite (local file)
#
# To use Supabase as primary, set environment variables:
#   SUPABASE_URL=https://your-project.supabase.co
#   SUPABASE_KEY=your-anon-key
#
# For MySQL fallback, set:
#   DB_USER=your_mysql_user
#   DB_PASS=your_mysql_password
#   DB_NAME=your_database_name

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
