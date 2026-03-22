// ============================================================================
// FUNDS TAB COMPONENT (REFACTORED)
// ============================================================================

import React, { useEffect, useRef } from 'react';
import { Box, Card, CardContent, Typography } from '@mui/material';
import { FundsTabProps } from './types/funds-tab.types';
import { FundsFilters } from './components/FundsFilters';
import { FundsTable } from './components/FundsTable';
import { FundsCards } from './components/FundsCards';
import { 
  useDebouncedSearch, 
  useResponsiveView, 
  useTableSorting 
} from '@/shared/hooks/ui';
import { useFundsFilters } from '@/fund/hooks';

export const FundsTab: React.FC<FundsTabProps> = ({
  data,
  loading,
  onParamsChange,
  currentParams,
  onDeleteFund,
}) => {
  // Refs to track previous values and prevent infinite loops
  const prevSortFieldRef = useRef<string | undefined>(currentParams.sort_field);
  const prevSortDirectionRef = useRef<string | undefined>(currentParams.sort_direction);
  const prevViewModeRef = useRef<string | undefined>(currentParams.view_mode);

  // Initialize hooks
  const { viewMode, handleViewModeChange } = useResponsiveView({
    defaultView: (currentParams.view_mode as 'table' | 'cards') || 'table',
  });

  const { sortField, sortDirection, handleSort } = useTableSorting({
    defaultField: currentParams.sort_field || 'start_date',
    defaultDirection: (currentParams.sort_direction as 'asc' | 'desc') || 'desc',
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
    onFiltersChange: (filters) => {
      onParamsChange((prev: any) => ({ ...prev, ...filters }));
    },
  });

  const { searchTerm, handleSearchChange } = useDebouncedSearch({
    initialValue: currentParams.search || '',
    onSearchChange: (value) => {
      onParamsChange((prev: any) => ({ ...prev, search: value, page: 1 }));
    },
  });

  // Update params when sorting changes (only if actually different)
  useEffect(() => {
    const sortFieldChanged = sortField && sortField !== prevSortFieldRef.current;
    const sortDirectionChanged = sortDirection !== prevSortDirectionRef.current;
    
    if (sortFieldChanged || sortDirectionChanged) {
      prevSortFieldRef.current = sortField;
      prevSortDirectionRef.current = sortDirection;
      
      onParamsChange((prev: any) => ({
        ...prev,
        sort_field: sortField,
        sort_direction: sortDirection,
        page: 1,
      }));
    }
  }, [sortField, sortDirection, onParamsChange]);

  // Update params when view mode changes (only if actually different)
  useEffect(() => {
    if (viewMode !== prevViewModeRef.current) {
      prevViewModeRef.current = viewMode;
      onParamsChange((prev: any) => ({
        ...prev,
        view_mode: viewMode,
      }));
    }
  }, [viewMode, onParamsChange]);

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
                  : 'This company doesn\'t have any funds yet.'}
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

