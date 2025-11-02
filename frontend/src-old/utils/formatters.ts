/**
 * Centralized formatting utilities for consistent display across the application
 */

/**
 * Format currency values with Excel accounting format (parentheses for negatives)
 * @param amount - The amount to format
 * @param currency - Currency code (default: 'AUD')
 * @returns Formatted currency string or '-' for null/undefined values
 */
export const formatCurrency = (amount: number | null, currency: string = 'AUD'): string => {
  if (amount === null) return '-';
  
  // Excel accounting format: parentheses for negatives, no minus sign
  const absAmount = Math.abs(amount);
  const formatted = new Intl.NumberFormat('en-AU', {
    style: 'currency',
    currency: currency,
  }).format(absAmount);
  
  return amount < 0 ? `(${formatted})` : formatted;
};

/**
 * Format brokerage fees with rounded values and no decimal places for whole numbers
 * @param amount - The brokerage fee amount
 * @param currency - Currency code (default: 'AUD')
 * @returns Formatted brokerage fee string or '-' for null/undefined values
 */
export const formatBrokerageFee = (amount: number | null, currency: string = 'AUD'): string => {
  if (amount === null) return '-';
  const rounded = Math.round(amount);
  const formatted = new Intl.NumberFormat('en-AU', {
    style: 'currency',
    currency: currency,
  }).format(rounded);
  
  // Remove .00 for whole numbers
  return formatted.replace(/\.00$/, '');
};

/**
 * Format dates in a consistent DD-MMM-YY format
 * @param dateString - Date string to format
 * @returns Formatted date string or '-' for null/undefined values
 */
export const formatDate = (dateString: string | null): string => {
  if (!dateString) return '-';
  const date = new Date(dateString);
  const day = date.getDate();
  const month = date.toLocaleDateString('en-AU', { month: 'short' });
  const year = date.getFullYear().toString().slice(-2);
  return `${day}-${month}-${year}`;
};

/**
 * Format numbers with optional decimal places
 * @param value - Number to format
 * @param decimals - Number of decimal places (default: 2)
 * @returns Formatted number string or '-' for null/undefined values
 */
export   const formatNumber = (value: number | null | undefined, decimals: number = 2): string => {
    if (value === null || value === undefined) return '-';
    
    // Handle negative zero
    if (value === 0) value = 0;
    
    return new Intl.NumberFormat('en-AU', {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals,
    }).format(value);
  };

/**
 * Format percentages with consistent decimal places
 * @param value - Percentage value (0-100)
 * @param decimals - Number of decimal places (default: 1)
 * @returns Formatted percentage string or '-' for null/undefined values
 */
export const formatPercentage = (value: number | null | undefined, decimals: number = 1): string => {
  if (value === null || value === undefined) return '-';
  
  return `${formatNumber(value, decimals)}%`;
};

/**
 * Format large numbers with K/M/B suffixes for readability
 * @param value - Number to format
 * @returns Formatted number with appropriate suffix
 */
export const formatLargeNumber = (value: number | null | undefined): string => {
  if (value === null || value === undefined) return '-';
  
  const absValue = Math.abs(value);
  const sign = value < 0 ? '-' : '';
  
  if (absValue >= 1e9) {
    return `${sign}${(absValue / 1e9).toFixed(1)}B`;
  } else if (absValue >= 1e6) {
    return `${sign}${(absValue / 1e6).toFixed(1)}M`;
  } else if (absValue >= 1e3) {
    return `${sign}${(absValue / 1e3).toFixed(1)}K`;
  }
  
  return formatNumber(value);
}; 