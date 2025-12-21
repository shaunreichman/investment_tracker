/**
 * Fund labels for UI display.
 * 
 * Maps fund-related enum values to user-friendly strings.
 */

import {
  FundStatus,
  TaxPaymentType,
  EventType,
  DistributionType,
  FundInvestmentType,
  FundTrackingType,
} from '@/fund/types';

/**
 * Fund status labels for UI display.
 * 
 * Maps FundStatus enum values to user-friendly strings.
 */
export const FUND_STATUS_LABELS: Record<FundStatus, string> = {
  [FundStatus.ACTIVE]: 'Active',
  [FundStatus.SUSPENDED]: 'Suspended',
  [FundStatus.REALIZED]: 'Realized',
  [FundStatus.COMPLETED]: 'Completed',
};

/**
 * Tax payment type labels for UI display.
 * 
 * Maps TaxPaymentType enum values to user-friendly strings.
 */
export const TAX_PAYMENT_TYPE_LABELS: Record<TaxPaymentType, string> = {
  [TaxPaymentType.NON_RESIDENT_INTEREST_WITHHOLDING]: 'Non-Resident Interest Withholding',
  [TaxPaymentType.CAPITAL_GAINS_TAX]: 'Capital Gains Tax',
  [TaxPaymentType.EOFY_INTEREST_TAX]: 'EOFY Interest Tax',
  [TaxPaymentType.DIVIDENDS_FRANKED_TAX]: 'Dividends Franked Tax',
  [TaxPaymentType.DIVIDENDS_UNFRANKED_TAX]: 'Dividends Unfranked Tax',
};

/**
 * Event type labels for UI display.
 * 
 * Maps EventType enum values to user-friendly strings.
 */
export const EVENT_TYPE_LABELS: Record<EventType, string> = {
  [EventType.CAPITAL_CALL]: 'Capital Call',
  [EventType.RETURN_OF_CAPITAL]: 'Return of Capital',
  [EventType.DISTRIBUTION]: 'Distribution',
  [EventType.UNIT_PURCHASE]: 'Unit Purchase',
  [EventType.UNIT_SALE]: 'Unit Sale',
  [EventType.NAV_UPDATE]: 'NAV Update',
  [EventType.DAILY_RISK_FREE_INTEREST_CHARGE]: 'Daily Risk-Free Interest Charge',
  [EventType.EOFY_DEBT_COST]: 'EOFY Debt Cost',
  [EventType.TAX_PAYMENT]: 'Tax Payment',
};

/**
 * Distribution type labels for UI display.
 * 
 * Maps DistributionType enum values to user-friendly strings.
 */
export const DISTRIBUTION_TYPE_LABELS: Record<DistributionType, string> = {
  [DistributionType.INCOME]: 'Income',
  [DistributionType.DIVIDEND_FRANKED]: 'Franked Dividend',
  [DistributionType.DIVIDEND_UNFRANKED]: 'Unfranked Dividend',
  [DistributionType.INTEREST]: 'Interest',
  [DistributionType.RENT]: 'Rent',
  [DistributionType.CAPITAL_GAIN]: 'Capital Gain',
};

/**
 * Fund investment type labels for UI display.
 * 
 * Maps FundInvestmentType enum values to user-friendly strings.
 */
export const FUND_INVESTMENT_TYPE_LABELS: Record<FundInvestmentType, string> = {
  [FundInvestmentType.PRIVATE_EQUITY]: 'Private Equity',
  [FundInvestmentType.VENTURE_CAPITAL]: 'Venture Capital',
  [FundInvestmentType.PRIVATE_DEBT]: 'Private Debt',
  [FundInvestmentType.REAL_ESTATE]: 'Real Estate',
  [FundInvestmentType.INFRASTRUCTURE]: 'Infrastructure',
  [FundInvestmentType.OTHER]: 'Other',
};

/**
 * Fund tracking type labels for UI display.
 * 
 * Maps FundTrackingType enum values to user-friendly strings.
 */
export const FUND_TRACKING_TYPE_LABELS: Record<FundTrackingType, string> = {
  [FundTrackingType.COST_BASED]: 'Cost-Based',
  [FundTrackingType.NAV_BASED]: 'NAV-Based',
};

/**
 * Get fund status label with fallback.
 * 
 * @param status - The fund status enum value
 * @returns User-friendly label or the enum value itself if not found
 */
export function getFundStatusLabel(status: FundStatus): string {
  return FUND_STATUS_LABELS[status] || status;
}

/**
 * Get tax payment type label with fallback.
 * 
 * @param type - The tax payment type enum value
 * @returns User-friendly label or the enum value itself if not found
 */
export function getTaxPaymentTypeLabel(type: TaxPaymentType): string {
  return TAX_PAYMENT_TYPE_LABELS[type] || type;
}

/**
 * Get event type label with fallback.
 * 
 * @param eventType - The event type enum value
 * @returns User-friendly label or the enum value itself if not found
 */
export function getEventTypeLabel(eventType: EventType): string {
  return EVENT_TYPE_LABELS[eventType] || eventType;
}

/**
 * Get distribution type label with fallback.
 * 
 * @param distributionType - The distribution type enum value
 * @returns User-friendly label or the enum value itself if not found
 */
export function getDistributionTypeLabel(distributionType: DistributionType): string {
  return DISTRIBUTION_TYPE_LABELS[distributionType] || distributionType;
}

/**
 * Get fund investment type label with fallback.
 * 
 * @param investmentType - The fund investment type enum value
 * @returns User-friendly label or the enum value itself if not found
 */
export function getFundInvestmentTypeLabel(investmentType: FundInvestmentType): string {
  return FUND_INVESTMENT_TYPE_LABELS[investmentType] || investmentType;
}

/**
 * Get fund tracking type label with fallback.
 * 
 * @param trackingType - The fund tracking type enum value
 * @returns User-friendly label or the enum value itself if not found
 */
export function getFundTrackingTypeLabel(trackingType: FundTrackingType): string {
  return FUND_TRACKING_TYPE_LABELS[trackingType] || trackingType;
}

