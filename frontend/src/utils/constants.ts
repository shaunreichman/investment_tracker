/**
 * Centralized constants and enums for consistent application configuration
 */

import { 
  FundInvestmentType,
  FundStatus,
  EventType,
  DistributionType,
  TaxPaymentType,
  FundTrackingType
} from '../types/enums/fund.enums';

// Note: This module only exports string icon identifiers for UI components to map elsewhere.

/**
 * Sub-distribution types for specific distribution categories
 */
export type SubDistributionType = 'DIVIDEND_FRANKED' | 'DIVIDEND_UNFRANKED' | 'REGULAR' | 'WITHHOLDING_TAX';

/**
 * Event templates for the create event modal
 * 
 * Note: Values use EventType enum. TAX_STATEMENT is a UI concept that maps to TAX_PAYMENT event type.
 */
export const EVENT_TEMPLATES: {
  label: string;
  value: EventType | 'TAX_STATEMENT';
  description: string;
  icon: string;
  trackingType: 'nav_based' | 'cost_based' | 'both';
}[] = [
  {
    label: 'Capital Call',
    value: EventType.CAPITAL_CALL,
    description: 'Add a capital call (cost-based funds)',
    icon: 'AccountBalance',
    trackingType: 'cost_based'
  },
  {
    label: 'Capital Return',
    value: EventType.RETURN_OF_CAPITAL,
    description: 'Return capital to investors (cost-based funds)',
    icon: 'AccountBalance',
    trackingType: 'cost_based'
  },
  {
    label: 'Unit Purchase',
    value: EventType.UNIT_PURCHASE,
    description: 'Buy units (NAV-based funds)',
    icon: 'Add',
    trackingType: 'nav_based'
  },
  {
    label: 'Unit Sale',
    value: EventType.UNIT_SALE,
    description: 'Sell units (NAV-based funds)',
    icon: 'TrendingUp',
    trackingType: 'nav_based'
  },
  {
    label: 'NAV Update',
    value: EventType.NAV_UPDATE,
    description: 'Update NAV per share (NAV-based funds)',
    icon: 'TrendingUp',
    trackingType: 'nav_based'
  },
  {
    label: 'Distribution',
    value: EventType.DISTRIBUTION,
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
    trackingType: 'cost_based' as const
  },
  {
    label: 'NAV-Based Fund',
    value: 'nav_based',
    description: 'Track unit purchases and NAV updates',
    icon: 'TrendingUp',
    trackingType: 'nav_based' as const
  },
];

/**
 * Fund investment type options
 */
export const FUND_TYPES: { label: string; value: FundInvestmentType }[] = [
  { label: 'Private Equity', value: FundInvestmentType.PRIVATE_EQUITY },
  { label: 'Venture Capital', value: FundInvestmentType.VENTURE_CAPITAL },
  { label: 'Private Debt', value: FundInvestmentType.PRIVATE_DEBT },
  { label: 'Real Estate', value: FundInvestmentType.REAL_ESTATE },
  { label: 'Infrastructure', value: FundInvestmentType.INFRASTRUCTURE },
  { label: 'Other', value: FundInvestmentType.OTHER },
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
 * 
 * Uses EventType enum values. TAX_STATEMENT is a UI concept.
 * Also includes distribution type colors for UI display.
 */
export const EVENT_TYPE_COLORS: Record<string, 'primary' | 'success' | 'warning' | 'info' | 'error' | 'default'> = {
  [EventType.CAPITAL_CALL]: 'primary',
  [EventType.DISTRIBUTION]: 'success',
  [EventType.RETURN_OF_CAPITAL]: 'warning',
  [EventType.NAV_UPDATE]: 'info',
  [EventType.UNIT_PURCHASE]: 'primary',
  [EventType.UNIT_SALE]: 'warning',
  [EventType.TAX_PAYMENT]: 'error',
  'TAX_STATEMENT': 'info', // UI concept, not in EventType enum
  // Distribution type colors (UI simplified versions)
  'INTEREST': 'success',
  'DIVIDEND': 'success',
  'OTHER': 'default',
};

/**
 * Fund status color mappings
 * 
 * Note: For fund status labels (text), see utils/labels.ts
 */
export const FUND_STATUS_COLORS: Partial<Record<FundStatus, 'success' | 'warning' | 'info'>> = {
  [FundStatus.ACTIVE]: 'success',
  [FundStatus.SUSPENDED]: 'info',
  [FundStatus.REALIZED]: 'warning',
  [FundStatus.COMPLETED]: 'info',
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