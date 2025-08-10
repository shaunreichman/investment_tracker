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
  const color = normalized === 'nav_based' ? 'primary' : normalized === 'cost_based' ? 'secondary' : 'default';

  return (
    <Chip
      component="div"
      label={label}
      size={size}
      color={color as any}
      className={className || ''}
      aria-label={`tracking: ${label}`}
    />
  );
};

export default TrackingTypeChip;


