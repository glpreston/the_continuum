# continuum/core/logger.py

import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime
from uuid import uuid4
import sys

# ---------------------------------------------------------------------
# UTF‑8 stdout (Streamlit-safe)
# ---------------------------------------------------------------------
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass  # Streamlit sometimes wraps stdout; safe to ignore


# ---------------------------------------------------------------------
# SESSION + PATH SETUP
# ---------------------------------------------------------------------

SESSION_ID = os.getenv("CONTINUUM_SESSION_ID", f"session-{uuid4().hex[:8]}")

BASE_LOG_DIR = os.path.join(os.getcwd(), "logs")
SESSION_DIR = os.path.join(BASE_LOG_DIR, "sessions")

os.makedirs(BASE_LOG_DIR, exist_ok=True)
os.makedirs(SESSION_DIR, exist_ok=True)

SESSION_LOG_PATH = os.path.join(SESSION_DIR, f"{SESSION_ID}.log")
ERROR_LOG_PATH = os.path.join(BASE_LOG_DIR, "errors.log")
DEBUG_LOG_PATH = os.path.join(BASE_LOG_DIR, "debug.log")
ROTATING_LOG_PATH = os.path.join(BASE_LOG_DIR, "continuum.log")


# ---------------------------------------------------------------------
# UNIFIED LOGGER INITIALIZATION
# ---------------------------------------------------------------------

logger = logging.getLogger("continuum")
logger.setLevel(logging.DEBUG)  # Capture everything; handlers decide output

# Prevent duplicate handlers on reload
if not logger.handlers:

    # -------------------------------------------------------------
    # Rotating main log (5MB × 5 files)
    # -------------------------------------------------------------
    rotating_handler = RotatingFileHandler(
        ROTATING_LOG_PATH,
        maxBytes=5 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8"
    )
    rotating_handler.setLevel(logging.INFO)

    # -------------------------------------------------------------
    # Session log (per-run trace)
    # -------------------------------------------------------------
    session_handler = logging.FileHandler(SESSION_LOG_PATH, encoding="utf-8")
    session_handler.setLevel(logging.INFO)

    # -------------------------------------------------------------
    # Debug log (full trace)
    # -------------------------------------------------------------
    debug_handler = logging.FileHandler(DEBUG_LOG_PATH, encoding="utf-8")
    debug_handler.setLevel(logging.DEBUG)

    # -------------------------------------------------------------
    # Console handler (warnings and above)
    # -------------------------------------------------------------
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)

    # -------------------------------------------------------------
    # Unified log format
    # -------------------------------------------------------------
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] [session=%(session)s] [phase=%(phase)s] %(message)s"
    )

    for h in (rotating_handler, session_handler, debug_handler, console_handler):
        h.setFormatter(formatter)
        logger.addHandler(h)


# ---------------------------------------------------------------------
# CONTEXT FILTER (injects session + phase)
# ---------------------------------------------------------------------

class ContextFilter(logging.Filter):
    def filter(self, record):
        record.session = SESSION_ID
        if not hasattr(record, "phase"):
            record.phase = "unknown"
        return True

logger.addFilter(ContextFilter())


# ---------------------------------------------------------------------
# PUBLIC LOGGING FUNCTIONS
# ---------------------------------------------------------------------

def log_error(message, phase="error"):
    """
    Log an error message.
    Also writes to errors.log explicitly for quick access.
    """
    logger.error(message, extra={"phase": phase})

    # Dedicated error file (append-only)
    try:
        with open(ERROR_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(f"{datetime.now()} [session={SESSION_ID}] [{phase}] {message}\n")
    except Exception:
        pass


def log_debug(message, phase="debug"):
    """
    Log a debug message.
    """
    logger.debug(message, extra={"phase": phase})


def log_info(message, phase="info"):
    """
    Log an informational message.
    """
    logger.info(message, extra={"phase": phase})