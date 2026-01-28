# continuum/core/logger.py
import logging
import os
from datetime import datetime
from uuid import uuid4

logging.getLogger().handlers.clear()
logging.getLogger().propagate = False

import sys
sys.stdout.reconfigure(encoding='utf-8')

# Generate session ID once per run
SESSION_ID = os.getenv("CONTINUUM_SESSION_ID", f"session-{uuid4().hex[:8]}")

# Ensure log directory exists
BASE_LOG_DIR = os.path.join(os.getcwd(), "logs", "sessions")
os.makedirs(BASE_LOG_DIR, exist_ok=True)

# Per-session log file
SESSION_LOG_PATH = os.path.join(BASE_LOG_DIR, f"{SESSION_ID}.log")

# Global logs
ERROR_LOG_PATH = os.path.join(os.getcwd(), "logs", "errors.log")
DEBUG_LOG_PATH = os.path.join(os.getcwd(), "logs", "debug.log")

# Configure root logger with UTF‑8 encoding
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] [%(message)s",
    handlers=[
        logging.FileHandler(SESSION_LOG_PATH, encoding="utf-8"),
        logging.FileHandler(DEBUG_LOG_PATH, encoding="utf-8"),
        logging.StreamHandler()
    ]
)

# Create named loggers
logger = logging.getLogger("continuum")

# Inject session + phase into log records
class ContextFilter(logging.Filter):
    def filter(self, record):
        record.session = SESSION_ID
        if not hasattr(record, "phase"):
            record.phase = "unknown"
        return True

logger.addFilter(ContextFilter())

def log_error(message, phase="error"):
    logger.error(message, extra={"phase": phase})
    # Write UTF‑8 here too
    with open(ERROR_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"{datetime.now()} [{SESSION_ID}] [{phase}] {message}\n")

def log_debug(message, phase="debug"):
    logger.debug(message, extra={"phase": phase})

def log_info(message, phase="info"):
    logger.info(message, extra={"phase": phase})