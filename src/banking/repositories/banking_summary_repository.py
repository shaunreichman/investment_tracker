"""
Banking Summary Repository.

This repository provides data access operations for banking summary data
and aggregated calculations, implementing the repository pattern for clean
separation of concerns.

Key responsibilities:
- Banking summary data and statistics
- Aggregated calculations across banks and accounts
- Cross-module data access for reporting
- Performance-optimized summary queries
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, asc

from src.banking.models import Bank, BankAccount


class BankingSummaryRepository:
    """
    Repository for banking summary data and aggregated calculations.
    
    This repository handles all summary and aggregated operations for banking
    data including statistics, reporting data, and cross-module information.
    It provides a clean interface for business logic components to access
    summary data without direct database access.
    
    Attributes:
        _cache (Dict): Internal cache for frequently accessed summary data
        _cache_ttl (int): Time-to-live for cached data in seconds
    """
    
    def __init__(self, cache_ttl: int = 300):
        """
        Initialize the banking summary repository.
        
        Args:
            cache_ttl: Time-to-live for cached data in seconds (default: 5 minutes)
        """
        self._cache: Dict[str, Any] = {}
        self._cache_ttl = cache_ttl
    
    def get_banking_overview(self, session: Session) -> Dict[str, Any]:
        """
        Get comprehensive banking overview statistics.
        
        Args:
            session: Database session
            
        Returns:
            Dictionary containing banking overview statistics
        """
        cache_key = "banking:overview"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Get total counts
        total_banks = session.query(Bank).count()
        total_accounts = session.query(BankAccount).count()
        active_accounts = session.query(BankAccount).filter(BankAccount.is_active == True).count()
        inactive_accounts = session.query(BankAccount).filter(BankAccount.is_active == False).count()
        
        # Get currency distribution
        currency_counts = session.query(
            BankAccount.currency,
            func.count(BankAccount.id).label('count')
        ).group_by(BankAccount.currency).all()
        
        # Get country distribution
        country_counts = session.query(
            Bank.country,
            func.count(Bank.id).label('count')
        ).group_by(Bank.country).all()
        
        # Format overview data
        overview = {
            'total_banks': total_banks,
            'total_accounts': total_accounts,
            'active_accounts': active_accounts,
            'inactive_accounts': inactive_accounts,
            'currency_distribution': {currency: count for currency, count in currency_counts},
            'country_distribution': {country: count for country, count in country_counts}
        }
        
        # Cache the result
        self._cache[cache_key] = overview
        
        return overview
    
    def get_bank_summary(self, bank_id: int, session: Session) -> Dict[str, Any]:
        """
        Get summary information for a specific bank.
        
        Args:
            bank_id: Bank ID
            session: Database session
            
        Returns:
            Dictionary containing bank summary information
        """
        cache_key = f"banking:bank_summary:{bank_id}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Get bank information
        bank = session.query(Bank).filter(Bank.id == bank_id).first()
        if not bank:
            return {}
        
        # Get account counts and currency distribution
        account_stats = session.query(
            BankAccount.currency,
            BankAccount.is_active,
            func.count(BankAccount.id).label('count')
        ).filter(BankAccount.bank_id == bank_id).group_by(
            BankAccount.currency, BankAccount.is_active
        ).all()
        
        # Format account statistics
        currency_stats = {}
        active_count = 0
        inactive_count = 0
        
        for currency, is_active, count in account_stats:
            if currency not in currency_stats:
                currency_stats[currency] = {'active': 0, 'inactive': 0}
            
            if is_active:
                currency_stats[currency]['active'] = count
                active_count += count
            else:
                currency_stats[currency]['inactive'] = count
                inactive_count += count
        
        # Format summary data
        summary = {
            'bank_id': bank.id,
            'bank_name': bank.name,
            'bank_country': bank.country,
            'bank_swift_bic': bank.swift_bic,
            'total_accounts': active_count + inactive_count,
            'active_accounts': active_count,
            'inactive_accounts': inactive_count,
            'currency_distribution': currency_stats
        }
        
        # Cache the result
        self._cache[cache_key] = summary
        
        return summary
    
    def get_entity_banking_summary(self, entity_id: int, session: Session) -> Dict[str, Any]:
        """
        Get banking summary for a specific entity.
        
        Args:
            entity_id: Entity ID
            session: Database session
            
        Returns:
            Dictionary containing entity banking summary
        """
        cache_key = f"banking:entity_summary:{entity_id}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Get account counts and bank distribution
        account_stats = session.query(
            BankAccount.bank_id,
            BankAccount.currency,
            BankAccount.is_active,
            func.count(BankAccount.id).label('count')
        ).filter(BankAccount.entity_id == entity_id).group_by(
            BankAccount.bank_id, BankAccount.currency, BankAccount.is_active
        ).all()
        
        # Get bank information
        bank_ids = list(set(stat[0] for stat in account_stats))
        banks = session.query(Bank).filter(Bank.id.in_(bank_ids)).all()
        bank_map = {bank.id: bank for bank in banks}
        
        # Format account statistics
        bank_stats = {}
        currency_stats = {}
        active_count = 0
        inactive_count = 0
        
        for bank_id, currency, is_active, count in account_stats:
            # Bank statistics
            if bank_id not in bank_stats:
                bank_stats[bank_id] = {
                    'bank_name': bank_map.get(bank_id, {}).get('name', 'Unknown'),
                    'bank_country': bank_map.get(bank_id, {}).get('country', 'Unknown'),
                    'accounts': {'active': 0, 'inactive': 0}
                }
            
            if is_active:
                bank_stats[bank_id]['accounts']['active'] += count
                active_count += count
            else:
                bank_stats[bank_id]['accounts']['inactive'] += count
                inactive_count += count
            
            # Currency statistics
            if currency not in currency_stats:
                currency_stats[currency] = {'active': 0, 'inactive': 0}
            
            if is_active:
                currency_stats[currency]['active'] += count
            else:
                currency_stats[currency]['inactive'] += count
        
        # Format summary data
        summary = {
            'entity_id': entity_id,
            'total_accounts': active_count + inactive_count,
            'active_accounts': active_count,
            'inactive_accounts': inactive_count,
            'bank_distribution': bank_stats,
            'currency_distribution': currency_stats
        }
        
        # Cache the result
        self._cache[cache_key] = summary
        
        return summary
    
    def get_currency_summary(self, session: Session) -> Dict[str, Any]:
        """
        Get summary information for all currencies.
        
        Args:
            session: Database session
            
        Returns:
            Dictionary containing currency summary information
        """
        cache_key = "banking:currency_summary"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Get currency statistics
        currency_stats = session.query(
            BankAccount.currency,
            BankAccount.is_active,
            func.count(BankAccount.id).label('count')
        ).group_by(BankAccount.currency, BankAccount.is_active).all()
        
        # Format currency statistics
        currency_summary = {}
        for currency, is_active, count in currency_stats:
            if currency not in currency_summary:
                currency_summary[currency] = {'active': 0, 'inactive': 0}
            
            if is_active:
                currency_summary[currency]['active'] = count
            else:
                currency_summary[currency]['inactive'] = count
        
        # Add totals
        for currency in currency_summary:
            currency_summary[currency]['total'] = (
                currency_summary[currency]['active'] + 
                currency_summary[currency]['inactive']
            )
        
        # Cache the result
        self._cache[cache_key] = currency_summary
        
        return currency_summary
    
    def get_country_summary(self, session: Session) -> Dict[str, Any]:
        """
        Get summary information for all countries.
        
        Args:
            session: Database session
            
        Returns:
            Dictionary containing country summary information
        """
        cache_key = "banking:country_summary"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Get country statistics
        country_stats = session.query(
            Bank.country,
            func.count(Bank.id).label('bank_count'),
            func.count(BankAccount.id).label('account_count')
        ).outerjoin(Bank.accounts).group_by(Bank.country).all()
        
        # Format country statistics
        country_summary = {}
        for country, bank_count, account_count in country_stats:
            country_summary[country] = {
                'bank_count': bank_count,
                'account_count': account_count
            }
        
        # Cache the result
        self._cache[cache_key] = country_summary
        
        return country_summary
    
    def get_top_banks_by_accounts(self, session: Session, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get top banks by number of accounts.
        
        Args:
            limit: Maximum number of banks to return
            session: Database session
            
        Returns:
            List of top banks with account counts
        """
        cache_key = f"banking:top_banks:{limit}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Query top banks
        top_banks = session.query(
            Bank,
            func.count(BankAccount.id).label('account_count')
        ).outerjoin(Bank.accounts).group_by(Bank.id).order_by(
            desc(func.count(BankAccount.id))
        ).limit(limit).all()
        
        # Format result
        result = []
        for bank, account_count in top_banks:
            bank_data = {
                'bank_id': bank.id,
                'bank_name': bank.name,
                'bank_country': bank.country,
                'account_count': account_count
            }
            result.append(bank_data)
        
        # Cache the result
        self._cache[cache_key] = result
        
        return result
    
    def get_banking_activity_summary(self, session: Session) -> Dict[str, Any]:
        """
        Get banking activity summary for reporting.
        
        Args:
            session: Database session
            
        Returns:
            Dictionary containing banking activity summary
        """
        cache_key = "banking:activity_summary"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Get various statistics
        total_banks = session.query(Bank).count()
        total_accounts = session.query(BankAccount).count()
        active_accounts = session.query(BankAccount).filter(BankAccount.is_active == True).count()
        
        # Get unique currencies and countries
        unique_currencies = session.query(BankAccount.currency).distinct().count()
        unique_countries = session.query(Bank.country).distinct().count()
        
        # Get accounts per bank average
        accounts_per_bank = session.query(
            func.avg(func.count(BankAccount.id))
        ).join(Bank.accounts).group_by(Bank.id).scalar() or 0
        
        # Format activity summary
        activity_summary = {
            'total_banks': total_banks,
            'total_accounts': total_accounts,
            'active_accounts': active_accounts,
            'inactive_accounts': total_accounts - active_accounts,
            'unique_currencies': unique_currencies,
            'unique_countries': unique_countries,
            'accounts_per_bank_avg': round(accounts_per_bank, 2),
            'activity_rate': round((active_accounts / total_accounts * 100) if total_accounts > 0 else 0, 2)
        }
        
        # Cache the result
        self._cache[cache_key] = activity_summary
        
        return activity_summary
    
    def clear_cache(self) -> None:
        """Clear all caches."""
        self._cache.clear()
    
    def clear_bank_caches(self, bank_id: int) -> None:
        """Clear caches related to a specific bank."""
        keys_to_remove = [key for key in self._cache.keys() if f":{bank_id}" in key]
        for key in keys_to_remove:
            del self._cache[key]
    
    def clear_entity_caches(self, entity_id: int) -> None:
        """Clear caches related to a specific entity."""
        keys_to_remove = [key for key in self._cache.keys() if f":{entity_id}" in key]
        for key in keys_to_remove:
            del self._cache[key]
