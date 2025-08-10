import { 
  CompanyOverviewResponse, 
  CompanyDetailsResponse, 
  EnhancedFundsResponse 
} from '../types/api';
import { 
  createMockCompanyOverview, 
  createMockCompanyDetails, 
  createMockEnhancedFundsResponse,
  createMockEnhancedFund
} from './mock-data';

// ============================================================================
// MOCK API SERVICE PATTERNS
// ============================================================================

// Mock API responses for testing
export const mockApiResponses = {
  // Company overview responses
  companyOverview: {
    success: createMockCompanyOverview(),
    empty: createMockCompanyOverview({
      portfolio_summary: {
        total_committed_capital: 0,
        total_current_value: 0,
        total_invested_capital: 0,
        active_funds_count: 0,
        completed_funds_count: 0,
        fund_status_breakdown: { active: 0, completed: 0, suspended: 0 }
      },
      performance_summary: {
        average_completed_irr: null,
        total_realized_gains: null,
        total_realized_losses: null
      },
      last_activity: {
        last_activity_date: null,
        days_since_last_activity: null
      }
    }),
    multiCurrency: createMockCompanyOverview({
      portfolio_summary: {
        total_committed_capital: 2500000,
        total_current_value: 2750000,
        total_invested_capital: 2250000,
        active_funds_count: 3,
        completed_funds_count: 0,
        fund_status_breakdown: { active: 3, completed: 0, suspended: 0 }
      }
    }),
    completedFunds: createMockCompanyOverview({
      portfolio_summary: {
        total_committed_capital: 3000000,
        total_current_value: 3750000,
        total_invested_capital: 3000000,
        active_funds_count: 0,
        completed_funds_count: 3,
        fund_status_breakdown: { active: 0, completed: 3, suspended: 0 }
      },
      performance_summary: {
        average_completed_irr: 25.5,
        total_realized_gains: 750000,
        total_realized_losses: 0
      }
    }),
    highPerformance: createMockCompanyOverview({
      performance_summary: {
        average_completed_irr: 45.2,
        total_realized_gains: 900000,
        total_realized_losses: 0
      },
      portfolio_summary: {
        total_committed_capital: 2000000,
        total_current_value: 2900000,
        total_invested_capital: 2000000,
        active_funds_count: 1,
        completed_funds_count: 0,
        fund_status_breakdown: { active: 1, completed: 0, suspended: 0 }
      }
    })
  },

  // Company details responses
  companyDetails: {
    success: createMockCompanyDetails(),
    empty: createMockCompanyDetails({
      company: {
        id: 1,
        name: 'Empty Test Company',
        company_type: null,
        business_address: null,
        website: null,
        contacts: []
      }
    }),
    withContacts: createMockCompanyDetails({
      company: {
        id: 1,
        name: 'Contact-Rich Company',
        company_type: 'Private Equity',
        business_address: '456 Business Ave, Melbourne VIC 3000',
        website: 'https://contactrich.com',
        contacts: [
          {
            id: 1,
            name: 'Jane Smith',
            title: 'CEO',
            direct_number: '+61 2 9123 4567',
            direct_email: 'jane.smith@contactrich.com',
            notes: 'Chief Executive Officer'
          },
          {
            id: 2,
            name: 'Bob Johnson',
            title: 'CFO',
            direct_number: '+61 2 9123 4568',
            direct_email: 'bob.johnson@contactrich.com',
            notes: 'Chief Financial Officer'
          }
        ]
      }
    })
  },

  // Enhanced funds responses
  enhancedFunds: {
    success: createMockEnhancedFundsResponse(),
    empty: createMockEnhancedFundsResponse({ funds: [] }),
    singleFund: createMockEnhancedFundsResponse({
      funds: [createMockEnhancedFund()]
    }),
    multiCurrency: createMockEnhancedFundsResponse({
      funds: [
        createMockEnhancedFund({ currency: 'AUD' }),
        createMockEnhancedFund({ currency: 'USD' }),
        createMockEnhancedFund({ currency: 'EUR' })
      ]
    }),
    activeFunds: createMockEnhancedFundsResponse({
      funds: [
        createMockEnhancedFund({ status: 'active' }),
        createMockEnhancedFund({ status: 'active' }),
        createMockEnhancedFund({ status: 'active' })
      ]
    }),
    completedFunds: createMockEnhancedFundsResponse({
      funds: [
        createMockEnhancedFund({ status: 'completed', end_date: '2023-12-31' }),
        createMockEnhancedFund({ status: 'completed', end_date: '2023-06-30' }),
        createMockEnhancedFund({ status: 'completed', end_date: '2023-03-31' })
      ]
    }),
    highPerformance: createMockEnhancedFundsResponse({
      funds: [
        createMockEnhancedFund({ 
          estimated_return: { expected_irr: 25.0, duration_months: null },
          equity: { current_equity_balance: 1300000, commitment: 1000000, invested_capital: 1000000, current_value: 1300000 }
        }),
        createMockEnhancedFund({ 
          estimated_return: { expected_irr: 20.0, duration_months: null },
          equity: { current_equity_balance: 1200000, commitment: 1000000, invested_capital: 1000000, current_value: 1200000 }
        })
      ]
    }),
    mixedStatus: createMockEnhancedFundsResponse({
      funds: [
        createMockEnhancedFund({ status: 'active' }),
        createMockEnhancedFund({ status: 'completed', end_date: '2023-12-31' }),
        createMockEnhancedFund({ status: 'suspended' })
      ]
    })
  }
};

