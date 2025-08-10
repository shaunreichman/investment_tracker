import React from 'react';
import { Chip } from '@mui/material';
import { DistributionType, EventType } from '../../types/api';
import { getEventTypeColor } from '../../utils/helpers';
import { getEventTypeLabelSimple } from '../../utils/transformers/eventTransformers';

export interface EventTypeChipProps {
  eventType: EventType | DistributionType | string;
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
  // CALCULATED: Determine if this is a distribution type or event type
  const isDistributionType = ['INTEREST', 'DIVIDEND', 'OTHER'].includes(eventType);
  
  // CALCULATED: Get the appropriate label
  const label = isDistributionType ? eventType : getEventTypeLabelSimple(String(eventType));
  
  // CALCULATED: Get the appropriate color
  const color = getEventTypeColor(String(eventType)) as any;

  return (
    <Chip
      component="div"
      label={label}
      size={size}
      color={color}
      className={className || ''}
      aria-label={`event type: ${label}`}
    />
  );
};

export default EventTypeChip;


