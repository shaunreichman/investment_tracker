import { renderHook } from '@testing-library/react';
import { useCreateEventValidation } from './useCreateEventValidation';

describe('useCreateEventValidation', () => {
  const defaultConfig = {
    eventType: '' as any,
    distributionType: '',
    subDistributionType: '',
    withholdingAmountType: '' as 'gross' | 'net' | '',
    withholdingTaxType: '' as 'amount' | 'rate' | '',
    formData: {}
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Create Mode Validation', () => {
    it('should require event type selection', () => {
      const { result } = renderHook(() => useCreateEventValidation({
        ...defaultConfig,
        eventType: '',
        formData: { event_date: '2024-01-15' }
      }));

      expect(result.current.isFormValid).toBe(false);
      expect(result.current.validationErrors.event_type).toBe('Please select an event type');
    });

    it('should validate required fields for capital call', () => {
      const { result } = renderHook(() => useCreateEventValidation({
        ...defaultConfig,
        eventType: 'CAPITAL_CALL',
        formData: { 
          event_date: '2024-01-15',
          amount: '1000'
        }
      }));

      expect(result.current.isFormValid).toBe(true);
      expect(result.current.validationErrors).toEqual({});
    });

    it('should validate distribution type for distributions', () => {
      const { result } = renderHook(() => useCreateEventValidation({
        ...defaultConfig,
        eventType: 'DISTRIBUTION',
        formData: { 
          event_date: '2024-01-15',
          amount: '1000'
        }
      }));

      expect(result.current.isFormValid).toBe(false);
      expect(result.current.validationErrors.distribution_type).toBe('Distribution type is required');
    });

    it('should validate withholding tax configuration', () => {
      const { result } = renderHook(() => useCreateEventValidation({
        ...defaultConfig,
        eventType: 'DISTRIBUTION',
        distributionType: 'INTEREST',
        subDistributionType: 'WITHHOLDING_TAX',
        formData: { 
          event_date: '2024-01-15',
          gross_amount: '1000',
          withholding_tax_amount: '100'
        }
      }));

      expect(result.current.isFormValid).toBe(false);
      expect(result.current.validationErrors.gross_amount).toBe('Select amount type (Gross or Net)');
      expect(result.current.validationErrors.withholding_tax_rate).toBe('Select tax type (Amount or Rate)');
    });

    it('should validate unit purchase fields', () => {
      const { result } = renderHook(() => useCreateEventValidation({
        ...defaultConfig,
        eventType: 'UNIT_PURCHASE',
        formData: { 
          event_date: '2024-01-15',
          units_purchased: '100',
          unit_price: '10'
        }
      }));

      expect(result.current.isFormValid).toBe(true);
      expect(result.current.validationErrors).toEqual({});
    });

    it('should validate NAV update fields', () => {
      const { result } = renderHook(() => useCreateEventValidation({
        ...defaultConfig,
        eventType: 'NAV_UPDATE',
        formData: { 
          event_date: '2024-01-15',
          nav_per_share: '10.50'
        }
      }));

      expect(result.current.isFormValid).toBe(true);
      expect(result.current.validationErrors).toEqual({});
    });
  });

  describe('Shared Validation Logic', () => {
    it('should require event date', () => {
      const { result } = renderHook(() => useCreateEventValidation({
        ...defaultConfig,
        eventType: 'CAPITAL_CALL',
        formData: {}
      }));

      expect(result.current.isFormValid).toBe(false);
      expect(result.current.validationErrors.event_date).toBe('Event date is required');
    });

    it('should validate amount for capital events', () => {
      const { result } = renderHook(() => useCreateEventValidation({
        ...defaultConfig,
        eventType: 'CAPITAL_CALL',
        formData: { 
          event_date: '2024-01-15'
        }
      }));

      expect(result.current.isFormValid).toBe(false);
      expect(result.current.validationErrors.amount).toBe('Amount is required');
    });
  });

  describe('Validation Updates', () => {
    it('should update validation when config changes', () => {
      const { result, rerender } = renderHook(
        (config) => useCreateEventValidation(config),
        { initialProps: defaultConfig }
      );

      // Initially invalid (no event date)
      expect(result.current.isFormValid).toBe(false);

      // Update with valid data
      rerender({
        ...defaultConfig,
        eventType: 'CAPITAL_CALL',
        formData: { 
          event_date: '2024-01-15',
          amount: '1000'
        }
      });

      expect(result.current.isFormValid).toBe(true);
      expect(result.current.validationErrors).toEqual({});
    });
  });
}); 