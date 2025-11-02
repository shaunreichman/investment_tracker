// ============================================================================
// TABLE SORTING HOOK
// ============================================================================

import { useState, useCallback } from 'react';

export type SortDirection = 'asc' | 'desc';

interface UseTableSortingProps {
  defaultField?: string;
  defaultDirection?: SortDirection;
}

export const useTableSorting = ({
  defaultField = '',
  defaultDirection = 'desc',
}: UseTableSortingProps = {}) => {
  const [sortField, setSortField] = useState(defaultField);
  const [sortDirection, setSortDirection] = useState<SortDirection>(defaultDirection);

  const handleSort = useCallback((field: string) => {
    if (sortField === field) {
      // Toggle direction if same field
      setSortDirection(prev => prev === 'asc' ? 'desc' : 'asc');
    } else {
      // Set new field with default direction
      setSortField(field);
      setSortDirection('desc');
    }
  }, [sortField]);

  const getSortIcon = useCallback((field: string) => {
    if (sortField !== field) {
      return 'unfold_more';
    }
    return sortDirection === 'asc' ? 'expand_less' : 'expand_more';
  }, [sortField, sortDirection]);

  const resetSort = useCallback(() => {
    setSortField(defaultField);
    setSortDirection(defaultDirection);
  }, [defaultField, defaultDirection]);

  return {
    sortField,
    sortDirection,
    handleSort,
    getSortIcon,
    resetSort,
  };
};
