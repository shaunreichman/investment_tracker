// ============================================================================
// TRACKING TYPE CHIP COMPONENT
// ============================================================================

import React from 'react';
import { Chip, useTheme } from '@mui/material';
import type { TrackingTypeChipProps } from './TrackingTypeChip.types';

/**
 * TrackingTypeChip - Display fund tracking type indicators
 * 
 * Displays whether a fund is NAV-based (primary) or Cost-based (success).
 * 
 * @example
 * ```tsx
 * <TrackingTypeChip trackingType="nav_based" />
 * <TrackingTypeChip trackingType="cost_based" size="medium" />
 * ```
 */
export const TrackingTypeChip: React.FC<TrackingTypeChipProps> = ({ 
  trackingType, 
  size = 'small', 
  className 
}) => {
  const theme = useTheme();
  const normalized = String(trackingType).toLowerCase();
  const label = normalized === 'nav_based' ? 'nav_based' : normalized === 'cost_based' ? 'cost_based' : trackingType;
  
  // Docker color scheme for tracking types
  const getChipStyle = () => {
    if (normalized === 'nav_based') {
      return {
        backgroundColor: theme.palette.primary.main,
        color: theme.palette.text.primary
      };
    } else if (normalized === 'cost_based') {
      return {
        backgroundColor: theme.palette.success.main,
        color: theme.palette.text.primary
      };
    } else {
      return {
        backgroundColor: theme.palette.text.disabled || theme.palette.text.muted,
        color: theme.palette.text.primary
      };
    }
  };

  return (
    <Chip
      component="div"
      label={label}
      size={size}
      className={className || ''}
      sx={{
        ...getChipStyle(),
        fontWeight: 500,
        textTransform: 'none',
        '& .MuiChip-label': {
          px: 1,
        },
      }}
    />
  );
};

