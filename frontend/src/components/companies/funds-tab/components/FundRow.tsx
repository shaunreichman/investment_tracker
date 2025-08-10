// ============================================================================
// FUND ROW COMPONENT
// ============================================================================

import React from 'react';
import {
  TableRow,
  TableCell,
  Typography,
  Link,
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { StatusChip } from '../../../ui/StatusChip';
import { TrackingTypeChip } from '../../../ui/TrackingTypeChip';
import { formatCurrency, formatPercentage } from '../../../../utils/formatters';
import { FundRowProps } from '../types/funds-tab.types';

export const FundRow: React.FC<FundRowProps> = ({ fund }) => {
  const navigate = useNavigate();

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
      <TableCell>{fund.fund_type}</TableCell>
      <TableCell>
        <TrackingTypeChip trackingType={fund.tracking_type} />
      </TableCell>
      <TableCell>
        <StatusChip status={fund.status} />
      </TableCell>
      
      {/* Estimated Return */}
      <TableCell align="right">
        {fund.estimated_return.expected_irr !== null
          ? formatPercentage(fund.estimated_return.expected_irr)
          : '-'}
      </TableCell>
      <TableCell align="right">
        {fund.estimated_return.duration_months !== null
          ? fund.estimated_return.duration_months
          : '-'}
      </TableCell>
      
      {/* Dates */}
      <TableCell>
        {new Date(fund.fund_details.start_date).toLocaleDateString()}
      </TableCell>
      <TableCell>
        {fund.fund_details.end_date
          ? new Date(fund.fund_details.end_date).toLocaleDateString()
          : '-'}
      </TableCell>
      <TableCell align="right">
        {fund.fund_details.days_since_last_activity}
      </TableCell>
      
      {/* Equity */}
      <TableCell align="right">
        {formatCurrency(fund.equity.commitment)}
      </TableCell>
      <TableCell align="right">
        {formatCurrency(fund.equity.invested_capital)}
      </TableCell>
      <TableCell align="right">
        {formatCurrency(fund.equity.current_value)}
      </TableCell>
      <TableCell align="right">
        {formatCurrency(fund.equity.current_equity_balance)}
      </TableCell>
      
      {/* Distributions */}
      <TableCell align="right">
        {fund.distributions.distribution_count}
      </TableCell>
      <TableCell align="right">
        {formatCurrency(fund.distributions.total_distribution_amount)}
      </TableCell>
      
      {/* Returns */}
      <TableCell align="right">
        {fund.returns.completed_irr !== null
          ? formatPercentage(fund.returns.completed_irr)
          : '-'}
      </TableCell>
      <TableCell align="right">
        {fund.returns.performance_vs_expected !== null
          ? formatPercentage(fund.returns.performance_vs_expected)
          : '-'}
      </TableCell>
      
      {/* Performance */}
      <TableCell align="right">
        <Typography
          color={fund.performance.unrealized_gains_losses >= 0 ? 'success.main' : 'error.main'}
        >
          {formatCurrency(fund.performance.unrealized_gains_losses)}
        </Typography>
      </TableCell>
      <TableCell align="right">
        <Typography
          color={fund.performance.realized_gains_losses >= 0 ? 'success.main' : 'error.main'}
        >
          {formatCurrency(fund.performance.realized_gains_losses)}
        </Typography>
      </TableCell>
      <TableCell align="right">
        <Typography
          color={fund.performance.total_profit_loss >= 0 ? 'success.main' : 'error.main'}
          fontWeight="bold"
        >
          {formatCurrency(fund.performance.total_profit_loss)}
        </Typography>
      </TableCell>
    </TableRow>
  );
};
