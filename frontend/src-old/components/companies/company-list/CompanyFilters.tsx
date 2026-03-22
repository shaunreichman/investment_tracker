/**
 * CompanyFilters Component
 * 
 * Filter and sort controls for the company list.
 */

import React from 'react';
import {
  Box,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Button,
  Typography,
  IconButton,
  Tooltip,
  useTheme
} from '@mui/material';
import {
  ViewList as ViewListIcon,
  ViewModule as ViewModuleIcon,
  Clear as ClearIcon
} from '@mui/icons-material';
import { CompanyType, CompanyStatus } from '../../../types/enums/company.enums';

interface CompanyFiltersProps {
  typeFilter: CompanyType | 'all';
  onTypeFilterChange: (type: CompanyType | 'all') => void;
  statusFilter: CompanyStatus | 'all';
  onStatusFilterChange: (status: CompanyStatus | 'all') => void;
  sortBy: 'name' | 'fund_count' | 'total_equity_balance' | 'active_funds';
  sortOrder: 'asc' | 'desc';
  onSortChange: (field: 'name' | 'fund_count' | 'total_equity_balance' | 'active_funds') => void;
  viewMode: 'table' | 'cards';
  onViewModeChange: (mode: 'table' | 'cards') => void;
  onClearFilters: () => void;
  totalCount: number;
  hasActiveFilters: boolean;
}

export const CompanyFilters: React.FC<CompanyFiltersProps> = ({
  typeFilter,
  onTypeFilterChange,
  statusFilter,
  onStatusFilterChange,
  sortBy,
  sortOrder,
  onSortChange,
  viewMode,
  onViewModeChange,
  onClearFilters,
  totalCount,
  hasActiveFilters
}) => {
  const theme = useTheme();

  return (
    <Box sx={{ mb: 2 }}>
      {/* Header with count and view mode */}
      <Box sx={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center',
        mb: 2
      }}>
        <Typography variant="body2" sx={{ color: theme.palette.text.secondary }}>
          {totalCount} {totalCount === 1 ? 'company' : 'companies'}
        </Typography>
        
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Tooltip title="Table view">
            <IconButton
              size="small"
              onClick={() => onViewModeChange('table')}
              sx={{
                color: viewMode === 'table' ? theme.palette.primary.main : theme.palette.text.secondary,
                backgroundColor: viewMode === 'table' ? theme.palette.action.selected : 'transparent'
              }}
            >
              <ViewListIcon />
            </IconButton>
          </Tooltip>
          <Tooltip title="Card view">
            <IconButton
              size="small"
              onClick={() => onViewModeChange('cards')}
              sx={{
                color: viewMode === 'cards' ? theme.palette.primary.main : theme.palette.text.secondary,
                backgroundColor: viewMode === 'cards' ? theme.palette.action.selected : 'transparent'
              }}
            >
              <ViewModuleIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {/* Filter controls */}
      <Box sx={{ 
        display: 'flex', 
        gap: 2, 
        flexWrap: 'wrap',
        alignItems: 'center'
      }}>
        {/* Company Type Filter */}
        <FormControl size="small" sx={{ minWidth: 180 }}>
          <InputLabel>Company Type</InputLabel>
          <Select
            value={typeFilter}
            onChange={(e) => onTypeFilterChange(e.target.value as CompanyType | 'all')}
            label="Company Type"
          >
            <MenuItem value="all">All Types</MenuItem>
            <MenuItem value={CompanyType.PRIVATE_EQUITY}>Private Equity</MenuItem>
            <MenuItem value={CompanyType.VENTURE_CAPITAL}>Venture Capital</MenuItem>
            <MenuItem value={CompanyType.REAL_ESTATE}>Real Estate</MenuItem>
            <MenuItem value={CompanyType.INFRASTRUCTURE}>Infrastructure</MenuItem>
            <MenuItem value={CompanyType.CREDIT}>Credit</MenuItem>
            <MenuItem value={CompanyType.HEDGE_FUND}>Hedge Fund</MenuItem>
            <MenuItem value={CompanyType.FAMILY_OFFICE}>Family Office</MenuItem>
            <MenuItem value={CompanyType.INVESTMENT_BANK}>Investment Bank</MenuItem>
            <MenuItem value={CompanyType.ASSET_MANAGEMENT}>Asset Management</MenuItem>
            <MenuItem value={CompanyType.INVESTMENT_GROUP}>Investment Group</MenuItem>
            <MenuItem value={CompanyType.OTHER}>Other</MenuItem>
          </Select>
        </FormControl>

        {/* Status Filter */}
        <FormControl size="small" sx={{ minWidth: 150 }}>
          <InputLabel>Status</InputLabel>
          <Select
            value={statusFilter}
            onChange={(e) => onStatusFilterChange(e.target.value as CompanyStatus | 'all')}
            label="Status"
          >
            <MenuItem value="all">All Statuses</MenuItem>
            <MenuItem value={CompanyStatus.ACTIVE}>Active</MenuItem>
            <MenuItem value={CompanyStatus.INACTIVE}>Inactive</MenuItem>
            <MenuItem value={CompanyStatus.COMPLETED}>Completed</MenuItem>
            <MenuItem value={CompanyStatus.SUSPENDED}>Suspended</MenuItem>
            <MenuItem value={CompanyStatus.CLOSED}>Closed</MenuItem>
          </Select>
        </FormControl>

        {/* Sort By */}
        <FormControl size="small" sx={{ minWidth: 180 }}>
          <InputLabel>Sort By</InputLabel>
          <Select
            value={sortBy}
            onChange={(e) => onSortChange(e.target.value as any)}
            label="Sort By"
          >
            <MenuItem value="name">Name</MenuItem>
            <MenuItem value="fund_count">Total Funds</MenuItem>
            <MenuItem value="active_funds">Active Funds</MenuItem>
            <MenuItem value="total_equity_balance">Total Equity</MenuItem>
          </Select>
        </FormControl>

        {/* Sort Order */}
        <FormControl size="small" sx={{ minWidth: 120 }}>
          <InputLabel>Order</InputLabel>
          <Select
            value={sortOrder}
            onChange={(e) => {
              // Toggle sort order by clicking the current field
              onSortChange(sortBy);
            }}
            label="Order"
          >
            <MenuItem value="asc">Ascending</MenuItem>
            <MenuItem value="desc">Descending</MenuItem>
          </Select>
        </FormControl>

        {/* Clear Filters Button */}
        {hasActiveFilters && (
          <Button
            size="small"
            variant="outlined"
            startIcon={<ClearIcon />}
            onClick={onClearFilters}
            sx={{
              borderColor: theme.palette.divider,
              color: theme.palette.text.secondary,
              '&:hover': {
                borderColor: theme.palette.text.secondary,
                backgroundColor: theme.palette.action.hover
              }
            }}
          >
            Clear Filters
          </Button>
        )}
      </Box>
    </Box>
  );
};
