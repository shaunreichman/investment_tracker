/**
 * Fund Domain Enums
 * 
 * TypeScript enums matching backend fund domain enums exactly.
 * Source: src/fund/enums/*.py
 * 
 * DO NOT modify these enums without updating the corresponding Python enums.
 * These must remain in sync with the backend for API communication.
 */

// ============================================================================
// FUND ENUMS
// ============================================================================

/**
 * Fund lifecycle status enum.
 * 
 * Represents the current state of a fund in its lifecycle.
 * 
 * Source: src/fund/enums/fund_enums.py::FundStatus
 */
export enum FundStatus {
  /** Fund has capital at risk and is actively managed */
  ACTIVE = 'ACTIVE',
  /** Fund temporarily suspended/on hold (equity balance may be > 0 but no new activity) */
  SUSPENDED = 'SUSPENDED',
  /** All capital has been returned, fund is realized */
  REALIZED = 'REALIZED',
  /** Fund is realized and all tax obligations are complete */
  COMPLETED = 'COMPLETED',
}

/**
 * Fund tracking type enum.
 * 
 * Determines how the fund tracks and calculates values.
 * 
 * Source: src/fund/enums/fund_enums.py::FundTrackingType
 */
export enum FundTrackingType {
  /** Fund tracks cost basis and commitment amounts */
  COST_BASED = 'COST_BASED',
  /** Fund tracks NAV per share and unit-based calculations */
  NAV_BASED = 'NAV_BASED',
}

/**
 * Fund investment type enum.
 * 
 * Determines the type of investment for a fund.
 * 
 * Source: src/fund/enums/fund_enums.py::FundInvestmentType
 */
export enum FundInvestmentType {
  PRIVATE_EQUITY = 'PRIVATE_EQUITY',
  VENTURE_CAPITAL = 'VENTURE_CAPITAL',
  PRIVATE_DEBT = 'PRIVATE_DEBT',
  REAL_ESTATE = 'REAL_ESTATE',
  INFRASTRUCTURE = 'INFRASTRUCTURE',
  OTHER = 'OTHER',
}

/**
 * Fund tax statement financial year type enum.
 * 
 * Determines the financial year type for tax statements.
 * 
 * Source: src/fund/enums/fund_enums.py::FundTaxStatementFinancialYearType
 */
export enum FundTaxStatementFinancialYearType {
  /** Calendar year (Jan 1 - Dec 31) */
  CALENDAR_YEAR = 'CALENDAR_YEAR',
  /** Half year (Jul 1 - Jun 30 for AU, Apr 6 - Apr 5 for UK) */
  HALF_YEAR = 'HALF_YEAR',
}

/**
 * Sort field enum for funds.
 * 
 * Defines the fields that can be used for sorting in APIs and queries.
 * 
 * Source: src/fund/enums/fund_enums.py::SortFieldFund
 */
export enum SortFieldFund {
  START_DATE = 'START_DATE',
  NAME = 'NAME',
  STATUS = 'STATUS',
  COMMITMENT_AMOUNT = 'COMMITMENT_AMOUNT',
  CURRENT_EQUITY_BALANCE = 'CURRENT_EQUITY_BALANCE',
  CREATED_AT = 'CREATED_AT',
  UPDATED_AT = 'UPDATED_AT',
  EVENT_DATE = 'EVENT_DATE',
}

// ============================================================================
// FUND EVENT ENUMS
// ============================================================================

/**
 * Fund event type enum.
 * 
 * Defines all possible types of events that can occur in a fund.
 * 
 * Source: src/fund/enums/fund_event_enums.py::EventType
 */
export enum EventType {
  /** Capital call event */
  CAPITAL_CALL = 'CAPITAL_CALL',
  /** Return of capital event */
  RETURN_OF_CAPITAL = 'RETURN_OF_CAPITAL',
  /** Distribution event */
  DISTRIBUTION = 'DISTRIBUTION',
  /** Unit purchase event */
  UNIT_PURCHASE = 'UNIT_PURCHASE',
  /** Unit sale event */
  UNIT_SALE = 'UNIT_SALE',
  /** NAV update event */
  NAV_UPDATE = 'NAV_UPDATE',
  /** Daily interest charge */
  DAILY_RISK_FREE_INTEREST_CHARGE = 'DAILY_RISK_FREE_INTEREST_CHARGE',
  /** End of financial year debt cost */
  EOFY_DEBT_COST = 'EOFY_DEBT_COST',
  /** Tax payment event */
  TAX_PAYMENT = 'TAX_PAYMENT',
}

