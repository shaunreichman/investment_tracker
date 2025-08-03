/**
 * Centralized helper utilities for common application functions
 */

import { EVENT_TYPE_COLORS, FUND_STATUS_COLORS, FUND_STATUS_LABELS, TAX_PAYMENT_TYPE_LABELS } from './constants';

/**
 * Extended fund event interface for component-specific data
 */
export interface ExtendedFundEvent {
  id: number;
  fund_id: number;
  event_type: string;
  event_date: string;
  amount: number | null;
  distribution_type?: string;
  sub_distribution_type?: string;
  units_purchased?: number | null;
  units_sold?: number | null;
  unit_price?: number | null;
  nav_per_share?: number | null;
  brokerage_fee?: number | null;
  tax_payment_type?: string;
  description?: string;
  reference_number?: string;
  // Additional fields for component display
  displayAmount?: string;
  formattedDate?: string;
  isEditable?: boolean;
  has_withholding_tax?: boolean;
  withholding_amount?: number | null;
  withholding_rate?: number | null;
  net_interest?: number | null;
}

/**
 * Extended fund interface for component-specific data
 */
export interface ExtendedFund {
  id: number;
  name: string;
  fund_type?: string;
  tracking_type: 'nav_based' | 'cost_based';
  description?: string;
  currency: string;
  commitment_amount?: number | null;
  expected_irr?: number | null;
  expected_duration_months?: number | null;
  current_equity_balance: number | null;
  average_equity_balance: number | null;
  status: string;
  end_date?: string | null;
  irr_gross?: number | null;
  irr_after_tax?: number | null;
  irr_real?: number | null;
  current_units?: number | null;
  current_unit_price?: number | null;
  current_nav_total?: number | null;
  investment_company_id: number;
  entity_id: number;
  created_at: string;
  updated_at: string;
  // Additional fields for component display
  isActiveNavFund?: boolean;
}

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
export const getEventTypeLabel = (event: ExtendedFundEvent): string => {
  // Show only subtype if available, otherwise show the main type
  if (event.distribution_type) {
    // Format distribution type to be consistent (uppercase)
    return event.distribution_type.toUpperCase();
  }
  if (event.tax_payment_type) {
    return event.tax_payment_type;
  }
  
  // For events without subtypes, show the main type
  return event.event_type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
};

/**
 * Get fund status information for display
 * @param status - The fund status string
 * @returns Object with label and color
 */
export const getStatusInfo = (status: string) => {
  const statusKey = status as keyof typeof FUND_STATUS_COLORS;
  return {
    label: FUND_STATUS_LABELS[statusKey] || status,
    color: FUND_STATUS_COLORS[statusKey] || 'default',
  };
};

/**
 * Get tracking type color for display
 * @param trackingType - The fund tracking type string
 * @returns Material-UI color value
 */
export const getTrackingTypeColor = (trackingType: string): 'primary' | 'secondary' | 'default' => {
  switch (trackingType.toLowerCase()) {
    case 'nav_based':
      return 'primary';
    case 'cost_based':
      return 'secondary';
    default:
      return 'default';
  }
};

/**
 * Get status tooltip text for display
 * @param status - The fund status string
 * @returns Tooltip text
 */
export const getStatusTooltip = (status: string): string => {
  switch (status.toLowerCase()) {
    case 'active':
      return 'Fund is still invested and has capital at risk';
    case 'realized':
      return 'All capital has been returned. Fund will be completed once the final tax statement is added.';
    case 'completed':
      return 'Fund is fully realized and all tax obligations are complete';
    default:
      return 'Unknown fund status';
  }
};

/**
 * Get status color for display
 * @param status - The fund status string
 * @returns Color value
 */
export const getStatusColor = (status: string): string => {
  switch (status.toLowerCase()) {
    case 'active':
      return '#4caf50'; // Lighter green
    case 'realized':
      return '#424242'; // Dark gray
    case 'completed':
      return '#000000'; // Black
    default:
      return 'default';
  }
};

/**
 * Check if fund is an active NAV-based fund
 * @param fund - The fund object
 * @returns True if fund is active and NAV-based
 */
export const isActiveNavFund = (fund: ExtendedFund): boolean => {
  return fund.tracking_type === 'nav_based' && fund.status === 'ACTIVE';
};

/**
 * Combine interest and withholding tax events for display
 * @param events - Array of fund events
 * @returns Array of events with combined interest/withholding tax
 */
