import { createValidator } from './createValidator';
import { validationRules } from './validationRules';

/**
 * Event-specific validation functions
 */
export const eventValidators = {
  /**
   * Validate event date field
   */
  eventDate: createValidator(
    validationRules.required('Event date'),
    validationRules.validDate('Event date')
  ),

  /**
   * Validate amount field for capital events
   */
  amount: createValidator(
    validationRules.required('Amount'),
    validationRules.positiveNumber('Amount')
  ),

  /**
   * Validate distribution type field
   */
  distributionType: createValidator(
    validationRules.required('Distribution type')
  ),

  /**
   * Validate sub-distribution type field
   */
  subDistributionType: createValidator(
    validationRules.required('Sub-distribution type')
  ),

  /**
   * Validate units purchased field
   */
  unitsPurchased: createValidator(
    validationRules.required('Units purchased'),
    validationRules.positiveNumber('Units purchased')
  ),

  /**
   * Validate units sold field
   */
  unitsSold: createValidator(
    validationRules.required('Units sold'),
    validationRules.positiveNumber('Units sold')
  ),

  /**
   * Validate unit price field
   */
  unitPrice: createValidator(
    validationRules.required('Unit price'),
    validationRules.positiveNumber('Unit price')
  ),

  /**
   * Validate NAV per share field
   */
  navPerShare: createValidator(
    validationRules.required('NAV per share'),
    validationRules.positiveNumber('NAV per share')
  ),

  /**
   * Validate brokerage fee field
   */
  brokerageFee: createValidator(
    validationRules.nonNegativeNumber('Brokerage fee')
  ),

  /**
   * Validate gross amount field
   */
  grossAmount: createValidator(
    validationRules.positiveNumber('Gross amount')
  ),

  /**
   * Validate net amount field
   */
  netAmount: createValidator(
    validationRules.positiveNumber('Net amount')
  ),

  /**
   * Validate withholding tax amount field
   */
  withholdingTaxAmount: createValidator(
    validationRules.nonNegativeNumber('Withholding tax amount')
  ),

  /**
   * Validate withholding tax rate field
   */
  withholdingTaxRate: createValidator(
    validationRules.percentageRate('Withholding tax rate')
  ),

  /**
   * Validate financial year field
   */
  financialYear: createValidator(
    validationRules.required('Financial year')
  ),

  /**
   * Validate statement date field
   */
  statementDate: createValidator(
    validationRules.required('Statement date'),
    validationRules.validDate('Statement date')
  ),

  /**
   * Validate debt interest deduction rate field
   */
  debtInterestDeductionRate: createValidator(
    validationRules.required('Debt interest deduction rate'),
    validationRules.percentageRate('Debt interest deduction rate')
  ),

  /**
   * Validate interest income fields
   */
  interestIncome: createValidator(
    validationRules.nonNegativeNumber('Interest income amount')
  ),

  /**
   * Validate tax rate fields
   */
  taxRate: createValidator(
    validationRules.percentageRate('Tax rate')
  ),
};