/**
 * Distribution type enum.
 * 
 * Classifies distributions for tax and reporting purposes.
 * 
 * Source: src/fund/enums/fund_event_enums.py::DistributionType
 */
export enum DistributionType {
  /** Ordinary income distribution */
  INCOME = 'INCOME',
  /** Dividend with franking credits (reduces tax liability) */
  DIVIDEND_FRANKED = 'DIVIDEND_FRANKED',
  /** Dividend without franking credits (fully taxable) */
  DIVIDEND_UNFRANKED = 'DIVIDEND_UNFRANKED',
  /** Interest income (fully taxable) */
  INTEREST = 'INTEREST',
  /** Rental income */
  RENT = 'RENT',
  /** Capital gains (may have CGT discount) */
  CAPITAL_GAIN = 'CAPITAL_GAIN',
}

/**
 * Tax payment type enum.
 * 
 * Classifies different types of tax payments for reporting and calculations.
 * 
 * Source: src/fund/enums/fund_event_enums.py::TaxPaymentType
 */
export enum TaxPaymentType {
  /** Non-resident interest withholding tax */
  NON_RESIDENT_INTEREST_WITHHOLDING = 'NON_RESIDENT_INTEREST_WITHHOLDING',
  /** Capital gains tax payments */
  CAPITAL_GAINS_TAX = 'CAPITAL_GAINS_TAX',
  /** End of financial year interest tax */
  EOFY_INTEREST_TAX = 'EOFY_INTEREST_TAX',
  /** Tax on franked dividends */
  DIVIDENDS_FRANKED_TAX = 'DIVIDENDS_FRANKED_TAX',
  /** Tax on unfranked dividends */
  DIVIDENDS_UNFRANKED_TAX = 'DIVIDENDS_UNFRANKED_TAX',
}

/**
 * Event grouping type enum.
 * 
 * Defines how events can be grouped together for reporting and analysis.
 * 
 * Source: src/fund/enums/fund_event_enums.py::GroupType
 */
export enum GroupType {
  /** Interest distribution events paired with withholding tax events */
  INTEREST_WITHHOLDING = 'INTEREST_WITHHOLDING',
  /** Tax statement events grouped by financial year */
  TAX_STATEMENT = 'TAX_STATEMENT',
}

/**
 * Sort field enum for fund events.
 * 
 * Defines the fields that can be used to sort fund events.
 * 
 * Source: src/fund/enums/fund_event_enums.py::SortFieldFundEvent
 */
export enum SortFieldFundEvent {
  EVENT_DATE = 'EVENT_DATE',
  EVENT_TYPE = 'EVENT_TYPE',
}

// ============================================================================
// FUND EVENT CASH FLOW ENUMS
// ============================================================================

/**
 * Cash flow direction enum.
 * 
 * Indicates the direction of money flow from the investor's perspective.
 * 
 * Source: src/fund/enums/fund_event_cash_flow_enums.py::CashFlowDirection
 */
export enum CashFlowDirection {
  /** Money received by investor (e.g., distributions, returns) */
  INFLOW = 'INFLOW',
  /** Money paid out by investor (e.g., capital calls, fees) */
  OUTFLOW = 'OUTFLOW',
}

/**
 * Sort field enum for fund event cash flows.
 * 
 * Defines the fields that can be used for sorting in APIs and queries.
 * 
 * Source: src/fund/enums/fund_event_cash_flow_enums.py::SortFieldFundEventCashFlow
 */
export enum SortFieldFundEventCashFlow {
  TRANSFER_DATE = 'TRANSFER_DATE',
  AMOUNT = 'AMOUNT',
  CREATED_AT = 'CREATED_AT',
  UPDATED_AT = 'UPDATED_AT',
}

