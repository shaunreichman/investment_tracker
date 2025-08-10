import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Chip,
  Divider,
} from '@mui/material';
import {
  AccountBalance,
  TrendingUp,
  Business,
  Event,
  Schedule,
  AttachMoney,
} from '@mui/icons-material';
import { CompanyOverviewResponse } from '../../types/api';
import { formatCurrency, formatPercentage } from '../../utils/formatters';

// ============================================================================
// TYPES
// ============================================================================

interface OverviewTabProps {
  data: CompanyOverviewResponse;
  loading: boolean;
}

// ============================================================================
// COMPONENT
// ============================================================================

export const OverviewTab: React.FC<OverviewTabProps> = ({ data, loading }) => {
  if (loading) {
    return (
      <Box p={3}>
        <Typography>Loading overview...</Typography>
      </Box>
    );
  }

  const { portfolio_summary, performance_summary, last_activity } = data;
  
  // Calculate total funds from available breakdown
  const totalFunds = portfolio_summary.active_funds_count + portfolio_summary.completed_funds_count + 
    (portfolio_summary.fund_status_breakdown.suspended || 0);

  return (
    <Box p={3}>
      {/* Portfolio Summary Cards */}
      <Box 
        display="grid" 
        gap={3} 
        sx={{ 
          gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr', md: '1fr 1fr 1fr' },
          mb: 4 
        }}
      >
        {/* Total Committed Capital */}
        <Card>
          <CardContent>
            <Box display="flex" alignItems="center" mb={2}>
              <AccountBalance sx={{ mr: 1, color: 'primary.main' }} />
              <Typography variant="h6">Total Committed</Typography>
            </Box>
            <Typography variant="h4" color="primary.main" gutterBottom>
              {formatCurrency(portfolio_summary.total_committed_capital)}
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
              {formatCurrency(portfolio_summary.total_current_value)}
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
              {portfolio_summary.active_funds_count}
            </Typography>
            <Typography variant="body2" color="textSecondary">
              of {totalFunds} total funds
            </Typography>
          </CardContent>
        </Card>
      </Box>

      {/* Fund Status Breakdown */}
      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Fund Status Breakdown
          </Typography>
          <Box 
            display="grid" 
            gap={2} 
            sx={{ 
              gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr', md: '1fr 1fr 1fr' }
            }}
          >
            {Object.entries(portfolio_summary.fund_status_breakdown).map(([status, count]) => (
              <Box key={status} display="flex" alignItems="center" justifyContent="space-between">
                <Box display="flex" alignItems="center">
                  <Chip 
                    label={status} 
                    size="small" 
                    color={status === 'active' ? 'success' : 'default'}
                    sx={{ mr: 1 }}
                  />
                  <Typography variant="body2">{count} funds</Typography>
                </Box>
              </Box>
            ))}
          </Box>
        </CardContent>
      </Card>

      {/* Performance Summary - Only show when there are completed funds */}
      {portfolio_summary.completed_funds_count > 0 && performance_summary.average_completed_irr !== null && (
        <Card sx={{ mb: 4 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Performance Summary
            </Typography>
            <Box 
              display="grid" 
              gap={3} 
              sx={{ 
                gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr', md: '1fr 1fr 1fr' }
              }}
            >
              <Box textAlign="center">
                <Typography variant="subtitle2" color="textSecondary" gutterBottom>
                  Average Completed IRR
                </Typography>
                <Typography variant="h4" color="success.main" gutterBottom>
                  {formatPercentage(performance_summary.average_completed_irr)}
                </Typography>
              </Box>
              <Box textAlign="center">
                <Typography variant="subtitle2" color="textSecondary" gutterBottom>
                  Total Realized Gains
                </Typography>
                <Typography variant="h4" color="success.main" gutterBottom>
                  {formatCurrency(performance_summary.total_realized_gains || 0)}
                </Typography>
              </Box>
              <Box textAlign="center">
                <Typography variant="subtitle2" color="textSecondary" gutterBottom>
                  Total Realized Losses
                </Typography>
                <Typography variant="h4" color="error.main" gutterBottom>
                  {formatCurrency(performance_summary.total_realized_losses || 0)}
                </Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>
      )}

      {/* Last Activity */}
      {last_activity.last_activity_date && (
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Last Activity
            </Typography>
            <Box display="flex" alignItems="center" gap={2}>
              <Schedule color="action" />
              <Box>
                <Typography variant="body1">
                  {new Date(last_activity.last_activity_date).toLocaleDateString()}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  {last_activity.days_since_last_activity} days ago
                </Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>
      )}

      {/* Empty State for No Completed Funds */}
      {portfolio_summary.completed_funds_count === 0 && (
        <Card>
          <CardContent>
            <Box textAlign="center" py={4}>
              <TrendingUp sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
              <Typography variant="h6" color="textSecondary" gutterBottom>
                No Performance Data Yet
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Performance metrics will appear once you have completed funds.
              </Typography>
            </Box>
          </CardContent>
        </Card>
      )}
    </Box>
  );
};
