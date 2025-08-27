import React from 'react';
import {
  Typography,
  Paper,
  Box
} from '@mui/material';
import { TrendingUp } from '@mui/icons-material';
import { ExtendedFund } from '../../../../types/api';

interface SectionProps {
  fund: ExtendedFund;
  formatCurrency: (amount: number | null, currency?: string) => string;
  formatDate: (dateString: string | null) => string;
  events?: any[];
}

/**
 * Expected Performance Section - Planned/expected fund metrics
 */
const ExpectedPerformanceSection: React.FC<SectionProps> = ({ fund, formatCurrency, formatDate }) => {
  // Phase 3.3: Enhanced data organization for performance metrics
  const performanceMetrics = [
    {
      label: 'Expected IRR',
      value: fund.expected_irr,
      unit: '%',
      color: 'success.main',
      icon: '📈',
      priority: 1
    },
    {
      label: 'Expected Duration',
      value: fund.expected_duration_months,
      unit: ' months',
      color: 'success.main',
      icon: '⏱️',
      priority: 2
    }
  ].filter(metric => metric.value !== null && metric.value !== undefined);

  // Only show if metrics exist
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
        <TrendingUp color="success" sx={{ mr: 0.5, fontSize: 16 }} />
        <Typography variant="h6" sx={{ fontSize: 16 }}>Expected Performance</Typography>
      </Box>
      
      {/* Phase 3.3: Enhanced card layout with better density */}
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
              backgroundColor: 'success.50',
              border: '1px solid',
              borderColor: 'grey.200',
              // Very obvious hover effects for consistent user experience
              transition: 'all 0.2s ease-in-out',
              cursor: 'pointer',
              '&:hover': {
                backgroundColor: 'success.300',
                borderColor: 'success.main',
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
              {metric.value}{metric.unit}
            </Typography>
          </Box>
        ))}
      </Box>
    </Paper>
  );
};

export default ExpectedPerformanceSection; 