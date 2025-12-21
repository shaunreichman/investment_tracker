/**
 * Fund API
 * 
 * All fund-related API methods including:
 * - Funds (CRUD operations)
 * - Fund Events (CRUD operations for different event types)
 * - Fund Event Cash Flows (CRUD operations)
 * - Fund Tax Statements (CRUD operations)
 * 
 * Funds represent investment funds tracked in the system, with events
 * representing capital movements, NAV updates, distributions, and tax information.
 */

import { ApiClient } from '@/shared/api';
import {
  Fund,
  FundEvent,
  FundEventCashFlow,
  FundTaxStatement,
  CreateFundRequest,
  CreateCapitalCallRequest,
  CreateReturnOfCapitalRequest,
  CreateUnitPurchaseRequest,
  CreateUnitSaleRequest,
  CreateNavUpdateRequest,
  CreateDistributionRequest,
  CreateFundEventCashFlowRequest,
  CreateFundTaxStatementRequest,
  GetFundsResponse,
  GetFundResponse,
  GetFundEventsResponse,
  GetFundEventResponse,
  GetFundEventCashFlowsResponse,
  GetFundEventCashFlowResponse,
  GetFundTaxStatementsResponse,
  GetFundTaxStatementResponse,
  GetFundsQueryParams,
  GetFundEventsQueryParams,
  GetFundEventCashFlowsQueryParams,
  GetFundTaxStatementsQueryParams,
  FundFinancialYearMap,
} from '../types';

export class FundApi {
  constructor(private client: ApiClient) {}

  // ============================================================================
  // FUNDS
  // ============================================================================

  /**
   * Get all funds with optional filters.
   * 
   * Supports filtering by:
   * - company_id (single) or company_ids (multiple)
   * - entity_id (single) or entity_ids (multiple)
   * - fund_status (single) or fund_statuses (multiple)
   * - fund_tracking_type (single) or fund_tracking_types (multiple)
   * - start_start_date, end_start_date (date range for start_date)
   * - start_end_date, end_end_date (date range for end_date)
   * 
   * Supports sorting by: START_DATE, NAME, STATUS, COMMITMENT_AMOUNT, CURRENT_EQUITY_BALANCE, CREATED_AT, UPDATED_AT
   * 
   * Supports including relationships:
   * - include_fund_events
   * - include_fund_event_cash_flows
   * - include_fund_tax_statements
   * 
   * @param params Query parameters for filtering and sorting
   * @returns Array of funds
   * 
   * @example
   * ```typescript
   * // Get all funds
   * const funds = await api.funds.getFunds();
   * 
   * // Get all ACTIVE funds for a specific entity
   * const activeFunds = await api.funds.getFunds({
   *   entity_id: 1,
   *   fund_status: FundStatus.ACTIVE
   * });
   * 
   * // Get funds with events included
   * const fundsWithEvents = await api.funds.getFunds({
   *   include_fund_events: true
   * });
   * ```
   */
  async getFunds(params: GetFundsQueryParams = {}): Promise<GetFundsResponse> {
    return this.client.get<GetFundsResponse>('/api/funds', params);
  }

  /**
   * Get a single fund by ID.
   * 
   * @param fundId The ID of the fund to retrieve
   * @param params Query parameters for including relationships
   * @returns Single fund object
   * 
   * @throws ApiError with RESOURCE_NOT_FOUND if fund doesn't exist
   * 
   * @example
   * ```typescript
   * const fund = await api.funds.getFund(1);
   * console.log(fund.name, fund.status);
   * 
   * // Get fund with all related data
   * const fundWithRelated = await api.funds.getFund(1, {
   *   include_fund_events: true,
   *   include_fund_event_cash_flows: true,
   *   include_fund_tax_statements: true
   * });
   * ```
   */
  async getFund(
    fundId: number,
    params: {
      include_fund_events?: boolean;
      include_fund_event_cash_flows?: boolean;
      include_fund_tax_statements?: boolean;
    } = {}
  ): Promise<GetFundResponse> {
    return this.client.get<GetFundResponse>(`/api/funds/${fundId}`, params);
  }

