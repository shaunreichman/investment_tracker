"""
Banking Cache Warming Utilities.

This module provides utilities for warming the banking cache with frequently
accessed data, improving response times for common operations.
"""

import logging
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from src.banking.services.banking_cache_service import get_banking_cache_service
from src.banking.repositories.bank_repository import BankRepository
from src.banking.repositories.bank_account_repository import BankAccountRepository
from src.banking.repositories.banking_summary_repository import BankingSummaryRepository

logger = logging.getLogger(__name__)


class BankingCacheWarmer:
    """
    Utility for warming banking cache with frequently accessed data.
    
    This class pre-loads common banking queries into cache to improve
    response times for typical operations.
    """
    
    def __init__(self):
        """Initialize the cache warmer."""
        self.cache_service = get_banking_cache_service()
        self.bank_repo = BankRepository()
        self.bank_account_repo = BankAccountRepository()
        self.summary_repo = BankingSummaryRepository()
    
    def warm_essential_cache(self, session: Session) -> Dict[str, Any]:
        """
        Warm cache with essential banking data.
        
        Args:
            session: Database session
            
        Returns:
            Dictionary with warming results
        """
        logger.info("🔥 Warming essential banking cache...")
        
        results = {
            'banks_warmed': 0,
            'accounts_warmed': 0,
            'summaries_warmed': 0,
            'errors': []
        }
        
        try:
            # Warm bank data
            results['banks_warmed'] = self._warm_bank_cache(session)
            
            # Warm bank account data
            results['accounts_warmed'] = self._warm_bank_account_cache(session)
            
            # Warm summary data
            results['summaries_warmed'] = self._warm_summary_cache(session)
            
            logger.info(f"✅ Cache warming complete: {results['banks_warmed']} banks, {results['accounts_warmed']} accounts, {results['summaries_warmed']} summaries")
            
        except Exception as e:
            error_msg = f"Cache warming failed: {str(e)}"
            results['errors'].append(error_msg)
            logger.error(error_msg)
        
        return results
    
    def _warm_bank_cache(self, session: Session) -> int:
        """Warm cache with bank data."""
        try:
            # Get all banks
            banks = self.bank_repo.get_all_banks(session)
            
            # Cache individual banks
            for bank in banks:
                cache_key = self.cache_service.get_cache_key('bank', bank.id)
                self.cache_service.set(cache_key, bank, ttl=600)  # 10 minutes
            
            # Cache bank list
            cache_key = self.cache_service.get_cache_key('banks', 'all')
            self.cache_service.set(cache_key, [b.id for b in banks], ttl=300)  # 5 minutes
            
            return len(banks)
            
        except Exception as e:
            logger.warning(f"⚠️ Bank cache warming failed: {e}")
            return 0
    
    def _warm_bank_account_cache(self, session: Session) -> int:
        """Warm cache with bank account data."""
        try:
            # Get all active accounts
            accounts = self.bank_account_repo.get_active_accounts(session)
            
            # Cache individual accounts
            for account in accounts:
                cache_key = self.cache_service.get_cache_key('account', account.id)
                self.cache_service.set(cache_key, account, ttl=600)  # 10 minutes
            
            # Cache account lists by entity
            entity_accounts = {}
            for account in accounts:
                if account.entity_id not in entity_accounts:
                    entity_accounts[account.entity_id] = []
                entity_accounts[account.entity_id].append(account.id)
            
            for entity_id, account_ids in entity_accounts.items():
                cache_key = self.cache_service.get_cache_key('accounts', 'entity', entity_id)
                self.cache_service.set(cache_key, account_ids, ttl=300)  # 5 minutes
            
            return len(accounts)
            
        except Exception as e:
            logger.warning(f"⚠️ Bank account cache warming failed: {e}")
            return 0
    
    def _warm_summary_cache(self, session: Session) -> int:
        """Warm cache with banking summary data."""
        try:
            # Get banking summary
            summary = self.summary_repo.get_banking_summary(session)
            
            if summary:
                cache_key = self.cache_service.get_cache_key('summary', 'banking')
                self.cache_service.set(cache_key, summary, ttl=1800)  # 30 minutes
                return 1
            
            return 0
            
        except Exception as e:
            logger.warning(f"⚠️ Summary cache warming failed: {e}")
            return 0
    
    def warm_entity_cache(self, session: Session, entity_id: int) -> bool:
        """
        Warm cache for a specific entity.
        
        Args:
            session: Database session
            entity_id: Entity ID to warm cache for
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get entity's bank accounts
            accounts = self.bank_account_repo.get_accounts_by_entity(session, entity_id)
            
            # Cache entity's banking data
            cache_key = self.cache_service.get_cache_key('entity', 'banking', entity_id)
            self.cache_service.set(cache_key, {
                'account_count': len(accounts),
                'accounts': [a.id for a in accounts],
                'currencies': list(set(a.currency for a in accounts))
            }, ttl=600)  # 10 minutes
            
            logger.info(f"✅ Entity {entity_id} banking cache warmed")
            return True
            
        except Exception as e:
            logger.warning(f"⚠️ Entity {entity_id} cache warming failed: {e}")
            return False
    
    def clear_expired_cache(self) -> int:
        """
        Clear expired cache entries.
        
        Returns:
            Number of entries cleared
        """
        try:
            # This is a simplified version - in production you might want
            # more sophisticated cache cleanup
            cleared_count = 0
            
            # Clear memory cache expired entries
            current_time = self.cache_service.memory_cache_ttl
            expired_keys = [
                key for key, ttl in current_time.items()
                if ttl < self.cache_service.memory_cache_ttl.get(key, 0)
            ]
            
            for key in expired_keys:
                self.cache_service.delete(key)
                cleared_count += 1
            
            logger.info(f"✅ Cleared {cleared_count} expired cache entries")
            return cleared_count
            
        except Exception as e:
            logger.warning(f"⚠️ Cache cleanup failed: {e}")
            return 0


def warm_banking_cache(session: Session) -> Dict[str, Any]:
    """
    Convenience function to warm banking cache.
    
    Args:
        session: Database session
        
    Returns:
        Dictionary with warming results
    """
    warmer = BankingCacheWarmer()
    return warmer.warm_essential_cache(session)
