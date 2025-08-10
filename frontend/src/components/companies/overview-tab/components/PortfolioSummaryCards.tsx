import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
} from '@mui/material';
import {
  AccountBalance,
  TrendingUp,
  Business,
} from '@mui/icons-material';
import { formatCurrency } from '../../../../utils/formatters';
import { PortfolioSummaryCardsProps } from '../types/overview-tab.types';

export const PortfolioSummaryCards: React.FC<PortfolioSummaryCardsProps> = ({ portfolioSummary }) => {
  // Calculate total funds from available breakdown
  const totalFunds = portfolioSummary.active_funds_count + portfolioSummary.completed_funds_count + 
    (portfolioSummary.fund_status_breakdown.suspended || 0);

  return (
    <Box data-testid="portfolio-summary-cards" mb={3}>
      <Typography variant="h6" gutterBottom>
        Portfolio Summary
      </Typography>
      {/* Total Committed Capital */}
      <Card>
        <CardContent>
          <Box display="flex" alignItems="center" mb={2}>
            <AccountBalance sx={{ mr: 1, color: 'primary.main' }} />
            <Typography variant="h6">Total Committed</Typography>
          </Box>
          <Typography variant="h4" color="primary.main" gutterBottom>
            {formatCurrency(portfolioSummary.total_committed_capital)}
          </Typography>
          <Typography variant="body2" color="textSecondary">
            Across {totalFunds} funds
          </Typography>
        </CardContent>
      </Card>

      {/* Current Value */}
      <Card>
        <CardContent>
          <Box display="flex" alignItems="center" mb={2}>
            <TrendingUp sx={{ mr: 1, color: 'success.main' }} />
            <Typography variant="h6">Current Value</Typography>
          </Box>
          <Typography variant="h4" color="success.main" gutterBottom>
            {formatCurrency(portfolioSummary.total_current_value)}
          </Typography>
          <Typography variant="body2" color="textSecondary">
            Total portfolio value
          </Typography>
        </CardContent>
      </Card>

      {/* Active Funds */}
      <Card>
        <CardContent>
          <Box display="flex" alignItems="center" mb={2}>
            <Business sx={{ mr: 1, color: 'info.main' }} />
            <Typography variant="h6">Active Funds</Typography>
          </Box>
          <Typography variant="h4" color="info.main" gutterBottom>
            {portfolioSummary.active_funds_count}
          </Typography>
          <Typography variant="body2" color="textSecondary">
            Currently active investments
          </Typography>
        </CardContent>
      </Card>
    </Box>
  );
};
