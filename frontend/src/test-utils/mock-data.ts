import { 
  CompanyOverviewResponse, 
  CompanyDetailsResponse, 
  Fund, 
  FundEvent, 
  EnhancedFundsResponse,
  EnhancedFund,
  FundStatus,
  FundType,
  EventType
} from '../types/api';

// ============================================================================
// COMPANY CONTACT MOCK DATA FACTORIES
// ============================================================================

export const createMockCompanyContact = (overrides: any = {}) => ({
  id: 1,
  name: 'John Doe',
  title: 'Investment Manager',
  direct_number: '+61 2 1234 5678',
  direct_email: 'john.doe@testcompany.com',
  notes: 'Primary contact for investment decisions',
  ...overrides
});

// ============================================================================
// COMPANY OVERVIEW MOCK DATA FACTORIES
// ============================================================================

export const createMockCompanyOverview = (overrides: Partial<CompanyOverviewResponse> = {}): CompanyOverviewResponse => ({
  company: {
    id: 1,
    name: 'Test Investment Company',
    company_type: 'Private Equity',
    business_address: '123 Investment Street, Sydney NSW 2000',
    website: 'https://testcompany.com',
    contacts: [createMockCompanyContact()]
  },
  portfolio_summary: {
    total_committed_capital: 5000000,
    total_current_value: 5500000,
    total_invested_capital: 4500000,
    active_funds_count: 3,
    completed_funds_count: 2,
            fund_status_breakdown: { active_funds_count: 3, completed_funds_count: 2, suspended_funds_count: 0, realized_funds_count: 0 }
  },
  performance_summary: {
    average_completed_irr: 15.5,
    total_realized_gains: 500000,
    total_realized_losses: 0
  },
  last_activity: {
    last_activity_date: '2023-12-01',
    days_since_last_activity: 30
  },
  ...overrides
});

// ============================================================================
// COMPANY DETAILS MOCK DATA FACTORIES
// ============================================================================

export const createMockCompanyDetails = (overrides: Partial<CompanyDetailsResponse> = {}): CompanyDetailsResponse => ({
  company: {
    id: 1,
    name: 'Test Investment Company',
    company_type: 'Private Equity',
    business_address: '123 Investment Street, Sydney NSW 2000',
    website: 'https://testcompany.com',
    contacts: [createMockCompanyContact()]
  },
  ...overrides
});

// ============================================================================
// FUND MOCK DATA FACTORIES
// ============================================================================

export const createMockFund = (overrides: Partial<Fund> = {}): Fund => ({
  id: 1,
  name: 'Test Fund 1',
  fund_type: 'Private Equity',
  tracking_type: FundType.NAV_BASED,
  description: 'A test fund for demonstration purposes',
  currency: 'AUD',
  commitment_amount: 1000000,
  expected_irr: 15.0,
  expected_duration_months: 60,
  investment_company_id: 1,
  entity_id: 1,
  current_equity_balance: 950000,
  average_equity_balance: 900000,
  status: FundStatus.ACTIVE,
  final_tax_statement_received: false,
  current_units: 1000,
  current_unit_price: 950,
  current_nav_total: 950000,
  total_cost_basis: 900000,
  created_at: '2023-01-01T00:00:00Z',
  updated_at: '2023-12-01T00:00:00Z',
  ...overrides
});

export const createMockFundsList = (count: number = 5): Fund[] => {
  return Array.from({ length: count }, (_, index) => 
    createMockFund({
      id: index + 1,
      name: `Test Fund ${index + 1}`,
      status: index < 3 ? FundStatus.ACTIVE : FundStatus.COMPLETED
    })
  );
};

// ============================================================================
// ENHANCED FUND MOCK DATA FACTORIES
// ============================================================================

