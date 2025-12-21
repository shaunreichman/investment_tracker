// ============================================================================
// OVERVIEW TAB COMPONENT (REFACTORED)
// ============================================================================

import React from 'react';
import { Box, Typography } from '@mui/material';
import { OverviewTabProps } from './types/overview-tab.types';
import { PortfolioSummaryCards } from './components/PortfolioSummaryCards';
import { QuickStatsGrid } from './components/QuickStatsGrid';
import { PerformanceSummary } from './components/PerformanceSummary';

export const OverviewTab: React.FC<OverviewTabProps> = ({ data, loading }) => {
  if (loading) {
    return (
      <Box p={3}>
        <Typography>Loading overview...</Typography>
      </Box>
    );
  }

  if (!data) {
    return (
      <Box p={3}>
        <Typography>No overview data available</Typography>
      </Box>
    );
  }

  const { portfolio_summary, performance_summary, last_activity } = data;

  return (
    <Box p={3} className="overview-tab" data-testid="overview-tab">
      <Typography variant="h4" gutterBottom>
        Portfolio Overview
      </Typography>
      
      <PortfolioSummaryCards portfolioSummary={portfolio_summary} />
      <QuickStatsGrid 
        portfolioSummary={portfolio_summary}
        lastActivity={last_activity}
      />
      <PerformanceSummary performanceSummary={performance_summary} />
    </Box>
  );
};
