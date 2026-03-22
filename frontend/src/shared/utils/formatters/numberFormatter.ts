/**
 * Numeric formatting helpers shared across the application.
 */

const NUMBER_FORMAT_LOCALE = 'en-AU';

export const formatNumber = (
  value: number | null | undefined,
  decimals: number = 2
): string => {
  if (value === null || value === undefined) {
    return '-';
  }

  const safeValue = Object.is(value, -0) ? 0 : value;

  return new Intl.NumberFormat(NUMBER_FORMAT_LOCALE, {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(safeValue);
};

export const formatPercentage = (
  value: number | null | undefined,
  decimals: number = 1
): string => {
  if (value === null || value === undefined) {
    return '-';
  }

  return `${formatNumber(value, decimals)}%`;
};

export const formatLargeNumber = (
  value: number | null | undefined
): string => {
  if (value === null || value === undefined) {
    return '-';
  }

  const absValue = Math.abs(value);
  const sign = value < 0 ? '-' : '';

  if (absValue >= 1e9) {
    return `${sign}${(absValue / 1e9).toFixed(1)}B`;
  }

  if (absValue >= 1e6) {
    return `${sign}${(absValue / 1e6).toFixed(1)}M`;
  }

  if (absValue >= 1e3) {
    return `${sign}${(absValue / 1e3).toFixed(1)}K`;
  }

  return formatNumber(value);
};

