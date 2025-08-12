import React from 'react';
import { Chip } from '@mui/material';

export interface TrackingTypeChipProps {
  trackingType: 'nav_based' | 'cost_based' | string;
  size?: 'small' | 'medium';
  className?: string;
}

export const TrackingTypeChip: React.FC<TrackingTypeChipProps> = ({ trackingType, size = 'small', className }) => {
  const normalized = String(trackingType).toLowerCase();
  const label = normalized === 'nav_based' ? 'nav_based' : normalized === 'cost_based' ? 'cost_based' : trackingType;
  
  // Docker color scheme for tracking types
  const getChipStyle = () => {
    if (normalized === 'nav_based') {
      return {
        backgroundColor: '#2496ED',
        color: '#FFFFFF'
      };
    } else if (normalized === 'cost_based') {
      return {
        backgroundColor: '#06a58c',
        color: '#FFFFFF'
      };
    } else {
      return {
        backgroundColor: '#6B7280',
        color: '#FFFFFF'
      };
    }
  };

  const chipStyle = getChipStyle();

  return (
    <Chip
      component="div"
      label={label}
      size={size}
      className={className || ''}
      aria-label={`tracking: ${label}`}
      sx={{
        ...chipStyle,
        fontWeight: 600,
        fontSize: '12px',
        height: size === 'small' ? '24px' : '32px',
        borderRadius: '6px',
        '& .MuiChip-label': {
          px: 1.5,
          py: 0.5
        }
      }}
    />
  );
};

export default TrackingTypeChip;


