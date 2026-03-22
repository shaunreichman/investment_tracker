"""
Formatters for Rate objects.

- Provide consistent response structure
"""

from typing import Dict, Any
from src.rates.models.risk_free_rate import RiskFreeRate
from src.rates.models.fx_rate import FxRate

def format_risk_free_rate(risk_free_rate: RiskFreeRate) -> Dict[str, Any]:
    """
    Format a RiskFreeRate object for HTTP response.

    Args:
        risk_free_rate: RiskFreeRate object to format

    Returns:
        Dictionary formatted for HTTP response
    """
    return {
        'id': risk_free_rate.id,
        'currency': risk_free_rate.currency.value if risk_free_rate.currency else None,
        'date': risk_free_rate.date.isoformat() if risk_free_rate.date else None,
        'rate': risk_free_rate.rate,
        'rate_type': risk_free_rate.rate_type.value if risk_free_rate.rate_type else None,
        'source': risk_free_rate.source,
        'created_at': risk_free_rate.created_at.isoformat() if risk_free_rate.created_at else None,
        'updated_at': risk_free_rate.updated_at.isoformat() if risk_free_rate.updated_at else None
    }

def format_fx_rate(fx_rate: FxRate) -> Dict[str, Any]:
    """
    Format a FxRate object for HTTP response.

    Args:
        fx_rate: FxRate object to format

    Returns:
        Dictionary formatted for HTTP response
    """
    return {
        'id': fx_rate.id,
        'from_currency': fx_rate.from_currency.value if fx_rate.from_currency else None,
        'to_currency': fx_rate.to_currency.value if fx_rate.to_currency else None,
        'date': fx_rate.date.isoformat() if fx_rate.date else None,
        'fx_rate': fx_rate.fx_rate,
        'created_at': fx_rate.created_at.isoformat() if fx_rate.created_at else None,
        'updated_at': fx_rate.updated_at.isoformat() if fx_rate.updated_at else None
    }