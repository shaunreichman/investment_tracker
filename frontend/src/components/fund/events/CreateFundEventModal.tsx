import React from 'react';
import UnifiedFundEventForm from './UnifiedFundEventForm';

interface CreateFundEventModalProps {
  open: boolean;
  onClose: () => void;
  onEventCreated: () => void;
  fundId: number;
  fundTrackingType: 'nav_based' | 'cost_based';
}

const CreateFundEventModal: React.FC<CreateFundEventModalProps> = ({ 
  open, 
  onClose, 
  onEventCreated, 
  fundId, 
  fundTrackingType 
}) => {
  return (
    <UnifiedFundEventForm
      open={open}
      onClose={onClose}
      onSuccess={onEventCreated}
      fundId={fundId}
      fundTrackingType={fundTrackingType}
    />
  );
};

export default CreateFundEventModal; 