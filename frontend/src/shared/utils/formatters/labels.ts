/**
 * Shared Geography and Currency Labels
 * 
 * Global label mappings for geography and currency that are used across domains.
 * These are truly cross-cutting concerns and belong in the shared domain.
 */

import { Country, Currency } from '@/shared/types/enums/sharedEnums';

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
 * Get currency label with fallback.
 * 
 * @param currency - The currency code
 * @returns Full currency name or the code itself if not found
 */
export function getCurrencyLabel(currency: Currency): string {
  return CURRENCY_LABELS[currency] || currency;
}

