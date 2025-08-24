#!/usr/bin/env python3
"""
Banking Utilities Runner.

This script provides easy access to common banking maintenance tasks
from within the banking module. Run this from the project root.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from src.database import get_database_session
from src.banking.scripts.cache_warmup import BankingCacheWarmer
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Main utility runner."""
    if len(sys.argv) < 2:
        print("🚀 Banking Utilities Runner")
        print("Usage: python -m src.banking.scripts.run_utilities <command>")
        print("\nAvailable commands:")
        print("  warm-cache     - Warm banking cache with essential data")
        print("  clear-cache    - Clear expired cache entries")
        print("  help           - Show this help message")
        return
    
    command = sys.argv[1].lower()
    
    try:
        if command == "warm-cache":
            warm_banking_cache()
        elif command == "clear-cache":
            clear_expired_cache()
        elif command == "help":
            show_help()
        else:
            print(f"❌ Unknown command: {command}")
            show_help()
            
    except Exception as e:
        logger.error(f"❌ Command failed: {e}")
        sys.exit(1)


def warm_banking_cache():
    """Warm banking cache with essential data."""
    print("🔥 Warming banking cache...")
    
    try:
        engine, session_factory, scoped_session = get_database_session()
        session = scoped_session()
        
        try:
            warmer = BankingCacheWarmer()
            results = warmer.warm_essential_cache(session)
            
            print("✅ Cache warming complete!")
            print(f"   Banks warmed: {results['banks_warmed']}")
            print(f"   Accounts warmed: {results['accounts_warmed']}")
            print(f"   Summaries warmed: {results['summaries_warmed']}")
            
            if results['errors']:
                print(f"   Errors: {len(results['errors'])}")
                for error in results['errors']:
                    print(f"      - {error}")
                    
        finally:
            session.close()
            
    except Exception as e:
        print(f"❌ Cache warming failed: {e}")
        raise


def clear_expired_cache():
    """Clear expired cache entries."""
    print("🧹 Clearing expired cache entries...")
    
    try:
        warmer = BankingCacheWarmer()
        cleared_count = warmer.clear_expired_cache()
        
        print(f"✅ Cleared {cleared_count} expired cache entries")
        
    except Exception as e:
        print(f"❌ Cache cleanup failed: {e}")
        raise


def show_help():
    """Show help information."""
    print("🚀 Banking Utilities Runner")
    print("\nThis script provides easy access to common banking maintenance tasks.")
    print("\nUsage:")
    print("  python -m src.banking.scripts.run_utilities <command>")
    print("\nCommands:")
    print("  warm-cache     - Warm banking cache with essential data")
    print("                  Improves response times for common operations")
    print("                  Run this after system startup or cache clearing")
    print("\n  clear-cache    - Clear expired cache entries")
    print("                  Frees up memory and removes stale data")
    print("                  Run this periodically for maintenance")
    print("\nExamples:")
    print("  python -m src.banking.scripts.run_utilities warm-cache")
    print("  python -m src.banking.scripts.run_utilities clear-cache")


if __name__ == "__main__":
    main()
