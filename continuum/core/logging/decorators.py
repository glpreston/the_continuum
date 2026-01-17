from functools import wraps
from ..logger import logger

def log_phase(phase_name):
    """
    Decorator that logs entry/exit of a function with session + timestamp + phase.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger.info(f"Entering {func.__name__}", extra={"phase": phase_name})
            result = func(*args, **kwargs)
            logger.info(f"Exiting {func.__name__}", extra={"phase": phase_name})
            return result
        return wrapper
    return decorator