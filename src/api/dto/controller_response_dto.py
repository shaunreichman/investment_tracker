"""
Controller Response Data Transfer Object (DTO).
Generic DTO for all controller responses between controller and route layers.
"""

from typing import Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum


class ControllerResponseStatus(Enum):
    """Status values for controller responses with HTTP status code mapping."""
    SUCCESS = "success"
    CREATED = "created"
    UPDATED = "updated"
    DELETED = "deleted"
    NOT_FOUND = "not_found"
    VALIDATION_ERROR = "validation_error"
    SERVER_ERROR = "server_error"
    UNAUTHORIZED = "unauthorized"
    FORBIDDEN = "forbidden"
    
    @classmethod
    def get_status_code(cls, status_string):
        """
        Get HTTP status code from status string with O(1) lookup.
        
        Args:
            status_string: Status string from DTO
            
        Returns:
            HTTP status code
        """
        # Static mapping for O(1) lookup performance
        status_to_code = {
            "success": 200,
            "created": 201,
            "updated": 200,
            "deleted": 204,
            "not_found": 404,
            "validation_error": 400,
            "server_error": 500,
            "unauthorized": 401,
            "forbidden": 403,
        }
        return status_to_code.get(status_string, 400)  # Default to 400


@dataclass
class ControllerResponseDTO:
    """Generic DTO for all controller responses."""
    data: Optional[Any] = None
    error: Optional[str] = None
    status: str = ControllerResponseStatus.SUCCESS.value
    message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response."""
        if self.error:
            return {
                "error": self.error,
                "status": self.status,
                "message": self.message
            }
        
        return {
            "data": self.data,  # Data should already be formatted by controller
            "status": self.status,
            "message": self.message
        }
