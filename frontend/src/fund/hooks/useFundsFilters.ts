/**
 * Fund Filters Hook
 * 
 * Manages filter state for fund lists (status, currency, tracking type).
 * Used by FundsTab component to handle filter changes and state.
 * 
 * @module fund/hooks/useFundsFilters
 */

import { useState, useCallback, ChangeEvent } from 'react';

// ============================================================================
// TYPES
// ============================================================================

/**
 * Filter values for fund filtering
 */
export type FundFilterValue = string | 'all';

/**
 * Fund filter state
 */
export interface FundFilters {
  /** Filter by fund status (FundStatus enum value or 'all') */
  status_filter: FundFilterValue;
  /** Filter by currency (Currency enum value or 'all') */
  currency_filter: FundFilterValue;
  /** Filter by fund tracking type (FundTrackingType enum value or 'all') */
  fund_type_filter: FundFilterValue;
  /** Reset to page 1 when filters change */
  page: number;
}

/**
 * Props for useFundsFilters hook
 */
export interface UseFundsFiltersProps {
  /** Initial filter values */
  initialFilters: {
    status_filter: FundFilterValue;
    currency_filter: FundFilterValue;
    fund_type_filter: FundFilterValue;
  };
  /** Callback when filters change */
  onFiltersChange: (filters: Partial<FundFilters>) => void;
}

/**
 * Return type for useFundsFilters hook
 */
export interface UseFundsFiltersResult {
  /** Current status filter value */
  statusFilter: FundFilterValue;
  /** Current currency filter value */
  currencyFilter: FundFilterValue;
  /** Current fund type filter value */
  fundTypeFilter: FundFilterValue;
  /** Handler for status filter change */
  handleStatusFilterChange: (event: ChangeEvent<{ value: unknown }>) => void;
  /** Handler for currency filter change */
  handleCurrencyFilterChange: (event: ChangeEvent<{ value: unknown }>) => void;
  /** Handler for fund tracking type filter change */
  handleFundTrackingTypeFilterChange: (event: ChangeEvent<{ value: unknown }>) => void;
  /** Clear all filters to 'all' */
  clearAllFilters: () => void;
  /** Whether any filter is active (not 'all') */
  hasActiveFilters: boolean;
}

// ============================================================================
// HOOK
// ============================================================================

/**
 * Hook for managing fund filter state
 * 
 * Manages three filter types:
 * - Status filter (fund status)
 * - Currency filter (fund currency)
 * - Fund type filter (tracking type)
 * 
 * Automatically resets to page 1 when any filter changes.
 * 
 * @param props - Hook configuration
 * @returns Filter state and handlers
 * 
 * @example
 * ```typescript
 * const {
 *   statusFilter,
 *   currencyFilter,
 *   fundTypeFilter,
 *   handleStatusFilterChange,
 *   handleCurrencyFilterChange,
 *   handleFundTrackingTypeFilterChange,
 *   clearAllFilters,
 *   hasActiveFilters,
 * } = useFundsFilters({
 *   initialFilters: {
 *     status_filter: 'all',
 *     currency_filter: 'all',
 *     fund_type_filter: 'all',
 *   },
 *   onFiltersChange: (filters) => {
 *     // Update query params or API call
 *   },
 * });
 * ```
 */
export const useFundsFilters = ({
  initialFilters,
  onFiltersChange,
}: UseFundsFiltersProps): UseFundsFiltersResult => {
  const [statusFilter, setStatusFilter] = useState<FundFilterValue>(
    initialFilters.status_filter || 'all'
  );
  const [currencyFilter, setCurrencyFilter] = useState<FundFilterValue>(
    initialFilters.currency_filter || 'all'
  );
  const [fundTypeFilter, setFundTrackingTypeFilter] = useState<FundFilterValue>(
    initialFilters.fund_type_filter || 'all'
  );

  const handleStatusFilterChange = useCallback(
    (event: ChangeEvent<{ value: unknown }>) => {
      const value = event.target.value as FundFilterValue;
      setStatusFilter(value);
      onFiltersChange({ status_filter: value, page: 1 });
    },
    [onFiltersChange]
  );

  const handleCurrencyFilterChange = useCallback(
    (event: ChangeEvent<{ value: unknown }>) => {
      const value = event.target.value as FundFilterValue;
      setCurrencyFilter(value);
      onFiltersChange({ currency_filter: value, page: 1 });
    },
    [onFiltersChange]
  );

  const handleFundTrackingTypeFilterChange = useCallback(
    (event: ChangeEvent<{ value: unknown }>) => {
      const value = event.target.value as FundFilterValue;
      setFundTrackingTypeFilter(value);
      onFiltersChange({ fund_type_filter: value, page: 1 });
    },
    [onFiltersChange]
  );

  const clearAllFilters = useCallback(() => {
    setStatusFilter('all');
    setCurrencyFilter('all');
    setFundTrackingTypeFilter('all');
    onFiltersChange({
      status_filter: 'all',
      currency_filter: 'all',
      fund_type_filter: 'all',
      page: 1,
    });
  }, [onFiltersChange]);

  const hasActiveFilters =
    statusFilter !== 'all' ||
    currencyFilter !== 'all' ||
    fundTypeFilter !== 'all';

  return {
    statusFilter,
    currencyFilter,
    fundTypeFilter,
    handleStatusFilterChange,
    handleCurrencyFilterChange,
    handleFundTrackingTypeFilterChange,
    clearAllFilters,
    hasActiveFilters,
  };
};

