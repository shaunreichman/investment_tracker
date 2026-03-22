"""
Standardized API response wrapper.
"""

from typing import Any, Optional, Dict
from datetime import datetime, timezone
from src.api.dto.response_codes import ApiResponseCode


class ApiResponse:
    """Standardized API response wrapper."""
    def __init__(self, data: Any = None, response_code: ApiResponseCode = ApiResponseCode.SUCCESS, message: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        self.response_code = response_code
        self.message = message
        self.data = data
        self.details = details
        self.timestamp = datetime.now(timezone.utc)
        self.success = response_code.get_http_status_code() < 400  # Auto-determine success from HTTP status

    def to_dict(self) -> dict:
        return {
            "success": self.success,
            "response_code": self.response_code.value,
            "message": self.message,
            "data": self.data,
            "details": self.details,
            "timestamp": self.timestamp.isoformat()
        }
