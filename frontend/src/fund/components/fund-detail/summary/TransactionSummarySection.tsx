import React from 'react';
import {
  Typography,
  Paper,
  Box
} from '@mui/material';
import { Receipt } from '@mui/icons-material';
import { Fund, FundTrackingType } from '@/fund/types';
// formatCurrency is supplied via props

interface SectionProps {
  fund: Fund;
  formatCurrency: (amount: number | null, currency?: string) => string;
  formatDate: (dateString: string | null) => string;
  events?: any[];
  isLoading?: boolean; // ENTERPRISE: Individual loading state for this section
}

/**
 * Transaction Summary Section - Summary of all transaction types
 */
const TransactionSummarySection: React.FC<SectionProps> = ({ fund, formatCurrency, formatDate, events, isLoading = false }) => {
  // NOTE: Total fields (total_capital_calls, total_unit_purchases, etc.) are not available in Fund type
  // These would need to be calculated from events or fetched separately
  // For now, we'll hide this section until totals can be calculated from events
  // TODO: Calculate totals from events array if provided
  if (!events || events.length === 0) {
    return null;
  }

  // Calculate totals from events if provided
  const calculateTotals = () => {
    const totals = {
      total_capital_calls: 0,
      total_capital_returns: 0,
      total_unit_purchases: 0,
      total_unit_sales: 0,
      total_distributions: 0,
      total_tax_payments: 0,
      total_daily_interest_charges: 0,
    };

    if (!events) return totals;
    
    events.forEach((event: any) => {
      if (event.event_type === 'CAPITAL_CALL' && event.amount) {
        totals.total_capital_calls += event.amount;
      } else if (event.event_type === 'RETURN_OF_CAPITAL' && event.amount) {
        totals.total_capital_returns += event.amount;
      } else if (event.event_type === 'UNIT_PURCHASE' && event.amount) {
        totals.total_unit_purchases += event.amount;
      } else if (event.event_type === 'UNIT_SALE' && event.amount) {
        totals.total_unit_sales += event.amount;
      } else if (event.event_type === 'DISTRIBUTION' && event.amount) {
        totals.total_distributions += event.amount;
      } else if (event.event_type === 'TAX_PAYMENT' && event.amount) {
        totals.total_tax_payments += event.amount;
      } else if (event.event_type === 'DAILY_RISK_FREE_INTEREST_CHARGE' && event.amount) {
        totals.total_daily_interest_charges += event.amount;
      }
    });

    return totals;
  };

  const totals = calculateTotals();

  const transactionData = [
    // Capital transactions (cost-based funds)
    ...(fund.tracking_type === FundTrackingType.COST_BASED ? [
      { type: 'Capital Calls', amount: totals.total_capital_calls || null, color: 'error.main', icon: '📤' },
      { type: 'Returns of Capital', amount: totals.total_capital_returns || null, color: 'success.main', icon: '📥' }
    ] : []),
    // Unit transactions (NAV-based funds)
    ...(fund.tracking_type === FundTrackingType.NAV_BASED ? [
      { type: 'Unit Purchases', amount: totals.total_unit_purchases || null, color: 'primary.main', icon: '📈' },
      { type: 'Unit Sales', amount: totals.total_unit_sales || null, color: 'secondary.main', icon: '📉' }
    ] : []),
    // Income transactions (all funds)
    { type: 'Distributions', amount: totals.total_distributions || null, color: 'info.main', icon: '💰' },
    { type: 'Tax Payments', amount: totals.total_tax_payments || null, color: 'warning.main', icon: '🏛️' },
    { type: 'Total Cost of Capital Interest', amount: totals.total_daily_interest_charges || null, color: 'info.main', icon: '📊' }
  ].filter(item => item.amount !== null && item.amount !== 0);

  if (transactionData.length === 0) {
    return null;
  }

  return (
    <Paper sx={{ 
      p: 0.75, 
      mb: 1, 
      borderRadius: 2,
      // Phase 4: Enhanced visual effects
      boxShadow: '0 2px 8px rgba(0,0,0,0.08), 0 1px 3px rgba(0,0,0,0.12)',
      transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
      '&:hover': {
        boxShadow: '0 4px 16px rgba(0,0,0,0.12), 0 2px 6px rgba(0,0,0,0.16)',
        transform: 'translateY(-1px)'
      }
    }}>
      <Box display="flex" alignItems="center" mb={0.5}>
        <Receipt color="secondary" sx={{ mr: 0.5, fontSize: 16 }} />
        <Typography variant="h6" sx={{ fontSize: 16 }}>Transaction Summary</Typography>
      </Box>
      
      {/* Phase 3B: Enhanced card layout with consistent styling */}
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
        {transactionData.map((item, index) => (
          <Box 
            key={index}
            sx={{ 
              display: 'flex', 
              justifyContent: 'space-between', 
              alignItems: 'center',
              p: 0.5,
              borderRadius: 1,
              backgroundColor: 'transparent',
              border: '1px solid',
              borderColor: 'divider',
              // Very obvious hover effects for consistent user experience
              transition: 'all 0.2s ease-in-out',
              cursor: 'pointer',
              '&:hover': {
                backgroundColor: 'primary.dark',
                borderColor: 'primary.main',
                borderWidth: '2px',
                transform: 'translateX(4px)',
                boxShadow: '0 4px 12px rgba(0,0,0,0.2)'
              }
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
              <span style={{ fontSize: '12px' }}>{item.icon}</span>
              <Typography variant="body2" color="text.secondary" sx={{ fontSize: 11 }}>
                {item.type}
            </Typography>
          </Box>
            <Typography variant="body2" sx={{ color: item.color, fontSize: 12, fontWeight: 600 }}>
              {formatCurrency(item.amount, fund.currency)}
            </Typography>
          </Box>
        ))}
          </Box>
    </Paper>
  );
};

export default TransactionSummarySection;