// ============================================================================
// FUND TAX STATEMENT ENUMS
// ============================================================================

/**
 * Sort field enum for fund tax statements.
 * 
 * Source: src/fund/enums/fund_tax_statement_enums.py::SortFieldFundTaxStatement
 */
export enum SortFieldFundTaxStatement {
  TAX_PAYMENT_DATE = 'TAX_PAYMENT_DATE',
  FINANCIAL_YEAR = 'FINANCIAL_YEAR',
  CREATED_AT = 'CREATED_AT',
  UPDATED_AT = 'UPDATED_AT',
}

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

/**
 * Check if an event type is an equity event.
 */
export function isEquityEvent(eventType: EventType): boolean {
  const equityEvents = new Set([
    EventType.CAPITAL_CALL,
    EventType.RETURN_OF_CAPITAL,
    EventType.UNIT_PURCHASE,
    EventType.UNIT_SALE,
  ]);
  return equityEvents.has(eventType);
}

/**
 * Check if an event type is a distribution event.
 */
export function isDistributionEvent(eventType: EventType): boolean {
  return eventType === EventType.DISTRIBUTION;
}

/**
 * Check if an event type is a system-generated event.
 */
export function isSystemEvent(eventType: EventType): boolean {
  const systemEvents = new Set([EventType.DAILY_RISK_FREE_INTEREST_CHARGE]);
  return systemEvents.has(eventType);
}

/**
 * Check if an event type is an equity call event.
 */
export function isEquityCallEvent(eventType: EventType): boolean {
  const equityCallEvents = new Set([EventType.CAPITAL_CALL, EventType.UNIT_PURCHASE]);
  return equityCallEvents.has(eventType);
}

/**
 * Check if an event type is an equity return event.
 */
export function isEquityReturnEvent(eventType: EventType): boolean {
  const equityReturnEvents = new Set([EventType.RETURN_OF_CAPITAL, EventType.UNIT_SALE]);
  return equityReturnEvents.has(eventType);
}

/**
 * Check if an event type is a tax statement event.
 */
export function isTaxStatementEvent(eventType: EventType): boolean {
  const taxStatementEvents = new Set([EventType.TAX_PAYMENT]);
  return taxStatementEvents.has(eventType);
}

/**
 * Check if a distribution type is taxable.
 */
export function isTaxableDistribution(distributionType: DistributionType): boolean {
  const taxableTypes = new Set([
    DistributionType.INCOME,
    DistributionType.DIVIDEND_FRANKED,
    DistributionType.DIVIDEND_UNFRANKED,
    DistributionType.INTEREST,
    DistributionType.RENT,
    DistributionType.CAPITAL_GAIN,
  ]);
  return taxableTypes.has(distributionType);
}

/**
 * Check if a distribution type has franking credits.
 */
export function hasFrankingCredits(distributionType: DistributionType): boolean {
  return distributionType === DistributionType.DIVIDEND_FRANKED;
}

/**
 * Check if tax payment type is a withholding tax.
 */
export function isWithholdingTax(taxPaymentType: TaxPaymentType): boolean {
  const withholdingTypes = new Set([TaxPaymentType.NON_RESIDENT_INTEREST_WITHHOLDING]);
  return withholdingTypes.has(taxPaymentType);
}

/**
 * Check if tax payment type is related to dividends.
 */
export function isDividendTax(taxPaymentType: TaxPaymentType): boolean {
  const dividendTaxTypes = new Set([
    TaxPaymentType.DIVIDENDS_FRANKED_TAX,
    TaxPaymentType.DIVIDENDS_UNFRANKED_TAX,
  ]);
  return dividendTaxTypes.has(taxPaymentType);
}

/**
 * Check if cash flow direction is incoming to investor.
 */
export function isIncomingCashFlow(direction: CashFlowDirection): boolean {
  return direction === CashFlowDirection.INFLOW;
}

/**
 * Check if cash flow direction is outgoing from investor.
 */
export function isOutgoingCashFlow(direction: CashFlowDirection): boolean {
  return direction === CashFlowDirection.OUTFLOW;
}

