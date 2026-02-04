# continuum/db/sqlalchemy_connection.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from continuum.db.mysql_connection import MySQLConfigDB

# ---------------------------------------------------------
# Use the SAME database as your config DB
# ---------------------------------------------------------
config_db = MySQLConfigDB(
    host="192.168.50.114",
    port=3306,
    user="hal",
    password="Hal@2025!",
    database="aira_config"
)

# ---------------------------------------------------------
# Build SQLAlchemy connection string
# ---------------------------------------------------------

DATABASE_URL = (
    "mysql+pymysql://hal:Hal%402025%21@192.168.50.114:3306/aira_config"
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

def get_db_session():
    return SessionLocal()