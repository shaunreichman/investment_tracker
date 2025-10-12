## Inputs

def setup_test_data(session):
    """Set up test data using domain methods with proper session management."""
    print("Setting up test data using domain methods...")
    
    # Create company using class method
    company = Company.create(
        name="Alceon",
        description="Alceon Pty Ltd",
        session=session
    )
    
    # Create entity using class method
    entity = Entity.create(
        name="Shaun Reichman",
        description="Personal entity",
        session=session
    )
    
    # Create company for shares using class method
    company_shares = Company.create(
        name="Shares",
        description="Share trading",
        session=session
    )
    
    # Create Senior Debt Fund No.24 using direct object method
    senior_debt_fund = company.create_fund(
        entity=entity,  # Pass entity object, not ID
        name="Senior Debt Fund No.24",
        fund_type="Private Debt",
        tracking_type=FundType.COST_BASED,
        commitment_amount=100000.0,
        expected_irr=10.0,
        expected_duration_months=48,
        currency="AUD",
        description="Senior Debt Fund No.24",
        session=session
    )
    
    # Create 3PG Finance (Cost-based) using direct object method
    finance_fund = company.create_fund(
        entity=entity,  # Pass entity object, not ID
        name="3PG Finance",
        fund_type="Private Debt",
        tracking_type=FundType.COST_BASED,
        commitment_amount=100000.0,
        expected_irr=10.0,
        expected_duration_months=48,
        currency="AUD",
        description="3PG Finance debt fund",
        session=session
    )
    
    # Create NAV-based test fund using direct object method
    abc_fund = company_shares.create_fund(
        entity=entity,  # Pass entity object, not ID
        name="ABC Ltd",
        fund_type="Equity - Consumer Discretionary",
        tracking_type=FundType.NAV_BASED,
        currency="AUD",
        description="ABC Ltd on the ASX",
        session=session
    )
    
    # Add events for Senior Debt Fund No.24 using domain methods
    print("Adding Senior Debt Fund events using domain methods...")
    
    # Add capital call
    senior_debt_fund.add_capital_call(
        amount=100000.0,
        date=date(2023, 6, 23),
        description="Initial capital call",
        session=session
    )
    debug_average_equity_after_event(senior_debt_fund, "Senior Debt Fund capital call", session)
    
    # Add returns of capital
    senior_debt_fund.add_return_of_capital(
        amount=7000.0,
        date=date(2023, 12, 8),
        description="Return of capital",
        session=session
    )
    debug_average_equity_after_event(senior_debt_fund, "Senior Debt Fund return of capital 1", session)
    senior_debt_fund.add_return_of_capital(
        amount=45000.0,
        date=date(2024, 3, 26),
        description="Partial exit distribution",
        session=session
    )
    debug_average_equity_after_event(senior_debt_fund, "Senior Debt Fund return of capital 2", session)
    senior_debt_fund.add_return_of_capital(
        amount=48000.0,
        date=date(2024, 8, 2),
        description="Return of capital",
        session=session
    )
    debug_average_equity_after_event(senior_debt_fund, "Senior Debt Fund return of capital 3", session)
    
    # Add distribution events with tax using domain methods
    print("Adding Senior Debt Fund distributions with tax...")
    senior_debt_fund.add_distribution(
        event_date=date(2023, 10, 20),
        distribution_type=DistributionType.INTEREST,
        gross_interest_amount=3030.62,
        withholding_tax_rate=10.0,
        has_withholding_tax=True,
        description="Interest distribution",
        session=session
    )
    debug_average_equity_after_event(senior_debt_fund, "Senior Debt Fund distribution 1", session)
    senior_debt_fund.add_distribution(
        event_date=date(2024, 1, 16),
        distribution_type=DistributionType.INTEREST,
        gross_interest_amount=2836.98,
        withholding_tax_rate=10.0,
        has_withholding_tax=True,
        description="Interest distribution",
        session=session
    )
    debug_average_equity_after_event(senior_debt_fund, "Senior Debt Fund distribution 2", session)
    senior_debt_fund.add_distribution(
        event_date=date(2024, 3, 26),
        distribution_type=DistributionType.INTEREST,
        gross_interest_amount=2630.16,
        withholding_tax_rate=10.0,
        has_withholding_tax=True,
        description="Interest distribution",
        session=session
    )
    debug_average_equity_after_event(senior_debt_fund, "Senior Debt Fund distribution 3", session)
    senior_debt_fund.add_distribution(
        event_date=date(2024, 7, 9),
        distribution_type=DistributionType.INTEREST,
        gross_interest_amount=1392.19,
        withholding_tax_amount=139.22,
        has_withholding_tax=True,
        description="Interest distribution",
        session=session
    )
    debug_average_equity_after_event(senior_debt_fund, "Senior Debt Fund distribution 4", session)
    senior_debt_fund.add_distribution(
        event_date=date(2024, 8, 2),
        distribution_type=DistributionType.INTEREST,
        gross_interest_amount=509.84,
        withholding_tax_rate=10.0,
        has_withholding_tax=True,
        description="Interest distribution",
        session=session
    )
    debug_average_equity_after_event(senior_debt_fund, "Senior Debt Fund distribution 5", session)
    
    # Add events for 3PG Finance using domain methods
    print("Adding 3PG Finance events using domain methods...")
    
    # Add capital call
    finance_fund.add_capital_call(
        amount=100000.0,
        date=date(2022, 11, 24),
        description="Initial capital call",
        session=session
    )
    debug_average_equity_after_event(finance_fund, "3PG Finance capital call", session)
    
    # Add returns of capital
    finance_fund.add_return_of_capital(
        amount=7324.42,
        date=date(2023, 3, 24),
        description="Return of capital",
        session=session
    )
    debug_average_equity_after_event(finance_fund, "3PG Finance return of capital 1", session)
    finance_fund.add_return_of_capital(
        amount=26326.88,
        date=date(2023, 7, 7),
        description="Partial exit distribution",
        session=session
    )
    finance_fund.add_return_of_capital(
        amount=8527.53,
        date=date(2023, 8, 4),
        description="Return of capital",
        session=session
    )
    finance_fund.add_return_of_capital(
        amount=8805.21,
        date=date(2023, 9, 22),
        description="Return of capital",
        session=session
    )
    finance_fund.add_return_of_capital(
        amount=9814.74,
        date=date(2023, 10, 13),
        description="Return of capital",
        session=session
    )
    finance_fund.add_return_of_capital(
        amount=6967.81,
        date=date(2023, 11, 21),
        description="Return of capital",
        session=session
    )
    finance_fund.add_return_of_capital(
        amount=32233.41,
        date=date(2024, 4, 19),
        description="Final return of capital",
        session=session
    )
    
    # Add distribution events with tax using domain methods
    print("Adding 3PG Finance distributions with tax...")
    # First distribution (no tax)
    finance_fund.add_distribution(
        event_date=date(2023, 3, 24),
        distribution_type=DistributionType.INTEREST,
        distribution_amount=3075.58,
        description="Interest distribution",
        session=session
    )
    # Remaining distributions (with 10% tax)
    finance_fund.add_distribution(
        event_date=date(2023, 7, 7),
        distribution_type=DistributionType.INTEREST,
        gross_interest_amount=4472.36,
        withholding_tax_rate=10.0,
        has_withholding_tax=True,
        description="Interest distribution",
        session=session
    )
    finance_fund.add_distribution(
        event_date=date(2023, 8, 4),
        distribution_type=DistributionType.INTEREST,
        gross_interest_amount=871.63,
        withholding_tax_rate=10.0,
        has_withholding_tax=True,
        description="Interest distribution",
        session=session
    )
    finance_fund.add_distribution(
        event_date=date(2023, 9, 22),
        distribution_type=DistributionType.INTEREST,
        gross_interest_amount=794.21,
        withholding_tax_amount=79.42,
        has_withholding_tax=True,
        description="Interest distribution",
        session=session
    )
    finance_fund.add_distribution(
        event_date=date(2023, 10, 13),
        distribution_type=DistributionType.INTEREST,
        gross_interest_amount=684.73,
        withholding_tax_rate=10.0,
        has_withholding_tax=True,
        description="Interest distribution",
        session=session
    )
    finance_fund.add_distribution(
        event_date=date(2023, 11, 21),
        distribution_type=DistributionType.INTEREST,
        gross_interest_amount=531.32,
        withholding_tax_amount=53.13,
        has_withholding_tax=True,
        description="Interest distribution",
        session=session
    )
    finance_fund.add_distribution(
        event_date=date(2024, 4, 19),
        distribution_type=DistributionType.INTEREST,
        gross_interest_amount=4399.27,
        withholding_tax_rate=10.0,
        has_withholding_tax=True,
        description="Interest distribution",
        session=session
    )
    
    # Add events for ABC Ltd NAV-based fund (match original test)
    # Initial unit purchase
    abc_fund.add_unit_purchase(
        units_purchased=85.0,
        unit_price=58.00,
        date=date(2013, 3, 28),
        brokerage_fee=19.95,
        description="Initial unit purchase",
        session=session
    )
    # NAV updates
    abc_fund.add_nav_update(
        nav_per_share=57.20,
        date=date(2013, 3, 31),
        description="March 2013 NAV update",
        session=session
    )
    abc_fund.add_nav_update(
        nav_per_share=55.80,
        date=date(2013, 4, 30),
        description="April 2013 NAV update",
        session=session
    )
    abc_fund.add_nav_update(
        nav_per_share=55.18,
        date=date(2013, 5, 31),
        description="May 2013 NAV update",
        session=session
    )
    abc_fund.add_nav_update(
        nav_per_share=52.37,
        date=date(2013, 6, 30),
        description="June 2013 NAV update",
        session=session
    )
    abc_fund.add_nav_update(
        nav_per_share=57.51,
        date=date(2013, 7, 31),
        description="July 2013 NAV update",
        session=session
    )
    abc_fund.add_nav_update(
        nav_per_share=58.30,
        date=date(2013, 8, 31),
        description="August 2013 NAV update",
        session=session
    )
    # Partial unit sale
    abc_fund.add_unit_sale(
        units_sold=40.0,
        unit_price=61.20,
        date=date(2013, 9, 4),
        brokerage_fee=24.95,
        description="Partial unit sale",
        session=session
    )
    # Distribution
    abc_fund.add_distribution(
        event_date=date(2013, 9, 12),
        distribution_type=DistributionType.DIVIDEND_FRANKED,
        distribution_amount=79.05,
        description="Fully Franked Dividend",
        session=session
    )
    # More NAV updates
    abc_fund.add_nav_update(
        nav_per_share=59.30,
        date=date(2013, 9, 30),
        description="September 2013 NAV update",
        session=session
    )
    abc_fund.add_nav_update(
        nav_per_share=53.30,
        date=date(2013, 10, 31),
        description="October 2013 NAV update",
        session=session
    )
    abc_fund.add_nav_update(
        nav_per_share=54.30,
        date=date(2013, 11, 30),
        description="November 2013 NAV update",
        session=session
    )
    abc_fund.add_nav_update(
        nav_per_share=48.30,
        date=date(2013, 12, 31),
        description="December 2013 NAV update",
        session=session
    )
    abc_fund.add_nav_update(
        nav_per_share=59.30,
        date=date(2014, 1, 31),
        description="January 2014 NAV update",
        session=session
    )
    abc_fund.add_nav_update(
        nav_per_share=54.30,
        date=date(2014, 2, 28),
        description="February 2014 NAV update",
        session=session
    )
    abc_fund.add_nav_update(
        nav_per_share=56.30,
        date=date(2014, 3, 31),
        description="March 2014 NAV update",
        session=session
    )
    # Additional unit purchase
    abc_fund.add_unit_purchase(
        units_purchased=120.0,
        unit_price=61.4,
        date=date(2014, 4, 30),
        brokerage_fee=19.95,
        description="Additional unit purchase",
        session=session
    )
    # NAV update on same date as purchase
    abc_fund.add_nav_update(
        nav_per_share=61.25,
        date=date(2014, 4, 30),
        description="April 2014 NAV update",
        session=session
    )
    # Final unit sale
    abc_fund.add_unit_sale(
        units_sold=165.0,
        unit_price=62.62,
        date=date(2014, 5, 13),
        brokerage_fee=19.95,
        description="Full unit sale",
        session=session
    )
    
    # Add tax statements using domain methods (copied from original test)
    # Senior Debt Fund No.24 Tax Statements
    senior_debt_fund.create_or_update_tax_statement(
        entity_id=entity.id,
        financial_year="2022-23",
        notes="FY23 tax statement from fund manager",
        accountant='Findex',
        statement_date=date(2024, 8, 24),
        interest_income_tax_rate=10.0,
        eofy_debt_interest_deduction_rate=32.5,
        session=session
    )
    senior_debt_fund.create_or_update_tax_statement(
        entity_id=entity.id,
        financial_year="2023-24",
        notes="FY24 tax statement from fund manager",
        interest_received_in_cash=8499.98,
        interest_non_resident_withholding_tax_from_statement=852.0,
        accountant='Findex',
        statement_date=date(2024, 8, 12),
        interest_income_tax_rate=10.0,
        eofy_debt_interest_deduction_rate=32.5,
        session=session
    )
    # 3PG Finance Tax Statements
    finance_fund.create_or_update_tax_statement(
        entity_id=entity.id,
        financial_year="2022-23",
        notes="FY23 tax statement from fund manager",
        interest_received_in_cash=3075.58,
        accountant='Findex',
        statement_date=date(2024, 8, 24),
        interest_income_tax_rate=10.0,
        eofy_debt_interest_deduction_rate=32.5,
        session=session
    )
    finance_fund.create_or_update_tax_statement(
        entity_id=entity.id,
        financial_year="2023-24",
        notes="FY24 tax statement from fund manager",
        interest_received_in_cash=10763.96,
        interest_non_resident_withholding_tax_from_statement=1076.4,
        accountant='Findex',
        statement_date=date(2024, 8, 12),
        interest_income_tax_rate=10.0,
        eofy_debt_interest_deduction_rate=32.5,
        session=session
    )
    # ABC Ltd Tax Statements (NAV-based fund)
    abc_tax_statement_2012_13 = abc_fund.create_or_update_tax_statement(
        entity_id=entity.id,
        financial_year="2012-13",
        notes="FY13 tax statement from fund manager",
        accountant='Findex',
        statement_date=date(2024, 8, 24),
        eofy_debt_interest_deduction_rate=32.5,
        session=session
    )
    abc_tax_statement_2013_14 = abc_fund.create_or_update_tax_statement(
        entity_id=entity.id,
        financial_year="2013-14",
        notes="FY14 tax statement from fund manager",
        accountant='Findex',
        statement_date=date(2024, 8, 12),
        capital_gain_income_tax_rate=30,
        eofy_debt_interest_deduction_rate=32.5,
        session=session
    )