  /**
   * Create a new fund.
   * 
   * Required fields:
   * - name: 2-255 characters
   * - entity_id: Valid entity ID
   * - company_id: Valid company ID
   * - tracking_type: Valid FundTrackingType enum
   * - tax_jurisdiction: Valid Country enum
   * - currency: Valid Currency enum
   * 
   * Optional fields:
   * - fund_investment_type: Valid FundInvestmentType enum
   * - description: Max 1000 characters
   * - expected_irr: 0.0-100.0
   * - expected_duration_months: 0-1200
   * - commitment_amount: 0.0-999999999.0
   * 
   * @param data Fund creation data
   * @returns Created fund object
   * 
   * @throws ApiError with VALIDATION_ERROR if data is invalid
   * @throws ApiError with BUSINESS_LOGIC_ERROR if entity or company doesn't exist
   * 
   * @example
   * ```typescript
   * const newFund = await api.funds.createFund({
   *   name: 'Test Fund LP',
   *   entity_id: 1,
   *   company_id: 2,
   *   tracking_type: FundTrackingType.NAV_BASED,
   *   tax_jurisdiction: Country.AU,
   *   currency: Currency.AUD,
   *   fund_investment_type: FundInvestmentType.PRIVATE_EQUITY,
   *   expected_irr: 15.0,
   *   commitment_amount: 1000000
   * });
   * ```
   */
  async createFund(data: CreateFundRequest): Promise<Fund> {
    return this.client.post<Fund>('/api/funds', data);
  }

  /**
   * Delete a fund.
   * 
   * Warning: This will cascade delete all related data:
   * - Fund events
   * - Fund event cash flows
   * - Fund tax statements
   * 
   * @param fundId The ID of the fund to delete
   * @returns Deletion confirmation with deleted ID
   * 
   * @throws ApiError with RESOURCE_NOT_FOUND if fund doesn't exist
   * @throws ApiError with BUSINESS_LOGIC_ERROR if fund has dependencies that prevent deletion
   * 
   * @example
   * ```typescript
   * await api.funds.deleteFund(1);
   * console.log('Fund deleted successfully');
   * ```
   */
  async deleteFund(fundId: number): Promise<{ message: string; deleted_id: number }> {
    return this.client.delete<{ message: string; deleted_id: number }>(`/api/funds/${fundId}`);
  }

  // ============================================================================
  // FUND EVENTS
  // ============================================================================

  /**
   * Get all fund events with optional filters.
   * 
   * Supports filtering by:
   * - fund_id (single) or fund_ids (multiple)
   * - event_type (single) or event_types (multiple)
   * - distribution_type (single) or distribution_types (multiple)
   * - tax_payment_type (single) or tax_payment_types (multiple)
   * - group_id (single) or group_ids (multiple)
   * - group_type (single) or group_types (multiple)
   * - is_cash_flow_complete
   * - start_event_date, end_event_date (date range)
   * 
   * Supports sorting by: EVENT_DATE, EVENT_TYPE
   * 
   * @param params Query parameters for filtering and sorting
   * @returns Array of fund events
   * 
   * @example
   * ```typescript
   * // Get all events
   * const events = await api.funds.getFundEvents();
   * 
   * // Get all capital call events for a fund
   * const capitalCalls = await api.funds.getFundEvents({
   *   fund_id: 1,
   *   event_type: EventType.CAPITAL_CALL
   * });
   * ```
   */
  async getFundEvents(params: GetFundEventsQueryParams = {}): Promise<GetFundEventsResponse> {
    return this.client.get<GetFundEventsResponse>('/api/fund-events', params);
  }

  /**
   * Get all events for a specific fund.
   * 
   * @param fundId The ID of the fund
   * @param params Query parameters for including relationships
   * @returns Array of fund events
   * 
   * @example
   * ```typescript
   * const events = await api.funds.getFundEventsByFundId(1);
   * ```
   */
  async getFundEventsByFundId(
    fundId: number,
    params: { include_fund_event_cash_flows?: boolean } = {}
  ): Promise<GetFundEventsResponse> {
    return this.client.get<GetFundEventsResponse>(`/api/funds/${fundId}/fund-events`, params);
  }

