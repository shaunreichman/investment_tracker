/**
 * Tests for formatters utility functions
 */

import {
  formatCurrency,
  formatBrokerageFee,
  formatDate,
  formatNumber,
  formatPercentage,
  formatLargeNumber,
} from './formatters';

describe('formatters', () => {
  describe('formatCurrency', () => {
    it('should format positive amounts correctly', () => {
      expect(formatCurrency(1234.56)).toBe('$1,234.56');
      expect(formatCurrency(0)).toBe('$0.00');
      expect(formatCurrency(1000000)).toBe('$1,000,000.00');
    });

    it('should format negative amounts with parentheses', () => {
      expect(formatCurrency(-1234.56)).toBe('($1,234.56)');
      expect(formatCurrency(-0)).toBe('$0.00');
      expect(formatCurrency(-1000000)).toBe('($1,000,000.00)');
    });

    it('should handle null values', () => {
      expect(formatCurrency(null)).toBe('-');
    });

    it('should support different currencies', () => {
      expect(formatCurrency(1234.56, 'USD')).toBe('USD\u00A01,234.56');
      expect(formatCurrency(1234.56, 'EUR')).toBe('EUR\u00A01,234.56');
      expect(formatCurrency(1234.56, 'GBP')).toBe('GBP\u00A01,234.56');
    });

    it('should handle decimal precision correctly', () => {
      expect(formatCurrency(1234.5)).toBe('$1,234.50');
      expect(formatCurrency(1234.567)).toBe('$1,234.57'); // Rounds to 2 decimal places
    });
  });

  describe('formatBrokerageFee', () => {
    it('should format brokerage fees correctly', () => {
      expect(formatBrokerageFee(50)).toBe('$50');
      expect(formatBrokerageFee(50.5)).toBe('$51'); // Rounds to whole number
      expect(formatBrokerageFee(0)).toBe('$0');
    });

    it('should round brokerage fees to whole numbers', () => {
      expect(formatBrokerageFee(50.7)).toBe('$51');
      expect(formatBrokerageFee(50.3)).toBe('$50');
    });

    it('should handle null values', () => {
      expect(formatBrokerageFee(null)).toBe('-');
    });

    it('should support different currencies', () => {
      expect(formatBrokerageFee(50, 'USD')).toBe('USD\u00A050');
      expect(formatBrokerageFee(50, 'EUR')).toBe('EUR\u00A050');
    });
  });

  describe('formatDate', () => {
    it('should format dates correctly', () => {
      expect(formatDate('2023-01-15')).toBe('15-Jan-23');
      expect(formatDate('2023-12-31')).toBe('31-Dec-23');
      expect(formatDate('2024-06-01')).toBe('1-June-24'); // Month name varies by locale
    });

    it('should handle null and empty values', () => {
      expect(formatDate(null)).toBe('-');
      expect(formatDate('')).toBe('-');
    });

    it('should handle invalid date strings gracefully', () => {
      expect(formatDate('invalid-date')).toBe('NaN-Invalid Date-aN');
    });

    it('should format dates with different years correctly', () => {
      expect(formatDate('2020-01-01')).toBe('1-Jan-20');
      expect(formatDate('2030-12-31')).toBe('31-Dec-30');
    });
  });

  describe('formatNumber', () => {
    it('should format numbers with default 2 decimal places', () => {
      expect(formatNumber(1234.56)).toBe('1,234.56');
      expect(formatNumber(0)).toBe('0.00');
      expect(formatNumber(1000000)).toBe('1,000,000.00');
    });

    it('should format numbers with custom decimal places', () => {
      expect(formatNumber(1234.56, 0)).toBe('1,235');
      expect(formatNumber(1234.56, 1)).toBe('1,234.6');
      expect(formatNumber(1234.56, 3)).toBe('1,234.560');
    });

    it('should handle null and undefined values', () => {
      expect(formatNumber(null)).toBe('-');
      expect(formatNumber(undefined)).toBe('-');
    });

    it('should handle negative numbers', () => {
      expect(formatNumber(-1234.56)).toBe('-1,234.56');
      expect(formatNumber(-0)).toBe('0.00');
    });
  });

  describe('formatPercentage', () => {
    it('should format percentages correctly', () => {
      expect(formatPercentage(12.5)).toBe('12.5%');
      expect(formatPercentage(0)).toBe('0.0%');
      expect(formatPercentage(100)).toBe('100.0%');
    });

    it('should format percentages with custom decimal places', () => {
      expect(formatPercentage(12.567, 2)).toBe('12.57%');
      expect(formatPercentage(12.5, 0)).toBe('13%');
    });

    it('should handle null and undefined values', () => {
      expect(formatPercentage(null)).toBe('-');
      expect(formatPercentage(undefined)).toBe('-');
    });

    it('should handle negative percentages', () => {
      expect(formatPercentage(-12.5)).toBe('-12.5%');
    });
  });

  describe('formatLargeNumber', () => {
    it('should format large numbers with K suffix', () => {
      expect(formatLargeNumber(1500)).toBe('1.5K');
      expect(formatLargeNumber(10000)).toBe('10.0K');
      expect(formatLargeNumber(999999)).toBe('1000.0K');
    });

    it('should format large numbers with M suffix', () => {
      expect(formatLargeNumber(1500000)).toBe('1.5M');
      expect(formatLargeNumber(10000000)).toBe('10.0M');
      expect(formatLargeNumber(999999999)).toBe('1000.0M');
    });

    it('should format large numbers with B suffix', () => {
      expect(formatLargeNumber(1500000000)).toBe('1.5B');
      expect(formatLargeNumber(10000000000)).toBe('10.0B');
    });

    it('should handle numbers below 1000', () => {
      expect(formatLargeNumber(500)).toBe('500.00');
      expect(formatLargeNumber(999)).toBe('999.00');
    });

    it('should handle null and undefined values', () => {
      expect(formatLargeNumber(null)).toBe('-');
      expect(formatLargeNumber(undefined)).toBe('-');
    });

    it('should handle negative numbers', () => {
      expect(formatLargeNumber(-1500)).toBe('-1.5K');
      expect(formatLargeNumber(-1500000)).toBe('-1.5M');
    });
  });
}); 