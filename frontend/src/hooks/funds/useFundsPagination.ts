// ============================================================================
// FUNDS PAGINATION HOOK
// ============================================================================

import { useCallback } from 'react';

interface UseFundsPaginationProps {
  currentPage: number;
  perPage: number;
  totalItems: number;
  onPageChange: (page: number) => void;
  onRowsPerPageChange: (perPage: number) => void;
}

export const useFundsPagination = ({
  currentPage,
  perPage,
  totalItems,
  onPageChange,
  onRowsPerPageChange,
}: UseFundsPaginationProps) => {
  const handlePageChange = useCallback((event: unknown, newPage: number) => {
    onPageChange(newPage + 1); // MUI uses 0-based indexing, we use 1-based
  }, [onPageChange]);

  const handleRowsPerPageChange = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    const newPerPage = parseInt(event.target.value, 10);
    onRowsPerPageChange(newPerPage);
  }, [onRowsPerPageChange]);

  const totalPages = Math.ceil(totalItems / perPage);
  const hasNextPage = currentPage < totalPages;
  const hasPrevPage = currentPage > 1;

  return {
    handlePageChange,
    handleRowsPerPageChange,
    totalPages,
    hasNextPage,
    hasPrevPage,
    // MUI pagination expects 0-based page index
    muiPage: currentPage - 1,
  };
};
