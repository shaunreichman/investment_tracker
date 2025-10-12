/**
 * UI Label Mappings
 * 
 * This file contains mappings from technical enum values to user-friendly display strings.
 * These are used throughout the UI for dropdowns, filters, chips, and other display elements.
 * 
 * @example
 * ```typescript
 * import { ENTITY_TYPE_LABELS } from '@/utils/labels';
 * 
 * <MenuItem value={EntityType.PERSON}>
 *   {ENTITY_TYPE_LABELS[EntityType.PERSON]} // Displays: "Person"
 * </MenuItem>
 * ```
 */

import { EntityType } from '../types/enums/entity.enums';
import { Country, Currency } from '../types/enums/shared.enums';
import { 
  FundStatus, 
  TaxPaymentType, 
  EventType, 
  DistributionType,
  FundInvestmentType,
  FundTrackingType 
} from '../types/enums/fund.enums';
import {
  BankType,
  BankStatus,
  BankAccountType,
  BankAccountStatus
} from '../types/enums/banking.enums';

// ============================================================================
// ENTITY LABELS
// ============================================================================

/**
 * Entity type labels for UI display.
 * 
 * Maps EntityType enum values to user-friendly strings.
 */
export const ENTITY_TYPE_LABELS: Record<EntityType, string> = {
  [EntityType.PERSON]: 'Person',
  [EntityType.COMPANY]: 'Company',
  [EntityType.TRUST]: 'Trust',
  [EntityType.FUND]: 'Fund',
  [EntityType.OTHER]: 'Other',
};

// ============================================================================
// GEOGRAPHY LABELS
// ============================================================================

/**
 * Country labels for UI display.
 * 
 * Maps ISO 3166-1 alpha-2 country codes to full country names.
 */
export const COUNTRY_LABELS: Record<Country, string> = {
  [Country.AU]: 'Australia',
  [Country.US]: 'United States',
  [Country.UK]: 'United Kingdom',
  [Country.CA]: 'Canada',
  [Country.NZ]: 'New Zealand',
  [Country.SG]: 'Singapore',
  [Country.HK]: 'Hong Kong',
  [Country.JP]: 'Japan',
  [Country.DE]: 'Germany',
  [Country.FR]: 'France',
  [Country.CN]: 'China',
  [Country.KR]: 'Korea',
};

/**
 * Currency labels for UI display.
 * 
 * Maps ISO 4217 currency codes to full currency names.
 */
export const CURRENCY_LABELS: Record<Currency, string> = {
  [Currency.AUD]: 'Australian Dollar',
  [Currency.USD]: 'US Dollar',
  [Currency.EUR]: 'Euro',
  [Currency.GBP]: 'British Pound',
  [Currency.CAD]: 'Canadian Dollar',
  [Currency.NZD]: 'New Zealand Dollar',
  [Currency.SGD]: 'Singapore Dollar',
  [Currency.HKD]: 'Hong Kong Dollar',
  [Currency.JPY]: 'Japanese Yen',
  [Currency.CHF]: 'Swiss Franc',
  [Currency.CNY]: 'Chinese Yuan',
  [Currency.KRW]: 'Korean Won',
};

// ============================================================================
// FUND LABELS
// ============================================================================

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

// ============================================================================
// BANKING LABELS
// ============================================================================

/**
 * Bank type labels for UI display.
 * 
 * Maps BankType enum values to user-friendly strings.
 */
export const BANK_TYPE_LABELS: Record<BankType, string> = {
  [BankType.COMMERCIAL]: 'Commercial Bank',
  [BankType.INVESTMENT]: 'Investment Bank',
  [BankType.CENTRAL]: 'Central Bank',
  [BankType.COOPERATIVE]: 'Cooperative Bank',
  [BankType.DIGITAL]: 'Digital Bank',
};

/**
 * Bank status labels for UI display.
 * 
 * Maps BankStatus enum values to user-friendly strings.
 */
export const BANK_STATUS_LABELS: Record<BankStatus, string> = {
  [BankStatus.ACTIVE]: 'Active',
  [BankStatus.INACTIVE]: 'Inactive',
  [BankStatus.CLOSED]: 'Closed',
};

/**
 * Bank account type labels for UI display.
 * 
 * Maps BankAccountType enum values to user-friendly strings.
 */
export const BANK_ACCOUNT_TYPE_LABELS: Record<BankAccountType, string> = {
  [BankAccountType.CHECKING]: 'Checking Account',
  [BankAccountType.SAVINGS]: 'Savings Account',
  [BankAccountType.INVESTMENT]: 'Investment Account',
  [BankAccountType.BUSINESS]: 'Business Account',
  [BankAccountType.TRUST]: 'Trust Account',
  [BankAccountType.JOINT]: 'Joint Account',
};

/**
 * Bank account status labels for UI display.
 * 
 * Maps BankAccountStatus enum values to user-friendly strings.
 */
export const BANK_ACCOUNT_STATUS_LABELS: Record<BankAccountStatus, string> = {
  [BankAccountStatus.ACTIVE]: 'Active',
  [BankAccountStatus.INACTIVE]: 'Inactive',
  [BankAccountStatus.CLOSED]: 'Closed',
  [BankAccountStatus.SUSPENDED]: 'Suspended',
  [BankAccountStatus.OVERDRAFT]: 'Overdraft',
};

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

/**
 * Get entity type label with fallback.
 * 
 * @param entityType - The entity type enum value
 * @returns User-friendly label or the enum value itself if not found
 */
export function getEntityTypeLabel(entityType: EntityType): string {
  return ENTITY_TYPE_LABELS[entityType] || entityType;
}

/**
 * Get country label with fallback.
 * 
 * @param country - The country code
 * @returns Full country name or the code itself if not found
 */
export function getCountryLabel(country: Country): string {
  return COUNTRY_LABELS[country] || country;
}

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

/**
 * Get currency label with fallback.
 * 
 * @param currency - The currency code
 * @returns Full currency name or the code itself if not found
 */
export function getCurrencyLabel(currency: Currency): string {
  return CURRENCY_LABELS[currency] || currency;
}

/**
 * Get bank type label with fallback.
 * 
 * @param bankType - The bank type enum value
 * @returns User-friendly label or the enum value itself if not found
 */
export function getBankTypeLabel(bankType: BankType): string {
  return BANK_TYPE_LABELS[bankType] || bankType;
}

/**
 * Get bank status label with fallback.
 * 
 * @param status - The bank status enum value
 * @returns User-friendly label or the enum value itself if not found
 */
export function getBankStatusLabel(status: BankStatus): string {
  return BANK_STATUS_LABELS[status] || status;
}

/**
 * Get bank account type label with fallback.
 * 
 * @param accountType - The bank account type enum value
 * @returns User-friendly label or the enum value itself if not found
 */
export function getBankAccountTypeLabel(accountType: BankAccountType): string {
  return BANK_ACCOUNT_TYPE_LABELS[accountType] || accountType;
}

/**
 * Get bank account status label with fallback.
 * 
 * @param status - The bank account status enum value
 * @returns User-friendly label or the enum value itself if not found
 */
export function getBankAccountStatusLabel(status: BankAccountStatus): string {
  return BANK_ACCOUNT_STATUS_LABELS[status] || status;
}
