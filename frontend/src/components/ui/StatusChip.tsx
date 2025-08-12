import React from 'react';
import { Chip } from '@mui/material';
import { FundStatus } from '../../types/api';
import { getStatusInfo } from '../../utils/helpers';

export interface StatusChipProps {
  status: FundStatus | string;
  size?: 'small' | 'medium';
  className?: string;
}

export const StatusChip: React.FC<StatusChipProps> = ({ status, size = 'small', className }) => {
  const info = getStatusInfo(String(status));

  return (
    <Chip
      component="div"
      label={info.value}
      size={size}
      className={className || ''}
      aria-label={`status: ${info.value}`}
      sx={{
        backgroundColor: info.color,
        color: '#FFFFFF',
        fontWeight: 600,
        fontSize: '12px',
        height: size === 'small' ? '24px' : '32px',
        borderRadius: '6px',
        '& .MuiChip-label': {
          px: 1.5,
          py: 0.5
        }
      }}
      title={info.tooltip}
    />
  );
};

export default StatusChip;


