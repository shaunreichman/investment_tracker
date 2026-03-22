// ============================================================================
// FUNDS FILTERS COMPONENT
// ============================================================================

import React from 'react';
import {
  Box,
  Card,
  CardContent,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  IconButton,
  Tooltip,
  Chip,
  Typography,
} from '@mui/material';
import {
  Search,
  ViewList,
  ViewModule,
} from '@mui/icons-material';
import { FundsFiltersProps } from '../types/funds-tab.types';

export const FundsFilters: React.FC<FundsFiltersProps> = ({
  searchTerm,
  statusFilter,
  currencyFilter,
  fundTypeFilter,
  viewMode,
  onSearchChange,
  onStatusFilterChange,
  onCurrencyFilterChange,
  onFundTrackingTypeFilterChange,
  onViewModeChange,
  onClearFilters,
}) => {
  const hasActiveFilters = statusFilter !== 'all' || currencyFilter !== 'all' || fundTypeFilter !== 'all' || searchTerm;

  return (
    <Card sx={{ mb: 3 }}>
      <CardContent>
        <Box display="flex" gap={2} flexWrap="wrap" alignItems="center">
          <TextField
            label="Search Funds"
            variant="outlined"
            size="small"
            value={searchTerm}
            onChange={onSearchChange}
            InputProps={{
              startAdornment: <Search sx={{ mr: 1, color: 'text.secondary' }} />,
            }}
            sx={{ minWidth: 250 }}
          />
          
          <FormControl size="small" sx={{ minWidth: 150 }}>
            <InputLabel>Status Filter</InputLabel>
            <Select
              value={statusFilter}
              label="Status Filter"
              onChange={onStatusFilterChange}
            >
              <MenuItem value="all">All Statuses</MenuItem>
              <MenuItem value="active">Active</MenuItem>
              <MenuItem value="completed">Completed</MenuItem>
              <MenuItem value="suspended">Suspended</MenuItem>
            </Select>
          </FormControl>

          <FormControl size="small" sx={{ minWidth: 150 }}>
            <InputLabel>Currency Filter</InputLabel>
            <Select
              value={currencyFilter}
              label="Currency Filter"
              onChange={onCurrencyFilterChange}
            >
              <MenuItem value="all">All Currencies</MenuItem>
              <MenuItem value="AUD">AUD</MenuItem>
              <MenuItem value="USD">USD</MenuItem>
              <MenuItem value="EUR">EUR</MenuItem>
              <MenuItem value="GBP">GBP</MenuItem>
            </Select>
          </FormControl>

          <FormControl size="small" sx={{ minWidth: 150 }}>
            <InputLabel>Fund Type Filter</InputLabel>
            <Select
              value={fundTypeFilter}
              label="Fund Type Filter"
              onChange={onFundTrackingTypeFilterChange}
            >
              <MenuItem value="all">All Types</MenuItem>
              <MenuItem value="venture_capital">Venture Capital</MenuItem>
              <MenuItem value="private_equity">Private Equity</MenuItem>
              <MenuItem value="real_estate">Real Estate</MenuItem>
              <MenuItem value="infrastructure">Infrastructure</MenuItem>
              <MenuItem value="debt">Debt</MenuItem>
            </Select>
          </FormControl>

          {/* View Toggle */}
          <Box display="flex" alignItems="center" gap={1}>
            <Tooltip title="Table View">
              <IconButton
                size="small"
                onClick={() => onViewModeChange('table')}
                color={viewMode === 'table' ? 'primary' : 'default'}
              >
                <ViewList />
              </IconButton>
            </Tooltip>
            <Tooltip title="Card View">
              <IconButton
                size="small"
                onClick={() => onViewModeChange('cards')}
                color={viewMode === 'cards' ? 'primary' : 'default'}
              >
                <ViewModule />
              </IconButton>
            </Tooltip>
          </Box>
        </Box>
        
        {/* Active Filters Summary */}
        {hasActiveFilters && (
          <Box mt={2} display="flex" gap={1} flexWrap="wrap" alignItems="center">
            <Typography variant="caption" color="textSecondary">
              Active filters:
            </Typography>
            {statusFilter !== 'all' && (
              <Chip
                label={`Status: ${statusFilter}`}
                size="small"
                onDelete={() => onStatusFilterChange({ target: { value: 'all' } } as any)}
              />
            )}
            {currencyFilter !== 'all' && (
              <Chip
                label={`Currency: ${currencyFilter}`}
                size="small"
                onDelete={() => onCurrencyFilterChange({ target: { value: 'all' } } as any)}
              />
            )}
            {fundTypeFilter !== 'all' && (
              <Chip
                label={`Type: ${fundTypeFilter}`}
                size="small"
                onDelete={() => onFundTrackingTypeFilterChange({ target: { value: 'all' } } as any)}
              />
            )}
            {searchTerm && (
              <Chip
                label={`Search: "${searchTerm}"`}
                size="small"
                onDelete={() => onSearchChange({ target: { value: '' } } as any)}
              />
            )}
            <Chip
              label="Clear All"
              size="small"
              variant="outlined"
              onClick={onClearFilters}
              sx={{ cursor: 'pointer' }}
            />
          </Box>
        )}
      </CardContent>
    </Card>
  );
};
