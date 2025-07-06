"""
Test utilities for the investment tracker.

This module contains utilities specifically for testing, such as database clearing
and test data setup functions.
"""

from sqlalchemy import text


def clear_database_except_rates(session):
    """
    Clear all data from the database except Risk Free Rates.
    Uses the provided session (managed by outermost layer).
    
    Args:
        session: Database session (managed by outermost backend layer)
    """
    # Get the engine from the session
    engine = session.bind
    
    with engine.connect() as conn:
        # Disable foreign key constraints temporarily
        conn.execute(text("PRAGMA foreign_keys=OFF;"))
        
        # Clear all tables except risk_free_rates
        tables = ['tax_statements', 'fund_events', 'funds', 'entities', 'investment_companies']
        for table in tables:
            conn.execute(text(f"DELETE FROM {table};"))
            print(f"Cleared {table}")
        
        # Re-enable foreign key constraints
        conn.execute(text("PRAGMA foreign_keys=ON;"))
        conn.commit()
    
    print("Database cleared (Risk Free Rates preserved)")


def reset_database_for_testing(session):
    """
    Reset the database to a clean state for testing.
    This is a convenience function that clears all data except reference data.
    
    Args:
        session: Database session (managed by outermost backend layer)
    """
    clear_database_except_rates(session) 