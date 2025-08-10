/**
 * Centralized constants and enums for consistent application configuration
 */

// Note: This module only exports string icon identifiers for UI components to map elsewhere.

/**
 * Event types for fund events
 */
export type EventType = 'CAPITAL_CALL' | 'DISTRIBUTION' | 'UNIT_PURCHASE' | 'UNIT_SALE' | 'NAV_UPDATE' | 'TAX_STATEMENT' | 'RETURN_OF_CAPITAL';

/**
 * Distribution types for distribution events
 */
export type DistributionType = 'INTEREST' | 'DIVIDEND' | 'OTHER';

/**
 * Sub-distribution types for specific distribution categories
 */
export type SubDistributionType = 'DIVIDEND_FRANKED' | 'DIVIDEND_UNFRANKED' | 'REGULAR' | 'WITHHOLDING_TAX';

/**
 * Fund tracking types
 */
export type FundTrackingType = 'nav_based' | 'cost_based';

/**
 * Fund types
 */
export type FundType = 'Private Equity' | 'Venture Capital' | 'Private Debt' | 'Real Estate' | 'Infrastructure' | 'Other';

/**
 * Fund status types
 */
export type FundStatus = 'ACTIVE' | 'REALIZED' | 'COMPLETED';

/**
 * Tax payment types
 */
export type TaxPaymentType = 'NON_RESIDENT_INTEREST_WITHHOLDING' | 'INTEREST_TAX' | 'DIVIDEND_TAX' | 'CAPITAL_GAIN_TAX';

/**
 * Event templates for the create event modal
 */
export const EVENT_TEMPLATES: {
  label: string;
  value: EventType | 'RETURN_OF_CAPITAL';
  description: string;
  icon: string;
  trackingType: 'nav_based' | 'cost_based' | 'both';
}[] = [
  {
    label: 'Capital Call',
    value: 'CAPITAL_CALL',
    description: 'Add a capital call (cost-based funds)',
    icon: 'AccountBalance',
    trackingType: 'cost_based'
  },
  {
    label: 'Capital Return',
    value: 'RETURN_OF_CAPITAL',
    description: 'Return capital to investors (cost-based funds)',
    icon: 'AccountBalance',
    trackingType: 'cost_based'
  },
  {
    label: 'Unit Purchase',
    value: 'UNIT_PURCHASE',
    description: 'Buy units (NAV-based funds)',
    icon: 'Add',
    trackingType: 'nav_based'
  },
  {
    label: 'Unit Sale',
    value: 'UNIT_SALE',
    description: 'Sell units (NAV-based funds)',
    icon: 'TrendingUp',
    trackingType: 'nav_based'
  },
  {
    label: 'NAV Update',
    value: 'NAV_UPDATE',
    description: 'Update NAV per share (NAV-based funds)',
    icon: 'TrendingUp',
    trackingType: 'nav_based'
  },
  {
    label: 'Distribution',
    value: 'DISTRIBUTION',
    description: 'Add a distribution (all funds)',
    icon: 'MonetizationOn',
    trackingType: 'both'
  },
  {
    label: 'Tax Statement',
    value: 'TAX_STATEMENT',
    description: 'Add a tax statement (all funds)',
    icon: 'Receipt',
    trackingType: 'both'
  },
];

/**
 * Distribution type templates
 */
export const DISTRIBUTION_TEMPLATES = [
  {
    label: 'Interest',
    value: 'INTEREST',
    description: 'Interest distribution',
    icon: 'MonetizationOn'
  },
  {
    label: 'Dividend',
    value: 'DIVIDEND',
    description: 'Dividend distribution',
    icon: 'MonetizationOn'
  },
  {
    label: 'Other',
    value: 'OTHER',
    description: 'Other distribution',
    icon: 'MonetizationOn'
  },
];

/**
 * Dividend sub-distribution templates
 */
export const DIVIDEND_SUB_TEMPLATES = [
  {
    label: 'Franked',
    value: 'DIVIDEND_FRANKED',
    description: 'Franked dividend',
    icon: 'MonetizationOn'
  },
  {
    label: 'Unfranked',
    value: 'DIVIDEND_UNFRANKED',
    description: 'Unfranked dividend',
    icon: 'MonetizationOn'
  },
];

/**
 * Interest sub-distribution templates
 */
export const INTEREST_SUB_TEMPLATES = [
  {
    label: 'Regular',
    value: 'REGULAR',
    description: 'Regular interest',
    icon: 'MonetizationOn'
  },
  {
    label: 'Withholding Tax',
    value: 'WITHHOLDING_TAX',
    description: 'Interest with withholding tax',
    icon: 'MonetizationOn'
  },
];

/**
 * Fund creation templates
 */
export const FUND_TEMPLATES = [
  {
    label: 'Cost-Based Fund',
    value: 'cost_based',
    description: 'Track capital calls and returns',
    icon: 'Business',
    trackingType: 'cost_based'
  },
  {
    label: 'NAV-Based Fund',
    value: 'nav_based',
    description: 'Track unit purchases and NAV updates',
    icon: 'TrendingUp',
    trackingType: 'nav_based'
  },
];

/**
 * Fund type options
 */
export const FUND_TYPES: { label: string; value: FundType }[] = [
  { label: 'Private Equity', value: 'Private Equity' },
  { label: 'Venture Capital', value: 'Venture Capital' },
  { label: 'Private Debt', value: 'Private Debt' },
  { label: 'Real Estate', value: 'Real Estate' },
  { label: 'Infrastructure', value: 'Infrastructure' },
  { label: 'Other', value: 'Other' },
];

