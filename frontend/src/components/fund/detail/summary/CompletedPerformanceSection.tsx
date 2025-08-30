import React from 'react';
import {
  Typography,
  Paper,
  Box
} from '@mui/material';
import { Assessment } from '@mui/icons-material';
import { ExtendedFund, FundStatus } from '../../../../types/api';

interface SectionProps {
  fund: ExtendedFund;
  formatCurrency: (amount: number | null, currency?: string) => string;
  formatDate: (dateString: string | null) => string;
  events?: any[];
}

/**
 * Completed Performance Section - Historical performance for finished funds
 */
const CompletedPerformanceSection: React.FC<SectionProps> = ({ fund, formatCurrency, formatDate }) => {
  // Only show if fund is completed (not active)
  if (fund.status === FundStatus.ACTIVE) {
    return null;
  }

  // Phase 3B: Enhanced data organization for completed performance
  const performanceMetrics = [
    {
      label: 'IRR',
      value: fund.completed_irr,
      unit: '%',
      color: 'info.main',
      icon: '📊',
      priority: 1
    },
    {
      label: 'Net-tax IRR',
      value: fund.completed_after_tax_irr,
      unit: '%',
      color: 'info.main',
      icon: '💰',
      priority: 2
    },
    {
      label: 'Gross IRR',
      value: fund.completed_real_irr,
      unit: '%',
      color: 'info.main',
      icon: '📈',
      priority: 3
    },
    ...(fund.actual_duration_months ? [{
      label: 'Actual Duration',
      value: fund.actual_duration_months,
      unit: ' months',
      color: 'info.main',
      icon: '⏱️',
      priority: 4
    }] : [])
  ].filter(metric => metric.value !== null && metric.value !== undefined);

  if (performanceMetrics.length === 0) {
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
        <Assessment color="info" sx={{ mr: 0.5, fontSize: 16 }} />
        <Typography variant="h6" sx={{ fontSize: 16 }}>Completed Performance</Typography>
      </Box>
      
      {/* Phase 3B: Enhanced card layout with consistent styling */}
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
        {performanceMetrics.map((metric, index) => (
          <Box 
            key={index}
            sx={{ 
              display: 'flex', 
              justifyContent: 'space-between', 
              alignItems: 'center',
              p: 0.5,
              borderRadius: 1,
              backgroundColor: 'info.dark',
              border: '1px solid',
              borderColor: 'divider',
              // Very obvious hover effects for consistent user experience
              transition: 'all 0.2s ease-in-out',
              cursor: 'pointer',
              '&:hover': {
                backgroundColor: 'info.main',
                borderColor: 'info.main',
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
                fontWeight: 600
              }}
            >
              {metric.label === 'Actual Duration' 
                ? `${metric.value}${metric.unit}`
                : `${metric.value ? (metric.value * 100).toFixed(2) : '0.00'}${metric.unit}`}
            </Typography>
          </Box>
        ))}
      </Box>
    </Paper>
  );
};

export default CompletedPerformanceSection; 