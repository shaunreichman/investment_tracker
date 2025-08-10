// ============================================================================
// COMPANIES PAGINATION HOOK
// ============================================================================

import { useState, useCallback } from 'react';

interface UseCompaniesPaginationProps {
  initialPage?: number;
  initialPerPage?: number;
  onPaginationChange: (page: number, perPage: number) => void;
}

export const useCompaniesPagination = ({
  initialPage = 1,
  initialPerPage = 25,
  onPaginationChange,
}: UseCompaniesPaginationProps) => {
  const [currentPage, setCurrentPage] = useState(initialPage);
  const [perPage, setPerPage] = useState(initialPerPage);

  const handlePageChange = useCallback((newPage: number) => {
    setCurrentPage(newPage);
    onPaginationChange(newPage, perPage);
  }, [perPage, onPaginationChange]);

  const handleRowsPerPageChange = useCallback((newPerPage: number) => {
    setPerPage(newPerPage);
    setCurrentPage(1); // Reset to first page when changing page size
    onPaginationChange(1, newPerPage);
  }, [onPaginationChange]);

  const resetPagination = useCallback(() => {
    setCurrentPage(initialPage);
    setPerPage(initialPerPage);
    onPaginationChange(initialPage, initialPerPage);
  }, [initialPage, initialPerPage, onPaginationChange]);

  return {
    currentPage,
    perPage,
    handlePageChange,
    handleRowsPerPageChange,
    resetPagination,
  };
};