/**
 * Currency options
 */
export const CURRENCIES = [
  { label: 'Australian Dollar (AUD)', value: 'AUD' },
  { label: 'US Dollar (USD)', value: 'USD' },
  { label: 'Euro (EUR)', value: 'EUR' },
  { label: 'British Pound (GBP)', value: 'GBP' },
];

/**
 * Event type color mappings
 */
export const EVENT_TYPE_COLORS: Record<string, 'primary' | 'success' | 'warning' | 'info' | 'error' | 'default'> = {
  'CAPITAL_CALL': 'primary',
  'DISTRIBUTION': 'success',
  'RETURN_OF_CAPITAL': 'warning',
  'NAV_UPDATE': 'info',
  'UNIT_PURCHASE': 'primary',
  'UNIT_SALE': 'warning',
  'TAX_PAYMENT': 'error',
  'TAX_STATEMENT': 'info',
  // Distribution type colors
  'INTEREST': 'success',
  'DIVIDEND': 'success',
  'OTHER': 'default',
};

/**
 * Fund status color mappings
 */
export const FUND_STATUS_COLORS: Record<FundStatus, 'success' | 'warning' | 'info'> = {
  'ACTIVE': 'success',
  'REALIZED': 'warning',
  'COMPLETED': 'info',
};

/**
 * Fund status labels
 */
export const FUND_STATUS_LABELS: Record<FundStatus, string> = {
  'ACTIVE': 'Active',
  'REALIZED': 'Realized',
  'COMPLETED': 'Completed',
};

/**
 * Tax payment type labels
 */
export const TAX_PAYMENT_TYPE_LABELS: Record<TaxPaymentType, string> = {
  'NON_RESIDENT_INTEREST_WITHHOLDING': 'Non-Resident Interest Withholding',
  'INTEREST_TAX': 'Interest Tax',
  'DIVIDEND_TAX': 'Dividend Tax',
  'CAPITAL_GAIN_TAX': 'Capital Gain Tax',
};

/**
 * Default tax rates
 */
export const DEFAULT_TAX_RATES = {
  INTEREST_INCOME: 10.0,
  DIVIDEND_FRANKED: 0.0,
  DIVIDEND_UNFRANKED: 10.0,
  CAPITAL_GAIN: 10.0,
  WITHHOLDING_TAX: 10.0,
  DEBT_INTEREST_DEDUCTION: 32.5,
};

/**
 * Financial year options (last 5 years + current)
 */
export const getFinancialYears = (): string[] => {
  const currentYear = new Date().getFullYear();
  const years: string[] = [];
  
  for (let i = 0; i < 6; i++) {
    const year = currentYear - i;
    years.push(`${year}-${(year + 1).toString().slice(-2)}`);
  }
  
  return years;
};

/**
 * Chart configuration
 */
export const CHART_CONFIG = {
  COLORS: {
    NAV_LINE: '#1976d2',
    PURCHASE_POINT: '#4caf50',
    SALE_POINT: '#f44336',
    GRID: '#e0e0e0',
    BACKGROUND: '#ffffff',
  },
  DIMENSIONS: {
    HEIGHT: 200,
    MARGIN: { top: 20, right: 20, bottom: 30, left: 40 },
  },
  ANIMATION: {
    DURATION: 300,
    EASING: 'ease-in-out',
  },
};

/**
 * Table configuration
 */
export const TABLE_CONFIG = {
  ROWS_PER_PAGE_OPTIONS: [10, 25, 50, 100],
  DEFAULT_ROWS_PER_PAGE: 25,
  SORT_DIRECTIONS: {
    ASC: 'asc',
    DESC: 'desc',
  },
};

/**
 * Form configuration
 */
export const FORM_CONFIG = {
  DEBOUNCE_DELAY: 300,
  AUTO_SAVE_DELAY: 2000,
  MAX_FILE_SIZE: 5 * 1024 * 1024, // 5MB
  ALLOWED_FILE_TYPES: ['.csv', '.xlsx', '.xls'],
};

/**
 * API configuration
 */
export const API_CONFIG = {
  TIMEOUT: 30000,
  RETRY_ATTEMPTS: 3,
  RETRY_DELAY: 1000,
  CACHE_DURATION: 5 * 60 * 1000, // 5 minutes
};

/**
 * Local storage keys
 */
export const STORAGE_KEYS = {
  SIDEBAR_VISIBLE: 'fundDetailSidebarVisible',
  USER_PREFERENCES: 'userPreferences',
  THEME: 'theme',
  LANGUAGE: 'language',
};

/**
 * Error messages
 */
export const ERROR_MESSAGES = {
  NETWORK_ERROR: 'Network error. Please check your connection and try again.',
  SERVER_ERROR: 'Server error. Please try again later.',
  VALIDATION_ERROR: 'Please check your input and try again.',
  UNAUTHORIZED: 'You are not authorized to perform this action.',
  NOT_FOUND: 'The requested resource was not found.',
  GENERIC: 'An unexpected error occurred. Please try again.',
};

/**
 * Success messages
 */
export const SUCCESS_MESSAGES = {
  FUND_CREATED: 'Fund created successfully.',
  FUND_UPDATED: 'Fund updated successfully.',
  EVENT_CREATED: 'Event created successfully.',
  EVENT_UPDATED: 'Event updated successfully.',
  EVENT_DELETED: 'Event deleted successfully.',
  TAX_STATEMENT_CREATED: 'Tax statement created successfully.',
  TAX_STATEMENT_UPDATED: 'Tax statement updated successfully.',
}; 