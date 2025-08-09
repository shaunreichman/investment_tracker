import React from 'react';
import { Chip } from '@mui/material';
import { DistributionType, EventType } from '../../types/api';
import { getEventTypeColor } from '../../utils/helpers';
import { getEventTypeLabelSimple } from '../../utils/transformers/eventTransformers';

export interface EventTypeChipProps {
  eventType: EventType | string;
  distributionType?: DistributionType | string;
  size?: 'small' | 'medium';
  className?: string;
}

export const EventTypeChip: React.FC<EventTypeChipProps> = ({
  eventType,
  distributionType,
  size = 'small',
  className,
}) => {
  const baseLabel = getEventTypeLabelSimple(String(eventType));
  const label = distributionType ? `${baseLabel}` : baseLabel;
  const color = getEventTypeColor(String(eventType)) as any;

  return (
    <Chip
      label={label}
      size={size}
      color={color}
      className={className}
      aria-label={`event type: ${label}`}
    />
  );
};

export default EventTypeChip;


