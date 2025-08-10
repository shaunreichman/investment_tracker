// ============================================================================
// DEBOUNCED SEARCH HOOK
// ============================================================================

import { useState, useEffect, useCallback } from 'react';

interface UseDebouncedSearchProps {
  initialValue?: string;
  delay?: number;
  onSearchChange: (value: string) => void;
}

export const useDebouncedSearch = ({
  initialValue = '',
  delay = 300,
  onSearchChange,
}: UseDebouncedSearchProps) => {
  const [searchTerm, setSearchTerm] = useState(initialValue);

  // Debounced effect for API calls
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      onSearchChange(searchTerm);
    }, delay);

    return () => clearTimeout(timeoutId);
  }, [searchTerm, delay, onSearchChange]);

  // Handle immediate search term changes
  const handleSearchChange = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    const value = event.target.value;
    setSearchTerm(value);
  }, []);

  // Handle programmatic search term changes
  const setSearchTermDirectly = useCallback((value: string) => {
    setSearchTerm(value);
  }, []);

  return {
    searchTerm,
    handleSearchChange,
    setSearchTermDirectly,
  };
};