## Expected Results

Starting comprehensive system test...
Demonstrating proper session management architecture:
- Outermost backend layer manages sessions
- Domain methods accept session parameters
- No direct database operations from external clients

1. Clearing database (preserving Risk Free Rates)...
Cleared tax_statements
Cleared fund_events
Cleared funds
Cleared entities
Cleared companies
Database cleared (Risk Free Rates preserved)

2. Setting up test data...
Setting up test data using domain methods...
Adding Senior Debt Fund events using domain methods...
  [IRR] Fund 'Senior Debt Fund No.24' REALIZED - gross IRR: None
Fund 'Senior Debt Fund No.24' status updated: active → realized
Adding Senior Debt Fund distributions with tax...
Adding 3PG Finance events using domain methods...
  [IRR] Fund '3PG Finance' REALIZED - gross IRR: None
Fund '3PG Finance' status updated: active → realized
Adding 3PG Finance distributions with tax...
  [IRR] Fund 'ABC Ltd' REALIZED - gross IRR: 11.43%
Fund 'ABC Ltd' status updated: active → realized
  [IRR] Fund 'Senior Debt Fund No.24' REALIZED - gross IRR: 11.92%
Fund 'Senior Debt Fund No.24' tax statement added, but remains realized - IRRs recalculated
  [IRR] Fund 'Senior Debt Fund No.24' REALIZED - gross IRR: 11.92%
