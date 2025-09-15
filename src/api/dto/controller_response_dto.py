"""
Controller Response Data Transfer Object (DTO).
Generic DTO for all controller responses between controller and route layers.
"""

from typing import Optional, Dict, Any
from dataclasses import dataclass
from src.api.dto.response_codes import ApiResponseCode


@dataclass
class ControllerResponseDTO:
    """Generic DTO for all controller responses."""
    data: Optional[Any] = None
    error: Optional[str] = None
    response_code: ApiResponseCode = ApiResponseCode.SUCCESS
    message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response."""
        if self.error:
            return {
                "error": self.error,
                "response_code": self.response_code.value,
                "message": self.message
            }
        
        return {
            "data": self.data,  # Data should already be formatted by controller
            "response_code": self.response_code.value,
            "message": self.message
        }
