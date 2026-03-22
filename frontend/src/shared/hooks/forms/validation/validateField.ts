import { eventValidators } from './eventValidators';
import { fundValidators } from './fundValidators';

/**
 * Generic field validation function for use in components
 * @param field - Field name to validate
 * @param value - Field value to validate
 * @param eventType - Current event type for conditional validation
 * @param distributionType - Current distribution type for conditional validation
 * @returns Validation error message or undefined if valid
 */
export const validateField = (
  field: string, 
  value: string, 
  eventType?: string, 
  distributionType?: string
): string | undefined => {
  switch (field) {
    case 'event_date':
      return eventValidators.eventDate(value);
      
    case 'amount':
      if (eventType === 'CAPITAL_CALL' || eventType === 'DISTRIBUTION' || eventType === 'RETURN_OF_CAPITAL') {
        return eventValidators.amount(value);
      }
      return undefined;
      
    case 'distribution_type':
      if (eventType === 'DISTRIBUTION' && !distributionType) {
        return eventValidators.distributionType(value);
      }
      return undefined;
      
    case 'sub_distribution_type':
      if ((distributionType === 'DIVIDEND_FRANKED' || distributionType === 'DIVIDEND_UNFRANKED') && !value) {
        return eventValidators.subDistributionType(value);
      }
      return undefined;
      
    case 'units_purchased':
      if (eventType === 'UNIT_PURCHASE') {
        return eventValidators.unitsPurchased(value);
      }
      return undefined;
      
    case 'units_sold':
      if (eventType === 'UNIT_SALE') {
        return eventValidators.unitsSold(value);
      }
      return undefined;
      
    case 'unit_price':
      if (eventType === 'UNIT_PURCHASE' || eventType === 'UNIT_SALE' || eventType === 'NAV_UPDATE') {
        return eventValidators.unitPrice(value);
      }
      return undefined;
      
    case 'nav_per_share':
      if (eventType === 'NAV_UPDATE') {
        return eventValidators.navPerShare(value);
      }
      return undefined;
      
    case 'brokerage_fee':
      return eventValidators.brokerageFee(value);
      
    case 'gross_amount':
    case 'net_amount':
    case 'withholding_tax_amount':
      if (distributionType === 'INTEREST' && eventType === 'DISTRIBUTION') {
        return eventValidators.grossAmount(value);
      }
      return undefined;
      
    case 'withholding_tax_rate':
      if (distributionType === 'INTEREST' && eventType === 'DISTRIBUTION') {
        return eventValidators.withholdingTaxRate(value);
      }
      return undefined;
      
    // Tax Statement validation
    case 'financial_year':
      if (eventType === 'TAX_STATEMENT') {
        return eventValidators.financialYear(value);
      }
      return undefined;
      
    case 'statement_date':
      if (eventType === 'TAX_STATEMENT') {
        return eventValidators.statementDate(value);
      }
      return undefined;
      
    case 'eofy_debt_interest_deduction_rate':
      if (eventType === 'TAX_STATEMENT') {
        return eventValidators.debtInterestDeductionRate(value);
      }
      return undefined;
      
    case 'interest_received_in_cash':
    case 'interest_receivable_this_fy':
    case 'interest_receivable_prev_fy':
    case 'interest_non_resident_withholding_tax_from_statement':
    case 'dividend_franked_income_amount':
    case 'dividend_unfranked_income_amount':
    case 'capital_gain_income_amount':
      if (eventType === 'TAX_STATEMENT' && value) {
        return eventValidators.interestIncome(value);
      }
      return undefined;
      
    case 'interest_income_tax_rate':
    case 'dividend_franked_income_tax_rate':
    case 'dividend_unfranked_income_tax_rate':
    case 'capital_gain_income_tax_rate':
      if (eventType === 'TAX_STATEMENT' && value) {
        return eventValidators.taxRate(value);
      }
      return undefined;
      
    // Fund validation
    case 'name':
      return fundValidators.name(value);
      
    case 'fund_type':
      return fundValidators.fundType(value);
      
    case 'commitment_amount':
      return fundValidators.commitmentAmount(value);
      
    case 'expected_irr':
      return fundValidators.expectedIrr(value);
      
    case 'expected_duration_months':
      return fundValidators.expectedDuration(value);
      
    case 'description':
      return fundValidators.description(value);
      
    default:
      return undefined;
  }
};

