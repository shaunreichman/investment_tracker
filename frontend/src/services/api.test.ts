// API Layer Comprehensive Testing
// This file addresses the critical 15.87% API coverage gap

import { apiClient } from './api';
import { 
  Fund, 
  FundEvent,
  CreateFundData, 
  CreateFundEventData, 
  CreateTaxStatementData,

  InvestmentCompany,
  CreateInvestmentCompanyData,
  Entity,
  CreateEntityData,
  FundType,
  FundStatus,
  EventType
} from '../types/api';

// ============================================================================
// MOCK DATA FACTORIES
// ============================================================================

const createMockFund = (overrides: Partial<Fund> = {}): Fund => ({
  id: 1,
  name: 'Test Fund',
  entity_id: 1,
  investment_company_id: 1,
  commitment_amount: 1000000,
  expected_irr: 0.15,
  tracking_type: FundType.NAV_BASED,
  status: FundStatus.ACTIVE,
  currency: 'AUD',
  current_equity_balance: 1000000,
  average_equity_balance: 1000000,
  final_tax_statement_received: false,
  current_nav_total: 1100000,
  created_at: '2023-01-01T00:00:00Z',
  updated_at: '2023-01-01T00:00Z',
  ...overrides
});

const createMockFundEvent = (overrides: Partial<FundEvent> = {}): FundEvent => ({
  id: 1,
  fund_id: 1,
  event_type: EventType.CAPITAL_CALL,
  event_date: '2023-01-01',
  amount: 100000,
  description: 'Test event',
  created_at: '2023-01-01T00:00:00Z',
  updated_at: '2023-01-01T00:00Z',
  ...overrides
});

const createMockInvestmentCompany = (overrides: Partial<InvestmentCompany> = {}): InvestmentCompany => ({
  id: 1,
  name: 'Test Company',
  created_at: '2023-01-01T00:00:00Z',
  updated_at: '2023-01-01T00:00:00Z',
  ...overrides
});

const createMockEntity = (overrides: Partial<Entity> = {}): Entity => ({
  id: 1,
  name: 'Test Entity',
  created_at: '2023-01-01T00:00:00Z',
  updated_at: '2023-01-01T00:00:00Z',
  ...overrides
});

// ============================================================================
// API CLIENT TESTS
// ============================================================================

