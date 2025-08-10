/**
 * Tests for validators utility functions
 */

import {
  createValidator,
  validationRules,
  eventValidators,
  fundValidators,
  validateField,
} from './validators';

describe('validators', () => {
  describe('createValidator', () => {
    it('should create a validator from multiple rules', () => {
      const validator = createValidator(
        validationRules.required('Test field'),
        validationRules.positiveNumber('Test field')
      );

      expect(validator('')).toBe('Test field is required');
      expect(validator('-5')).toBe('Test field must be a positive number');
      expect(validator('10')).toBeUndefined();
    });

    it('should return first error found', () => {
      const validator = createValidator(
        validationRules.required('Test field'),
        validationRules.positiveNumber('Test field')
      );

      expect(validator('')).toBe('Test field is required');
    });
  });

  describe('validationRules', () => {
    describe('required', () => {
      it('should validate required fields', () => {
        const required = validationRules.required('Name');
        
        expect(required('')).toBe('Name is required');
        expect(required('   ')).toBe('Name is required');
        expect(required('John')).toBeUndefined();
      });

      it('should use default field name', () => {
        const required = validationRules.required();
        
        expect(required('')).toBe('This field is required');
      });
    });

    describe('positiveNumber', () => {
      it('should validate positive numbers', () => {
        const positiveNumber = validationRules.positiveNumber('Amount');
        
        expect(positiveNumber('')).toBeUndefined(); // Let required handle empty
        expect(positiveNumber('abc')).toBe('Amount must be a valid number');
        expect(positiveNumber('0')).toBe('Amount must be a positive number');
        expect(positiveNumber('-5')).toBe('Amount must be a positive number');
        expect(positiveNumber('10')).toBeUndefined();
        expect(positiveNumber('10.5')).toBeUndefined();
      });
    });

    describe('nonNegativeNumber', () => {
      it('should validate non-negative numbers', () => {
        const nonNegativeNumber = validationRules.nonNegativeNumber('Amount');
        
        expect(nonNegativeNumber('')).toBeUndefined(); // Let required handle empty
        expect(nonNegativeNumber('abc')).toBe('Amount must be a valid number');
        expect(nonNegativeNumber('-5')).toBe('Amount must be a non-negative number');
        expect(nonNegativeNumber('0')).toBeUndefined();
        expect(nonNegativeNumber('10')).toBeUndefined();
        expect(nonNegativeNumber('10.5')).toBeUndefined();
      });
    });

    describe('percentageRate', () => {
      it('should validate percentage rates', () => {
        const percentageRate = validationRules.percentageRate('Rate');
        
        expect(percentageRate('')).toBeUndefined(); // Let required handle empty
        expect(percentageRate('abc')).toBe('Rate must be a valid number');
        expect(percentageRate('-5')).toBe('Rate must be between 0 and 100');
        expect(percentageRate('105')).toBe('Rate must be between 0 and 100');
        expect(percentageRate('0')).toBeUndefined();
        expect(percentageRate('50')).toBeUndefined();
        expect(percentageRate('100')).toBeUndefined();
      });
    });

    describe('validDate', () => {
      it('should validate dates', () => {
        const validDate = validationRules.validDate('Date');
        
        expect(validDate('')).toBeUndefined(); // Let required handle empty
        expect(validDate('invalid')).toBe('Date must be a valid date');
        expect(validDate('2023-13-01')).toBe('Date must be a valid date');
        expect(validDate('2023-01-01')).toBeUndefined();
        expect(validDate('2023-12-31')).toBeUndefined();
      });
    });

    describe('email', () => {
      it('should validate email addresses', () => {
        const email = validationRules.email('Email');
        
        expect(email('')).toBeUndefined(); // Let required handle empty
        expect(email('invalid')).toBe('Email must be a valid email address');
        expect(email('test@')).toBe('Email must be a valid email address');
        expect(email('@example.com')).toBe('Email must be a valid email address');
        expect(email('test@example.com')).toBeUndefined();
        expect(email('test.name@example.co.uk')).toBeUndefined();
      });
    });

    describe('url', () => {
      it('should validate URLs', () => {
        const url = validationRules.url('URL');
        
        expect(url('')).toBeUndefined(); // Let required handle empty
        expect(url('invalid')).toBe('URL must be a valid URL');
        expect(url('http://')).toBe('URL must be a valid URL');
        expect(url('https://example.com')).toBeUndefined();
        expect(url('http://example.com/path')).toBeUndefined();
      });
    });
  });

  describe('eventValidators', () => {
    describe('eventDate', () => {
      it('should validate event dates', () => {
        expect(eventValidators.eventDate('')).toBe('Event date is required');
        expect(eventValidators.eventDate('invalid')).toBe('Event date must be a valid date');
        expect(eventValidators.eventDate('2023-01-01')).toBeUndefined();
      });
    });

    describe('amount', () => {
      it('should validate amounts', () => {
        expect(eventValidators.amount('')).toBe('Amount is required');
        expect(eventValidators.amount('abc')).toBe('Amount must be a valid number');
        expect(eventValidators.amount('0')).toBe('Amount must be a positive number');
        expect(eventValidators.amount('-5')).toBe('Amount must be a positive number');
        expect(eventValidators.amount('100')).toBeUndefined();
      });
    });

    describe('distributionType', () => {
      it('should validate distribution types', () => {
        expect(eventValidators.distributionType('')).toBe('Distribution type is required');
        expect(eventValidators.distributionType('INTEREST')).toBeUndefined();
      });
    });

    describe('unitsPurchased', () => {
      it('should validate units purchased', () => {
        expect(eventValidators.unitsPurchased('')).toBe('Units purchased is required');
        expect(eventValidators.unitsPurchased('abc')).toBe('Units purchased must be a valid number');
        expect(eventValidators.unitsPurchased('0')).toBe('Units purchased must be a positive number');
        expect(eventValidators.unitsPurchased('100')).toBeUndefined();
      });
    });

    describe('unitPrice', () => {
      it('should validate unit prices', () => {
        expect(eventValidators.unitPrice('')).toBe('Unit price is required');
        expect(eventValidators.unitPrice('abc')).toBe('Unit price must be a valid number');
        expect(eventValidators.unitPrice('0')).toBe('Unit price must be a positive number');
        expect(eventValidators.unitPrice('10.50')).toBeUndefined();
      });
    });

    describe('brokerageFee', () => {
      it('should validate brokerage fees', () => {
        expect(eventValidators.brokerageFee('')).toBeUndefined(); // Optional field
        expect(eventValidators.brokerageFee('abc')).toBe('Brokerage fee must be a valid number');
        expect(eventValidators.brokerageFee('-5')).toBe('Brokerage fee must be a non-negative number');
        expect(eventValidators.brokerageFee('0')).toBeUndefined();
        expect(eventValidators.brokerageFee('25')).toBeUndefined();
      });
    });

    describe('withholdingTaxRate', () => {
      it('should validate withholding tax rates', () => {
        expect(eventValidators.withholdingTaxRate('')).toBeUndefined(); // Optional field
        expect(eventValidators.withholdingTaxRate('abc')).toBe('Withholding tax rate must be a valid number');
        expect(eventValidators.withholdingTaxRate('-5')).toBe('Withholding tax rate must be between 0 and 100');
        expect(eventValidators.withholdingTaxRate('105')).toBe('Withholding tax rate must be between 0 and 100');
        expect(eventValidators.withholdingTaxRate('10')).toBeUndefined();
      });
    });
  });

  describe('fundValidators', () => {
    describe('name', () => {
      it('should validate fund names', () => {
        expect(fundValidators.name('')).toBe('Fund name is required');
        expect(fundValidators.name('My Fund')).toBeUndefined();
      });
    });

    describe('commitmentAmount', () => {
      it('should validate commitment amounts', () => {
        expect(fundValidators.commitmentAmount('')).toBeUndefined(); // Optional field
        expect(fundValidators.commitmentAmount('abc')).toBe('Commitment amount must be a valid number');
        expect(fundValidators.commitmentAmount('0')).toBe('Commitment amount must be a positive number');
        expect(fundValidators.commitmentAmount('1000000')).toBeUndefined();
      });
    });

    describe('expectedIrr', () => {
      it('should validate expected IRR', () => {
        expect(fundValidators.expectedIrr('')).toBeUndefined(); // Optional field
        expect(fundValidators.expectedIrr('abc')).toBe('Expected IRR must be a valid number');
        expect(fundValidators.expectedIrr('-5')).toBe('Expected IRR must be between 0 and 100');
        expect(fundValidators.expectedIrr('105')).toBe('Expected IRR must be between 0 and 100');
        expect(fundValidators.expectedIrr('15.5')).toBeUndefined();
      });
    });
  });

  describe('validateField', () => {
    it('should validate event_date field', () => {
      expect(validateField('event_date', '')).toBe('Event date is required');
      expect(validateField('event_date', 'invalid')).toBe('Event date must be a valid date');
      expect(validateField('event_date', '2023-01-01')).toBeUndefined();
    });

    it('should validate amount field for capital events', () => {
      expect(validateField('amount', '', 'CAPITAL_CALL')).toBe('Amount is required');
      expect(validateField('amount', 'abc', 'CAPITAL_CALL')).toBe('Amount must be a valid number');
      expect(validateField('amount', '100', 'CAPITAL_CALL')).toBeUndefined();
      expect(validateField('amount', '100', 'NAV_UPDATE')).toBeUndefined(); // Not required for NAV updates
    });

    it('should validate distribution_type field', () => {
      expect(validateField('distribution_type', '', 'DISTRIBUTION')).toBe('Distribution type is required');
      expect(validateField('distribution_type', 'INTEREST', 'DISTRIBUTION')).toBeUndefined();
      expect(validateField('distribution_type', 'INTEREST', 'CAPITAL_CALL')).toBeUndefined(); // Not required for capital calls
    });

    it('should validate units_purchased field', () => {
      expect(validateField('units_purchased', '', 'UNIT_PURCHASE')).toBe('Units purchased is required');
      expect(validateField('units_purchased', '100', 'UNIT_PURCHASE')).toBeUndefined();
      expect(validateField('units_purchased', '100', 'CAPITAL_CALL')).toBeUndefined(); // Not required for capital calls
    });

    it('should validate unit_price field', () => {
      expect(validateField('unit_price', '', 'UNIT_PURCHASE')).toBe('Unit price is required');
      expect(validateField('unit_price', '10.50', 'UNIT_PURCHASE')).toBeUndefined();
      expect(validateField('unit_price', '10.50', 'NAV_UPDATE')).toBeUndefined();
      expect(validateField('unit_price', '10.50', 'CAPITAL_CALL')).toBeUndefined(); // Not required for capital calls
    });

    it('should validate nav_per_share field', () => {
      expect(validateField('nav_per_share', '', 'NAV_UPDATE')).toBe('NAV per share is required');
      expect(validateField('nav_per_share', '10.50', 'NAV_UPDATE')).toBeUndefined();
      expect(validateField('nav_per_share', '10.50', 'CAPITAL_CALL')).toBeUndefined(); // Not required for capital calls
    });

    it('should validate brokerage_fee field', () => {
      expect(validateField('brokerage_fee', 'abc')).toBe('Brokerage fee must be a valid number');
      expect(validateField('brokerage_fee', '25')).toBeUndefined();
      expect(validateField('brokerage_fee', '')).toBeUndefined(); // Optional field
    });

    it('should validate tax statement fields', () => {
      expect(validateField('financial_year', '', 'TAX_STATEMENT')).toBe('Financial year is required');
      expect(validateField('financial_year', '2023-24', 'TAX_STATEMENT')).toBeUndefined();
      expect(validateField('financial_year', '2023-24', 'CAPITAL_CALL')).toBeUndefined(); // Not required for capital calls

      expect(validateField('statement_date', '', 'TAX_STATEMENT')).toBe('Statement date is required');
      expect(validateField('statement_date', '2023-01-01', 'TAX_STATEMENT')).toBeUndefined();

      expect(validateField('eofy_debt_interest_deduction_rate', '', 'TAX_STATEMENT')).toBe('Debt interest deduction rate is required');
      expect(validateField('eofy_debt_interest_deduction_rate', '32.5', 'TAX_STATEMENT')).toBeUndefined();
    });

    it('should validate interest income fields', () => {
      expect(validateField('interest_received_in_cash', 'abc', 'TAX_STATEMENT')).toBe('Interest income amount must be a valid number');
      expect(validateField('interest_received_in_cash', '1000', 'TAX_STATEMENT')).toBeUndefined();
      expect(validateField('interest_received_in_cash', '', 'TAX_STATEMENT')).toBeUndefined(); // Optional field
    });

    it('should validate tax rate fields', () => {
      expect(validateField('interest_income_tax_rate', 'abc', 'TAX_STATEMENT')).toBe('Tax rate must be a valid number');
      expect(validateField('interest_income_tax_rate', '10', 'TAX_STATEMENT')).toBeUndefined();
      expect(validateField('interest_income_tax_rate', '', 'TAX_STATEMENT')).toBeUndefined(); // Optional field
    });

    it('should return undefined for unknown fields', () => {
      expect(validateField('unknown_field', 'value')).toBeUndefined();
    });
  });
}); 