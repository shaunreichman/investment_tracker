/**
 * EntityFilters Component
 * 
 * Filter controls for entity list including:
 * - Type filter (PERSON, COMPANY, TRUST, etc.)
 * - Jurisdiction filter (AU, US, UK, etc.)
 * - Sort controls
 * - View mode toggle (table/cards)
 */

import React from 'react';
import {
  Box,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Button,
  IconButton,
  Chip,
  Typography,
  useTheme
} from '@mui/material';
import {
  Clear as ClearIcon,
  ViewList as ViewListIcon,
  ViewModule as ViewModuleIcon
} from '@mui/icons-material';
import { EntityType, SortFieldEntity } from '../../types/enums/entity.enums';
import { Country, SortOrder } from '../../types/enums/shared.enums';
import { ENTITY_TYPE_LABELS, COUNTRY_LABELS } from '../../utils/labels';

export interface EntityFiltersProps {
  typeFilter: EntityType | 'all';
  onTypeFilterChange: (type: EntityType | 'all') => void;
  jurisdictionFilter: Country | 'all';
  onJurisdictionFilterChange: (jurisdiction: Country | 'all') => void;
  sortBy: SortFieldEntity;
  sortOrder: SortOrder;
  onSortChange: (field: SortFieldEntity) => void;
  viewMode: 'table' | 'cards';
  onViewModeChange: (mode: 'table' | 'cards') => void;
  onClearFilters: () => void;
  totalCount: number;
  hasActiveFilters: boolean;
}

const SORT_LABELS: Record<SortFieldEntity, string> = {
  [SortFieldEntity.NAME]: 'Name',
  [SortFieldEntity.TYPE]: 'Type',
  [SortFieldEntity.TAX_JURISDICTION]: 'Jurisdiction',
  [SortFieldEntity.CREATED_AT]: 'Created Date',
  [SortFieldEntity.UPDATED_AT]: 'Updated Date',
};

export const EntityFilters: React.FC<EntityFiltersProps> = ({
  typeFilter,
  onTypeFilterChange,
  jurisdictionFilter,
  onJurisdictionFilterChange,
  sortBy,
  sortOrder,
  onSortChange,
  viewMode,
  onViewModeChange,
  onClearFilters,
  totalCount,
  hasActiveFilters,
}) => {
  const theme = useTheme();

  return (
    <Box sx={{ mb: 2 }}>
      {/* Filter Controls */}
      <Box
        sx={{
          display: 'flex',
          gap: 2,
          flexWrap: 'wrap',
          alignItems: 'center',
          mb: 1,
        }}
      >
        {/* Entity Type Filter */}
        <FormControl size="small" sx={{ minWidth: 150 }}>
          <InputLabel>Type</InputLabel>
          <Select
            value={typeFilter}
            onChange={(e) => onTypeFilterChange(e.target.value as EntityType | 'all')}
            label="Type"
          >
            <MenuItem value="all">All Types</MenuItem>
            {Object.entries(ENTITY_TYPE_LABELS).map(([value, label]) => (
              <MenuItem key={value} value={value}>
                {label}
              </MenuItem>
            ))}
          </Select>
        </FormControl>

        {/* Jurisdiction Filter */}
        <FormControl size="small" sx={{ minWidth: 180 }}>
          <InputLabel>Jurisdiction</InputLabel>
          <Select
            value={jurisdictionFilter}
            onChange={(e) => onJurisdictionFilterChange(e.target.value as Country | 'all')}
            label="Jurisdiction"
          >
            <MenuItem value="all">All Jurisdictions</MenuItem>
            {Object.entries(COUNTRY_LABELS).map(([value, label]) => (
              <MenuItem key={value} value={value}>
                {label}
              </MenuItem>
            ))}
          </Select>
        </FormControl>

        {/* Sort By */}
        <FormControl size="small" sx={{ minWidth: 150 }}>
          <InputLabel>Sort By</InputLabel>
          <Select
            value={sortBy}
            onChange={(e) => onSortChange(e.target.value as SortFieldEntity)}
            label="Sort By"
          >
            {Object.entries(SORT_LABELS).map(([value, label]) => (
              <MenuItem key={value} value={value}>
                {label} {sortBy === value && (sortOrder === SortOrder.ASC ? '↑' : '↓')}
              </MenuItem>
            ))}
          </Select>
        </FormControl>

        {/* Clear Filters */}
        {hasActiveFilters && (
          <Button
            size="small"
            startIcon={<ClearIcon />}
            onClick={onClearFilters}
            variant="outlined"
          >
            Clear Filters
          </Button>
        )}

        {/* Spacer */}
        <Box sx={{ flexGrow: 1 }} />

        {/* View Mode Toggle */}
        <Box sx={{ display: 'flex', gap: 0.5, alignItems: 'center' }}>
          <IconButton
            size="small"
            onClick={() => onViewModeChange('table')}
            sx={{
              backgroundColor: viewMode === 'table' ? theme.palette.action.selected : 'transparent',
            }}
            aria-label="Table view"
          >
            <ViewListIcon />
          </IconButton>
          <IconButton
            size="small"
            onClick={() => onViewModeChange('cards')}
            sx={{
              backgroundColor: viewMode === 'cards' ? theme.palette.action.selected : 'transparent',
            }}
            aria-label="Card view"
          >
            <ViewModuleIcon />
          </IconButton>
        </Box>
      </Box>

      {/* Results Count */}
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <Typography variant="body2" color="text.secondary">
          Showing {totalCount} {totalCount === 1 ? 'entity' : 'entities'}
        </Typography>
        {hasActiveFilters && (
          <Chip
            label="Filtered"
            size="small"
            color="primary"
            variant="outlined"
          />
        )}
      </Box>
    </Box>
  );
};

