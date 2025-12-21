/**
 * Currency options presented across the application.
 *
 * Maintained as MANUAL copy because supported currencies are curated for
 * investor reporting today.
 */
export interface CurrencyOption {
  label: string;
  value: string;
}

export const CURRENCIES: CurrencyOption[] = [
  { label: 'Australian Dollar (AUD)', value: 'AUD' },
  { label: 'US Dollar (USD)', value: 'USD' },
  { label: 'Euro (EUR)', value: 'EUR' },
  { label: 'British Pound (GBP)', value: 'GBP' },
];

