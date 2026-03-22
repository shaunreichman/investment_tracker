// ============================================================================
// FUND ROW COMPONENT
// ============================================================================

import React from 'react';
import {
  TableRow,
  TableCell,
  Typography,
  Link,
  Button,
} from '@mui/material';
import { Delete as DeleteIcon } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { StatusChip, TrackingTypeChip } from '@/shared/ui';
import { formatCurrency, formatPercentage } from '@/shared/utils/formatters';
import { getFundInvestmentTypeLabel } from '@/fund/utils/labels';
import { FundRowProps } from '../types/funds-tab.types';

export const FundRow: React.FC<FundRowProps> = ({ fund, onDeleteFund }) => {
  const navigate = useNavigate();

  const handleDeleteClick = () => {
    if (onDeleteFund) {
      onDeleteFund(fund.id, fund.name);
    }
  };

  return (
    <TableRow hover>
      {/* Fund Details */}
      <TableCell>
        <Link
          component="button"
          variant="subtitle2"
          onClick={() => navigate(`/funds/${fund.id}`)}
          sx={{ textDecoration: 'none', cursor: 'pointer' }}
        >
          {fund.name}
        </Link>
        {fund.description && (
          <Typography variant="caption" color="textSecondary" display="block">
            {fund.description}
          </Typography>
        )}
      </TableCell>
      <TableCell>{getFundInvestmentTypeLabel(fund.fund_investment_type)}</TableCell>
      <TableCell>
        <TrackingTypeChip trackingType={fund.tracking_type} />
      </TableCell>
      <TableCell>
        <StatusChip status={fund.status} />
      </TableCell>
      
      {/* Estimated Return */}
      <TableCell align="right">
        {fund.expected_irr !== null
          ? formatPercentage(fund.expected_irr)
          : '-'}
      </TableCell>
      <TableCell align="right">
        {fund.expected_duration_months !== null
          ? fund.expected_duration_months
          : '-'}
      </TableCell>
      
      {/* Dates */}
      <TableCell>
        {fund.start_date ? new Date(fund.start_date).toLocaleDateString() : '-'}
      </TableCell>
      <TableCell>
        {fund.end_date
          ? new Date(fund.end_date).toLocaleDateString()
          : '-'}
      </TableCell>
      <TableCell align="right">
        {fund.current_duration || '-'}
      </TableCell>
      
      {/* Equity */}
      <TableCell align="right">
        {formatCurrency(fund.commitment_amount || 0)}
      </TableCell>
      <TableCell align="right">
        {formatCurrency(fund.total_cost_basis || 0)}
      </TableCell>
      <TableCell align="right">
        {formatCurrency(fund.current_nav_total || 0)}
      </TableCell>
      <TableCell align="right">
        {formatCurrency(fund.current_equity_balance || 0)}
      </TableCell>
      
      {/* Completed IRRs */}
      <TableCell align="right">
        {fund.completed_irr_gross !== null
          ? formatPercentage(fund.completed_irr_gross)
          : '-'}
      </TableCell>
      <TableCell align="right">
        {fund.completed_irr_after_tax !== null
          ? formatPercentage(fund.completed_irr_after_tax)
          : '-'}
      </TableCell>
      
      {/* Additional Info */}
      <TableCell align="right">
        {fund.average_equity_balance > 0 ? formatCurrency(fund.average_equity_balance) : '-'}
      </TableCell>
      <TableCell align="right">
        {fund.current_units || '-'}
      </TableCell>
      <TableCell align="right">
        {fund.current_unit_price ? formatCurrency(fund.current_unit_price) : '-'}
      </TableCell>
      
      {/* Actions */}
      <TableCell align="right">
        {onDeleteFund && (
          <Button
            size="small"
            variant="outlined"
            color="error"
            startIcon={<DeleteIcon />}
            onClick={handleDeleteClick}
            sx={{
              minWidth: 'auto',
              px: 1,
              py: 0.5,
              fontSize: '12px'
            }}
          >
            Delete
          </Button>
        )}
      </TableCell>
    </TableRow>
  );
};

