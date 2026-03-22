/**
 * EntityList Component
 * 
 * Main component for displaying and managing entities.
 * Provides filtering, sorting, and deletion capabilities.
 * 
 * Note: Entities are immutable - they cannot be edited after creation.
 */

import React, { useState, useMemo } from 'react';
import { Box, Typography, Card, CardContent, Alert, Snackbar } from '@mui/material';
import { parseEntityDependencyError, isEntityDependencyError } from '@/entity/hooks';
import { entityApi } from '@/entity/api';
import type { Entity } from '@/entity/types';
import { EntityType, SortFieldEntity } from '@/entity/types';
import { Country, SortOrder } from '@/shared/types';
import type { ErrorInfo } from '@/shared/types/errors';
import { EntityFilters } from './EntityFilters';
import { EntityTable } from './EntityTable';
import { EntityCards } from './EntityCards';
import { DependencyBlockedDialog } from './DependencyBlockedDialog';
import { LoadingSpinner, ErrorDisplay } from '@/shared/ui/feedback';

export interface EntityDependencyError {
  entityName: string;
  details: {
    funds?: number;
    bankAccounts?: number;
    taxStatements?: number;
  };
}

export interface EntityListProps {
  /** Entity data array */
  data: Entity[] | null;
  /** Loading state */
  loading: boolean;
  /** Error information */
  error: ErrorInfo | null;
  /** Function to refresh entity data */
  onRefresh: () => Promise<void>;
}

