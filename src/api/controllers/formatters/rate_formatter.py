"""
Formatters for Rate objects.

- Provide consistent response structure
"""

from typing import Dict, Any
from src.rates.models.risk_free_rate import RiskFreeRate

def format_risk_free_rate(risk_free_rate: RiskFreeRate) -> Dict[str, Any]:
    """
    Format a RiskFreeRate object for HTTP response.
    """
    return {
        'id': risk_free_rate.id,
        'currency': risk_free_rate.currency,
        'date': risk_free_rate.date,
        'rate': risk_free_rate.rate,
        'rate_type': risk_free_rate.rate_type,
        'source': risk_free_rate.source,
        'created_at': risk_free_rate.created_at.isoformat() if risk_free_rate.created_at else None,
        'updated_at': risk_free_rate.updated_at.isoformat() if risk_free_rate.updated_at else None
    }