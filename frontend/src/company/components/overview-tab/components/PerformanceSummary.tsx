import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Divider,
} from '@mui/material';
import { TrendingUp } from '@mui/icons-material';
import { formatCurrency, formatPercentage } from '@/shared/utils/formatters';
import { PerformanceSummaryProps } from '../types/overview-tab.types';

export const PerformanceSummary: React.FC<PerformanceSummaryProps> = ({ performanceSummary }) => {
  // Only show performance summary if there are completed funds with data
  if (!performanceSummary.average_completed_irr && !performanceSummary.total_realized_gains) {
    return null;
  }

  return (
    <Box data-testid="performance-summary">
      <Typography variant="h6" gutterBottom>
        Performance Summary
      </Typography>
      <Card>
        <CardContent>
          <Box display="flex" alignItems="center" mb={3}>
            <TrendingUp sx={{ mr: 2, color: 'success.main', fontSize: 32 }} />
            <Typography variant="h5">Performance Summary</Typography>
          </Box>
          
          <Divider sx={{ mb: 3 }} />
          
          <Box 
            display="grid" 
            gap={3} 
            sx={{ 
              gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr' }
            }}
          >
            {/* Completed Funds Count */}
            <Box>
              <Typography variant="h6" gutterBottom>
                Completed Funds
              </Typography>
              <Typography variant="h4" color="primary.main">
                {performanceSummary.total_realized_gains ? 'Yes' : 'No'}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Successfully exited investments
              </Typography>
            </Box>

            {/* Average IRR */}
            <Box>
              <Typography variant="h6" gutterBottom>
                Average IRR
              </Typography>
              <Typography variant="h4" color="success.main">
                {performanceSummary.average_completed_irr ? formatPercentage(performanceSummary.average_completed_irr) : 'N/A'}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Across all completed funds
              </Typography>
            </Box>

            {/* Total Realized Gains */}
            <Box>
              <Typography variant="h6" gutterBottom>
                Total Realized Gains
              </Typography>
              <Typography variant="h4" color="success.main">
                {formatCurrency(performanceSummary.total_realized_gains)}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                From completed investments
              </Typography>
            </Box>

            {/* Average Duration */}
            <Box>
              <Typography variant="h6" gutterBottom>
                Average Duration
              </Typography>
              <Typography variant="h4" color="info.main">
                N/A
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Time to completion
              </Typography>
            </Box>
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
};