export const combineInterestWithholdingEvents = (events: ExtendedFundEvent[]): ExtendedFundEvent[] => {
  const combinedEvents: ExtendedFundEvent[] = [];
  const processedEvents = new Set<number>();

  events.forEach((event, index) => {
    if (processedEvents.has(event.id)) return;

    if (event.event_type === 'DISTRIBUTION' && event.distribution_type === 'INTEREST') {
      // Look for withholding tax event on the same date
      const sameDateEvents = events.filter(e => e.event_date === event.event_date);
      const withholdingEvent = sameDateEvents.find(e => 
        e.event_type === 'TAX_PAYMENT' && e.tax_payment_type === 'NON_RESIDENT_INTEREST_WITHHOLDING'
      );

      if (withholdingEvent) {
        // Combine the events
        const combinedEvent = {
          ...event,
          has_withholding_tax: true,
          withholding_amount: withholdingEvent.amount,
          withholding_rate: 10, // Default rate
          net_interest: (event.amount || 0) - (withholdingEvent.amount || 0)
        };
        combinedEvents.push(combinedEvent);
        processedEvents.add(event.id);
        processedEvents.add(withholdingEvent.id);
      } else {
        combinedEvents.push(event);
        processedEvents.add(event.id);
      }
    } else if (event.event_type === 'TAX_PAYMENT' && event.tax_payment_type === 'NON_RESIDENT_INTEREST_WITHHOLDING') {
      // Skip withholding events that are already combined
      if (!processedEvents.has(event.id)) {
        combinedEvents.push(event);
        processedEvents.add(event.id);
      }
    } else {
      combinedEvents.push(event);
      processedEvents.add(event.id);
    }
  });

  return combinedEvents;
};

/**
 * Prepare chart data for NAV performance visualization
 * @param events - Array of fund events
 * @param fund - The fund object
 * @returns Chart data object
 */
export const prepareChartData = (events: ExtendedFundEvent[], fund: ExtendedFund) => {
  if (fund.tracking_type !== 'nav_based') {
    return { navData: [], purchaseData: [], saleData: [] };
  }

  const navData: Array<{ date: string; nav: number }> = [];
  const purchaseData: Array<{ date: string; price: number; units: number }> = [];
  const saleData: Array<{ date: string; price: number; units: number }> = [];

  events.forEach(event => {
    const date = event.event_date;
    
    if (event.event_type === 'NAV_UPDATE' && event.nav_per_share) {
      navData.push({ date, nav: event.nav_per_share });
    } else if (event.event_type === 'UNIT_PURCHASE' && event.unit_price && event.units_purchased) {
      purchaseData.push({ date, price: event.unit_price, units: event.units_purchased });
    } else if (event.event_type === 'UNIT_SALE' && event.unit_price && event.units_sold) {
      saleData.push({ date, price: event.unit_price, units: event.units_sold });
    }
  });

  return { navData, purchaseData, saleData };
};

/**
 * Calculate date range for chart display
 * @param events - Array of fund events
 * @returns Object with start and end dates
 */
export const calculateDateRange = (events: ExtendedFundEvent[]) => {
  if (events.length === 0) {
    const today = new Date();
    const sixMonthsAgo = new Date(today.getFullYear(), today.getMonth() - 6, today.getDate());
    return {
      startDate: sixMonthsAgo.toISOString().split('T')[0],
      endDate: today.toISOString().split('T')[0]
    };
  }

  const dates = events.map(e => new Date(e.event_date));
  const startDate = new Date(Math.min(...dates.map(d => d.getTime())));
  const endDate = new Date(Math.max(...dates.map(d => d.getTime())));

  // Add some padding to the date range
  startDate.setMonth(startDate.getMonth() - 1);
  endDate.setMonth(endDate.getMonth() + 1);

  return {
    startDate: startDate.toISOString().split('T')[0],
    endDate: endDate.toISOString().split('T')[0]
  };
};

/**
 * Generate chart ticks for date axis
 * @param startDate - Start date string
 * @param endDate - End date string
 * @returns Array of date strings for ticks
 */
export const generateChartTicks = (startDate: string, endDate: string): string[] => {
  const start = new Date(startDate);
  const end = new Date(endDate);
  const ticks: string[] = [];
  
  const current = new Date(start);
  while (current <= end) {
    ticks.push(current.toISOString().split('T')[0]);
    current.setMonth(current.getMonth() + 1);
  }
  
  return ticks;
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
 * Calculate tax payment date from financial year
 * @param financialYear - Financial year string (e.g., "2023-24")
 * @returns Tax payment date string
 */
export const calculateTaxPaymentDate = (financialYear: string): string => {
  const year = parseInt(financialYear.split('-')[0]);
  return `${year + 1}-05-15`; // May 15th of the following year
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
 * Check if two objects are deeply equal
 * @param obj1 - First object
 * @param obj2 - Second object
 * @returns True if objects are deeply equal
 */
export const deepEqual = (obj1: any, obj2: any): boolean => {
  if (obj1 === obj2) return true;
  if (obj1 == null || obj2 == null) return obj1 === obj2;
  if (typeof obj1 !== typeof obj2) return false;
  
  if (typeof obj1 === 'object') {
    if (Array.isArray(obj1) !== Array.isArray(obj2)) return false;
    
    const keys1 = Object.keys(obj1);
    const keys2 = Object.keys(obj2);
    
    if (keys1.length !== keys2.length) return false;
    
    for (const key of keys1) {
      if (!keys2.includes(key) || !deepEqual(obj1[key], obj2[key])) {
        return false;
      }
    }
    return true;
  }
  
  return false;
}; 