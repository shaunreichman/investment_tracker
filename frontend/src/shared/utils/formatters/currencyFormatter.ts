/**
 * Currency formatting utilities shared across domains.
 */

const DEFAULT_CURRENCY = 'AUD';
const NUMBER_FORMAT_LOCALE = 'en-AU';

export const formatCurrency = (
  amount: number | null,
  currency: string = DEFAULT_CURRENCY
): string => {
  if (amount === null) {
    return '-';
  }

  const absAmount = Math.abs(amount);
  const formatted = new Intl.NumberFormat(NUMBER_FORMAT_LOCALE, {
    style: 'currency',
    currency,
  }).format(absAmount);

  return amount < 0 ? `(${formatted})` : formatted;
};

export const formatBrokerageFee = (
  amount: number | null,
  currency: string = DEFAULT_CURRENCY
): string => {
  if (amount === null) {
    return '-';
  }

  const rounded = Math.round(amount);
  const formatted = new Intl.NumberFormat(NUMBER_FORMAT_LOCALE, {
    style: 'currency',
    currency,
  }).format(rounded);

  return formatted.replace(/\.00$/, '');
};

