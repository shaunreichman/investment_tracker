// ============================================================================
// FUNDS TAB TYPES
// ============================================================================

import { Fund } from '@/fund/types';

// ============================================================================
// COMPONENT PROPS
// ============================================================================

/**
 * Funds data response structure for FundsTab component
 * Maintains compatibility with existing filter structure while using Fund type
 */
export interface FundsTabData {
  funds: Fund[];
  filters?: {
    applied_status_filter: string;
    applied_search: string | null;
  };
}

export interface FundsTabProps {
  data: FundsTabData | null;
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
  data: FundsTabData;
  onSort: (field: string) => void;
  sortField: string;
  sortDirection: 'asc' | 'desc';
  onDeleteFund?: (fundId: number, fundName: string) => void;
}

export interface FundsCardsProps {
  data: FundsTabData;
}

export interface FundRowProps {
  fund: Fund;
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