Fund 'Senior Debt Fund No.24' tax statement added, but remains realized - IRRs recalculated
  [IRR] Fund '3PG Finance' REALIZED - gross IRR: 16.54%
Fund '3PG Finance' tax statement added, but remains realized - IRRs recalculated
Created 512 daily risk-free interest charge events for 3PG Finance
  [IRR] Fund '3PG Finance' COMPLETED - gross: 16.54%, after-tax: 15.22%, real: 11.17%
Fund '3PG Finance' status updated: realized → completed (final tax statement received)
  [IRR] Fund 'ABC Ltd' REALIZED - gross IRR: 11.43%
Fund 'ABC Ltd' tax statement added, but remains realized - IRRs recalculated
Created 411 daily risk-free interest charge events for ABC Ltd
  [IRR] Fund 'ABC Ltd' COMPLETED - gross: 11.43%, after-tax: 11.43%, real: 8.64%
Fund 'ABC Ltd' status updated: realized → completed (final tax statement received)
ABC Ltd capital gain for 2013-14: 397.50 (discount: 196.35, tax: 119.25)
Test data setup complete!
Created 2 funds for Alceon
Created 1 funds for Shares
Funds after setup: ['1: Senior Debt Fund No.24', '2: 3PG Finance', '3: ABC Ltd']

