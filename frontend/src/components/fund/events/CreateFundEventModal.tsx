import React from 'react';
import CreateFundEventForm from './CreateFundEventForm';

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
          <CreateFundEventForm
      open={open}
      onClose={onClose}
      onSuccess={onEventCreated}
      fundId={fundId}
      fundTrackingType={fundTrackingType}
    />
  );
};

export default CreateFundEventModal; 