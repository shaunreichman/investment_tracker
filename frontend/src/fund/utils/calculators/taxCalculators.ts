/**
 * Tax calculation utilities for fund domain.
 * 
 * Provides helpers for calculating tax-related amounts and dates.
 */

/**
 * Calculate net amount from gross and withholding tax
 * @param grossAmount - Gross amount
 * @param withholdingAmount - Withholding tax amount
 * @returns Net amount
 */
export const calculateNetAmount = (grossAmount: number, withholdingAmount: number): number => {
  return grossAmount - withholdingAmount;
};

/**
 * Calculate withholding tax amount
 * @param grossAmount - Gross amount
 * @param rate - Tax rate percentage
 * @returns Withholding tax amount
 */
export const calculateWithholdingTax = (grossAmount: number, rate: number): number => {
  return (grossAmount * rate) / 100;
};

/**
 * Calculate tax payment date based on financial year (defaults to last day of financial year)
 * @param financialYear - Financial year string (e.g., '2024-25' or '2024')
 * @param taxJurisdiction - Tax jurisdiction code (defaults to 'AU')
 * @returns Date string in YYYY-MM-DD format (ISO format for API compatibility)
 */
export const calculateTaxPaymentDate = (financialYear: string, taxJurisdiction: string = 'AU'): string => {
  if (!financialYear) return '';
  
  let startYear: number;
  let endYear: number;
  
  if (financialYear.includes('-')) {
    const parts = financialYear.split('-');
    if (parts.length !== 2) return '';
    
    const start = parts[0];
    const end = parts[1];
    
    if (!start || !end) return '';
    
    startYear = parseInt(start);
    if (isNaN(startYear)) return '';
    
    endYear = parseInt(end.length === 2 ? `20${end}` : end);
    if (isNaN(endYear)) return '';
  } else {
    startYear = parseInt(financialYear);
    if (isNaN(startYear)) return '';
    endYear = startYear + 1;
  }
  
  // For AU tax jurisdiction: FY runs July 1 to June 30
  // For other jurisdictions: FY runs January 1 to December 31
  if (taxJurisdiction === 'AU') {
    // Last day of financial year is June 30 of the end year
    return `${endYear}-06-30`;
  } else {
    // Last day of financial year is December 31 of the start year
    return `${startYear}-12-31`;
  }
};