// Mock API error responses
export const mockApiErrors = {
  // Network errors
  networkError: new Error('Network error: Failed to fetch'),
  
  // HTTP error responses
  notFound: { status: 404, message: 'Company not found' },
  unauthorized: { status: 401, message: 'Unauthorized access' },
  serverError: { status: 500, message: 'Internal server error' },
  badRequest: { status: 400, message: 'Bad request: Invalid company ID' },
  
  // API-specific errors
  invalidCompanyId: { status: 400, message: 'Invalid company ID format' },
  companyAccessDenied: { status: 403, message: 'Access denied to company data' },
  rateLimitExceeded: { status: 429, message: 'Rate limit exceeded' }
};

// Mock API service functions
export const mockApiService = {
  // Company overview API
  getCompanyOverview: jest.fn().mockResolvedValue(mockApiResponses.companyOverview.success),
  
  // Company details API
  getCompanyDetails: jest.fn().mockResolvedValue(mockApiResponses.companyDetails.success),
  
  // Enhanced funds API
  getEnhancedFunds: jest.fn().mockResolvedValue(mockApiResponses.enhancedFunds.success)
};

// Mock API service with configurable responses
export const createMockApiService = (overrides: Partial<typeof mockApiService> = {}) => ({
  ...mockApiService,
  ...overrides
});

// Mock API service that returns errors
export const createMockApiServiceWithErrors = (errorType: keyof typeof mockApiErrors) => ({
  getCompanyOverview: jest.fn().mockRejectedValue(mockApiErrors[errorType]),
  getCompanyDetails: jest.fn().mockRejectedValue(mockApiErrors[errorType]),
  getEnhancedFunds: jest.fn().mockRejectedValue(mockApiErrors[errorType])
});

// Mock API service with loading delays
export const createMockApiServiceWithDelays = (delayMs: number = 1000) => ({
  getCompanyOverview: jest.fn().mockImplementation(() => 
    new Promise<any>(resolve => setTimeout(() => resolve(mockApiResponses.companyOverview.success), delayMs))
  ),
  getCompanyDetails: jest.fn().mockImplementation(() => 
    new Promise<any>(resolve => setTimeout(() => resolve(mockApiResponses.companyDetails.success), delayMs))
  ),
  getEnhancedFunds: jest.fn().mockImplementation(() => 
    new Promise<any>(resolve => setTimeout(() => resolve(mockApiResponses.enhancedFunds.success), delayMs))
  )
});

// Mock API service with specific response scenarios
export const createMockApiServiceWithScenario = (scenario: 'singleFund' | 'multiCurrency' | 'completedFunds' | 'highPerformance') => {
  let testData: any;
  
  switch (scenario) {
    case 'singleFund':
      testData = {
        company: createMockCompanyOverview({
          portfolio_summary: { active_funds_count: 1, completed_funds_count: 0 }
        }),
        funds: [createMockFund()]
      };
      break;
    case 'multiCurrency':
      testData = {
        company: createMockCompanyOverview({
          currency_breakdown: { AUD: 1500000, USD: 800000, EUR: 200000 }
        }),
        funds: [
          createMockFund({ currency: 'AUD', committed_capital: 1500000 }),
          createMockFund({ currency: 'USD', committed_capital: 800000 }),
          createMockFund({ currency: 'EUR', committed_capital: 200000 })
        ]
      };
      break;
    case 'completedFunds':
      testData = {
        company: createMockCompanyOverview({
          portfolio_summary: {
            active_funds_count: 0,
            completed_funds_count: 3
          },
          performance_summary: {
            total_return_percentage: 25.5
          }
        }),
        funds: [
          createMockFund({ status: 'COMPLETED', end_date: '2023-12-31' }),
          createMockFund({ status: 'COMPLETED', end_date: '2023-06-30' }),
          createMockFund({ status: 'COMPLETED', end_date: '2023-03-31' })
        ]
      };
      break;
    case 'highPerformance':
      testData = {
        company: createMockCompanyOverview({
          performance_summary: {
            total_return_percentage: 45.2
          },
          portfolio_summary: {
            total_current_value: 2000000
          }
        }),
        funds: [
          createMockFund({ expected_irr: 25.0, unrealized_gains: 300000 }),
          createMockFund({ expected_irr: 20.0, unrealized_gains: 200000 })
        ]
      };
      break;
  }
  
  return {
    getCompanyOverview: jest.fn().mockResolvedValue(testData.company),
    getCompanyDetails: jest.fn().mockResolvedValue(mockApiResponses.companyDetails.success),
    getEnhancedFunds: jest.fn().mockResolvedValue({
      funds: testData.funds,
      total_count: testData.funds.length,
      page: 1,
      page_size: 10,
      total_pages: 1
    })
  };
};

// Mock API service utilities
export const mockApiUtils = {
  // Reset all mocks
  resetAllMocks: () => {
    Object.values(mockApiService).forEach(mock => mock.mockReset());
  },
  
  // Set specific response for a method
  setResponse: (method: keyof typeof mockApiService, response: any) => {
    mockApiService[method].mockResolvedValue(response);
  },
  
  // Set error for a method
  setError: (method: keyof typeof mockApiService, error: any) => {
    mockApiService[method].mockRejectedValue(error);
  },
  
  // Check if method was called
  wasCalled: (method: keyof typeof mockApiService) => {
    return mockApiService[method].mock.calls.length > 0;
  },
  
  // Get call count for a method
  getCallCount: (method: keyof typeof mockApiService) => {
    return mockApiService[method].mock.calls.length;
  },
  
  // Get last call arguments for a method
  getLastCallArgs: (method: keyof typeof mockApiService) => {
    const calls = mockApiService[method].mock.calls;
    return calls.length > 0 ? calls[calls.length - 1] : [];
  }
};