  /**
   * Get a specific fund event.
   * 
   * @param fundId The ID of the fund
   * @param fundEventId The ID of the event
   * @param params Query parameters for including relationships
   * @returns Single fund event object
   * 
   * @throws ApiError with RESOURCE_NOT_FOUND if event doesn't exist
   * 
   * @example
   * ```typescript
   * const event = await api.funds.getFundEvent(1, 5);
   * ```
   */
  async getFundEvent(
    fundId: number,
    fundEventId: number,
    params: { include_fund_event_cash_flows?: boolean } = {}
  ): Promise<GetFundEventResponse> {
    return this.client.get<GetFundEventResponse>(
      `/api/funds/${fundId}/fund-events/${fundEventId}`,
      params
    );
  }

  /**
   * Create a new capital call event for a specific fund.
   * 
   * @param fundId The ID of the fund
   * @param data Capital call creation data
   * @returns Created fund event object
   * 
   * @throws ApiError with VALIDATION_ERROR if data is invalid
   * @throws ApiError with BUSINESS_LOGIC_ERROR if fund doesn't exist or tracking type incompatible
   * 
   * @example
   * ```typescript
   * const capitalCall = await api.funds.createCapitalCall(1, {
   *   event_date: '2024-01-15',
   *   amount: 50000,
   *   description: 'Q1 2024 Capital Call',
   *   reference_number: 'CC-2024-01'
   * });
   * ```
   */
  async createCapitalCall(fundId: number, data: CreateCapitalCallRequest): Promise<FundEvent> {
    return this.client.post<FundEvent>(`/api/funds/${fundId}/fund-events/capital-call`, data);
  }

  /**
   * Create a new return of capital event for a specific fund.
   * 
   * @param fundId The ID of the fund
   * @param data Return of capital creation data
   * @returns Created fund event object
   * 
   * @example
   * ```typescript
   * const returnOfCapital = await api.funds.createReturnOfCapital(1, {
   *   event_date: '2024-03-15',
   *   amount: 25000,
   *   description: 'Q1 2024 Return of Capital'
   * });
   * ```
   */
  async createReturnOfCapital(fundId: number, data: CreateReturnOfCapitalRequest): Promise<FundEvent> {
    return this.client.post<FundEvent>(`/api/funds/${fundId}/fund-events/return-of-capital`, data);
  }

  /**
   * Create a new unit purchase event for a specific fund.
   * 
   * @param fundId The ID of the fund
   * @param data Unit purchase creation data
   * @returns Created fund event object
   * 
   * @example
   * ```typescript
   * const unitPurchase = await api.funds.createUnitPurchase(1, {
   *   event_date: '2024-02-01',
   *   units_purchased: 100,
   *   unit_price: 10.50,
   *   brokerage_fee: 15.00,
   *   description: 'Monthly purchase'
   * });
   * ```
   */
  async createUnitPurchase(fundId: number, data: CreateUnitPurchaseRequest): Promise<FundEvent> {
    return this.client.post<FundEvent>(`/api/funds/${fundId}/fund-events/unit-purchase`, data);
  }

  /**
   * Create a new unit sale event for a specific fund.
   * 
   * @param fundId The ID of the fund
   * @param data Unit sale creation data
   * @returns Created fund event object
   * 
   * @example
   * ```typescript
   * const unitSale = await api.funds.createUnitSale(1, {
   *   event_date: '2024-06-15',
   *   units_sold: 50,
   *   unit_price: 12.00,
   *   brokerage_fee: 10.00
   * });
   * ```
   */
  async createUnitSale(fundId: number, data: CreateUnitSaleRequest): Promise<FundEvent> {
    return this.client.post<FundEvent>(`/api/funds/${fundId}/fund-events/unit-sale`, data);
  }

  /**
   * Create a new NAV update event for a specific fund.
   * 
   * @param fundId The ID of the fund
   * @param data NAV update creation data
   * @returns Created fund event object
   * 
   * @example
   * ```typescript
   * const navUpdate = await api.funds.createNavUpdate(1, {
   *   event_date: '2024-03-31',
   *   nav_per_share: 11.25,
   *   description: 'Q1 2024 NAV Update'
   * });
   * ```
   */
  async createNavUpdate(fundId: number, data: CreateNavUpdateRequest): Promise<FundEvent> {
    return this.client.post<FundEvent>(`/api/funds/${fundId}/fund-events/nav-update`, data);
  }