export const createMockEnhancedFund = (overrides: Partial<EnhancedFund> = {}): EnhancedFund => ({
  id: 1,
  name: 'Test Enhanced Fund 1',
  description: 'A test enhanced fund for demonstration purposes',
  currency: 'AUD',
  fund_type: 'Private Equity',
  status: 'active',
  tracking_type: 'nav_based',
  fund_details: {
    start_date: '2023-01-01',
    end_date: null,
    actual_duration_days: 365,
    days_since_last_activity: 30
  },
  equity: {
    commitment: 1000000,
    invested_capital: 900000,
    current_value: 950000,
    current_equity_balance: 950000
  },
  estimated_return: {
    expected_irr: 15.0,
    duration_months: 60
  },
  distributions: {
    distribution_count: 2,
    total_distribution_amount: 50000,
    last_distribution_date: '2023-12-01',
    distribution_frequency_months: 6
  },
  returns: {
    completed_irr: null,
    performance_vs_expected: null
  },
  performance: {
    unrealized_gains_losses: 100000,
    realized_gains_losses: 50000,
    total_profit_loss: 150000
  },
  ...overrides
});

export const createMockEnhancedFundsList = (count: number = 5): EnhancedFund[] => {
  return Array.from({ length: count }, (_, index) => 
    createMockEnhancedFund({
      id: index + 1,
      name: `Test Enhanced Fund ${index + 1}`,
      status: index < 3 ? 'active' : 'completed',
      fund_details: {
        start_date: '2023-01-01',
        end_date: index < 3 ? null : '2023-12-31',
        actual_duration_days: 365,
        days_since_last_activity: 30
      }
    })
  );
};

// ============================================================================
// ENHANCED FUNDS RESPONSE MOCK DATA FACTORIES
// ============================================================================

export const createMockEnhancedFundsResponse = (overrides: Partial<EnhancedFundsResponse> = {}): EnhancedFundsResponse => ({
  funds: createMockEnhancedFundsList(5),
  pagination: {
    current_page: 1,
    total_pages: 1,
    total_funds: 5,
    per_page: 10
  },
  filters: {
    applied_status_filter: '',
    applied_search: null
  },
  ...overrides
});

// ============================================================================
// FUND EVENT MOCK DATA FACTORIES
// ============================================================================

export const createMockFundEvent = (overrides: Partial<FundEvent> = {}): FundEvent => ({
  id: 1,
  fund_id: 1,
  event_type: EventType.CAPITAL_CALL,
  event_date: '2023-01-01',
  amount: 100000,
  description: 'Test capital call event',
  created_at: '2023-01-01T00:00:00Z',
  updated_at: '2023-01-01T00:00:00Z',
  ...overrides
});

export const createMockFundEventsList = (count: number = 5): FundEvent[] => {
  const eventTypes: EventType[] = [EventType.CAPITAL_CALL, EventType.DISTRIBUTION, EventType.NAV_UPDATE, EventType.MANAGEMENT_FEE, EventType.CARRIED_INTEREST];
  
  return Array.from({ length: count }, (_, index) => {
    const eventTypeIndex = index % eventTypes.length;
    const eventType = eventTypes[eventTypeIndex];
    if (!eventType) return createMockFundEvent({
      id: index + 1,
      fund_id: 1,
      event_type: EventType.OTHER,
      event_date: `2023-${String(index + 1).padStart(2, '0')}-01`,
      amount: 50000 + (index * 10000),
      description: 'Test unknown event',
    });
    
    return createMockFundEvent({
      id: index + 1,
      fund_id: 1,
      event_type: eventType,
      event_date: `2023-${String(index + 1).padStart(2, '0')}-01`,
      amount: 50000 + (index * 10000),
      description: `Test ${eventType.toLowerCase()} event`,
    });
  });
};

// ============================================================================
// COMPOSITE MOCK DATA FACTORIES
// ============================================================================

export const createMockCompanyWithFunds = (fundCount: number = 5) => ({
  company: createMockCompanyOverview(),
  funds: createMockFundsList(fundCount),
  events: createMockFundEventsList(fundCount * 2)
});

