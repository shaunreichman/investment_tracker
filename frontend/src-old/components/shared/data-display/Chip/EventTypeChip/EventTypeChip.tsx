// ============================================================================
// EVENT TYPE CHIP COMPONENT
// ============================================================================

import React from 'react';
import { Chip, useTheme } from '@mui/material';
import { getEventTypeColor } from '../../../../../utils/helpers';
import type { EventTypeChipProps } from './EventTypeChip.types';

/**
 * EventTypeChip - Display fund event types with semantic colors
 * 
 * Uses getEventTypeColor utility to map event types to appropriate colors.
 * 
 * @example
 * ```tsx
 * <EventTypeChip eventType="NAV_UPDATE" />
 * <EventTypeChip eventType="DISTRIBUTION" size="medium" />
 * ```
 */
export const EventTypeChip: React.FC<EventTypeChipProps> = ({ 
  eventType, 
  size = 'small', 
  className 
}) => {
  const theme = useTheme();
  const colorVariant = getEventTypeColor(eventType);
  
  // Map MUI color variants to theme colors
  const getChipStyle = () => {
    switch (colorVariant) {
      case 'primary':
        return {
          backgroundColor: theme.palette.primary.main,
          color: theme.palette.text.primary
        };
      case 'success':
        return {
          backgroundColor: theme.palette.success.main,
          color: theme.palette.text.primary
        };
      case 'warning':
        return {
          backgroundColor: theme.palette.warning.main,
          color: theme.palette.text.primary
        };
      case 'error':
        return {
          backgroundColor: theme.palette.error.main,
          color: theme.palette.text.primary
        };
      case 'info':
        return {
          backgroundColor: theme.palette.info.main,
          color: theme.palette.text.primary
        };
      default:
        return {
          backgroundColor: theme.palette.text.disabled || theme.palette.text.muted,
          color: theme.palette.text.primary
        };
    }
  };

  return (
    <Chip
      component="div"
      label={eventType}
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

