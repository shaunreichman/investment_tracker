// ============================================================================
// FUNDS FILTERS HOOK
// ============================================================================

import { useState, useCallback } from 'react';

interface UseFundsFiltersProps {
  initialFilters: {
    status_filter: string;
    currency_filter: string;
    fund_type_filter: string;
  };
  onFiltersChange: (filters: any) => void;
}

export const useFundsFilters = ({
  initialFilters,
  onFiltersChange,
}: UseFundsFiltersProps) => {
  const [statusFilter, setStatusFilter] = useState(initialFilters.status_filter || 'all');
  const [currencyFilter, setCurrencyFilter] = useState(initialFilters.currency_filter || 'all');
  const [fundTypeFilter, setFundTrackingTypeFilter] = useState(initialFilters.fund_type_filter || 'all');

  const handleStatusFilterChange = useCallback((event: any) => {
    const value = event.target.value;
    setStatusFilter(value);
    onFiltersChange({ status_filter: value, page: 1 });
  }, [onFiltersChange]);

  const handleCurrencyFilterChange = useCallback((event: any) => {
    const value = event.target.value;
    setCurrencyFilter(value);
    onFiltersChange({ currency_filter: value, page: 1 });
  }, [onFiltersChange]);

  const handleFundTrackingTypeFilterChange = useCallback((event: any) => {
    const value = event.target.value;
    setFundTrackingTypeFilter(value);
    onFiltersChange({ fund_type_filter: value, page: 1 });
  }, [onFiltersChange]);

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

  const hasActiveFilters = statusFilter !== 'all' || currencyFilter !== 'all' || fundTypeFilter !== 'all';

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
