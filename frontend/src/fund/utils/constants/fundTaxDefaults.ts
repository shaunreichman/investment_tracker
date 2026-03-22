/**
 * Fund tax default rates.
 *
 * These MANUAL defaults provide seed values for new funds. Users can override
 * them in the UI; they serve as guard rails for quick setup.
 */
export interface FundTaxRates {
  INTEREST_INCOME: number;
  DIVIDEND_FRANKED: number;
  DIVIDEND_UNFRANKED: number;
  CAPITAL_GAIN: number;
  WITHHOLDING_TAX: number;
  DEBT_INTEREST_DEDUCTION: number;
}

export const DEFAULT_TAX_RATES: FundTaxRates = {
  INTEREST_INCOME: 10.0,
  DIVIDEND_FRANKED: 0.0,
  DIVIDEND_UNFRANKED: 10.0,
  CAPITAL_GAIN: 10.0,
  WITHHOLDING_TAX: 10.0,
  DEBT_INTEREST_DEDUCTION: 32.5,
};

