"""
Banking API DTOs (Data Transfer Objects).

This module provides standardized response models for all banking API endpoints,
ensuring consistent data structure and format across the entire API.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum


class BankingErrorCode(str, Enum):
    """Standardized error codes for banking operations."""
    
    # Validation errors
    VALIDATION_ERROR = "VALIDATION_ERROR"
    MISSING_REQUIRED_FIELD = "MISSING_REQUIRED_FIELD"
    INVALID_FORMAT = "INVALID_FORMAT"
    INVALID_VALUE = "INVALID_VALUE"
    
    # Business logic errors
    BANK_NOT_FOUND = "BANK_NOT_FOUND"
    BANK_ACCOUNT_NOT_FOUND = "BANK_ACCOUNT_NOT_FOUND"
    ENTITY_NOT_FOUND = "ENTITY_NOT_FOUND"
    DUPLICATE_BANK = "DUPLICATE_BANK"
    DUPLICATE_ACCOUNT = "DUPLICATE_ACCOUNT"
    
    # System errors
    INTERNAL_ERROR = "INTERNAL_ERROR"
    DATABASE_ERROR = "DATABASE_ERROR"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"


@dataclass
class BankingError:
    """Standardized error response structure."""
    
    code: BankingErrorCode
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        result = asdict(self)
        if self.timestamp:
            result['timestamp'] = self.timestamp.isoformat()
        return result


@dataclass
class BankResponse:
    """Standardized bank response structure."""
    
    id: int
    name: str
    country: str
    swift_bic: Optional[str]
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        result = asdict(self)
        if self.created_at:
            result['created_at'] = self.created_at.isoformat()
        if self.updated_at:
            result['updated_at'] = self.updated_at.isoformat()
        return result


@dataclass
class BankAccountResponse:
    """Standardized bank account response structure."""
    
    id: int
    account_name: str
    account_number: str
    currency: str
    is_active: bool
    entity_id: int
    bank: BankResponse
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        result = asdict(self)
        result['bank'] = self.bank.to_dict()
        if self.created_at:
            result['created_at'] = self.created_at.isoformat()
        if self.updated_at:
            result['updated_at'] = self.updated_at.isoformat()
        return result


@dataclass
class BankAccountBalanceResponse:
    """Standardized bank account balance response structure."""
    
    account_id: int
    account_number: str
    currency: str
    balance: Optional[float]
    last_updated: Optional[datetime] = None
    message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        result = asdict(self)
        if self.last_updated:
            result['last_updated'] = self.last_updated.isoformat()
        return result


@dataclass
class BankAccountTransactionsResponse:
    """Standardized bank account transactions response structure."""
    
    account_id: int
    account_number: str
    currency: str
    transactions: List[Dict[str, Any]]
    total_count: int
    page: int
    page_size: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return asdict(self)


@dataclass
class BankingListResponse:
    """Standardized list response structure with pagination."""
    
    data: List[Any]
    total_count: int
    page: int
    page_size: int
    has_next: bool
    has_previous: bool
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        result = asdict(self)
        # Convert data items to dict format if they have to_dict method
        result['data'] = [
            item.to_dict() if hasattr(item, 'to_dict') else item 
            for item in self.data
        ]
        return result


@dataclass
class BankingSuccessResponse:
    """Standardized success response structure."""
    
    success: bool = True
    message: Optional[str] = None
    data: Optional[Any] = None
    timestamp: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        result = asdict(self)
        if self.timestamp:
            result['timestamp'] = self.timestamp.isoformat()
        if self.data and hasattr(self.data, 'to_dict'):
            result['data'] = self.data.to_dict()
        return result


@dataclass
class BankingErrorResponse:
    """Standardized error response structure."""
    
    success: bool = False
    error: BankingError
    timestamp: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        result = asdict(self)
        result['error'] = self.error.to_dict()
        if self.timestamp:
            result['timestamp'] = self.timestamp.isoformat()
        return result


# Response factory functions for consistent formatting
def create_success_response(
    data: Any = None, 
    message: str = "Operation completed successfully"
) -> BankingSuccessResponse:
    """Create a standardized success response."""
    return BankingSuccessResponse(
        success=True,
        message=message,
        data=data,
        timestamp=datetime.utcnow()
    )


def create_error_response(
    code: BankingErrorCode,
    message: str,
    details: Optional[Dict[str, Any]] = None
) -> BankingErrorResponse:
    """Create a standardized error response."""
    error = BankingError(
        code=code,
        message=message,
        details=details,
        timestamp=datetime.utcnow()
    )
    return BankingErrorResponse(
        success=False,
        error=error,
        timestamp=datetime.utcnow()
    )


def create_list_response(
    data: List[Any],
    total_count: int,
    page: int = 1,
    page_size: int = 50
) -> BankingListResponse:
    """Create a standardized list response with pagination."""
    return BankingListResponse(
        data=data,
        total_count=total_count,
        page=page,
        page_size=page_size,
        has_next=(page * page_size) < total_count,
        has_previous=page > 1
    )