  /**
   * Create a new distribution event for a specific fund.
   * 
   * Supports both simple distributions and distributions with withholding tax.
   * 
   * For simple distributions:
   * - Provide amount
   * 
   * For withholding tax distributions:
   * - Set has_withholding_tax to true
   * - Provide exactly one of: gross_amount OR net_amount
   * - Provide exactly one of: withholding_tax_amount OR withholding_tax_rate
   * 
   * @param fundId The ID of the fund
   * @param data Distribution creation data
   * @returns Created fund event object
   * 
   * @example
   * ```typescript
   * // Simple distribution
   * const distribution = await api.funds.createDistribution(1, {
   *   event_date: '2024-06-30',
   *   distribution_type: DistributionType.DIVIDEND_FRANKED,
   *   amount: 5000
   * });
   * 
   * // Distribution with withholding tax
   * const distributionWithTax = await api.funds.createDistribution(1, {
   *   event_date: '2024-06-30',
   *   distribution_type: DistributionType.INTEREST,
   *   has_withholding_tax: true,
   *   gross_amount: 5000,
   *   withholding_tax_rate: 10
   * });
   * ```
   */
  async createDistribution(fundId: number, data: CreateDistributionRequest): Promise<FundEvent> {
    return this.client.post<FundEvent>(`/api/funds/${fundId}/fund-events/distribution`, data);
  }

  /**
   * Delete a specific fund event.
   * 
   * Warning: This will cascade delete all related fund event cash flows.
   * 
   * @param fundId The ID of the fund
   * @param fundEventId The ID of the event to delete
   * @returns Deletion confirmation with deleted ID
   * 
   * @throws ApiError with RESOURCE_NOT_FOUND if event doesn't exist
   * 
   * @example
   * ```typescript
   * await api.funds.deleteFundEvent(1, 5);
   * console.log('Fund event deleted successfully');
   * ```
   */
  async deleteFundEvent(
    fundId: number,
    fundEventId: number
  ): Promise<{ message: string; deleted_id: number }> {
    return this.client.delete<{ message: string; deleted_id: number }>(
      `/api/funds/${fundId}/fund-events/${fundEventId}`
    );
  }

  // ============================================================================
  // FUND EVENT CASH FLOWS
  // ============================================================================

  /**
   * Get all fund event cash flows with optional filters.
   * 
   * Supports filtering by:
   * - fund_id (single) or fund_ids (multiple)
   * - fund_event_id (single) or fund_event_ids (multiple)
   * - bank_account_id (single) or bank_account_ids (multiple)
   * - different_month
   * - adjusted_bank_account_balance_id (single) or adjusted_bank_account_balance_ids (multiple)
   * - currency (single) or currencies (multiple)
   * - start_transfer_date, end_transfer_date (date range)
   * - start_fund_event_date, end_fund_event_date (date range)
   * 
   * Supports sorting by: TRANSFER_DATE, AMOUNT, CREATED_AT, UPDATED_AT
   * 
   * @param params Query parameters for filtering and sorting
   * @returns Array of fund event cash flows
   * 
   * @example
   * ```typescript
   * // Get all cash flows
   * const cashFlows = await api.funds.getFundEventCashFlows();
   * 
   * // Get cash flows for a specific bank account
   * const accountCashFlows = await api.funds.getFundEventCashFlows({
   *   bank_account_id: 5
   * });
   * ```
   */
  async getFundEventCashFlows(
    params: GetFundEventCashFlowsQueryParams = {}
  ): Promise<GetFundEventCashFlowsResponse> {
    return this.client.get<GetFundEventCashFlowsResponse>('/api/fund-event-cash-flows', params);
  }

  /**
   * Get all cash flows for a specific fund event.
   * 
   * @param fundId The ID of the fund
   * @param fundEventId The ID of the event
   * @returns Array of fund event cash flows
   * 
   * @example
   * ```typescript
   * const cashFlows = await api.funds.getFundEventCashFlowsByEvent(1, 5);
   * ```
   */
  async getFundEventCashFlowsByEvent(
    fundId: number,
    fundEventId: number
  ): Promise<GetFundEventCashFlowsResponse> {
    return this.client.get<GetFundEventCashFlowsResponse>(
      `/api/funds/${fundId}/fund-events/${fundEventId}/fund-event-cash-flows`
    );
  }

