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
      label={info.value}
      size={size}
      className={className}
      aria-label={`status: ${info.value}`}
      sx={{
        bgcolor: info.color,
        color: '#fff',
        fontWeight: 500,
      }}
      title={info.tooltip}
    />
  );
};

export default StatusChip;


