"""
Standardized API response wrapper.
"""

from typing import Any, Optional
from datetime import datetime, timezone

class ApiResponse:
    """Standardized API response wrapper."""
    def __init__(self, data: Any = None, success: bool = True, message: Optional[str] = None, details: Optional[str] = None):
        self.success = success
        self.message = message
        self.data = data
        self.details = details
        self.timestamp = datetime.now(timezone.utc)

    def to_dict(self) -> dict:
        return {
            "success": self.success,
            "message": self.message,
            "data": self.data,
            "details": self.details,
            "timestamp": self.timestamp.isoformat()
        }
