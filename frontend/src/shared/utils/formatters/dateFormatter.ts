/**
 * Date formatting helpers for consistent display.
 */

const DATE_FORMAT_LOCALE = 'en-AU';

export const formatDate = (dateString: string | null): string => {
  if (!dateString) {
    return '-';
  }

  const date = new Date(dateString);

  const day = date.getDate();
  const month = date.toLocaleDateString(DATE_FORMAT_LOCALE, { month: 'short' });
  const year = date.getFullYear().toString().slice(-2);

  return `${day}-${month}-${year}`;
};

/**
 * Calculate tax payment date based on financial year
 * 
 * For AU tax jurisdiction: Financial year runs July 1 to June 30
 * Tax payment date is the last day of the financial year (June 30)
 * 
 * For other jurisdictions: Financial year runs January 1 to December 31
 * Tax payment date is the last day of the financial year (December 31)
 * 
 * @param financialYear - Financial year string (e.g., '2024-25' or '2024')
 * @param taxJurisdiction - Tax jurisdiction code (defaults to 'AU')
 * @returns Date string in YYYY-MM-DD format (ISO format for API compatibility)
 * 
 * @example
 * ```typescript
 * calculateTaxPaymentDate('2024-25', 'AU') // Returns '2025-06-30'
 * calculateTaxPaymentDate('2024', 'AU') // Returns '2025-06-30'
 * calculateTaxPaymentDate('2024', 'US') // Returns '2024-12-31'
 * ```
 */
export const calculateTaxPaymentDate = (
  financialYear: string,
  taxJurisdiction: string = 'AU'
): string => {
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

