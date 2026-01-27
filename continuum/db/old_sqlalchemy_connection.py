# continuum/db/sqlalchemy_connection.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from continuum.config.config_loader import load_config

# ---------------------------------------------------------
# Load DB settings from your existing config loader
# ---------------------------------------------------------
config = load_config()

db_host = config["database"]["host"]
db_port = config["database"]["port"]
db_user = config["database"]["user"]
db_pass = config["database"]["password"]
db_name = config["database"]["name"]

# SQLAlchemy connection string
DATABASE_URL = (
    f"mysql+pymysql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
)

# ---------------------------------------------------------
# Create SQLAlchemy engine + session factory
# ---------------------------------------------------------
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

# ---------------------------------------------------------
# Public helper for the registry and ORM
# ---------------------------------------------------------
def get_db_session():
    """Return a new SQLAlchemy session."""
    return SessionLocal()