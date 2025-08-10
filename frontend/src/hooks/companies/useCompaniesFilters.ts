// ============================================================================
// COMPANIES FILTERS HOOK
// ============================================================================

import { useState, useCallback } from 'react';

interface UseCompaniesFiltersProps {
  initialFilters: Record<string, any>;
  onFiltersChange: (filters: any) => void;
}

export const useCompaniesFilters = ({
  initialFilters,
  onFiltersChange,
}: UseCompaniesFiltersProps) => {
  const [filters, setFilters] = useState(initialFilters);

  const updateFilter = useCallback((key: string, value: any) => {
    const newFilters = { ...filters, [key]: value, page: 1 };
    setFilters(newFilters);
    onFiltersChange(newFilters);
  }, [filters, onFiltersChange]);

  const clearFilter = useCallback((key: string) => {
    const newFilters = { ...filters, [key]: 'all', page: 1 };
    setFilters(newFilters);
    onFiltersChange(newFilters);
  }, [filters, onFiltersChange]);

  const clearAllFilters = useCallback(() => {
    const clearedFilters = Object.keys(filters).reduce((acc, key) => {
      if (key === 'page' || key === 'per_page') {
        acc[key] = key === 'page' ? 1 : filters[key];
      } else {
        acc[key] = 'all';
      }
      return acc;
    }, {} as Record<string, any>);
    
    setFilters(clearedFilters);
    onFiltersChange(clearedFilters);
  }, [filters, onFiltersChange]);

  const hasActiveFilters = Object.entries(filters).some(([key, value]) => {
    if (key === 'page' || key === 'per_page') return false;
    return value !== 'all' && value !== '';
  });

  return {
    filters,
    updateFilter,
    clearFilter,
    clearAllFilters,
    hasActiveFilters,
  };
};
