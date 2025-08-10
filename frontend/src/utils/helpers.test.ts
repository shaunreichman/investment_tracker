/**
 * Tests for helpers utility functions
 */

import {
  getEventTypeColor,
  getEventTypeLabel,
  getStatusInfo,
  isActiveNavFund,
  prepareChartData,
  calculateDateRange,
  generateChartTicks,
  calculateWithholdingTax,
  calculateNetAmount,
  formatNumber,
  parseNumber,
  calculateTaxPaymentDate,
  debounce,
  throttle,
  deepClone,
  deepEqual,
} from './helpers';
import { EventType, DistributionType, TaxPaymentType, FundType, FundStatus, ExtendedFundEvent, ExtendedFund } from '../types/api';

describe('helpers', () => {
  describe('getEventTypeColor', () => {
    it('should return correct colors for event types', () => {
      expect(getEventTypeColor('CAPITAL_CALL')).toBe('primary');
      expect(getEventTypeColor('DISTRIBUTION')).toBe('success');
      expect(getEventTypeColor('RETURN_OF_CAPITAL')).toBe('warning');
      expect(getEventTypeColor('NAV_UPDATE')).toBe('info');
      expect(getEventTypeColor('UNIT_PURCHASE')).toBe('primary');
      expect(getEventTypeColor('UNIT_SALE')).toBe('warning');
      expect(getEventTypeColor('TAX_PAYMENT')).toBe('error');
    });

    it('should return default for unknown event types', () => {
      expect(getEventTypeColor('UNKNOWN_TYPE')).toBe('default');
    });
  });

  describe('getEventTypeLabel', () => {
    const mockEvent: ExtendedFundEvent = {
      id: 1,
      fund_id: 1,
      event_type: EventType.DISTRIBUTION,
      event_date: '2023-01-01',
      amount: 1000,
      distribution_type: DistributionType.INTEREST,
      created_at: '2023-01-01',
      updated_at: '2023-01-01',
    };

    it('should return distribution type label when available', () => {
      expect(getEventTypeLabel(mockEvent)).toBe('INTEREST');
    });

    it('should return tax payment type label when available', () => {
      const taxEvent: ExtendedFundEvent = {
        ...mockEvent,
        event_type: EventType.TAX_PAYMENT,
        distribution_type: undefined, // Clear distribution_type to test tax_payment_type
        tax_payment_type: TaxPaymentType.NON_RESIDENT_INTEREST_WITHHOLDING,
      };
      expect(getEventTypeLabel(taxEvent)).toBe('NON_RESIDENT_INTEREST_WITHHOLDING');
    });

    it('should format event type when no subtype available', () => {
      const capitalEvent: ExtendedFundEvent = {
        ...mockEvent,
        event_type: EventType.CAPITAL_CALL,
        distribution_type: undefined,
      };
      expect(getEventTypeLabel(capitalEvent)).toBe('CAPITAL CALL');
    });
  });

  describe('getStatusInfo', () => {
    it('should return correct status info for known statuses', () => {
      expect(getStatusInfo('ACTIVE')).toEqual({
        value: 'Active',
        color: '#4caf50',
        icon: '📊',
        tooltip: 'Fund is still invested and has capital at risk'
      });
      expect(getStatusInfo('REALIZED')).toEqual({
        value: 'Realized',
        color: '#424242',
        icon: '📊',
        tooltip: 'All capital has been returned. Fund will be completed once the final tax statement is added.'
      });
      expect(getStatusInfo('COMPLETED')).toEqual({
        value: 'Completed',
        color: '#000000',
        icon: '📊',
        tooltip: 'Fund is fully realized and all tax obligations are complete'
      });
    });

    it('should return status as label for unknown statuses', () => {
      expect(getStatusInfo('UNKNOWN')).toEqual({
        value: 'Unknown',
        color: 'text.secondary',
        icon: '📊',
        tooltip: 'Unknown fund status'
      });
    });
  });

  describe('isActiveNavFund', () => {
    it('should return true for active NAV-based funds', () => {
      const fund: ExtendedFund = {
        id: 1,
        name: 'Test Fund',
        tracking_type: FundType.NAV_BASED,
        status: FundStatus.ACTIVE,
        currency: 'AUD',
        current_equity_balance: 100000,
        average_equity_balance: 100000,
        investment_company_id: 1,
        entity_id: 1,
        created_at: '2023-01-01',
        updated_at: '2023-01-01',
        investment_company: 'Co',
        entity: 'Entity',
        final_tax_statement_received: false,
      };
      expect(isActiveNavFund(fund)).toBe(true);
    });

    it('should return false for cost-based funds', () => {
      const fund: ExtendedFund = {
        id: 1,
        name: 'Test Fund',
        tracking_type: FundType.COST_BASED,
        status: FundStatus.ACTIVE,
        currency: 'AUD',
        current_equity_balance: 100000,
        average_equity_balance: 100000,
        investment_company_id: 1,
        entity_id: 1,
        created_at: '2023-01-01',
        updated_at: '2023-01-01',
        investment_company: 'Co',
        entity: 'Entity',
        final_tax_statement_received: false,
      };
      expect(isActiveNavFund(fund)).toBe(false);
    });

    it('should return false for inactive funds', () => {
      const fund: ExtendedFund = {
        id: 1,
        name: 'Test Fund',
        tracking_type: FundType.NAV_BASED,
        status: FundStatus.COMPLETED,
        currency: 'AUD',
        current_equity_balance: 0,
        average_equity_balance: 0,
        investment_company_id: 1,
        entity_id: 1,
        created_at: '2023-01-01',
        updated_at: '2023-01-01',
        investment_company: 'Co',
        entity: 'Entity',
        final_tax_statement_received: true,
      };
      expect(isActiveNavFund(fund)).toBe(false);
    });
  });

  describe('prepareChartData', () => {
    const navEvent: ExtendedFundEvent = {
      id: 1,
      fund_id: 1,
      event_type: EventType.NAV_UPDATE,
      event_date: '2023-01-01',
      amount: null,
      nav_per_share: 10.5,
      created_at: '2023-01-01',
      updated_at: '2023-01-01',
    };

    const purchaseEvent: ExtendedFundEvent = {
      id: 2,
      fund_id: 1,
      event_type: EventType.UNIT_PURCHASE,
      event_date: '2023-01-01',
      amount: 1000,
      units_purchased: 100,
      unit_price: 10.0,
      created_at: '2023-01-01',
      updated_at: '2023-01-01',
    };

    const saleEvent: ExtendedFundEvent = {
      id: 3,
      fund_id: 1,
      event_type: EventType.UNIT_SALE,
      event_date: '2023-01-01',
      amount: 500,
      units_sold: 50,
      unit_price: 10.0,
      created_at: '2023-01-01',
      updated_at: '2023-01-01',
    };

    const fund: ExtendedFund = {
      id: 1,
      name: 'Test Fund',
      tracking_type: FundType.NAV_BASED,
      status: FundStatus.ACTIVE,
      currency: 'AUD',
      current_equity_balance: 100000,
      average_equity_balance: 100000,
      investment_company_id: 1,
      entity_id: 1,
      created_at: '2023-01-01',
      updated_at: '2023-01-01',
      investment_company: 'Co',
      entity: 'Entity',
      final_tax_statement_received: false,
    };

    it('should prepare chart data for NAV-based funds', () => {
      const events = [navEvent, purchaseEvent, saleEvent];
      const chartData = prepareChartData(events, fund);

      expect(chartData.navData).toHaveLength(1);
      expect(chartData.navData[0]).toEqual({ date: '2023-01-01', nav: 10.5 });

      expect(chartData.purchaseData).toHaveLength(1);
      expect(chartData.purchaseData[0]).toEqual({ date: '2023-01-01', price: 10.0, units: 100 });

      expect(chartData.saleData).toHaveLength(1);
      expect(chartData.saleData[0]).toEqual({ date: '2023-01-01', price: 10.0, units: 50 });
    });

    it('should return empty arrays for cost-based funds', () => {
      const costBasedFund: ExtendedFund = { ...fund, tracking_type: FundType.COST_BASED };
      const events = [navEvent, purchaseEvent, saleEvent];
      const chartData = prepareChartData(events, costBasedFund);

      expect(chartData.navData).toHaveLength(0);
      expect(chartData.purchaseData).toHaveLength(0);
      expect(chartData.saleData).toHaveLength(0);
    });
  });

  describe('calculateDateRange', () => {
    it('should calculate date range from events', () => {
      const events: ExtendedFundEvent[] = [
        {
          id: 1,
          fund_id: 1,
          event_type: EventType.CAPITAL_CALL,
          event_date: '2023-01-01',
          amount: 1000,
          created_at: '2023-01-01',
          updated_at: '2023-01-01',
        },
        {
          id: 2,
          fund_id: 1,
          event_type: EventType.DISTRIBUTION,
          event_date: '2023-12-31',
          amount: 500,
          created_at: '2023-01-01',
          updated_at: '2023-01-01',
        },
      ];

      const dateRange = calculateDateRange(events);
      expect(dateRange.startDate).toBe('2022-12-01'); // One month before
      expect(dateRange.endDate).toBe('2024-01-31'); // One month after
    });

    it('should return default range for empty events', () => {
      const dateRange = calculateDateRange([]);
      const today = new Date();
      const sixMonthsAgo = new Date(today.getFullYear(), today.getMonth() - 6, today.getDate());

      expect(dateRange.startDate).toBe(sixMonthsAgo.toISOString().split('T')[0]);
      expect(dateRange.endDate).toBe(today.toISOString().split('T')[0]);
    });
  });

  describe('generateChartTicks', () => {
    it('should generate monthly ticks between dates', () => {
      const ticks = generateChartTicks('2023-01-01', '2023-03-31');
      expect(ticks).toEqual(['2023-01-01', '2023-02-01', '2023-03-01']);
    });

    it('should handle single month', () => {
      const ticks = generateChartTicks('2023-01-01', '2023-01-31');
      expect(ticks).toEqual(['2023-01-01']);
    });
  });

  describe('calculateWithholdingTax', () => {
    it('should calculate withholding tax correctly', () => {
      expect(calculateWithholdingTax(1000, 10)).toBe(100);
      expect(calculateWithholdingTax(500, 15)).toBe(75);
      expect(calculateWithholdingTax(0, 10)).toBe(0);
    });
  });

  describe('calculateNetAmount', () => {
    it('should calculate net amount correctly', () => {
      expect(calculateNetAmount(1000, 100)).toBe(900);
      expect(calculateNetAmount(500, 50)).toBe(450);
      expect(calculateNetAmount(1000, 0)).toBe(1000);
    });
  });

  describe('formatNumber', () => {
    it('should format numbers correctly', () => {
      expect(formatNumber('1234.56')).toBe('1234.56');
      expect(formatNumber('abc')).toBe('abc');
      expect(formatNumber('')).toBe('');
    });
  });

  describe('parseNumber', () => {
    it('should parse numbers correctly', () => {
      expect(parseNumber('1234.56')).toBe('1234.56');
      expect(parseNumber('abc')).toBe('');
      expect(parseNumber('')).toBe('');
    });
  });

  describe('calculateTaxPaymentDate', () => {
    it('should calculate tax payment date correctly', () => {
      expect(calculateTaxPaymentDate('2023-24')).toBe('2024-06-30');
      expect(calculateTaxPaymentDate('2022-23')).toBe('2023-06-30');
    });
  });

  describe('debounce', () => {
    it('should debounce function calls', (done) => {
      let callCount = 0;
      const debouncedFn = debounce(() => {
        callCount++;
      }, 100);

      debouncedFn();
      debouncedFn();
      debouncedFn();

      setTimeout(() => {
        expect(callCount).toBe(1);
        done();
      }, 150);
    });
  });

  describe('throttle', () => {
    it('should throttle function calls', (done) => {
      let callCount = 0;
      const throttledFn = throttle(() => {
        callCount++;
      }, 100);

      throttledFn();
      throttledFn();
      throttledFn();

      setTimeout(() => {
        expect(callCount).toBe(1);
        done();
      }, 50);
    });
  });

  describe('deepClone', () => {
    it('should clone primitive values', () => {
      expect(deepClone(42)).toBe(42);
      expect(deepClone('test')).toBe('test');
      expect(deepClone(null)).toBe(null);
      expect(deepClone(undefined)).toBe(undefined);
    });

    it('should clone objects', () => {
      const obj = { a: 1, b: { c: 2 } };
      const cloned = deepClone(obj);
      
      expect(cloned).toEqual(obj);
      expect(cloned).not.toBe(obj);
      expect(cloned.b).not.toBe(obj.b);
    });

    it('should clone arrays', () => {
      const arr = [1, { a: 2 }, [3, 4]];
      const cloned = deepClone(arr);
      
      expect(cloned).toEqual(arr);
      expect(cloned).not.toBe(arr);
      expect(cloned[1]).not.toBe(arr[1]);
      expect(cloned[2]).not.toBe(arr[2]);
    });

    it('should clone dates', () => {
      const date = new Date('2023-01-01');
      const cloned = deepClone(date);
      
      expect(cloned).toEqual(date);
      expect(cloned).not.toBe(date);
    });
  });

  describe('deepEqual', () => {
    it('should compare primitive values', () => {
      expect(deepEqual(42, 42)).toBe(true);
      expect(deepEqual(42, 43)).toBe(false);
      expect(deepEqual('test', 'test')).toBe(true);
      expect(deepEqual('test', 'other')).toBe(false);
    });

    it('should compare objects', () => {
      const obj1 = { a: 1, b: { c: 2 } };
      const obj2 = { a: 1, b: { c: 2 } };
      const obj3 = { a: 1, b: { c: 3 } };
      
      expect(deepEqual(obj1, obj2)).toBe(true);
      expect(deepEqual(obj1, obj3)).toBe(false);
    });

    it('should compare arrays', () => {
      const arr1 = [1, { a: 2 }, [3, 4]];
      const arr2 = [1, { a: 2 }, [3, 4]];
      const arr3 = [1, { a: 2 }, [3, 5]];
      
      expect(deepEqual(arr1, arr2)).toBe(true);
      expect(deepEqual(arr1, arr3)).toBe(false);
    });

    it('should handle null and undefined', () => {
      expect(deepEqual(null, null)).toBe(true);
      expect(deepEqual(undefined, undefined)).toBe(true);
      expect(deepEqual(null, undefined)).toBe(false);
    });
  });
}); 