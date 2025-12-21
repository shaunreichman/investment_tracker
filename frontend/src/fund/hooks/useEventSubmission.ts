/**
 * Fund Event Submission Hook
 * 
 * Orchestrates the submission of fund events and tax statements.
 * Handles payload preparation and routing to the appropriate mutation hook
 * based on event type.
 * 
 * @module fund/hooks/useEventSubmission
 */

import { useState, useCallback } from 'react';
import {
  useCreateCapitalCall,
  useCreateReturnOfCapital,
  useCreateUnitPurchase,
  useCreateUnitSale,
  useCreateNavUpdate,
  useCreateDistribution,
} from './useFundEvents';
import { useCreateFundTaxStatement } from './useFundTaxStatements';
import type { Fund } from '../types';
import type { FundEvent, FundTaxStatement } from '../types';

interface UseEventSubmissionProps {
  fundId: number;
  fundEntity: any;
  fundData?: Fund | null;
  onSuccess: () => void;
  onError: (error: any) => void;
}

interface SubmitEventParams {
  eventType: string;
  formData: any;
  distributionType?: string;
  subDistributionType?: string;
}

/**
 * Combined mutation state for fund events
 * Tracks the last executed mutation's state
 */
interface CombinedFundEventState {
  error: any;
  data: FundEvent | null;
  loading: boolean;
}

/**
 * Hook for submitting fund events and tax statements
 * 
 * Provides a unified interface for creating different types of fund events
 * and tax statements, handling payload preparation and routing to the
 * appropriate mutation hook.
 * 
 * @param props - Configuration including fundId, callbacks, and fund data
 * @returns Object with handleSubmit function and mutation results
 * 
 * @example
 * ```typescript
 * const { handleSubmit, createFundEvent, createTaxStatement } = useEventSubmission({
 *   fundId: 1,
 *   fundEntity: entity,
 *   fundData: fund,
 *   onSuccess: () => console.log('Success!'),
 *   onError: (error) => console.error(error)
 * });
 * 
 * await handleSubmit({
 *   eventType: 'CAPITAL_CALL',
 *   formData: { event_date: '2024-01-15', amount: '50000' }
 * });
 * ```
 */
