/**
 * CompanyList Component
 * 
 * Main component for displaying and managing companies.
 * Provides filtering, sorting, view modes, and deletion capabilities.
 * 
 * Receives data via props - parent page handles data fetching.
 */

import React, { useState, useMemo, useCallback } from 'react';
import { Box, Typography, Card, CardContent, Alert, Snackbar } from '@mui/material';
import type { Company } from '@/company/types';
import { CompanyType, CompanyStatus } from '@/company/types';
import { CompanyFilters } from './CompanyFilters';
import { CompanyTable } from './CompanyTable';
import { CompanyCards } from './CompanyCards';
import { LoadingSpinner, ErrorDisplay } from '@/shared/ui/feedback';
import { ConfirmDialog } from '@/shared/ui/overlays';
import type { ErrorInfo } from '@/shared/types/errors';
import { useDeleteCompany } from '@/company/hooks';

// ============================================================================
// PROPS INTERFACE
// ============================================================================

export interface CompanyListProps {
  /** Company data array */
  data: Company[] | null;
  
  /** Loading state */
  loading: boolean;
  
  /** Error information */
  error: ErrorInfo | null;
  
  /** Callback to refresh data */
  onRefresh: () => void | Promise<void>;
}

// ============================================================================
// COMPANY LIST COMPONENT
// ============================================================================

export const CompanyList: React.FC<CompanyListProps> = ({
  data,
  loading,
  error,
  onRefresh
}) => {
  // Filter and sort state
  const [typeFilter, setTypeFilter] = useState<CompanyType | 'all'>('all');
  const [statusFilter, setStatusFilter] = useState<CompanyStatus | 'all'>('all');
  const [sortBy, setSortBy] = useState<'name' | 'fund_count' | 'total_equity_balance' | 'active_funds'>('name');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');
  const [viewMode, setViewMode] = useState<'table' | 'cards'>('table');

  // Success notification state
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // Delete confirmation state
  const [deleteConfirm, setDeleteConfirm] = useState<{ id: number; name: string } | null>(null);
  const { mutate: deleteCompany, loading: isDeleting, error: deleteError, reset: resetDelete } =
    useDeleteCompany(deleteConfirm?.id ?? 0);

  const handleDeleteClick = useCallback((company: Company) => {
    setDeleteConfirm({ id: company.id, name: company.name });
  }, []);

  const handleDeleteConfirm = useCallback(async () => {
    if (!deleteConfirm) return;
    try {
      const result = await deleteCompany(undefined);
      if (result !== undefined) {
        const deletedName = deleteConfirm.name;
        setDeleteConfirm(null);
        resetDelete();
        setSuccessMessage(`Company "${deletedName}" deleted successfully.`);
        await onRefresh();
      }
    } catch {
      // Error surfaced via deleteError
    }
  }, [deleteConfirm, deleteCompany, onRefresh, resetDelete]);

  const handleCancelDelete = useCallback(() => {
    setDeleteConfirm(null);
    resetDelete();
  }, [resetDelete]);

  // Filter and sort companies client-side
  const filteredAndSortedCompanies = useMemo(() => {
    if (!data) return [];

    let filtered = data;

    // Filter by type
    if (typeFilter !== 'all') {
      filtered = filtered.filter(c => c.company_type === typeFilter);
    }

    // Filter by status
    if (statusFilter !== 'all') {
      filtered = filtered.filter(c => c.status === statusFilter);
    }

    // Sort
    const sorted = [...filtered].sort((a, b) => {
      let aVal: string | number;
      let bVal: string | number;

      switch (sortBy) {
        case 'name':
          aVal = a.name.toLowerCase();
          bVal = b.name.toLowerCase();
          break;
        case 'fund_count':
          aVal = a.total_funds || 0;
          bVal = b.total_funds || 0;
          break;
        case 'active_funds':
          aVal = a.total_funds_active || 0;
          bVal = b.total_funds_active || 0;
          break;
        case 'total_equity_balance':
          aVal = a.current_equity_balance || 0;
          bVal = b.current_equity_balance || 0;
          break;
        default:
          aVal = a.name.toLowerCase();
          bVal = b.name.toLowerCase();
      }

      if (aVal < bVal) return sortOrder === 'asc' ? -1 : 1;
      if (aVal > bVal) return sortOrder === 'asc' ? 1 : -1;
      return 0;
    });

    return sorted;
  }, [data, typeFilter, statusFilter, sortBy, sortOrder]);

  // Handle sort change
  const handleSort = (field: 'name' | 'fund_count' | 'total_equity_balance' | 'active_funds') => {
    if (sortBy === field) {
      // Toggle sort order if same field
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      // New field - default to ASC
      setSortBy(field);
      setSortOrder('asc');
    }
  };

  // Clear filters
  const handleClearFilters = () => {
    setTypeFilter('all');
    setStatusFilter('all');
    setSortBy('name');
    setSortOrder('asc');
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
        onRetry={onRefresh}
      />
    );
  }

  // Empty state
  if (!data || data.length === 0) {
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
        No companies found. Create your first company to get started.
      </Typography>
    );
  }

  // Main render
  return (
    <Box>
      {/* Filters */}
      <CompanyFilters
        typeFilter={typeFilter}
        onTypeFilterChange={setTypeFilter}
        statusFilter={statusFilter}
        onStatusFilterChange={setStatusFilter}
        sortBy={sortBy}
        sortOrder={sortOrder}
        onSortChange={handleSort}
        viewMode={viewMode}
        onViewModeChange={setViewMode}
        onClearFilters={handleClearFilters}
        totalCount={filteredAndSortedCompanies.length}
        hasActiveFilters={typeFilter !== 'all' || statusFilter !== 'all'}
      />

      {/* Content */}
      {filteredAndSortedCompanies.length === 0 ? (
        <Box sx={{ textAlign: 'center', py: 4 }}>
          <Typography variant="body2" color="text.secondary">
            No companies match your filters. Try adjusting your criteria.
          </Typography>
        </Box>
      ) : (
        <Card sx={{ mt: 2 }}>
          <CardContent sx={{ p: 0 }}>
            {viewMode === 'table' ? (
              <CompanyTable
                companies={filteredAndSortedCompanies}
                sortBy={sortBy}
                sortOrder={sortOrder}
                onSort={handleSort}
                onDeleteClick={handleDeleteClick}
                isDeleting={isDeleting}
              />
            ) : (
              <CompanyCards
                companies={filteredAndSortedCompanies}
                onDeleteClick={handleDeleteClick}
                isDeleting={isDeleting}
              />
            )}
          </CardContent>
        </Card>
      )}

      {/* Delete Confirmation Dialog */}
      <ConfirmDialog
        open={!!deleteConfirm}
        title="Delete company?"
        description={
          deleteConfirm
            ? `Are you sure you want to delete "${deleteConfirm.name}"? This action cannot be undone.`
            : ''
        }
        confirmAction={{
          label: 'Delete',
          variant: 'error',
          onClick: handleDeleteConfirm,
          loading: isDeleting,
        }}
        cancelAction={{
          label: 'Cancel',
          variant: 'outlined',
          onClick: handleCancelDelete,
        }}
        error={deleteError?.userMessage}
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

