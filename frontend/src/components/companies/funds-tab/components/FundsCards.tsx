// ============================================================================
// FUNDS CARDS COMPONENT
// ============================================================================

import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Link,
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { StatusChip } from '../../../ui/StatusChip';
import { TrackingTypeChip } from '../../../ui/TrackingTypeChip';
import { formatCurrency, formatPercentage } from '../../../../utils/formatters';
import { FundsCardsProps } from '../types/funds-tab.types';

export const FundsCards: React.FC<FundsCardsProps> = ({ data }) => {
  const navigate = useNavigate();

  return (
    <Box sx={{ p: 2 }}>
      <Box display="grid" gap={2} sx={{ 
        gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr', md: '1fr 1fr 1fr' }
      }}>
        {data.funds.map((fund) => (
          <Card key={fund.id} variant="outlined" sx={{ height: 'fit-content' }}>
            <CardContent>
              {/* Fund Header */}
              <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
                <Box>
                  <Link
                    component="button"
                    variant="h6"
                    onClick={() => navigate(`/funds/${fund.id}`)}
                    sx={{ textDecoration: 'none', cursor: 'pointer', textAlign: 'left' }}
                  >
                    {fund.name}
                  </Link>
                  {fund.description && (
                    <Typography variant="body2" color="textSecondary" mt={1}>
                      {fund.description}
                    </Typography>
                  )}
                </Box>
                <Box display="flex" gap={1}>
                  <StatusChip status={fund.status} />
                  <TrackingTypeChip trackingType={fund.tracking_type} />
                </Box>
              </Box>

              {/* Fund Details Grid */}
              <Box display="grid" gap={2} sx={{ gridTemplateColumns: '1fr 1fr' }}>
                {/* Basic Info */}
                <Box>
                  <Typography variant="caption" color="textSecondary">Type</Typography>
                  <Typography variant="body2">{fund.fund_type}</Typography>
                </Box>
                <Box>
                  <Typography variant="caption" color="textSecondary">Currency</Typography>
                  <Typography variant="body2">{fund.currency}</Typography>
                </Box>
                
                {/* Performance */}
                <Box>
                  <Typography variant="caption" color="textSecondary">Expected IRR</Typography>
                  <Typography variant="body2">
                    {fund.estimated_return.expected_irr !== null
                      ? formatPercentage(fund.estimated_return.expected_irr)
                      : '-'}
                  </Typography>
                </Box>
                <Box>
                  <Typography variant="caption" color="textSecondary">Current Value</Typography>
                  <Typography variant="body2">
                    {formatCurrency(fund.equity.current_value)}
                  </Typography>
                </Box>

                {/* Dates */}
                <Box>
                  <Typography variant="caption" color="textSecondary">Start Date</Typography>
                  <Typography variant="body2">
                    {new Date(fund.fund_details.start_date).toLocaleDateString()}
                  </Typography>
                </Box>
                <Box>
                  <Typography variant="caption" color="textSecondary">Days Since Activity</Typography>
                  <Typography variant="body2">
                    {fund.fund_details.days_since_last_activity}
                  </Typography>
                </Box>
              </Box>

              {/* Performance Summary */}
              <Box mt={2} p={1.5} sx={{ bgcolor: 'background.default', borderRadius: 1 }}>
                <Typography variant="caption" color="textSecondary" display="block" mb={1}>
                  Performance Summary
                </Typography>
                <Box display="flex" justifyContent="space-between">
                  <Box>
                    <Typography variant="caption" color="textSecondary">Total P/L</Typography>
                    <Typography 
                      variant="body2" 
                      color={fund.performance.total_profit_loss >= 0 ? 'success.main' : 'error.main'}
                      fontWeight="bold"
                    >
                      {formatCurrency(fund.performance.total_profit_loss)}
                    </Typography>
                  </Box>
                  <Box>
                    <Typography variant="caption" color="textSecondary">Completed IRR</Typography>
                    <Typography variant="body2">
                      {fund.returns.completed_irr !== null
                        ? formatPercentage(fund.returns.completed_irr)
                        : '-'}
                    </Typography>
                  </Box>
                </Box>
              </Box>
            </CardContent>
          </Card>
        ))}
      </Box>
    </Box>
  );
};
