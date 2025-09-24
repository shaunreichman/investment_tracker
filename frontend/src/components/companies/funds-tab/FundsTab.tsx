// ============================================================================
// FUNDS TAB COMPONENT (REFACTORED)
// ============================================================================

import React, { useEffect } from 'react';
import { Box, Card, CardContent, Typography } from '@mui/material';
import { FundsTabProps } from './types/funds-tab.types';
import { FundsFilters } from './components/FundsFilters';
import { FundsTable } from './components/FundsTable';
import { FundsCards } from './components/FundsCards';
import { 
  useDebouncedSearch, 
  useResponsiveView, 
  useTableSorting 
} from '../../../hooks/shared';
import { useFundsFilters } from '../../../hooks/funds';

export const FundsTab: React.FC<FundsTabProps> = ({
  data,
  loading,
  onParamsChange,
  currentParams,
  onDeleteFund,
}) => {
  // Initialize hooks
  const { viewMode, handleViewModeChange } = useResponsiveView({
    defaultView: 'table',
  });

  const { sortField, sortDirection, handleSort } = useTableSorting({
    defaultField: 'start_date',
    defaultDirection: 'desc',
  });

  const {
    statusFilter,
    currencyFilter,
    fundTypeFilter,
    handleStatusFilterChange,
    handleCurrencyFilterChange,
    handleFundTrackingTypeFilterChange,
    clearAllFilters,
  } = useFundsFilters({
    initialFilters: {
      status_filter: currentParams.status_filter || 'all',
      currency_filter: currentParams.currency_filter || 'all',
      fund_type_filter: currentParams.fund_type_filter || 'all',
    },
    onFiltersChange: (filters) => onParamsChange({ ...currentParams, ...filters }),
  });

  const { searchTerm, handleSearchChange } = useDebouncedSearch({
    initialValue: currentParams.search || '',
    onSearchChange: (value) => onParamsChange({ ...currentParams, search: value, page: 1 }),
  });

  // Update URL params when sorting changes
  useEffect(() => {
    if (sortField && sortField !== currentParams.sort_field) {
      onParamsChange({ 
        ...currentParams, 
        sort_field: sortField, 
        sort_direction: sortDirection,
        page: 1 
      });
    }
  }, [sortField, sortDirection, currentParams, onParamsChange]);

  // Update URL params when view mode changes
  useEffect(() => {
    if (viewMode !== currentParams.view_mode) {
      onParamsChange({ ...currentParams, view_mode: viewMode });
    }
  }, [viewMode, currentParams, onParamsChange]);

  if (loading) {
    return (
      <Box p={3}>
        <Typography>Loading funds data...</Typography>
      </Box>
    );
  }

  if (!data || data.funds.length === 0) {
    return (
      <Box p={3}>
        <Card>
          <CardContent>
            <Box textAlign="center" py={4}>
              <Typography variant="h6" color="textSecondary" gutterBottom>
                No Funds Found
              </Typography>
              <Typography variant="body2" color="textSecondary">
                {data?.filters?.applied_search || data?.filters?.applied_status_filter !== 'all'
                  ? 'Try adjusting your search or filter criteria.'
                  : 'This investment company doesn\'t have any funds yet.'}
              </Typography>
            </Box>
          </CardContent>
        </Card>
      </Box>
    );
  }

  return (
    <Box p={3}>
      {/* Filters and Search */}
      <FundsFilters
        searchTerm={searchTerm}
        statusFilter={statusFilter}
        currencyFilter={currencyFilter}
        fundTypeFilter={fundTypeFilter}
        viewMode={viewMode}
        onSearchChange={handleSearchChange}
        onStatusFilterChange={handleStatusFilterChange}
        onCurrencyFilterChange={handleCurrencyFilterChange}
        onFundTrackingTypeFilterChange={handleFundTrackingTypeFilterChange}
        onViewModeChange={handleViewModeChange}
        onClearFilters={clearAllFilters}
      />

      {/* Funds Display */}
      <Card>
        <CardContent sx={{ p: 0 }}>
          {viewMode === 'table' ? (
            <FundsTable
              data={data}
              onSort={handleSort}
              sortField={sortField}
              sortDirection={sortDirection}
              {...(onDeleteFund && { onDeleteFund })}
            />
          ) : (
            <FundsCards data={data} />
          )}
        </CardContent>
      </Card>
    </Box>
  );
};
