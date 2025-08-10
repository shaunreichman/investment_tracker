// ============================================================================
// COMPANIES SORTING HOOK
// ============================================================================

import { useState, useCallback } from 'react';
import { SortDirection } from '../shared/useTableSorting';

interface UseCompaniesSortingProps {
  initialField?: string;
  initialDirection?: SortDirection;
  onSortChange: (field: string, direction: SortDirection) => void;
}

export const useCompaniesSorting = ({
  initialField = '',
  initialDirection = 'desc',
  onSortChange,
}: UseCompaniesSortingProps) => {
  const [sortField, setSortField] = useState(initialField);
  const [sortDirection, setSortDirection] = useState<SortDirection>(initialDirection);

  const handleSort = useCallback((field: string) => {
    if (sortField === field) {
      // Toggle direction if same field
      const newDirection = sortDirection === 'asc' ? 'desc' : 'asc';
      setSortDirection(newDirection);
      onSortChange(field, newDirection);
    } else {
      // Set new field with default direction
      setSortField(field);
      setSortDirection('desc');
      onSortChange(field, 'desc');
    }
  }, [sortField, sortDirection, onSortChange]);

  const resetSort = useCallback(() => {
    setSortField(initialField);
    setSortDirection(initialDirection);
    onSortChange(initialField, initialDirection);
  }, [initialField, initialDirection, onSortChange]);

  return {
    sortField,
    sortDirection,
    handleSort,
    resetSort,
  };
};
