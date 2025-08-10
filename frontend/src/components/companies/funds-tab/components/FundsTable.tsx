// ============================================================================
// FUNDS TABLE COMPONENT
// ============================================================================

import React from 'react';
import {
  Box,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
} from '@mui/material';
import { UnfoldMore } from '@mui/icons-material';
import { FundsTableProps } from '../types/funds-tab.types';
import { FundRow } from './FundRow';

export const FundsTable: React.FC<FundsTableProps> = ({
  data,
  onSort,
  sortField,
  sortDirection,
}) => {
  const getSortIcon = (field: string) => {
    if (sortField !== field) {
      return <UnfoldMore />;
    }
    return sortDirection === 'asc' ? 'expand_less' : 'expand_more';
  };

  const renderSortableHeader = (field: string, label: string, width?: string) => (
    <TableCell 
      style={{ width, cursor: 'pointer', userSelect: 'none' }}
      onClick={() => onSort(field)}
    >
      <Box display="flex" alignItems="center" gap={1}>
        {label}
        <IconButton size="small" sx={{ p: 0 }}>
          {getSortIcon(field)}
        </IconButton>
      </Box>
    </TableCell>
  );

  return (
    <TableContainer component={Paper} variant="outlined">
      <Table>
        <TableHead>
          <TableRow>
            {/* Fund Details Section */}
            {renderSortableHeader('name', 'Fund Name', '200px')}
            <TableCell>Type</TableCell>
            <TableCell>Tracking</TableCell>
            {renderSortableHeader('status', 'Status', '100px')}
            
            {/* Estimated Return Section */}
            {renderSortableHeader('expected_irr', 'Expected IRR', '120px')}
            {renderSortableHeader('duration_months', 'Duration (Months)', '140px')}
            
            {/* Dates Section */}
            {renderSortableHeader('start_date', 'Start Date', '120px')}
            {renderSortableHeader('end_date', 'End Date', '120px')}
            {renderSortableHeader('days_since_last_activity', 'Days Since Activity', '150px')}
            
            {/* Equity Section */}
            {renderSortableHeader('commitment', 'Commitment', '120px')}
            {renderSortableHeader('invested_capital', 'Invested Capital', '130px')}
            {renderSortableHeader('current_value', 'Current Value', '130px')}
            {renderSortableHeader('current_equity_balance', 'Current Balance', '140px')}
            
            {/* Distributions Section */}
            {renderSortableHeader('distribution_count', 'Distributions', '120px')}
            {renderSortableHeader('total_distribution_amount', 'Total Amount', '130px')}
            
            {/* Returns Section */}
            {renderSortableHeader('completed_irr', 'Completed IRR', '130px')}
            {renderSortableHeader('performance_vs_expected', 'Performance vs Expected', '160px')}
            
            {/* Performance Section */}
            {renderSortableHeader('unrealized_gains_losses', 'Unrealized G/L', '140px')}
            {renderSortableHeader('realized_gains_losses', 'Realized G/L', '130px')}
            {renderSortableHeader('total_profit_loss', 'Total P/L', '120px')}
          </TableRow>
        </TableHead>
        <TableBody>
          {data.funds.map((fund) => (
            <FundRow key={fund.id} fund={fund} />
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
};