export const EntityList: React.FC<EntityListProps> = ({
  data: entities,
  loading,
  error,
  onRefresh: refetch,
}) => {
  const [isDeleting, setIsDeleting] = useState(false);

  // Filter and sort state
  const [typeFilter, setTypeFilter] = useState<EntityType | 'all'>('all');
  const [jurisdictionFilter, setJurisdictionFilter] = useState<Country | 'all'>('all');
  const [sortBy, setSortBy] = useState<SortFieldEntity>(SortFieldEntity.NAME);
  const [sortOrder, setSortOrder] = useState<SortOrder>(SortOrder.ASC);
  const [viewMode, setViewMode] = useState<'table' | 'cards'>('table');

  // Dependency error dialog state
  const [dependencyError, setDependencyError] = useState<EntityDependencyError | null>(null);

  // Success notification state
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // Filter and sort entities client-side
  const filteredAndSortedEntities = useMemo(() => {
    if (!entities) return [];

    let filtered = entities;

    // Filter by type
    if (typeFilter !== 'all') {
      filtered = filtered.filter(e => e.entity_type === typeFilter);
    }

    // Filter by jurisdiction
    if (jurisdictionFilter !== 'all') {
      filtered = filtered.filter(e => e.tax_jurisdiction === jurisdictionFilter);
    }

    // Sort
    const sorted = [...filtered].sort((a, b) => {
      let aVal: string | number;
      let bVal: string | number;

      switch (sortBy) {
        case SortFieldEntity.NAME:
          aVal = a.name.toLowerCase();
          bVal = b.name.toLowerCase();
          break;
        case SortFieldEntity.TYPE:
          aVal = a.entity_type;
          bVal = b.entity_type;
          break;
        case SortFieldEntity.TAX_JURISDICTION:
          aVal = a.tax_jurisdiction;
          bVal = b.tax_jurisdiction;
          break;
        case SortFieldEntity.CREATED_AT:
          aVal = new Date(a.created_at).getTime();
          bVal = new Date(b.created_at).getTime();
          break;
        case SortFieldEntity.UPDATED_AT:
          aVal = new Date(a.updated_at).getTime();
          bVal = new Date(b.updated_at).getTime();
          break;
        default:
          aVal = a.name.toLowerCase();
          bVal = b.name.toLowerCase();
      }

      if (aVal < bVal) return sortOrder === SortOrder.ASC ? -1 : 1;
      if (aVal > bVal) return sortOrder === SortOrder.ASC ? 1 : -1;
      return 0;
    });

    return sorted;
  }, [entities, typeFilter, jurisdictionFilter, sortBy, sortOrder]);

  // Handle delete entity
  const handleDelete = async (entity: Entity) => {
    setIsDeleting(true);
    try {
      await entityApi.deleteEntity(entity.id);
      // Success - refetch entities and show success message
      await refetch();
      setSuccessMessage(`Entity "${entity.name}" deleted successfully`);
    } catch (err: any) {
      if (isEntityDependencyError(err)) {
        // Parse dependency details and show blocked dialog
        const details = parseEntityDependencyError(err.message);
        setDependencyError({
          entityName: entity.name,
          details
        });
      }
      // Other errors should be handled appropriately
    } finally {
      setIsDeleting(false);
    }
  };

  // Handle sort change
  const handleSort = (field: SortFieldEntity) => {
    if (sortBy === field) {
      // Toggle sort order if same field
      setSortOrder(sortOrder === SortOrder.ASC ? SortOrder.DESC : SortOrder.ASC);
    } else {
      // New field - default to ASC
      setSortBy(field);
      setSortOrder(SortOrder.ASC);
    }
  };

  // Clear filters
  const handleClearFilters = () => {
    setTypeFilter('all');
    setJurisdictionFilter('all');
    setSortBy(SortFieldEntity.NAME);
    setSortOrder(SortOrder.ASC);
  };

  // Loading state
  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
        <LoadingSpinner size={40} />
      </Box>
    );
  }

  // Error state
  if (error) {
    return (
      <ErrorDisplay 
        error={error}
        onRetry={() => refetch()}
      />
    );
  }

  // Empty state
  if (!entities || entities.length === 0) {
    return (
      <Typography 
        variant="body2" 
        sx={{ 
          color: 'text.secondary',
          fontStyle: 'italic',
          textAlign: 'center',
          py: 2
        }}
      >
        No entities found. Create your first entity to get started.
      </Typography>
    );
  }

  // Main render
  return (
    <Box>
      {/* Filters */}
      <EntityFilters
        typeFilter={typeFilter}
        onTypeFilterChange={setTypeFilter}
        jurisdictionFilter={jurisdictionFilter}
        onJurisdictionFilterChange={setJurisdictionFilter}
        sortBy={sortBy}
        sortOrder={sortOrder}
        onSortChange={handleSort}
        viewMode={viewMode}
        onViewModeChange={setViewMode}
        onClearFilters={handleClearFilters}
        totalCount={filteredAndSortedEntities.length}
        hasActiveFilters={typeFilter !== 'all' || jurisdictionFilter !== 'all'}
      />

      {/* Content */}
      {filteredAndSortedEntities.length === 0 ? (
        <Box sx={{ textAlign: 'center', py: 4 }}>
          <Typography variant="body2" color="text.secondary">
            No entities match your filters. Try adjusting your criteria.
          </Typography>
        </Box>
      ) : (
        <Card sx={{ mt: 2 }}>
          <CardContent sx={{ p: 0 }}>
            {viewMode === 'table' ? (
              <EntityTable 
                entities={filteredAndSortedEntities}
                onDelete={handleDelete}
                sortBy={sortBy}
                sortOrder={sortOrder}
                onSort={handleSort}
                isDeleting={isDeleting}
              />
            ) : (
              <EntityCards 
                entities={filteredAndSortedEntities}
                onDelete={handleDelete}
                isDeleting={isDeleting}
              />
            )}
          </CardContent>
        </Card>
      )}

      {/* Dependency Blocked Dialog */}
      <DependencyBlockedDialog
        open={!!dependencyError}
        error={dependencyError}
        onClose={() => setDependencyError(null)}
      />

      {/* Success Notification */}
      <Snackbar
        open={!!successMessage}
        autoHideDuration={4000}
        onClose={() => setSuccessMessage(null)}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert
          onClose={() => setSuccessMessage(null)}
          severity="success"
          variant="filled"
          sx={{ width: '100%' }}
        >
          {successMessage}
        </Alert>
      </Snackbar>
    </Box>
  );
};

