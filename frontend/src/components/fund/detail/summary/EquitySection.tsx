import React from 'react';
import {
  Typography,
  Paper,
  Box
} from '@mui/material';
import { AccountBalance } from '@mui/icons-material';
import { ExtendedFund, FundType, FundStatus } from '../../../../types/api';
// formatCurrency is supplied via props

interface SectionProps {
  fund: ExtendedFund;
  formatCurrency: (amount: number | null, currency?: string) => string;
  formatDate: (dateString: string | null) => string;
  events?: any[];
}

/**
 * Equity & NAV Summary Section - Current investment position and NAV data
 */
const EquitySection: React.FC<SectionProps> = ({ fund, formatCurrency, formatDate }) => {
  // Enhanced data organization for equity and NAV metrics
  const isActiveNavFund = fund.tracking_type === FundType.NAV_BASED && fund.status === FundStatus.ACTIVE;
  
  const equityMetrics = [
    // Current Balance for cost-based funds, Current Cost of Units only for active NAV-based funds
    ...(fund.tracking_type === FundType.COST_BASED ? [{
      label: 'Current Balance',
      value: fund.current_equity_balance ?? null,
      color: 'primary.main',
      icon: '💰',
      priority: 1
    }] : isActiveNavFund ? [{
      label: 'Current Cost of Units',
      value: fund.current_equity_balance ?? null,
      color: 'primary.main',
      icon: '💰',
      priority: 1
    }] : []),
    {
      label: fund.tracking_type === FundType.NAV_BASED ? 'Average Cost of Units' : 'Average Balance',
      value: fund.average_equity_balance ?? null,
      color: 'primary.main',
      icon: '📊',
      priority: 2
    },
    {
      label: 'Commitment',
      value: fund.commitment_amount ?? null,
      color: 'info.main',
      icon: '📋',
      priority: 3
    },
    // NAV-specific metrics for NAV-based funds (only when active)
    ...(isActiveNavFund ? [
      {
        label: 'Current NAV',
        value: fund.current_unit_price ?? null,
        color: 'success.main',
        icon: '📊',
        priority: 4,
        formatValue: (value: number | null) => value ? formatCurrency(value, fund.currency) : 'N/A'
      },
      {
        label: 'Units Owned',
        value: fund.current_units ?? null,
        color: 'info.main',
        icon: '📈',
        priority: 5,
        formatValue: (value: number | null) => value ? `${value.toLocaleString()} units` : 'N/A'
      },
      {
        label: 'NAV Market Value',
        value: fund.current_nav_total ?? null,
        color: 'success.main',
        icon: '💰',
        priority: 6,
        formatValue: (value: number | null) => value ? formatCurrency(value, fund.currency) : 'N/A'
      }
    ] : [])
  ].filter(metric => metric.value !== null);

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
        <AccountBalance color="primary" sx={{ mr: 0.5, fontSize: 16 }} />
        <Typography variant="h6" sx={{ fontSize: 16 }}>
          {fund.tracking_type === FundType.NAV_BASED ? 'Equity & NAV Summary' : 'Equity Position'}
        </Typography>
      </Box>
      
      {/* Phase 3B: Enhanced card layout with consistent styling */}
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
        {equityMetrics.map((metric, index) => (
          <Box 
            key={index}
            sx={{ 
              display: 'flex', 
              justifyContent: 'space-between', 
              alignItems: 'center',
              p: 0.5,
              borderRadius: 1,
              backgroundColor: index === 0 ? 'primary.dark' : 'transparent',
              border: '1px solid',
              borderColor: 'divider',
              // Very obvious hover effects for consistent user experience
              transition: 'all 0.2s ease-in-out',
              cursor: 'pointer',
              '&:hover': {
                backgroundColor: index === 0 ? 'primary.main' : 'primary.dark',
                borderColor: 'primary.main',
                borderWidth: '2px',
                transform: 'translateX(4px)',
                boxShadow: '0 4px 12px rgba(0,0,0,0.2)'
              }
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
              <span style={{ fontSize: '12px' }}>{metric.icon}</span>
              <Typography variant="body2" color="text.secondary" sx={{ fontSize: 11 }}>
                {metric.label}
          </Typography>
        </Box>
            <Typography 
              variant="body2" 
              sx={{ 
                color: metric.color,
                fontSize: 12,
                fontWeight: index === 0 ? 700 : 600
              }}
            >
              {metric.formatValue ? metric.formatValue(metric.value) : formatCurrency(metric.value, fund.currency)}
          </Typography>
        </Box>
        ))}
      </Box>
    </Paper>
  );
};

export default EquitySection; 