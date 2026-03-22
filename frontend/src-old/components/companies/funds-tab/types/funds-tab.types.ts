// ============================================================================
// FUNDS TAB TYPES
// ============================================================================

import { EnhancedFund, EnhancedFundsResponse } from '../../../../types/api';

// ============================================================================
// COMPONENT PROPS
// ============================================================================

export interface FundsTabProps {
  data: EnhancedFundsResponse | null;
  loading: boolean;
  onParamsChange: (params: any) => void;
  currentParams: any;
  onDeleteFund?: (fundId: number, fundName: string) => void;
}

export interface FundsFiltersProps {
  searchTerm: string;
  statusFilter: string;
  currencyFilter: string;
  fundTypeFilter: string;
  viewMode: 'table' | 'cards';
  onSearchChange: (event: React.ChangeEvent<HTMLInputElement>) => void;
  onStatusFilterChange: (event: any) => void;
  onCurrencyFilterChange: (event: any) => void;
  onFundTrackingTypeFilterChange: (event: any) => void;
  onViewModeChange: (mode: 'table' | 'cards') => void;
  onClearFilters: () => void;
}

export interface FundsTableProps {
  data: EnhancedFundsResponse;
  onSort: (field: string) => void;
  sortField: string;
  sortDirection: 'asc' | 'desc';
  onDeleteFund?: (fundId: number, fundName: string) => void;
}

export interface FundsCardsProps {
  data: EnhancedFundsResponse;
}

export interface FundRowProps {
  fund: EnhancedFund;
  onDeleteFund?: ((fundId: number, fundName: string) => void) | undefined;
}

// ============================================================================
// FILTER TYPES
// ============================================================================

export interface FundFilters {
  search: string;
  status_filter: string;
  currency_filter: string;
  fund_type_filter: string;
  page: number;
  per_page: number;
  sort_field: string;
  sort_direction: 'asc' | 'desc';
}

// ============================================================================
// SORTING TYPES
// ============================================================================

export interface SortConfig {
  field: string;
  direction: 'asc' | 'desc';
}

// ============================================================================
// VIEW MODE TYPES
// ============================================================================

export type ViewMode = 'table' | 'cards';