export const createMockEmptyCompany = () => ({
  company: createMockCompanyOverview({
    portfolio_summary: {
      total_committed_capital: 0,
      total_current_value: 0,
      total_invested_capital: 0,
      active_funds_count: 0,
      completed_funds_count: 0,
              fund_status_breakdown: { active_funds_count: 0, completed_funds_count: 0, suspended_funds_count: 0, realized_funds_count: 0 }
    },
    performance_summary: {
      average_completed_irr: 0,
      total_realized_gains: 0,
      total_realized_losses: 0
    },
    last_activity: {
      last_activity_date: null,
      days_since_last_activity: null
    }
  }),
  funds: [],
  events: []
});

// ============================================================================
// TEST SCENARIOS
// ============================================================================

export const mockTestScenarios = {
  // Single fund company
  singleFund: () => ({
    company: createMockCompanyOverview({
      portfolio_summary: { 
        total_committed_capital: 1000000,
        total_current_value: 1100000,
        total_invested_capital: 900000,
        active_funds_count: 1, 
        completed_funds_count: 0,
        fund_status_breakdown: { active_funds_count: 1, completed_funds_count: 0, suspended_funds_count: 0, realized_funds_count: 0 }
      }
    }),
    funds: [createMockFund()],
    events: createMockFundEventsList(3)
  }),

  // Multi-currency company
  multiCurrency: () => ({
    company: createMockCompanyOverview({
      portfolio_summary: {
        total_committed_capital: 2500000,
        total_current_value: 2750000,
        total_invested_capital: 2250000,
        active_funds_count: 3,
        completed_funds_count: 0,
        fund_status_breakdown: { active_funds_count: 3, completed_funds_count: 0, suspended_funds_count: 0, realized_funds_count: 0 }
      }
    }),
    funds: [
      createMockFund({ currency: 'AUD', commitment_amount: 1500000 }),
      createMockFund({ currency: 'USD', commitment_amount: 800000 }),
      createMockFund({ currency: 'EUR', commitment_amount: 200000 })
    ],
    events: createMockFundEventsList(6)
  }),

  // Completed funds company
  completedFunds: () => ({
    company: createMockCompanyOverview({
      portfolio_summary: {
        total_committed_capital: 3000000,
        total_current_value: 3750000,
        total_invested_capital: 2700000,
        active_funds_count: 0,
        completed_funds_count: 3,
        fund_status_breakdown: { active_funds_count: 0, completed_funds_count: 3, suspended_funds_count: 0, realized_funds_count: 0 }
      },
      performance_summary: {
        average_completed_irr: 25.5,
        total_realized_gains: 750000,
        total_realized_losses: 0
      }
    }),
    funds: [
      createMockFund({ status: FundStatus.COMPLETED }),
      createMockFund({ status: FundStatus.COMPLETED }),
      createMockFund({ status: FundStatus.COMPLETED })
    ],
    events: createMockFundEventsList(9)
  }),

  // High-performance company
  highPerformance: () => ({
    company: createMockCompanyOverview({
      performance_summary: {
        average_completed_irr: 45.2,
        total_realized_gains: 500000,
        total_realized_losses: 0
      },
      portfolio_summary: {
        total_committed_capital: 2000000,
        total_current_value: 2000000,
        total_invested_capital: 1500000,
        active_funds_count: 2,
        completed_funds_count: 0,
        fund_status_breakdown: { active_funds_count: 2, completed_funds_count: 0, suspended_funds_count: 0, realized_funds_count: 0 }
      }
    }),
    funds: [
      createMockFund({ 
        expected_irr: 25.0, 
        current_equity_balance: 1300000 
      }),
      createMockFund({ 
        expected_irr: 20.0, 
        current_equity_balance: 1200000 
      })
    ],
    events: createMockFundEventsList(4)
  })
};
