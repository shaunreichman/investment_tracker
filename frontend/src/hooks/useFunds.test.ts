// useFunds Comprehensive Testing
// This file addresses the critical 37.54% coverage gap in hooks

import { renderHook, act, waitFor } from '@testing-library/react';
import {
  useFunds,
  useFund,
  useCreateFund,
  useCreateFundEvent,
  useDeleteFundEvent,
  useCreateTaxStatement,
  useFundDetail
} from './useFunds';
import {
  Fund,
  FundTrackingType,
  FundStatus,
  FundEvent,
  EventType,
  ExtendedFundEvent,
  DashboardFund,
} from '../types/api';
import { apiClient } from '../services/api';

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
  tracking_type: FundTrackingType.NAV_BASED,
  status: FundStatus.ACTIVE,
  currency: 'AUD',
  current_equity_balance: 1000000,
  average_equity_balance: 1000000,
  final_tax_statement_received: false,
  created_at: '2023-01-01T00:00:00Z',
  updated_at: '2023-01-01T00:00:00Z',
  ...overrides
});

const createMockDashboardFund = (overrides: Partial<DashboardFund> = {}): DashboardFund => ({
  id: 1,
  name: 'Test Fund',
  fund_type: 'Private Equity',
  tracking_type: 'nav_based',
  currency: 'AUD',
  current_equity_balance: 1000000,
  average_equity_balance: 1000000,
  status: 'active',
  recent_events_count: 5,
  created_at: '2023-01-01T00:00:00Z',
  investment_company_id: 1,
  investment_company: 'Test Company',
  entity_id: 1,
  entity: 'Test Entity',
  ...overrides
});

const createMockFundEvent = (overrides: Partial<FundEvent> = {}): FundEvent => ({
  id: 1,
  fund_id: 1,
  event_type: EventType.CAPITAL_CALL,
  event_date: '2023-01-01',
  amount: 100000,
  created_at: '2023-01-01T00:00:00Z',
  updated_at: '2023-01-01T00:00:00Z',
  ...overrides
});

// MANUAL: Helper function to create ExtendedFundEvent objects for testing
const createMockExtendedFundEvent = (overrides: Partial<ExtendedFundEvent> = {}): ExtendedFundEvent => ({
  id: 1,
  fund_id: 1,
  event_type: EventType.DISTRIBUTION,
  event_date: '2024-01-01',
  amount: 100000, // Required in ExtendedFundEvent
  description: 'Test distribution',
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z',
  // ExtendedFundEvent specific properties
  is_grouped: false,
  // Optional ExtendedFundEvent properties - use null for nullable, omit for optional
  previous_nav_per_share: null,
  nav_change_absolute: null,
  nav_change_percentage: null,
  interest_income_amount: null,
  interest_income_tax_rate: null,
  dividend_franked_income_amount: null,
  dividend_franked_income_tax_rate: null,
  dividend_unfranked_income_amount: null,
  dividend_unfranked_income_tax_rate: null,
  capital_gain_income_amount: null,
  capital_gain_income_tax_rate: null,
  eofy_debt_interest_deduction_sum_of_daily_interest: null,
  eofy_debt_interest_deduction_rate: null,
  eofy_debt_interest_deduction_total_deduction: null,
  has_withholding_tax: false,
  withholding_amount: null,
  withholding_rate: null,
  net_interest: null,
  ...overrides
});

// ============================================================================
// MOCK API CLIENT
// ============================================================================

jest.mock('../services/api', () => ({
  apiClient: {
    getFunds: jest.fn(),
    getFund: jest.fn(),
    getFundDetail: jest.fn(),
    createFund: jest.fn(),
    createFundEvent: jest.fn(),
    deleteFundEvent: jest.fn(),
    getFundEvents: jest.fn(),
    createTaxStatement: jest.fn(),
    getFundTaxStatements: jest.fn()
  }
}));

const mockApiClient = apiClient as jest.Mocked<typeof apiClient>;

// ============================================================================
// HOOK TESTS
// ============================================================================

