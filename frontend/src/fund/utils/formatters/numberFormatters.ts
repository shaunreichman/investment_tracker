/**
 * Number formatting utilities for fund domain.
 * 
 * Provides helpers for formatting and parsing numbers in fund-specific contexts.
 * Note: For general number formatting, use shared/utils/formatters/numberFormatter.
 */

/**
 * Format number for display with optional decimal places
 * @param value - Number to format (as string)
 * @returns Formatted number string
 */
export const formatNumber = (value: string): string => {
  const num = parseFloat(value);
  if (isNaN(num)) return value;
  return num.toFixed(2);
};

/**
 * Parse number from string with validation
 * @param value - String to parse
 * @returns Parsed number or original string
 */
export const parseNumber = (value: string): string => {
  const num = parseFloat(value);
  if (isNaN(num)) return '';
  return num.toString();
};

