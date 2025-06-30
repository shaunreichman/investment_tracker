#!/usr/bin/env python3
"""
Migration script to add interest expense and deduction fields to tax_statements table.
"""
import sqlite3

db_path = 'data/investment_tracker.db'

ALTERS = [
    "ALTER TABLE tax_statements ADD COLUMN total_interest_expense REAL DEFAULT 0.0;",
    "ALTER TABLE tax_statements ADD COLUMN interest_deduction_rate REAL DEFAULT 0.0;",
    "ALTER TABLE tax_statements ADD COLUMN interest_tax_benefit REAL DEFAULT 0.0;"
]

def main():
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    for stmt in ALTERS:
        try:
            cur.execute(stmt)
            print(f"Executed: {stmt.strip()}")
        except sqlite3.OperationalError as e:
            if 'duplicate column name' in str(e):
                print(f"Column already exists, skipping: {stmt.strip()}")
            else:
                print(f"Error: {e}")
    conn.commit()
    conn.close()
    print("Migration complete.")

if __name__ == "__main__":
    main() 