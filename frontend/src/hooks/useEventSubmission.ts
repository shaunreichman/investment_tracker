import { useCreateFundEvent, useCreateTaxStatement } from './useFunds';

interface UseEventSubmissionProps {
  fundId: number;
  fundEntity: any;
  onSuccess: () => void;
  onError: (error: any) => void;
}

interface SubmitEventParams {
  eventType: string;
  formData: any;
  distributionType?: string;
  subDistributionType?: string;
}

export const useEventSubmission = ({ fundId, fundEntity, onSuccess, onError }: UseEventSubmissionProps) => {
  const createFundEvent = useCreateFundEvent(fundId);
  const createTaxStatement = useCreateTaxStatement(fundId);

  const handleSubmit = async ({ eventType, formData, distributionType, subDistributionType }: SubmitEventParams) => {
    // Prepare payload based on event type
    const payload: any = {
      event_type: eventType,
      event_date: formData.event_date || '',
      description: formData.description || '',
      reference_number: formData.reference_number || '',
    };

    // Handle different event types
    if (eventType === 'CAPITAL_CALL' || eventType === 'RETURN_OF_CAPITAL') {
      const amount = formData.amount;      
      if (!amount || amount.trim() === '') {
        throw new Error('Amount is required for Capital Call and Return of Capital events');
      }
      const amountNum = Number(amount);
      if (isNaN(amountNum) || amountNum <= 0) {
        throw new Error('Amount must be a valid positive number');
      }
      payload.amount = amountNum;
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
          throw new Error('Either Gross Amount or Net Amount is required for Interest Distribution with Withholding Tax');
        }
        
        if (!hasTaxType) {
          throw new Error('Either Withholding Tax Amount or Withholding Tax Rate is required for Interest Distribution with Withholding Tax');
        }
        
        // Add the specialized fields to payload
        payload.distribution_type = distributionType;
        payload.interest_gross_amount = interestGrossAmount ? Number(interestGrossAmount) : undefined;
        payload.interest_net_amount = interestNetAmount ? Number(interestNetAmount) : undefined;
        payload.interest_withholding_tax_amount = interestWithholdingTaxAmount ? Number(interestWithholdingTaxAmount) : undefined;
        payload.interest_withholding_tax_rate = interestWithholdingTaxRate ? Number(interestWithholdingTaxRate) : undefined;
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
    } else if (eventType === 'UNIT_PURCHASE') {
      payload.units_purchased = Number(formData.units_purchased || '0');
      payload.unit_price = Number(formData.unit_price || '0');
      payload.brokerage_fee = formData.brokerage_fee ? Number(formData.brokerage_fee) : 0.0;
    } else if (eventType === 'UNIT_SALE') {
      payload.units_sold = Number(formData.units_sold || '0');
      payload.unit_price = Number(formData.unit_price || '0');
      payload.brokerage_fee = formData.brokerage_fee ? Number(formData.brokerage_fee) : 0.0;
    } else if (eventType === 'NAV_UPDATE') {
      payload.nav_per_share = Number(formData.nav_per_share || '0');
    }
    
    // Handle Tax Statement submission
    if (eventType === 'TAX_STATEMENT') {
      const taxStatementPayload = {
        entity_id: fundEntity?.id,
        financial_year: formData.financial_year || '',
        statement_date: formData.statement_date || '',
        eofy_debt_interest_deduction_rate: Number(formData.eofy_debt_interest_deduction_rate || '0'),
        interest_received_in_cash: Number(formData.interest_received_in_cash || '0'),
        interest_receivable_this_fy: Number(formData.interest_receivable_this_fy || '0'),
        interest_receivable_prev_fy: Number(formData.interest_receivable_prev_fy || '0'),
        interest_non_resident_withholding_tax_from_statement: Number(formData.interest_non_resident_withholding_tax_from_statement || '0'),
        interest_income_tax_rate: Number(formData.interest_income_tax_rate || '0'),
        dividend_franked_income_amount: Number(formData.dividend_franked_income_amount || '0'),
        dividend_unfranked_income_amount: Number(formData.dividend_unfranked_income_amount || '0'),
        dividend_franked_income_tax_rate: Number(formData.dividend_franked_income_tax_rate || '0'),
        dividend_unfranked_income_tax_rate: Number(formData.dividend_unfranked_income_tax_rate || '0'),
        capital_gain_income_amount: Number(formData.capital_gain_income_amount || '0'),
        capital_gain_income_tax_rate: Number(formData.capital_gain_income_tax_rate || '0'),
        accountant: formData.accountant || '',
        notes: formData.notes || '',
        non_resident: formData.non_resident || false
      };
      
      await createTaxStatement.mutate(taxStatementPayload);
      return;
    }
    
    await createFundEvent.mutate(payload);
  };

  return {
    handleSubmit,
    createFundEvent,
    createTaxStatement,
  };
}; 