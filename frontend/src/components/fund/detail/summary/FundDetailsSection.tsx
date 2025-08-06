import React from 'react';
import {
  Typography,
  Paper,
  Box,
  Tooltip as MuiTooltip
} from '@mui/material';
import { Info } from '@mui/icons-material';
import { ExtendedFund } from '../../types/api';
import { getStatusInfo } from '../../utils/helpers';

interface SectionProps {
  fund: ExtendedFund;
  formatCurrency: (amount: number | null, currency?: string) => string;
  formatDate: (dateString: string | null) => string;
  events?: any[];
}

/**
 * Fund Details Section - Basic fund information
 */
const FundDetailsSection: React.FC<SectionProps> = ({ fund, formatCurrency, formatDate }) => {
  const statusInfo = getStatusInfo(fund.status);
  
  const fundDetails = [
    { label: 'Status', value: statusInfo.value, color: statusInfo.color, icon: statusInfo.icon, priority: 1, isStatus: true },
    { label: 'Currency', value: fund.currency, color: 'text.primary', icon: '💱', priority: 2 },
    ...(fund.status === 'active' && fund.actual_duration_months ? [{ label: 'Current Duration', value: `${fund.actual_duration_months} months`, color: 'text.primary', icon: '⏱️', priority: 3 }] : [])
  ];

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
        <Info color="primary" sx={{ mr: 0.5, fontSize: 16 }} />
        <Typography variant="h6" sx={{ fontSize: 16 }}>Fund Details</Typography>
      </Box>
      
      {/* Phase 3B: Enhanced card layout with consistent styling */}
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
        {fundDetails.map((detail, index) => (
          <Box 
            key={index}
              sx={{
              display: 'flex', 
              justifyContent: 'space-between', 
              alignItems: 'center',
              p: 0.5,
              borderRadius: 1,
              backgroundColor: detail.priority === 1 ? 'success.50' : 'transparent',
              border: '1px solid',
              borderColor: 'grey.200',
              // Phase 4: Enhanced hover effects for individual items
              transition: 'all 0.2s ease-in-out',
              '&:hover': {
                backgroundColor: detail.priority === 1 ? 'success.100' : 'grey.50',
                borderColor: 'grey.300',
                transform: 'translateX(2px)'
              }
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
              <span style={{ fontSize: '12px' }}>{detail.icon}</span>
              <Typography variant="body2" color="text.secondary" sx={{ fontSize: 11 }}>
                {detail.label}
              </Typography>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
              {detail.isStatus && (
                <MuiTooltip title={statusInfo.tooltip} arrow>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, cursor: 'help' }}>
                    <Box sx={{ 
                    width: 8,
                    height: 8,
                    borderRadius: '50%',
                    bgcolor: statusInfo.color,
                      // Phase 4: Enhanced status indicator
                      transition: 'all 0.2s ease-in-out',
                      boxShadow: statusInfo.color === 'success.main' ? '0 0 4px rgba(76, 175, 80, 0.4)' : 'none'
                    }} />
                    <Typography variant="body2" sx={{ color: detail.color, fontSize: 12, fontWeight: detail.priority === 1 ? 600 : 500 }}>
                      {detail.value}
                    </Typography>
                  </Box>
                </MuiTooltip>
              )}
              {!detail.isStatus && (
                <Typography variant="body2" sx={{ color: detail.color, fontSize: 12, fontWeight: detail.priority === 1 ? 600 : 500 }}>
                  {detail.value}
                </Typography>
              )}
            </Box>
        </Box>
        ))}
      </Box>
    </Paper>
  );
};

export default FundDetailsSection; 