export const useEventSubmission = ({
  fundId,
  fundEntity,
  fundData,
  onSuccess,
  onError,
}: UseEventSubmissionProps) => {
  // Initialize all mutation hooks
  const createCapitalCall = useCreateCapitalCall(fundId);
  const createReturnOfCapital = useCreateReturnOfCapital(fundId);
  const createUnitPurchase = useCreateUnitPurchase(fundId);
  const createUnitSale = useCreateUnitSale(fundId);
  const createNavUpdate = useCreateNavUpdate(fundId);
  const createDistribution = useCreateDistribution(fundId);
  const createTaxStatement = useCreateFundTaxStatement(fundId);

  // Track the last executed fund event mutation for component state access
  const [lastFundEventMutation, setLastFundEventMutation] = useState<{
    error: any;
    data: FundEvent | null;
    loading: boolean;
  }>({
    error: null,
    data: null,
    loading: false,
  });

  const handleSubmit = async ({
    eventType,
    formData,
    distributionType,
    subDistributionType,
  }: SubmitEventParams) => {
    try {
      // Handle Tax Statement submission
      if (eventType === 'TAX_STATEMENT') {
        // Validate required fields
        if (!formData.financial_year) {
          throw new Error('Financial year is required for tax statements');
        }

        if (!formData.statement_date) {
          throw new Error('Statement date is required for tax statements');
        }

        if (!formData.eofy_debt_interest_deduction_rate) {
          throw new Error(
            'End of Financial Year Debt Interest Deduction Rate is required for tax statements'
          );
        }

        const taxStatementPayload = {
          fund_id: fundId,
          entity_id: fundData?.entity_id || fundEntity?.id || null,
          financial_year: formData.financial_year || '',
          statement_date: formData.statement_date || '',
          tax_payment_date: formData.tax_payment_date || '',
          eofy_debt_interest_deduction_rate: Number(
            formData.eofy_debt_interest_deduction_rate || '0'
          ),
          interest_received_in_cash: Number(formData.interest_received_in_cash || '0'),
          interest_receivable_this_fy: Number(formData.interest_receivable_this_fy || '0'),
          interest_receivable_prev_fy: Number(formData.interest_receivable_prev_fy || '0'),
          interest_non_resident_withholding_tax_from_statement: Number(
            formData.interest_non_resident_withholding_tax_from_statement || '0'
          ),
          interest_income_tax_rate: Number(formData.interest_income_tax_rate || '0'),
          dividend_franked_income_amount: Number(formData.dividend_franked_income_amount || '0'),
          dividend_unfranked_income_amount: Number(
            formData.dividend_unfranked_income_amount || '0'
          ),
          dividend_franked_income_tax_rate: Number(
            formData.dividend_franked_income_tax_rate || '0'
          ),
          dividend_unfranked_income_tax_rate: Number(
            formData.dividend_unfranked_income_tax_rate || '0'
          ),
          capital_gain_income_amount: Number(formData.capital_gain_income_amount || '0'),
          capital_gain_income_tax_rate: Number(formData.capital_gain_income_tax_rate || '0'),
          accountant: formData.accountant || '',
          notes: formData.notes || '',
          non_resident:
            formData.non_resident === 'true' || formData.non_resident === true,
        };

        try {
          const result = await createTaxStatement.mutateAsync(taxStatementPayload);
          onSuccess();
        } catch (error) {
          onError(error);
        }
        return;
      }

      // Prepare base payload for fund events
      const payload: any = {
        event_date: formData.event_date || '',
        description: formData.description || '',
        reference_number: formData.reference_number || '',
      };

      // Handle different event types
      if (eventType === 'CAPITAL_CALL' || eventType === 'RETURN_OF_CAPITAL') {
        const amount = formData.amount;
        if (!amount || amount.trim() === '') {
          throw new Error(
            'Amount is required for Capital Call and Return of Capital events'
          );
        }
        const amountNum = Number(amount);
        if (isNaN(amountNum) || amountNum <= 0) {
          throw new Error('Amount must be a valid positive number');
        }
        payload.amount = amountNum;

        if (eventType === 'CAPITAL_CALL') {
          try {
            setLastFundEventMutation({ error: null, data: null, loading: true });
            const data = await createCapitalCall.mutateAsync(payload);
            setLastFundEventMutation({ error: null, data, loading: false });
            onSuccess();
          } catch (error: any) {
            setLastFundEventMutation({ error, data: null, loading: false });
            onError(error);
          }
        } else {
          try {
            setLastFundEventMutation({ error: null, data: null, loading: true });
            const data = await createReturnOfCapital.mutateAsync(payload);
            setLastFundEventMutation({ error: null, data, loading: false });
            onSuccess();
          } catch (error: any) {
            setLastFundEventMutation({ error, data: null, loading: false });
            onError(error);
          }
        }
      } else if (eventType === 'DISTRIBUTION') {
        // Handle withholding tax distributions differently
        if (distributionType === 'INTEREST' && subDistributionType === 'WITHHOLDING_TAX') {
          // For withholding tax, we need the specialized interest fields
          const interestGrossAmount = formData.interest_gross_amount;
          const interestNetAmount = formData.interest_net_amount;
          const interestWithholdingTaxAmount = formData.interest_withholding_tax_amount;
          const interestWithholdingTaxRate = formData.interest_withholding_tax_rate;

          // Validate that we have at least one amount type and one tax type
          const hasAmountType = interestGrossAmount || interestNetAmount;
          const hasTaxType = interestWithholdingTaxAmount || interestWithholdingTaxRate;

          if (!hasAmountType) {
            throw new Error(
              'Either Gross Amount or Net Amount is required for Interest Distribution with Withholding Tax'
            );
          }

          if (!hasTaxType) {
            throw new Error(
              'Either Withholding Tax Amount or Withholding Tax Rate is required for Interest Distribution with Withholding Tax'
            );
          }

          // Add the specialized fields to payload
          payload.distribution_type = distributionType;
          payload.interest_gross_amount = interestGrossAmount
            ? Number(interestGrossAmount)
            : undefined;
          payload.interest_net_amount = interestNetAmount ? Number(interestNetAmount) : undefined;
          payload.interest_withholding_tax_amount = interestWithholdingTaxAmount
            ? Number(interestWithholdingTaxAmount)
            : undefined;
          payload.interest_withholding_tax_rate = interestWithholdingTaxRate
            ? Number(interestWithholdingTaxRate)
            : undefined;
        } else {
          // For simple distributions, amount is required
          const amount = formData.amount;

          if (!amount || amount.trim() === '') {
            throw new Error('Amount is required for Distribution events');
          }
          const amountNum = Number(amount);
          if (isNaN(amountNum) || amountNum <= 0) {
            throw new Error('Amount must be a valid positive number');
          }
          payload.amount = amountNum;

          // For dividend distributions, use subDistributionType as the distribution_type
          // since the backend expects the specific type (e.g., DIVIDEND_FRANKED, not DIVIDEND)
          if (distributionType === 'DIVIDEND') {
            payload.distribution_type = subDistributionType;
          } else {
            payload.distribution_type = distributionType;
          }
        }

        try {
          setLastFundEventMutation({ error: null, data: null, loading: true });
          const data = await createDistribution.mutateAsync(payload);
          setLastFundEventMutation({ error: null, data, loading: false });
          onSuccess();
        } catch (error: any) {
          setLastFundEventMutation({ error, data: null, loading: false });
          onError(error);
        }
      } else if (eventType === 'UNIT_PURCHASE') {
        payload.units_purchased = Number(formData.units_purchased || '0');
        payload.unit_price = Number(formData.unit_price || '0');
        payload.brokerage_fee = formData.brokerage_fee ? Number(formData.brokerage_fee) : 0.0;

        try {
          setLastFundEventMutation({ error: null, data: null, loading: true });
          const data = await createUnitPurchase.mutateAsync(payload);
          setLastFundEventMutation({ error: null, data, loading: false });
          onSuccess();
        } catch (error: any) {
          setLastFundEventMutation({ error, data: null, loading: false });
          onError(error);
        }
      } else if (eventType === 'UNIT_SALE') {
        payload.units_sold = Number(formData.units_sold || '0');
        payload.unit_price = Number(formData.unit_price || '0');
        payload.brokerage_fee = formData.brokerage_fee ? Number(formData.brokerage_fee) : 0.0;

        try {
          setLastFundEventMutation({ error: null, data: null, loading: true });
          const data = await createUnitSale.mutateAsync(payload);
          setLastFundEventMutation({ error: null, data, loading: false });
          onSuccess();
        } catch (error: any) {
          setLastFundEventMutation({ error, data: null, loading: false });
          onError(error);
        }
      } else if (eventType === 'NAV_UPDATE') {
        payload.nav_per_share = Number(formData.nav_per_share || '0');

        try {
          setLastFundEventMutation({ error: null, data: null, loading: true });
          const data = await createNavUpdate.mutateAsync(payload);
          setLastFundEventMutation({ error: null, data, loading: false });
          onSuccess();
        } catch (error: any) {
          setLastFundEventMutation({ error, data: null, loading: false });
          onError(error);
        }
      } else {
        throw new Error(`Unknown event type: ${eventType}`);
      }
    } catch (error) {
      onError(error);
      throw error;
    }
  };

  // Return mutation state objects for backward compatibility
  // Components can watch these for error/data state
  return {
    handleSubmit,
    // Combined state for fund events (tracks last executed mutation)
    createFundEvent: lastFundEventMutation,
    // Tax statement mutation state
    createTaxStatement,
  };
};

