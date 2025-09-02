/**
 * Centralized helper utilities for common application functions
 */

import { EVENT_TYPE_COLORS } from './constants';
// Types are re-exported from this module; avoid importing here to prevent unused warnings
import { getEventTypeLabel as _getEventTypeLabel, getEventTypeLabelSimple as _getEventTypeLabelSimple } from './transformers/eventTransformers';
import { prepareChartData as _prepareChartData, calculateDateRange as _calculateDateRange, generateChartTicks as _generateChartTicks } from './transformers/chartDataTransformers';
import { isActiveNavFund as _isActiveNavFund, getStatusInfo as _getStatusInfo, getStatusTooltip as _getStatusTooltip, getTrackingTypeColor as _getTrackingTypeColor } from './transformers/fundTransformers';
export type { ExtendedFundEvent, ExtendedFund } from '../types/api';

// Types are sourced from '../types/api' to avoid duplication

/**
 * Get event type color for consistent styling
 * @param eventType - The event type string
 * @returns Material-UI color value
 */
export const getEventTypeColor = (eventType: string): 'primary' | 'success' | 'warning' | 'info' | 'error' | 'default' => {
  return EVENT_TYPE_COLORS[eventType] || 'default';
};

/**
 * Get event type label for display
 * @param event - The fund event object
 * @returns Formatted event type label
 */
export const getEventTypeLabel = _getEventTypeLabel;

/**
 * Get fund status information for display (FundDetail interface)
 * @param status - The fund status string
 * @returns Status info object with value, color, icon, and tooltip
 */
export const getStatusInfo = _getStatusInfo;

/**
 * Get tracking type color for display
 * @param trackingType - The fund tracking type string
 * @returns Material-UI color value
 */
export const getTrackingTypeColor = _getTrackingTypeColor;

/**
 * Get status tooltip text for display
 * @param status - The fund status string
 * @returns Tooltip text
 */
export const getStatusTooltip = _getStatusTooltip;



/**
 * Check if fund is an active NAV-based fund
 * @param fund - The fund object
 * @returns True if fund is active and NAV-based
 */
export const isActiveNavFund = _isActiveNavFund;

/**
 * Prepare chart data for NAV performance visualization
 * @param events - Array of fund events
 * @param fund - The fund object
 * @returns Chart data object
 */
export const prepareChartData = _prepareChartData;

/**
 * Calculate date range for chart display
 * @param events - Array of fund events
 * @returns Object with start and end dates
 */
export const calculateDateRange = _calculateDateRange;

/**
 * Generate chart ticks for date axis
 * @param startDate - Start date string
 * @param endDate - End date string
 * @returns Array of date strings for ticks
 */
export const generateChartTicks = _generateChartTicks;

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
 * Format number for display with optional decimal places
 * @param value - Number to format
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

/**
 * Debounce function for input handling
 * @param func - Function to debounce
 * @param delay - Delay in milliseconds
 * @returns Debounced function
 */
export const debounce = <T extends (...args: any[]) => any>(func: T, delay: number): T => {
  let timeoutId: NodeJS.Timeout;
  return ((...args: any[]) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => func(...args), delay);
  }) as T;
};

/**
 * Throttle function for performance optimization
 * @param func - Function to throttle
 * @param delay - Delay in milliseconds
 * @returns Throttled function
 */
export const throttle = <T extends (...args: any[]) => any>(func: T, delay: number): T => {
  let lastCall = 0;
  return ((...args: any[]) => {
    const now = Date.now();
    if (now - lastCall >= delay) {
      lastCall = now;
      return func(...args);
    }
  }) as T;
};

/**
 * Deep clone object for state management
 * @param obj - Object to clone
 * @returns Cloned object
 */
export const deepClone = <T>(obj: T): T => {
  if (obj === null || typeof obj !== 'object') return obj;
  if (obj instanceof Date) return new Date(obj.getTime()) as unknown as T;
  if (Array.isArray(obj)) return obj.map(item => deepClone(item)) as unknown as T;
  
  const cloned = {} as T;
  for (const key in obj) {
    if (obj.hasOwnProperty(key)) {
      cloned[key] = deepClone(obj[key]);
    }
  }
  return cloned;
};

/**
 * Deep equality check for objects
 * @param obj1 - First object to compare
 * @param obj2 - Second object to compare
 * @returns True if objects are deeply equal
 */
export const deepEqual = (obj1: any, obj2: any): boolean => {
  if (obj1 === obj2) return true;
  if (obj1 == null || obj2 == null) return false;
  if (typeof obj1 !== typeof obj2) return false;
  
  if (typeof obj1 !== 'object') return obj1 === obj2;
  
  const keys1 = Object.keys(obj1);
  const keys2 = Object.keys(obj2);
  
  if (keys1.length !== keys2.length) return false;
  
  for (const key of keys1) {
    if (!keys2.includes(key)) return false;
    if (!deepEqual(obj1[key], obj2[key])) return false;
  }
  
  return true;
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
 * Get simple event type label for modal components
 * @param eventType - The event type string
 * @returns Simple event type label
 */
export const getEventTypeLabelSimple = _getEventTypeLabelSimple;