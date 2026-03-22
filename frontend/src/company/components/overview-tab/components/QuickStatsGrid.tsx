import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Chip,
} from '@mui/material';
import {
  Event,
  Schedule,
  AttachMoney,
} from '@mui/icons-material';
import { QuickStatsGridProps } from '../types/overview-tab.types';

export const QuickStatsGrid: React.FC<QuickStatsGridProps> = ({ portfolioSummary, lastActivity }) => {
  return (
    <Box data-testid="quick-stats-grid" mb={3}>
      <Typography variant="h6" gutterBottom>
        Quick Stats
      </Typography>
      {/* Fund Counts */}
      <Card>
        <CardContent>
          <Box display="flex" alignItems="center" mb={2}>
            <Event sx={{ mr: 1, color: 'text.secondary' }} />
            <Typography variant="h6">Fund Breakdown</Typography>
          </Box>
          <Box display="flex" flexDirection="column" gap={1}>
            <Box display="flex" justifyContent="space-between">
              <Typography variant="body2">Active:</Typography>
              <Chip 
                label={portfolioSummary.active_funds_count} 
                color="success" 
                size="small" 
                variant="outlined"
              />
            </Box>
            <Box display="flex" justifyContent="space-between">
              <Typography variant="body2">Completed:</Typography>
              <Chip 
                label={portfolioSummary.completed_funds_count} 
                color="primary" 
                size="small" 
                variant="outlined"
              />
            </Box>
            {portfolioSummary.fund_status_breakdown?.suspended_funds_count > 0 && (
              <Box display="flex" justifyContent="space-between">
                <Typography variant="body2">Suspended:</Typography>
                <Chip 
                  label={portfolioSummary.fund_status_breakdown.suspended_funds_count} 
                  color="warning" 
                  size="small" 
                  variant="outlined"
                />
              </Box>
            )}
          </Box>
        </CardContent>
      </Card>

      {/* Last Activity */}
      <Card>
        <CardContent>
          <Box display="flex" alignItems="center" mb={2}>
            <Schedule sx={{ mr: 1, color: 'text.secondary' }} />
            <Typography variant="h6">Last Activity</Typography>
          </Box>
          <Typography variant="h6" gutterBottom>
            {lastActivity?.last_activity_date ? new Date(lastActivity.last_activity_date).toLocaleDateString() : 'No activity'}
          </Typography>
          <Typography variant="body2" color="textSecondary">
            {lastActivity?.days_since_last_activity ? `${lastActivity.days_since_last_activity} days ago` : 'No recent events'}
          </Typography>
        </CardContent>
      </Card>

      {/* Currency Breakdown */}
      <Card>
        <CardContent>
          <Box display="flex" alignItems="center" mb={2}>
            <AttachMoney sx={{ mr: 1, color: 'text.secondary' }} />
            <Typography variant="h6">Currency Mix</Typography>
          </Box>
          <Box display="flex" flexDirection="column" gap={1}>
            <Typography variant="body2" color="textSecondary">
              Currency breakdown not available
            </Typography>
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
};
