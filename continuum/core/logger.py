# continuum/core/logger.py

import logging
import os
from datetime import datetime
from uuid import uuid4
import sys

# Ensure stdout uses UTF‑8
sys.stdout.reconfigure(encoding="utf-8")

# ---------------------------------------------------------------------
# SESSION + PATH SETUP
# ---------------------------------------------------------------------

SESSION_ID = os.getenv("CONTINUUM_SESSION_ID", f"session-{uuid4().hex[:8]}")

BASE_LOG_DIR = os.path.join(os.getcwd(), "logs", "sessions")
os.makedirs(BASE_LOG_DIR, exist_ok=True)

SESSION_LOG_PATH = os.path.join(BASE_LOG_DIR, f"{SESSION_ID}.log")
ERROR_LOG_PATH = os.path.join(os.getcwd(), "logs", "errors.log")
DEBUG_LOG_PATH = os.path.join(os.getcwd(), "logs", "debug.log")

# ---------------------------------------------------------------------
# ROOT LOGGER CONFIGURATION
# ---------------------------------------------------------------------

# Stream handler (terminal) — WARNING and above only
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.WARNING)

# File handlers
session_file = logging.FileHandler(SESSION_LOG_PATH, encoding="utf-8")
session_file.setLevel(logging.INFO)

debug_file = logging.FileHandler(DEBUG_LOG_PATH, encoding="utf-8")
debug_file.setLevel(logging.DEBUG)

# Configure root logger
logging.basicConfig(
    level=logging.DEBUG,  # root level (files capture everything)
    format="%(asctime)s [%(levelname)s] [%(message)s",
    handlers=[session_file, debug_file, stream_handler]
)

# ---------------------------------------------------------------------
# NAMED LOGGER
# ---------------------------------------------------------------------

logger = logging.getLogger("continuum")

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
    logger.error(message, extra={"phase": phase})
    with open(ERROR_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"{datetime.now()} [{SESSION_ID}] [{phase}] {message}\n")


def log_debug(message, phase="debug"):
    logger.debug(message, extra={"phase": phase})


def log_info(message, phase="info"):
    logger.info(message, extra={"phase": phase})