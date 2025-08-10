// ============================================================================
// FUNDS PAGINATION COMPONENT
// ============================================================================

import React from 'react';
import { TablePagination } from '@mui/material';
import { FundsPaginationProps } from '../types/funds-tab.types';

export const FundsPagination: React.FC<FundsPaginationProps> = ({
  pagination,
  onPageChange,
  onRowsPerPageChange,
}) => {
  return (
    <TablePagination
      component="div"
      count={pagination.total_funds}
      page={pagination.current_page - 1}
      onPageChange={onPageChange}
      rowsPerPage={pagination.per_page}
      onRowsPerPageChange={onRowsPerPageChange}
      rowsPerPageOptions={[10, 25, 50, 100]}
      labelDisplayedRows={({ from, to, count }) =>
        `${from}-${to} of ${count !== -1 ? count : `more than ${to}`}`
      }
    />
  );
};
