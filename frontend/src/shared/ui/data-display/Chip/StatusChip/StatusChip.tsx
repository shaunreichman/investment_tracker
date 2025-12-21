// ============================================================================
// STATUS CHIP COMPONENT
// ============================================================================

import React from 'react';
import { Chip, useTheme } from '@mui/material';
import type { StatusChipProps } from './StatusChip.types';

/**
 * StatusChip - Display status indicators with semantic colors
 * 
 * @example
 * ```tsx
 * <StatusChip status="active" />
 * <StatusChip status="error" size="medium" />
 * ```
 */
export const StatusChip: React.FC<StatusChipProps> = ({ 
  status, 
  size = 'small', 
  className 
}) => {
  const theme = useTheme();
  
  // Get status color based on status value
  const getStatusColor = () => {
    const normalizedStatus = status.toLowerCase();
    
    switch (normalizedStatus) {
      case 'active':
      case 'completed':
      case 'success':
        return {
          backgroundColor: theme.palette.success.main,
          color: theme.palette.text.primary
        };
      case 'pending':
      case 'processing':
      case 'warning':
        return {
          backgroundColor: theme.palette.warning.main,
          color: theme.palette.text.primary
        };
      case 'error':
      case 'failed':
      case 'cancelled':
        return {
          backgroundColor: theme.palette.error.main,
          color: theme.palette.text.primary
        };
      case 'info':
      case 'draft':
      default:
        return {
          backgroundColor: theme.palette.info.main,
          color: theme.palette.text.primary
        };
    }
  };

  return (
    <Chip
      component="div"
      label={status}
      size={size}
      className={className || ''}
      sx={{
        ...getStatusColor(),
        fontWeight: 500,
        textTransform: 'none',
        '& .MuiChip-label': {
          px: 1,
        },
      }}
    />
  );
};

