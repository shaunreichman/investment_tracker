import React from 'react';
import UnifiedFundEventForm from './UnifiedFundEventForm';
import { ExtendedFundEvent } from '../../../types/api';

interface EditFundEventModalProps {
  open: boolean;
  onClose: () => void;
  onEventUpdated: () => void;
  fundId: number;
  fundTrackingType: 'nav_based' | 'cost_based';
  event: ExtendedFundEvent | null;
  allEvents?: ExtendedFundEvent[]; // All events for edit mode to detect withholding tax
}

const EditFundEventModal: React.FC<EditFundEventModalProps> = ({ 
  open, 
  onClose, 
  onEventUpdated, 
  fundId, 
  fundTrackingType,
  event,
  allEvents
}) => {
  return (
    <UnifiedFundEventForm
      mode="edit"
      open={open}
      onClose={onClose}
      onSuccess={onEventUpdated}
      fundId={fundId}
      fundTrackingType={fundTrackingType}
      event={event || undefined}
      allEvents={allEvents}
    />
  );
};

export default EditFundEventModal; 