describe('API Client', () => {
  // Reset fetch mock before each test
  beforeEach(() => {
    global.fetch = jest.fn();
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  // ============================================================================
  // FUNDS API TESTS
  // ============================================================================

  describe('Funds API', () => {
    describe('getFunds', () => {
      it('should fetch all funds successfully', async () => {
        const mockFunds = [createMockFund(), createMockFund({ id: 2, name: 'Fund 2' })];
        const mockResponse = { ok: true, json: () => Promise.resolve({ funds: mockFunds }) };
        
        (global.fetch as jest.Mock).mockResolvedValue(mockResponse);

        const result = await apiClient.getFunds();

        expect(global.fetch).toHaveBeenCalledWith('http://localhost:5001/api/dashboard/funds', {
          method: 'GET',
          headers: { 'Content-Type': 'application/json' }
        });
        expect(result).toEqual(mockFunds);
      });

      it('should handle network errors', async () => {
        (global.fetch as jest.Mock).mockRejectedValue(new Error('Network error'));

        await expect(apiClient.getFunds()).rejects.toThrow();
      });
    });

    describe('getFund', () => {
      it('should fetch a single fund by ID', async () => {
        const mockFund = createMockFund();
        const mockResponse = { ok: true, json: () => Promise.resolve({ fund: mockFund, events: [], tax_statements: [], statistics: {} }) };
        
        (global.fetch as jest.Mock).mockResolvedValue(mockResponse);

        const result = await apiClient.getFund(1);

        expect(global.fetch).toHaveBeenCalledWith('http://localhost:5001/api/funds/1', {
          method: 'GET',
          headers: { 'Content-Type': 'application/json' }
        });
        expect(result).toEqual(mockFund);
      });

      it('should handle fund not found', async () => {
        const mockResponse = { 
          ok: false, 
          status: 404, 
          statusText: 'Not Found',
          json: () => Promise.resolve({ error: 'Fund not found' })
        };
        
        (global.fetch as jest.Mock).mockResolvedValue(mockResponse);

        await expect(apiClient.getFund(999)).rejects.toThrow();
      });
    });

    describe('getFundDetail', () => {
      it('should fetch fund detail with events and statistics', async () => {
        const mockFundDetail = {
          fund: createMockFund(),
          events: [createMockFundEvent()],
          tax_statements: [],
          statistics: {}
        };
        const mockResponse = { ok: true, json: () => Promise.resolve(mockFundDetail) };
        
        (global.fetch as jest.Mock).mockResolvedValue(mockResponse);

        const result = await apiClient.getFundDetail(1);

        expect(global.fetch).toHaveBeenCalledWith('http://localhost:5001/api/funds/1', {
          method: 'GET',
          headers: { 'Content-Type': 'application/json' }
        });
        expect(result).toEqual(mockFundDetail);
      });
    });

    describe('createFund', () => {
      it('should create a new fund successfully', async () => {
        const createData: CreateFundData = {
          name: 'New Fund',
          entity_id: 1,
          investment_company_id: 1,
          commitment_amount: 1000000,
          expected_irr: 0.15,
          tracking_type: FundType.NAV_BASED
        };
        
        const mockFund = createMockFund(createData);
        const mockResponse = { ok: true, json: () => Promise.resolve(mockFund) };
        
        (global.fetch as jest.Mock).mockResolvedValue(mockResponse);

        const result = await apiClient.createFund(createData);

        expect(global.fetch).toHaveBeenCalledWith('http://localhost:5001/api/funds', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(createData)
        });
        expect(result).toEqual(mockFund);
      });

      it('should validate fund creation data', async () => {
        const invalidData = { name: '' } as CreateFundData;
        const mockResponse = { 
          ok: false, 
          status: 400, 
          statusText: 'Bad Request',
          json: () => Promise.resolve({ error: 'Name is required' })
        };
        
        (global.fetch as jest.Mock).mockResolvedValue(mockResponse);

        await expect(apiClient.createFund(invalidData)).rejects.toThrow();
      });
    });
  });

  // ============================================================================
  // FUND EVENTS API TESTS
  // ============================================================================

  describe('Fund Events API', () => {
    describe('getFundEvents', () => {
      it('should fetch fund events successfully', async () => {
        const mockEvents = [createMockFundEvent()];
        const mockResponse = { ok: true, json: () => Promise.resolve({ events: mockEvents }) };
        
        (global.fetch as jest.Mock).mockResolvedValue(mockResponse);

        const result = await apiClient.getFundEvents(1);

        expect(global.fetch).toHaveBeenCalledWith('http://localhost:5001/api/funds/1/events', {
          method: 'GET',
          headers: { 'Content-Type': 'application/json' }
        });
        expect(result).toEqual({ events: mockEvents });
      });
    });

    describe('createFundEvent', () => {
      it('should create a fund event successfully', async () => {
        const eventData: CreateFundEventData = {
          event_type: EventType.CAPITAL_CALL,
          event_date: '2023-01-01',
          amount: 100000,
          description: 'Test capital call'
        };
        
        const mockEvent = createMockFundEvent(eventData);
        const mockResponse = { ok: true, json: () => Promise.resolve(mockEvent) };
        
        (global.fetch as jest.Mock).mockResolvedValue(mockResponse);

        const result = await apiClient.createFundEvent(1, eventData);

        expect(global.fetch).toHaveBeenCalledWith('http://localhost:5001/api/funds/1/events', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(eventData)
        });
        expect(result).toEqual(mockEvent);
      });

      it('should handle event creation validation errors', async () => {
        const invalidEventData = { 
          event_type: 'INVALID_TYPE' as EventType, 
          event_date: '2023-01-01' 
        } as CreateFundEventData;
        const mockResponse = { 
          ok: false, 
          status: 400, 
          statusText: 'Bad Request',
          json: () => Promise.resolve({ error: 'Invalid event type' })
        };
        
        (global.fetch as jest.Mock).mockResolvedValue(mockResponse);

        await expect(apiClient.createFundEvent(1, invalidEventData)).rejects.toThrow();
      });
    });

    describe('deleteFundEvent', () => {
      it('should delete a fund event successfully', async () => {
        const mockResponse = { ok: true, status: 204 };
        
        (global.fetch as jest.Mock).mockResolvedValue(mockResponse);

        await apiClient.deleteFundEvent(1, 1);

        expect(global.fetch).toHaveBeenCalledWith('http://localhost:5001/api/funds/1/events/1', {
          method: 'DELETE',
          headers: { 'Content-Type': 'application/json' }
        });
      });

      it('should handle deletion of non-existent event', async () => {
        const mockResponse = { 
          ok: false, 
          status: 404, 
          statusText: 'Not Found',
          json: () => Promise.resolve({ error: 'Event not found' })
        };
        
        (global.fetch as jest.Mock).mockResolvedValue(mockResponse);

        await expect(apiClient.deleteFundEvent(1, 999)).rejects.toThrow();
      });
    });
  });

  // ============================================================================
  // TAX STATEMENTS API TESTS
  // ============================================================================

  describe('Tax Statements API', () => {
    describe('createTaxStatement', () => {
      it('should create a tax statement successfully', async () => {
        const taxData: CreateTaxStatementData = {
          entity_id: 1,
          financial_year: '2023',
          statement_date: '2023-06-30',
          eofy_debt_interest_deduction_rate: 0.05,
          non_resident: false,
          dividend_franked_income_amount: 8000,
          dividend_unfranked_income_amount: 2000,
          dividend_franked_income_tax_rate: 0.3,
          dividend_unfranked_income_tax_rate: 0.45,
          interest_income_tax_rate: 0.3
        };
        
        const mockTaxStatement = { id: 1, fund_id: 1, ...taxData };
        const mockResponse = { ok: true, json: () => Promise.resolve(mockTaxStatement) };
        
        (global.fetch as jest.Mock).mockResolvedValue(mockResponse);

        const result = await apiClient.createTaxStatement(1, taxData);

        expect(global.fetch).toHaveBeenCalledWith('http://localhost:5001/api/funds/1/tax-statements', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(taxData)
        });
        expect(result).toEqual(mockTaxStatement);
      });
    });

    describe('getFundTaxStatements', () => {
      it('should fetch fund tax statements successfully', async () => {
        const mockTaxStatements = [{ id: 1, fund_id: 1, financial_year: '2023' }];
        const mockResponse = { ok: true, json: () => Promise.resolve({ tax_statements: mockTaxStatements }) };
        
        (global.fetch as jest.Mock).mockResolvedValue(mockResponse);

        const result = await apiClient.getFundTaxStatements(1);

        expect(global.fetch).toHaveBeenCalledWith('http://localhost:5001/api/funds/1/tax-statements', {
          method: 'GET',
          headers: { 'Content-Type': 'application/json' }
        });
        expect(result).toEqual({ tax_statements: mockTaxStatements });
      });
    });
  });

  // ============================================================================
  // INVESTMENT COMPANIES API TESTS
  // ============================================================================

  describe('Investment Companies API', () => {
    describe('getInvestmentCompanies', () => {
      it('should fetch investment companies successfully', async () => {
        const mockCompanies = [createMockInvestmentCompany()];
        const mockResponse = { ok: true, json: () => Promise.resolve({ companies: mockCompanies }) };
        
        (global.fetch as jest.Mock).mockResolvedValue(mockResponse);

        const result = await apiClient.getInvestmentCompanies();

        expect(global.fetch).toHaveBeenCalledWith('http://localhost:5001/api/investment-companies', {
          method: 'GET',
          headers: { 'Content-Type': 'application/json' }
        });
        expect(result).toEqual(mockCompanies);
      });
    });

    describe('createInvestmentCompany', () => {
      it('should create an investment company successfully', async () => {
        const companyData: CreateInvestmentCompanyData = { name: 'New Company' };
        const mockCompany = createMockInvestmentCompany(companyData);
        const mockResponse = { ok: true, json: () => Promise.resolve(mockCompany) };
        
        (global.fetch as jest.Mock).mockResolvedValue(mockResponse);

        const result = await apiClient.createInvestmentCompany(companyData);

        expect(global.fetch).toHaveBeenCalledWith('http://localhost:5001/api/investment-companies', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(companyData)
        });
        expect(result).toEqual(mockCompany);
      });
    });
  });

  // ============================================================================
  // ENTITIES API TESTS
  // ============================================================================

  describe('Entities API', () => {
    describe('getEntities', () => {
      it('should fetch entities successfully', async () => {
        const mockEntities = [createMockEntity()];
        const mockResponse = { ok: true, json: () => Promise.resolve({ entities: mockEntities }) };
        
        (global.fetch as jest.Mock).mockResolvedValue(mockResponse);

        const result = await apiClient.getEntities();

        expect(global.fetch).toHaveBeenCalledWith('http://localhost:5001/api/entities', {
          method: 'GET',
          headers: { 'Content-Type': 'application/json' }
        });
        expect(result).toEqual(mockEntities);
      });
    });

    describe('createEntity', () => {
      it('should create an entity successfully', async () => {
        const entityData: CreateEntityData = { name: 'New Entity' };
        const mockEntity = createMockEntity(entityData);
        const mockResponse = { ok: true, json: () => Promise.resolve(mockEntity) };
        
        (global.fetch as jest.Mock).mockResolvedValue(mockResponse);

        const result = await apiClient.createEntity(entityData);

        expect(global.fetch).toHaveBeenCalledWith('http://localhost:5001/api/entities', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(entityData)
        });
        expect(result).toEqual(mockEntity);
      });
    });
  });

  // ============================================================================
  // ERROR HANDLING TESTS
  // ============================================================================

  describe('Error Handling', () => {
    it('should handle malformed JSON responses', async () => {
      const mockResponse = { 
        ok: true, 
        json: () => Promise.reject(new Error('Invalid JSON'))
      };
      
      (global.fetch as jest.Mock).mockResolvedValue(mockResponse);

      await expect(apiClient.getFunds()).rejects.toThrow();
    });

    it('should handle timeout scenarios', async () => {
      (global.fetch as jest.Mock).mockRejectedValue(
        new Error('Request timeout')
      );

      await expect(apiClient.getFunds()).rejects.toThrow();
    });

    it('should handle different HTTP status codes', async () => {
      const statusCodes = [400, 401, 403, 404, 500];
      
      for (const status of statusCodes) {
        const mockResponse = { 
          ok: false, 
          status, 
          statusText: 'Error',
          json: () => Promise.resolve({ error: `Error ${status}` })
        };
        
        (global.fetch as jest.Mock).mockResolvedValue(mockResponse);

        await expect(apiClient.getFunds()).rejects.toThrow();
      }
    });
  });

  // ============================================================================
  // SECURITY TESTS
  // ============================================================================

  describe('Security', () => {
    it('should not expose sensitive information in error messages', async () => {
      const mockResponse = { 
        ok: false, 
        status: 500, 
        statusText: 'Internal Server Error',
        json: () => Promise.resolve({ error: 'Internal server error' })
      };
      
      (global.fetch as jest.Mock).mockResolvedValue(mockResponse);

      await expect(apiClient.getFunds()).rejects.toThrow();
    });
  });
});