Initial fund state:
  Senior Debt Fund No.24: equity=$0.00, avg=$81598.52
  3PG Finance: equity=$0.00, avg=$66045.18
  ABC Ltd: equity=$0.00, avg=$3746.21

4. Verifying results...
Funds at verification: ['1: Senior Debt Fund No.24', '2: 3PG Finance', '3: ABC Ltd']

=== VERIFICATION RESULTS ===

Funds found: 3

Senior Debt Fund No.24:
  Type: cost_based
  Current equity: $0.00
  Average equity: $81,598.52
  Status: REALIZED
  Events: {'capital_call': 1, 'return_of_capital': 3, 'distribution': 5, 'tax_payment': 5}
  Tax payment events: 5
  EOFY debt cost events: 0
  Daily interest charges: 0

3PG Finance:
  Type: cost_based
  Current equity: $0.00
  Average equity: $66,045.18
  Status: COMPLETED
  Events: {'capital_call': 1, 'return_of_capital': 7, 'distribution': 7, 'tax_payment': 6, 'daily_risk_free_interest_charge': 512}
  Tax payment events: 6
  EOFY debt cost events: 0
  Daily interest charges: 512

ABC Ltd:
  Type: nav_based
  Current equity: $0.00
  Average equity: $3,746.21
  Status: COMPLETED
  Events: {'unit_purchase': 2, 'nav_update': 14, 'unit_sale': 2, 'distribution': 1, 'daily_risk_free_interest_charge': 411}
  Tax payment events: 0
  EOFY debt cost events: 0
  Daily interest charges: 411
  Current units: 0.00
  Current unit price: $62.6200
  NAV update events: 14
  Unit purchases: 2, Unit sales: 2

