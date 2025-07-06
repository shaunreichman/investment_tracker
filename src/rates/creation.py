"""
Rates domain creation and management.

This module contains rates creation and management functions.
"""

from sqlalchemy.orm import Session
from datetime import date
from .models import RiskFreeRate


def create_risk_free_rate(currency, rate_date, rate, rate_type='government_bond', source=None, session=None):
    """
    Create a new risk-free rate.
    
    Args:
        currency (str): Currency code (e.g., 'AUD', 'USD', 'EUR')
        rate_date (date): Date the rate applies to
        rate (float): Risk-free rate as percentage (e.g., 4.5 for 4.5%)
        rate_type (str): Type of rate (e.g., 'government_bond', 'libor', 'sofr')
        source (str, optional): Source of the rate data
        session (Session, optional): Database session
    
    Returns:
        RiskFreeRate: The created risk-free rate
    """
    risk_free_rate = RiskFreeRate(
        currency=currency,
        rate_date=rate_date,
        rate=rate,
        rate_type=rate_type,
        source=source
    )
    
    if session:
        session.add(risk_free_rate)
        session.commit()
    
    return risk_free_rate


def get_risk_free_rates_for_currency(currency, session, start_date=None, end_date=None):
    """
    Get risk-free rates for a specific currency within an optional date range.
    
    Args:
        currency (str): Currency code
        session (Session): Database session
        start_date (date, optional): Start date for filtering
        end_date (date, optional): End date for filtering
    
    Returns:
        list: List of RiskFreeRate objects, sorted by date
    """
    query = session.query(RiskFreeRate).filter(RiskFreeRate.currency == currency)
    
    if start_date:
        query = query.filter(RiskFreeRate.rate_date >= start_date)
    
    if end_date:
        query = query.filter(RiskFreeRate.rate_date <= end_date)
    
    return query.order_by(RiskFreeRate.rate_date).all()


def get_all_risk_free_rates(session, currency=None, start_date=None, end_date=None):
    """
    Get all risk-free rates with optional filtering.
    
    Args:
        session (Session): Database session
        currency (str, optional): Currency code to filter by
        start_date (date, optional): Start date for filtering
        end_date (date, optional): End date for filtering
    
    Returns:
        list: List of RiskFreeRate objects, sorted by currency and date
    """
    query = session.query(RiskFreeRate)
    
    if currency:
        query = query.filter(RiskFreeRate.currency == currency)
    
    if start_date:
        query = query.filter(RiskFreeRate.rate_date >= start_date)
    
    if end_date:
        query = query.filter(RiskFreeRate.rate_date <= end_date)
    
    return query.order_by(RiskFreeRate.currency, RiskFreeRate.rate_date).all()


__all__ = [
    'create_risk_free_rate',
    'get_risk_free_rates_for_currency',
    'get_all_risk_free_rates',
] 