  /**
   * Get a cash flow by ID for a specific fund event.
   * 
   * @param fundId The ID of the fund
   * @param fundEventId The ID of the event
   * @param fundEventCashFlowId The ID of the cash flow
   * @returns Single fund event cash flow object
   * 
   * @throws ApiError with RESOURCE_NOT_FOUND if cash flow doesn't exist
   * 
   * @example
   * ```typescript
   * const cashFlow = await api.funds.getFundEventCashFlow(1, 5, 10);
   * ```
   */
  async getFundEventCashFlow(
    fundId: number,
    fundEventId: number,
    fundEventCashFlowId: number
  ): Promise<GetFundEventCashFlowResponse> {
    return this.client.get<GetFundEventCashFlowResponse>(
      `/api/funds/${fundId}/fund-events/${fundEventId}/fund-event-cash-flows/${fundEventCashFlowId}`
    );
  }

  /**
   * Create a new cash flow for a specific fund event.
   * 
   * @param fundId The ID of the fund
   * @param fundEventId The ID of the event
   * @param data Cash flow creation data
   * @returns Created fund event cash flow object
   * 
   * @throws ApiError with VALIDATION_ERROR if data is invalid
   * @throws ApiError with BUSINESS_LOGIC_ERROR if currency doesn't match bank account
   * 
   * @example
   * ```typescript
   * const cashFlow = await api.funds.createFundEventCashFlow(1, 5, {
   *   bank_account_id: 3,
   *   direction: CashFlowDirection.OUTFLOW,
   *   transfer_date: '2024-01-20',
   *   currency: 'AUD',
   *   amount: 50000,
   *   reference: 'Bank reference 12345'
   * });
   * ```
   */
  async createFundEventCashFlow(
    fundId: number,
    fundEventId: number,
    data: CreateFundEventCashFlowRequest
  ): Promise<FundEventCashFlow> {
    return this.client.post<FundEventCashFlow>(
      `/api/funds/${fundId}/fund-events/${fundEventId}/fund-event-cash-flows`,
      data
    );
  }

  /**
   * Delete a specific cash flow for a specific fund event.
   * 
   * @param fundId The ID of the fund
   * @param fundEventId The ID of the event
   * @param fundEventCashFlowId The ID of the cash flow
   * @returns Deletion confirmation with deleted ID
   * 
   * @throws ApiError with RESOURCE_NOT_FOUND if cash flow doesn't exist
   * 
   * @example
   * ```typescript
   * await api.funds.deleteFundEventCashFlow(1, 5, 10);
   * console.log('Cash flow deleted successfully');
   * ```
   */
  async deleteFundEventCashFlow(
    fundId: number,
    fundEventId: number,
    fundEventCashFlowId: number
  ): Promise<{ message: string; deleted_id: number }> {
    return this.client.delete<{ message: string; deleted_id: number }>(
      `/api/funds/${fundId}/fund-events/${fundEventId}/fund-event-cash-flows/${fundEventCashFlowId}`
    );
  }

  // ============================================================================
  // FUND TAX STATEMENTS
  // ============================================================================

  /**
   * Get all fund tax statements with optional filters.
   * 
   * Supports filtering by:
   * - fund_id (single) or fund_ids (multiple)
   * - entity_id (single) or entity_ids (multiple)
   * - financial_year (single) or financial_years (multiple)
   * - start_tax_payment_date, end_tax_payment_date (date range)
   * 
   * Supports sorting by: TAX_PAYMENT_DATE, FINANCIAL_YEAR, CREATED_AT, UPDATED_AT
   * 
   * @param params Query parameters for filtering and sorting
   * @returns Array of fund tax statements
   * 
   * @example
   * ```typescript
   * // Get all tax statements
   * const statements = await api.funds.getFundTaxStatements();
   * 
   * // Get tax statements for a specific fund and financial year
   * const fy2024Statements = await api.funds.getFundTaxStatements({
   *   fund_id: 1,
   *   financial_year: '2024'
   * });
   * ```
   */
  async getFundTaxStatements(
    params: GetFundTaxStatementsQueryParams = {}
  ): Promise<GetFundTaxStatementsResponse> {
    return this.client.get<GetFundTaxStatementsResponse>('/api/fund-tax-statements', params);
  }

