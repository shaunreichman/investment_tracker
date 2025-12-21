import React from 'react';
import {
  Box,
  Stack,
  Typography,
} from '@mui/material';
import {
  AccountBalance,
  TrendingUp,
  Business,
} from '@mui/icons-material';
import { formatCurrency } from '@/shared/utils/formatters';
import { StatCard } from '@/shared/ui/data-display/Card';
import { PortfolioSummaryCardsProps } from '../types/overview-tab.types';

export const PortfolioSummaryCards: React.FC<PortfolioSummaryCardsProps> = ({ portfolioSummary }) => {
  // Calculate total funds from available breakdown with safety checks
  const suspendedCount = portfolioSummary.fund_status_breakdown?.suspended_funds_count || 0;
  const totalFunds = portfolioSummary.active_funds_count + portfolioSummary.completed_funds_count + suspendedCount;

  return (
    <Box data-testid="portfolio-summary-cards" mb={3}>
      <Typography variant="h6" gutterBottom>
        Portfolio Summary
      </Typography>
      <Stack spacing={2}>
        {/* Total Committed Capital */}
        <StatCard
          title="Total Committed"
          value={formatCurrency(portfolioSummary.total_committed_capital)}
          subtitle={`Across ${totalFunds} funds`}
          icon={<AccountBalance />}
          color="primary"
        />

        {/* Current Value */}
        <StatCard
          title="Current Value"
          value={formatCurrency(portfolioSummary.total_current_value)}
          subtitle="Total portfolio value"
          icon={<TrendingUp />}
          color="success"
        />

        {/* Active Funds */}
        <StatCard
          title="Active Funds"
          value={portfolioSummary.active_funds_count}
          subtitle="Currently active investments"
          icon={<Business />}
          color="info"
        />
      </Stack>
    </Box>
  );
};
