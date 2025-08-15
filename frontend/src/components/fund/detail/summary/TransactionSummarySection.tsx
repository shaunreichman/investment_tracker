import React from 'react';
import {
  Typography,
  Paper,
  Box
} from '@mui/material';
import { Receipt } from '@mui/icons-material';
import { ExtendedFund } from '../../../../types/api';
// formatCurrency is supplied via props

interface SectionProps {
  fund: ExtendedFund;
  formatCurrency: (amount: number | null, currency?: string) => string;
  formatDate: (dateString: string | null) => string;
  events?: any[];
}

/**
 * Transaction Summary Section - Summary of all transaction types
 */
const TransactionSummarySection: React.FC<SectionProps> = ({ fund, formatCurrency, formatDate }) => {
  const transactionData = [
    // Capital transactions (cost-based funds)
    ...(fund.tracking_type === 'cost_based' ? [
      { type: 'Capital Calls', amount: fund.total_capital_calls ?? null, color: 'error.main', icon: '📤' },
      { type: 'Returns of Capital', amount: fund.total_capital_returns ?? null, color: 'success.main', icon: '📥' }
    ] : []),
    // Unit transactions (NAV-based funds)
    ...(fund.tracking_type === 'nav_based' ? [
      { type: 'Unit Purchases', amount: fund.total_unit_purchases ?? null, color: 'primary.main', icon: '📈' },
      { type: 'Unit Sales', amount: fund.total_unit_sales ?? null, color: 'secondary.main', icon: '📉' }
    ] : []),
    // Income transactions (all funds)
    { type: 'Distributions', amount: fund.total_distributions ?? null, color: 'info.main', icon: '💰' },
    { type: 'Tax Payments', amount: fund.total_tax_payments ?? null, color: 'warning.main', icon: '🏛️' },
    { type: 'Total Cost of Capital Interest', amount: fund.total_daily_interest_charges ?? null, color: 'info.main', icon: '📊' }
  ].filter(item => item.amount !== null);

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
              borderColor: 'grey.200',
              // Very obvious hover effects for consistent user experience
              transition: 'all 0.2s ease-in-out',
              cursor: 'pointer',
              '&:hover': {
                backgroundColor: 'primary.100',
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