  /**
   * Get all tax statements for a specific fund.
   * 
   * @param fundId The ID of the fund
   * @returns Array of fund tax statements
   * 
   * @example
   * ```typescript
   * const statements = await api.funds.getFundTaxStatementsByFundId(1);
   * ```
   */
  async getFundTaxStatementsByFundId(fundId: number): Promise<GetFundTaxStatementsResponse> {
    return this.client.get<GetFundTaxStatementsResponse>(`/api/funds/${fundId}/fund-tax-statements`);
  }

  /**
   * Get financial years for a fund.
   * 
   * Returns a map of financial year labels to the final calendar date for that year,
   * covering all financial years from the fund's start date through the current year.
   * Used for tax statement forms, default tax dates, and financial year filtering.
   * 
   * @param fundId The ID of the fund
   * @returns Financial year map (e.g., { "2024": "2024-06-30", "2023": "2023-06-30" })
   * 
   * @throws ApiError with RESOURCE_NOT_FOUND if fund doesn't exist
   * @throws ApiError with BUSINESS_LOGIC_ERROR if fund start date or financial year type not set
   * 
   * @example
   * ```typescript
   * const financialYears = await api.funds.getFundFinancialYears(1);
   * console.log(financialYears); // { "2024": "2024-06-30", "2023": "2023-06-30" }
   * ```
   */
  async getFundFinancialYears(fundId: number): Promise<FundFinancialYearMap> {
    return this.client.get<FundFinancialYearMap>(`/api/funds/${fundId}/financial-years`);
  }

  /**
   * Get a fund tax statement by ID.
   * 
   * @param fundId The ID of the fund
   * @param fundTaxStatementId The ID of the fund tax statement
   * @returns Single fund tax statement object
   * 
   * @throws ApiError with RESOURCE_NOT_FOUND if tax statement doesn't exist
   * 
   * @example
   * ```typescript
   * const statement = await api.funds.getFundTaxStatement(1, 3);
   * ```
   */
  async getFundTaxStatement(
    fundId: number,
    fundTaxStatementId: number
  ): Promise<GetFundTaxStatementResponse> {
    return this.client.get<GetFundTaxStatementResponse>(
      `/api/funds/${fundId}/fund-tax-statements/${fundTaxStatementId}`
    );
  }

  /**
   * Create a new fund tax statement for a specific fund.
   * 
   * Required fields:
   * - entity_id: Valid entity ID
   * - financial_year: 4 characters (e.g., "2024")
   * 
   * @param fundId The ID of the fund
   * @param data Tax statement creation data
   * @returns Created fund tax statement object
   * 
   * @throws ApiError with VALIDATION_ERROR if data is invalid
   * @throws ApiError with BUSINESS_LOGIC_ERROR if duplicate tax statement exists
   * 
   * @example
   * ```typescript
   * const statement = await api.funds.createFundTaxStatement(1, {
   *   entity_id: 2,
   *   financial_year: '2024',
   *   tax_payment_date: '2024-10-31',
   *   interest_income_tax_rate: 30.0,
   *   interest_received_in_cash: 15000,
   *   accountant: 'Smith & Co'
   * });
   * ```
   */
  async createFundTaxStatement(
    fundId: number,
    data: CreateFundTaxStatementRequest
  ): Promise<FundTaxStatement> {
    return this.client.post<FundTaxStatement>(`/api/funds/${fundId}/fund-tax-statements`, data);
  }

  /**
   * Delete a specific fund tax statement.
   * 
   * @param fundId The ID of the fund
   * @param fundTaxStatementId The ID of the fund tax statement
   * @returns Deletion confirmation with deleted ID
   * 
   * @throws ApiError with RESOURCE_NOT_FOUND if tax statement doesn't exist
   * 
   * @example
   * ```typescript
   * await api.funds.deleteFundTaxStatement(1, 3);
   * console.log('Tax statement deleted successfully');
   * ```
   */
  async deleteFundTaxStatement(
    fundId: number,
    fundTaxStatementId: number
  ): Promise<{ message: string; deleted_id: number }> {
    return this.client.delete<{ message: string; deleted_id: number }>(
      `/api/funds/${fundId}/fund-tax-statements/${fundTaxStatementId}`
    );
  }
}