Risk-free rates preserved: 88
Total events in database: 977
Tax statements: 6

=== Equity Balance Over Time: Senior Debt Fund No.24 ===
2023-06-23 | CAPITAL_CALL    | Equity:   100,000.00 | Days: 168
2023-12-08 | RETURN_OF_CAPITAL | Equity:    93,000.00 | Days: 109
2024-03-26 | RETURN_OF_CAPITAL | Equity:    48,000.00 | Days: 129
2024-08-02 | RETURN_OF_CAPITAL | Equity:         0.00 | Days: 0

=== Equity Balance Over Time: 3PG Finance ===
2022-11-24 | CAPITAL_CALL    | Equity:   100,000.00 | Days: 120
2023-03-24 | RETURN_OF_CAPITAL | Equity:    92,675.58 | Days: 105
2023-07-07 | RETURN_OF_CAPITAL | Equity:    66,348.70 | Days: 28
2023-08-04 | RETURN_OF_CAPITAL | Equity:    57,821.17 | Days: 49
2023-09-22 | RETURN_OF_CAPITAL | Equity:    49,015.96 | Days: 21
2023-10-13 | RETURN_OF_CAPITAL | Equity:    39,201.22 | Days: 39
2023-11-21 | RETURN_OF_CAPITAL | Equity:    32,233.41 | Days: 150
2024-04-19 | RETURN_OF_CAPITAL | Equity:         0.00 | Days: 0

=== Equity Balance Over Time: ABC Ltd ===
2013-03-28 | UNIT_PURCHASE   | Equity:     4,930.00 | Days: 160
2013-09-04 | UNIT_SALE       | Equity:     2,610.00 | Days: 238
2014-04-30 | UNIT_PURCHASE   | Equity:     9,978.00 | Days: 13
2014-05-13 | UNIT_SALE       | Equity:         0.00 | Days: 0

3. Printing all derived values and summaries...
Funds to print: ['1: Senior Debt Fund No.24', '2: 3PG Finance', '3: ABC Ltd']
Number of funds to print: 3

Summary for Senior Debt Fund No.24:
  Current Equity Balance: $0.00
  Average Equity Balance: $81,598.52
  Status: FundStatus.REALIZED
  End Date: 2024-08-02
