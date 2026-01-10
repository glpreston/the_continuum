from dataclasses import dataclass
from typing import Any, Dict

@dataclass
class MemoryRecord:
    """A single stored memory item."""
    key: str
    value: Any
    metadata: Dict[str, Any]