describe('useFunds', () => {
  // Reset mocks before each test
  beforeEach(() => {
    jest.clearAllMocks();
  });

  // ============================================================================
  // BASIC FUNCTIONALITY TESTS
  // ============================================================================

  describe('Basic Functionality', () => {
    it('should initialize with default state', () => {
      const { result } = renderHook(() => useFunds());

      expect(result.current.data).toBeNull();
      expect(result.current.loading).toBe(true);
      expect(result.current.error).toBeNull();
      expect(result.current.refetch).toBeInstanceOf(Function);
    });

    it('should fetch funds successfully', async () => {
      const mockFunds = [createMockDashboardFund(), createMockDashboardFund({ id: 2, name: 'Fund 2' })];
      mockApiClient.getFunds.mockResolvedValue(mockFunds);

      const { result } = renderHook(() => useFunds());

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(result.current.data).toEqual(mockFunds);
      expect(result.current.error).toBeNull();
    });
  });

  // ============================================================================
  // useFund TESTS
  // ============================================================================

  describe('useFund', () => {
    it('should fetch a single fund successfully', async () => {
      const mockFund = createMockFund();
      mockApiClient.getFund.mockResolvedValue(mockFund);

      const { result } = renderHook(() => useFund(1));

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(result.current.data).toEqual(mockFund);
      expect(result.current.error).toBeNull();
    });

    it('should handle fund fetch errors', async () => {
      const errorMessage = 'Failed to fetch fund';
      mockApiClient.getFund.mockRejectedValue(new Error(errorMessage));

      const { result } = renderHook(() => useFund(999));

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(result.current.error).toBeTruthy();
    });
  });

  // ============================================================================
  // useCreateFund TESTS
  // ============================================================================

  describe('useCreateFund', () => {
    it('should create a fund successfully', async () => {
      const mockFund = createMockFund();
      const createData = { name: 'New Fund', entity_id: 1, investment_company_id: 1, tracking_type: FundTrackingType.NAV_BASED };
      mockApiClient.createFund.mockResolvedValue(mockFund);

      const { result } = renderHook(() => useCreateFund());

      await act(async () => {
        await result.current.mutate(createData);
      });

      expect(mockApiClient.createFund).toHaveBeenCalledWith(createData);
    });

    it('should handle fund creation errors', async () => {
      const errorMessage = 'Failed to create fund';
      const createData = { name: 'New Fund', entity_id: 1, investment_company_id: 1, tracking_type: FundTrackingType.NAV_BASED };
      mockApiClient.createFund.mockRejectedValue(new Error(errorMessage));

      const { result } = renderHook(() => useCreateFund());

      await act(async () => {
        await result.current.mutate(createData);
      });

      expect(result.current.error).toBeTruthy();
    });
  });

  // ============================================================================
  // useCreateFundEvent TESTS
  // ============================================================================

  describe('useCreateFundEvent', () => {
    it('should create a fund event successfully', async () => {
      const mockEvent = createMockFundEvent();
      const eventData = { event_type: EventType.CAPITAL_CALL, amount: 100000, event_date: '2023-01-01' };
      mockApiClient.createFundEvent.mockResolvedValue(mockEvent);

      const { result } = renderHook(() => useCreateFundEvent(1));

      await act(async () => {
        await result.current.mutate(eventData);
      });

      expect(mockApiClient.createFundEvent).toHaveBeenCalledWith(1, eventData);
    });

    it('should handle fund event creation errors', async () => {
      const errorMessage = 'Failed to create fund event';
      const eventData = { event_type: EventType.CAPITAL_CALL, amount: 100000, event_date: '2023-01-01' };
      mockApiClient.createFundEvent.mockRejectedValue(new Error(errorMessage));

      const { result } = renderHook(() => useCreateFundEvent(1));

      await act(async () => {
        await result.current.mutate(eventData);
      });

      expect(result.current.error).toBeTruthy();
    });
  });

  // ============================================================================
  // useDeleteFundEvent TESTS
  // ============================================================================

  describe('useDeleteFundEvent', () => {
    it('should delete a fund event successfully', async () => {
      mockApiClient.deleteFundEvent.mockResolvedValue(undefined);

      const { result } = renderHook(() => useDeleteFundEvent(1, 1));

      await act(async () => {
        await result.current.mutate();
      });

      expect(mockApiClient.deleteFundEvent).toHaveBeenCalledWith(1, 1);
    });

    it('should handle fund event deletion errors', async () => {
      const errorMessage = 'Failed to delete fund event';
      mockApiClient.deleteFundEvent.mockRejectedValue(new Error(errorMessage));

      const { result } = renderHook(() => useDeleteFundEvent(1, 999));

      await act(async () => {
        await result.current.mutate();
      });

      expect(result.current.error).toBeTruthy();
    });
  });

  // ============================================================================
  // useCreateTaxStatement TESTS
  // ============================================================================

  describe('useCreateTaxStatement', () => {
    it('should create a tax statement successfully', async () => {
      const mockTaxStatement = {
        id: 1,
        fund_id: 1,
        entity_id: 1,
        financial_year: '2023',
        tax_payment_date: '2023-06-30',
        statement_date: '2023-06-30',
        interest_received_in_cash: 0,
        interest_receivable_this_fy: 0,
        interest_receivable_prev_fy: 0,
        interest_non_resident_withholding_tax_from_statement: 0,
        interest_income_tax_rate: 0,
        interest_income_amount: 0,
        interest_tax_amount: 0,
        interest_non_resident_withholding_tax_already_withheld: 0,
        dividend_franked_income_amount: 0,
        dividend_unfranked_income_amount: 0,
        dividend_franked_income_tax_rate: 0,
        dividend_unfranked_income_tax_rate: 0,
        capital_gain_income_amount: 0,
        capital_gain_income_tax_rate: 0,
        eofy_debt_interest_deduction_rate: 0,
        fy_debt_interest_deduction_sum_of_daily_interest: 0,
        fy_debt_interest_deduction_total_deduction: 0,
        foreign_income: 0,
        capital_gains: 0,
        other_income: 0,
        foreign_tax_credits: 0,
        non_resident: false,
        created_at: '2023-01-01T00:00:00Z',
        updated_at: '2023-01-01T00:00:00Z'
      };
      const taxData = {
        entity_id: 1,
        financial_year: '2023',
        statement_date: '2023-06-30',
        eofy_debt_interest_deduction_rate: 0
      };
      mockApiClient.createTaxStatement.mockResolvedValue(mockTaxStatement);

      const { result } = renderHook(() => useCreateTaxStatement(1));

      await act(async () => {
        await result.current.mutate(taxData);
      });

      expect(mockApiClient.createTaxStatement).toHaveBeenCalledWith(1, taxData);
    });

    it('should handle tax statement creation errors', async () => {
      const errorMessage = 'Failed to create tax statement';
      const taxData = {
        entity_id: 1,
        financial_year: '2023',
        statement_date: '2023-06-30',
        eofy_debt_interest_deduction_rate: 0
      };
      mockApiClient.createTaxStatement.mockRejectedValue(new Error(errorMessage));

      const { result } = renderHook(() => useCreateTaxStatement(1));

      await act(async () => {
        await result.current.mutate(taxData);
      });

      expect(result.current.error).toBeTruthy();
    });
  });

  // ============================================================================
  // useFundDetail TESTS
  // ============================================================================

  describe('useFundDetail', () => {
    it('should fetch fund details successfully', async () => {
      const mockFundDetail = {
        fund: {
          ...createMockFund(),
          investment_company: 'Test Company',
          entity: 'Test Entity'
        },
        events: [createMockExtendedFundEvent()],
        statistics: {
          total_events: 1,
          total_tax_statements: 0,
          recent_events_count: 1,
          current_equity_balance: 1000000,
          average_equity_balance: 1000000,
          capital_calls: 1,
          distributions: 0,
          nav_updates: 0,
          unit_purchases: 0,
          unit_sales: 0,
          total_capital_called: 100000,
          total_capital_returned: 0,
          total_distributions: 0,
          first_event_date: '2023-01-01',
          last_event_date: '2023-01-01'
        }
      };
      mockApiClient.getFundDetail.mockResolvedValue(mockFundDetail);

      const { result } = renderHook(() => useFundDetail(1));

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(result.current.data).toEqual(mockFundDetail);
      expect(result.current.error).toBeNull();
    });

    it('should handle fund detail fetch errors', async () => {
      const errorMessage = 'Failed to fetch fund details';
      mockApiClient.getFundDetail.mockRejectedValue(new Error(errorMessage));

      const { result } = renderHook(() => useFundDetail(999));

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(result.current.error).toBeTruthy();
    });
  });

  // ============================================================================
  // INTEGRATION TESTS
  // ============================================================================

  describe('Integration', () => {
    it('should work with different fund types', async () => {
      const navFund = createMockFund({ tracking_type: FundTrackingType.NAV_BASED });
              const costFund = createMockFund({ tracking_type: FundTrackingType.COST_BASED, id: 2 });

      mockApiClient.getFund.mockResolvedValueOnce(navFund);
      mockApiClient.getFund.mockResolvedValueOnce(costFund);

      const { result: navResult } = renderHook(() => useFund(1));
      const { result: costResult } = renderHook(() => useFund(2));

      await waitFor(() => {
        expect(navResult.current.loading).toBe(false);
      });
      await waitFor(() => {
        expect(costResult.current.loading).toBe(false);
      });

              expect(navResult.current.data?.tracking_type).toBe(FundTrackingType.NAV_BASED);
      expect(costResult.current.data?.tracking_type).toBe('cost_based');
    });

    it('should handle different event types', async () => {
      const capitalCallEvent = createMockFundEvent({ event_type: EventType.CAPITAL_CALL });
      const distributionEvent = createMockFundEvent({ event_type: EventType.DISTRIBUTION, id: 2 });

      mockApiClient.createFundEvent.mockResolvedValueOnce(capitalCallEvent);
      mockApiClient.createFundEvent.mockResolvedValueOnce(distributionEvent);

      const { result: capitalCallResult } = renderHook(() => useCreateFundEvent(1));
      const { result: distributionResult } = renderHook(() => useCreateFundEvent(1));

      await act(async () => {
        await capitalCallResult.current.mutate({ event_type: EventType.CAPITAL_CALL, amount: 100000, event_date: '2023-01-01' });
        await distributionResult.current.mutate({ event_type: EventType.DISTRIBUTION, amount: 50000, event_date: '2023-01-01' });
      });

      expect(mockApiClient.createFundEvent).toHaveBeenCalledTimes(2);
    });
  });

  // ============================================================================
  // EDGE CASES AND ERROR HANDLING
  // ============================================================================

  describe('Edge Cases and Error Handling', () => {
    it('should handle empty API responses', async () => {
      mockApiClient.getFunds.mockResolvedValue([]);

      const { result } = renderHook(() => useFunds());

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(result.current.data).toEqual([]);
    });

    it('should handle null API responses', async () => {
      mockApiClient.getFunds.mockRejectedValue(new Error('API returned null'));

      const { result } = renderHook(() => useFunds());

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(result.current.error).toBeTruthy();
    });

    it('should handle undefined API responses', async () => {
      mockApiClient.getFunds.mockRejectedValue(new Error('API returned undefined'));

      const { result } = renderHook(() => useFunds());

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(result.current.error).toBeTruthy();
    });

    it('should handle very large fund lists', async () => {
      const largeFundList = Array.from({ length: 1000 }, (_, i) =>
        createMockDashboardFund({ id: i + 1, name: `Fund ${i + 1}` })
      );
      mockApiClient.getFunds.mockResolvedValue(largeFundList);

      const { result } = renderHook(() => useFunds());

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(result.current.data).toHaveLength(1000);
    });
  });

  // ============================================================================
  // PERFORMANCE TESTS
  // ============================================================================

  describe('Performance', () => {
    it('should handle rapid successive operations efficiently', async () => {
      const mockFunds = [createMockDashboardFund()];
      mockApiClient.getFunds.mockResolvedValue(mockFunds);

      const { result } = renderHook(() => useFunds());

      const startTime = performance.now();

      await act(async () => {
        await Promise.all([
          result.current.refetch(),
          result.current.refetch(),
          result.current.refetch()
        ]);
      });

      const endTime = performance.now();
      const executionTime = endTime - startTime;

      // Should complete within reasonable time (adjust threshold as needed)
      expect(executionTime).toBeLessThan(1000);
    });

    it('should handle concurrent operations without state corruption', async () => {
      const mockFunds = [createMockDashboardFund()];
      mockApiClient.getFunds.mockResolvedValue(mockFunds);

      const { result } = renderHook(() => useFunds());

      // Start multiple concurrent operations
      const promises = [
        result.current.refetch(),
        result.current.refetch(),
        result.current.refetch()
      ];

      await act(async () => {
        await Promise.all(promises);
      });

      // State should remain consistent
      expect(result.current.data).toEqual(mockFunds);
      expect(result.current.loading).toBe(false);
    });
  });
});