Created 406 daily risk-free interest charge events for Senior Debt Fund No.24
Created 2 FY debt cost events for Senior Debt Fund No.24
  [IRR] Fund 'Senior Debt Fund No.24' REALIZED - gross IRR: 11.92%
Fund 'Senior Debt Fund No.24' status unchanged (realized) but IRRs recalculated
  IRR: 11.92%
  After-Tax IRR: None
  Real IRR: None
  IRR Cash Flows:
    capital_call | 2023-06-23 | 100,000.00 | Initial capital call: $-100,000.00
    distribution | 2023-10-20 | 3,030.62 | Interest distribution: $3,030.62
    return_of_capital | 2023-12-08 | 7,000.00 | Return of capital: $7,000.00
    distribution | 2024-01-16 | 2,836.98 | Interest distribution: $2,836.98
    return_of_capital | 2024-03-26 | 45,000.00 | Partial exit distribution: $45,000.00
    distribution | 2024-03-26 | 2,630.16 | Interest distribution: $2,630.16
    distribution | 2024-07-09 | 1,392.19 | Interest distribution: $1,392.19
    return_of_capital | 2024-08-02 | 48,000.00 | Return of capital: $48,000.00
    distribution | 2024-08-02 | 509.84 | Interest distribution: $509.84

Summary for 3PG Finance:
  Current Equity Balance: $0.00
  Average Equity Balance: $66,045.18
  Status: FundStatus.COMPLETED
  End Date: 2024-04-19
Created 2 FY debt cost events for 3PG Finance
  [IRR] Fund '3PG Finance' COMPLETED - gross: 16.54%, after-tax: 14.86%, real: 12.05%
Fund '3PG Finance' status unchanged (completed) but IRRs recalculated
  IRR: 16.54%
  After-Tax IRR: 14.86%
  Real IRR: 12.05%
  IRR Cash Flows:
    capital_call | 2022-11-24 | 100,000.00 | Initial capital call: $-100,000.00
    return_of_capital | 2023-03-24 | 7,324.42 | Return of capital: $7,324.42
    distribution | 2023-03-24 | 3,075.58 | Interest distribution: $3,075.58
    return_of_capital | 2023-07-07 | 26,326.88 | Partial exit distribution: $26,326.88
    distribution | 2023-07-07 | 4,472.36 | Interest distribution: $4,472.36
    return_of_capital | 2023-08-04 | 8,527.53 | Return of capital: $8,527.53
    distribution | 2023-08-04 | 871.63 | Interest distribution: $871.63
    return_of_capital | 2023-09-22 | 8,805.21 | Return of capital: $8,805.21
    distribution | 2023-09-22 | 794.21 | Interest distribution: $794.21
    return_of_capital | 2023-10-13 | 9,814.74 | Return of capital: $9,814.74
    distribution | 2023-10-13 | 684.73 | Interest distribution: $684.73
    return_of_capital | 2023-11-21 | 6,967.81 | Return of capital: $6,967.81
    distribution | 2023-11-21 | 531.32 | Interest distribution: $531.32
    return_of_capital | 2024-04-19 | 32,233.41 | Final return of capital: $32,233.41
    distribution | 2024-04-19 | 4,399.27 | Interest distribution: $4,399.27

Summary for ABC Ltd:
  Current Equity Balance: $0.00
  Average Equity Balance: $3,746.21
  Status: FundStatus.COMPLETED
  End Date: 2014-05-13
Created 2 FY debt cost events for ABC Ltd
  [IRR] Fund 'ABC Ltd' COMPLETED - gross: 11.43%, after-tax: 8.63%, real: 6.73%
Fund 'ABC Ltd' status unchanged (completed) but IRRs recalculated
  IRR: 11.43%
  After-Tax IRR: 8.63%
  Real IRR: 6.73%
  IRR Cash Flows:
    unit_purchase | 2013-03-28 | 4,949.95 | Initial unit purchase: $-4,949.95
    unit_sale | 2013-09-04 | 2,423.05 | Partial unit sale: $2,423.05
    distribution | 2013-09-12 | 79.05 | Fully Franked Dividend: $79.05
    unit_purchase | 2014-04-30 | 7,387.95 | Additional unit purchase: $-7,387.95
    unit_sale | 2014-05-13 | 10,312.35 | Full unit sale: $10,312.35