import { renderHook, act } from '@testing-library/react';
import { useUnifiedEventValidation } from './useUnifiedEventValidation';

describe('useUnifiedEventValidation', () => {
  const defaultConfig = {
    mode: 'create' as const,
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
    it('should require event type selection in create mode', () => {
      const { result } = renderHook(() => useUnifiedEventValidation({
        ...defaultConfig,
        mode: 'create',
        eventType: '',
        formData: { event_date: '2024-01-15' }
      }));

      expect(result.current.isFormValid).toBe(false);
      expect(result.current.validationErrors.event_type).toBe('Please select an event type');
    });

    it('should validate required fields for capital call', () => {
      const { result } = renderHook(() => useUnifiedEventValidation({
        ...defaultConfig,
        mode: 'create',
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
      const { result } = renderHook(() => useUnifiedEventValidation({
        ...defaultConfig,
        mode: 'create',
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
      const { result } = renderHook(() => useUnifiedEventValidation({
        ...defaultConfig,
        mode: 'create',
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
  });

  describe('Edit Mode Validation', () => {
    it('should not require event type selection in edit mode', () => {
      const { result } = renderHook(() => useUnifiedEventValidation({
        ...defaultConfig,
        mode: 'edit',
        eventType: 'CAPITAL_CALL',
        formData: { 
          event_date: '2024-01-15',
          amount: '1000'
        }
      }));

      expect(result.current.isFormValid).toBe(true);
      expect(result.current.validationErrors.event_type).toBeUndefined();
    });

    it('should validate required fields for capital call in edit mode', () => {
      const { result } = renderHook(() => useUnifiedEventValidation({
        ...defaultConfig,
        mode: 'edit',
        eventType: 'CAPITAL_CALL',
        formData: { 
          event_date: '2024-01-15',
          amount: '1000'
        }
      }));

      expect(result.current.isFormValid).toBe(true);
      expect(result.current.validationErrors).toEqual({});
    });

    it('should validate unit purchase fields', () => {
      const { result } = renderHook(() => useUnifiedEventValidation({
        ...defaultConfig,
        mode: 'edit',
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
      const { result } = renderHook(() => useUnifiedEventValidation({
        ...defaultConfig,
        mode: 'edit',
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
    it('should require event date for both modes', () => {
      const createResult = renderHook(() => useUnifiedEventValidation({
        ...defaultConfig,
        mode: 'create',
        eventType: 'CAPITAL_CALL',
        formData: {}
      }));

      const editResult = renderHook(() => useUnifiedEventValidation({
        ...defaultConfig,
        mode: 'edit',
        eventType: 'CAPITAL_CALL',
        formData: {}
      }));

      expect(createResult.result.current.isFormValid).toBe(false);
      expect(createResult.result.current.validationErrors.event_date).toBe('Event date is required');
      
      expect(editResult.result.current.isFormValid).toBe(false);
      expect(editResult.result.current.validationErrors.event_date).toBe('Event date is required');
    });

    it('should validate amount for capital events in both modes', () => {
      const createResult = renderHook(() => useUnifiedEventValidation({
        ...defaultConfig,
        mode: 'create',
        eventType: 'CAPITAL_CALL',
        formData: { 
          event_date: '2024-01-15'
        }
      }));

      const editResult = renderHook(() => useUnifiedEventValidation({
        ...defaultConfig,
        mode: 'edit',
        eventType: 'CAPITAL_CALL',
        formData: { 
          event_date: '2024-01-15'
        }
      }));

      expect(createResult.result.current.isFormValid).toBe(false);
      expect(createResult.result.current.validationErrors.amount).toBe('Amount is required');
      
      expect(editResult.result.current.isFormValid).toBe(false);
      expect(editResult.result.current.validationErrors.amount).toBe('Amount is required');
    });
  });

  describe('Validation Updates', () => {
    it('should update validation when config changes', () => {
      const { result, rerender } = renderHook(
        (config) => useUnifiedEventValidation(config),
        { initialProps: defaultConfig }
      );

      // Initially invalid (no event date)
      expect(result.current.isFormValid).toBe(false);

      // Update with valid data
      rerender({
        ...defaultConfig,
        mode: 'create',
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