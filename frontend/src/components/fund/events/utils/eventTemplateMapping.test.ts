import { mapEventToTemplates, mapEventToFormData, getTemplateDisplayLabel } from './eventTemplateMapping';
import { ExtendedFundEvent, EventType, DistributionType } from '../../../../types/api';

describe('eventTemplateMapping', () => {
  describe('mapEventToTemplates', () => {
    it('should map capital call event correctly', () => {
      const event = {
        id: 1,
        fund_id: 1,
        event_type: EventType.CAPITAL_CALL,
        event_date: '2024-01-15',
        amount: 1000,
        description: 'Test capital call',
        reference_number: 'CC001',
      } as ExtendedFundEvent;

      const result = mapEventToTemplates(event);

      expect(result).toEqual({
        eventType: 'CAPITAL_CALL',
        distributionType: '',
        subDistributionType: '',
        withholdingAmountType: '',
        withholdingTaxType: '',
      });
    });

    it('should map regular interest distribution correctly', () => {
      const event = {
        id: 1,
        fund_id: 1,
        event_type: EventType.DISTRIBUTION,
        event_date: '2024-01-15',
        amount: 500,
        distribution_type: DistributionType.INTEREST,
        description: 'Regular interest',
        has_withholding_tax: false,
      } as ExtendedFundEvent;

      const result = mapEventToTemplates(event);

      expect(result).toEqual({
        eventType: 'DISTRIBUTION',
        distributionType: 'INTEREST',
        subDistributionType: 'REGULAR',
        withholdingAmountType: '',
        withholdingTaxType: '',
      });
    });

    it('should map withholding tax interest distribution correctly', () => {
      const event = {
        id: 1,
        fund_id: 1,
        event_type: EventType.DISTRIBUTION,
        event_date: '2024-01-15',
        amount: 500,
        distribution_type: DistributionType.INTEREST,
        description: 'Interest with withholding tax',
        has_withholding_tax: true,
        net_interest: 500,
        withholding_amount: 100,
        withholding_rate: 10,
      } as ExtendedFundEvent;

      const result = mapEventToTemplates(event);

      expect(result).toEqual({
        eventType: 'DISTRIBUTION',
        distributionType: 'INTEREST',
        subDistributionType: 'WITHHOLDING_TAX',
        withholdingAmountType: 'gross',
        withholdingTaxType: 'amount',
      });
    });

    it('should map franked dividend distribution correctly', () => {
      const event = {
        id: 1,
        fund_id: 1,
        event_type: 'DISTRIBUTION' as const,
        event_date: '2024-01-15',
        amount: 500,
        distribution_type: 'DIVIDEND' as const,
        description: 'Franked dividend',
        dividend_franked_income_amount: 500,
        dividend_unfranked_income_amount: 0,
      } as ExtendedFundEvent;

      const result = mapEventToTemplates(event);

      expect(result).toEqual({
        eventType: 'DISTRIBUTION',
        distributionType: 'DIVIDEND',
        subDistributionType: 'DIVIDEND_FRANKED',
        withholdingAmountType: '',
        withholdingTaxType: '',
      });
    });

    it('should map unit purchase correctly', () => {
      const event = {
        id: 1,
        fund_id: 1,
        event_type: EventType.UNIT_PURCHASE,
        event_date: '2024-01-15',
        units_purchased: 100,
        unit_price: 10.5,
        brokerage_fee: 50,
        description: 'Unit purchase',
      } as ExtendedFundEvent;

      const result = mapEventToTemplates(event);

      expect(result).toEqual({
        eventType: 'UNIT_PURCHASE',
        distributionType: '',
        subDistributionType: '',
        withholdingAmountType: '',
        withholdingTaxType: '',
      });
    });

    it('should map NAV update correctly', () => {
      const event = {
        id: 1,
        fund_id: 1,
        event_type: EventType.NAV_UPDATE,
        event_date: '2024-01-15',
        nav_per_share: 12.5,
        description: 'NAV update',
      } as ExtendedFundEvent;

      const result = mapEventToTemplates(event);

      expect(result).toEqual({
        eventType: 'NAV_UPDATE',
        distributionType: '',
        subDistributionType: '',
        withholdingAmountType: '',
        withholdingTaxType: '',
      });
    });
  });

  describe('mapEventToFormData', () => {
    it('should map basic event fields correctly', () => {
      const event = {
        id: 1,
        fund_id: 1,
        event_type: EventType.CAPITAL_CALL,
        event_date: '2024-01-15',
        amount: 1000,
        description: 'Test capital call',
        reference_number: 'CC001',
      } as ExtendedFundEvent;

      const result = mapEventToFormData(event);

      expect(result).toEqual({
        event_date: '2024-01-15',
        amount: '1000',
        description: 'Test capital call',
        reference_number: 'CC001',
      });
    });

    it('should map NAV-based event fields correctly', () => {
      const event = {
        id: 1,
        fund_id: 1,
        event_type: EventType.UNIT_PURCHASE,
        event_date: '2024-01-15',
        units_purchased: 100,
        unit_price: 10.5,
        brokerage_fee: 50,
        description: 'Unit purchase',
      } as ExtendedFundEvent;

      const result = mapEventToFormData(event);

      expect(result).toEqual({
        event_date: '2024-01-15',
        units_purchased: '100',
        unit_price: '10.5',
        brokerage_fee: '50',
        description: 'Unit purchase',
      });
    });

    it('should map distribution fields correctly', () => {
      const event = {
        id: 1,
        fund_id: 1,
        event_type: EventType.DISTRIBUTION,
        event_date: '2024-01-15',
        amount: 500,
        distribution_type: DistributionType.INTEREST,
        net_interest: 500,
        withholding_amount: 100,
        withholding_rate: 10,
        description: 'Interest distribution',
      } as ExtendedFundEvent;

      const result = mapEventToFormData(event);

      expect(result).toEqual({
        event_date: '2024-01-15',
        amount: '500',
        net_interest: '500',
        withholding_amount: '100',
        withholding_rate: '10',
        description: 'Interest distribution',
      });
    });

    it('should handle null values correctly', () => {
      const event = {
        id: 1,
        fund_id: 1,
        event_type: EventType.CAPITAL_CALL,
        event_date: '2024-01-15',
        amount: null,
        description: undefined,
        reference_number: undefined,
        created_at: '2024-01-15T00:00:00Z',
        updated_at: '2024-01-15T00:00:00Z',
      } as ExtendedFundEvent;

      const result = mapEventToFormData(event);

      expect(result).toEqual({
        event_date: '2024-01-15',
      });
    });
  });

  describe('getTemplateDisplayLabel', () => {
    it('should return correct label for capital call', () => {
      const event = {
        id: 1,
        fund_id: 1,
        event_type: EventType.CAPITAL_CALL,
        event_date: '2024-01-15',
        amount: 1000,
        created_at: '2024-01-15T00:00:00Z',
        updated_at: '2024-01-15T00:00:00Z',
      } as ExtendedFundEvent;

      const result = getTemplateDisplayLabel(event);

      expect(result).toBe('Capital Call');
    });

    it('should return correct label for regular interest distribution', () => {
      const event = {
        id: 1,
        fund_id: 1,
        event_type: EventType.DISTRIBUTION,
        event_date: '2024-01-15',
        distribution_type: DistributionType.INTEREST,
        has_withholding_tax: false,
        created_at: '2024-01-15T00:00:00Z',
        updated_at: '2024-01-15T00:00:00Z',
      } as ExtendedFundEvent;

      const result = getTemplateDisplayLabel(event);

      expect(result).toBe('Distribution - Interest (Regular)');
    });

    it('should return correct label for withholding tax interest distribution', () => {
      const event = {
        id: 1,
        fund_id: 1,
        event_type: EventType.DISTRIBUTION,
        event_date: '2024-01-15',
        distribution_type: DistributionType.INTEREST,
        has_withholding_tax: true,
        created_at: '2024-01-15T00:00:00Z',
        updated_at: '2024-01-15T00:00:00Z',
      } as ExtendedFundEvent;

      const result = getTemplateDisplayLabel(event);

      expect(result).toBe('Distribution - Interest (Withholding Tax)');
    });

    it('should return correct label for franked dividend', () => {
      const event = {
        id: 1,
        fund_id: 1,
        event_type: EventType.DISTRIBUTION,
        event_date: '2024-01-15',
        distribution_type: DistributionType.DIVIDEND,
        dividend_franked_income_amount: 500,
        created_at: '2024-01-15T00:00:00Z',
        updated_at: '2024-01-15T00:00:00Z',
      } as ExtendedFundEvent;

      const result = getTemplateDisplayLabel(event);

      expect(result).toBe('Distribution - Dividend (Franked)');
    });

    it('should return correct label for unit purchase', () => {
      const event = {
        id: 1,
        fund_id: 1,
        event_type: EventType.UNIT_PURCHASE,
        event_date: '2024-01-15',
        created_at: '2024-01-15T00:00:00Z',
        updated_at: '2024-01-15T00:00:00Z',
      } as ExtendedFundEvent;

      const result = getTemplateDisplayLabel(event);

      expect(result).toBe('Unit Purchase');
    });

    it('should return unknown for invalid event type', () => {
      const event = {
        id: 1,
        fund_id: 1,
        event_type: 'INVALID_TYPE' as any,
        event_date: '2024-01-15',
        created_at: '2024-01-15T00:00:00Z',
        updated_at: '2024-01-15T00:00:00Z',
      } as ExtendedFundEvent;

      const result = getTemplateDisplayLabel(event);

      expect(result).toBe('INVALID_TYPE');
    });
  });
}); 