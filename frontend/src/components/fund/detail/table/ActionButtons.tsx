import React from 'react';
import {
  Box,
  IconButton
} from '@mui/material';
import {
  Edit as EditIcon,
  Delete as DeleteIcon
} from '@mui/icons-material';
import { ExtendedFundEvent } from '../../../types/api';

export interface ActionButtonsProps {
  event: ExtendedFundEvent;
  onEditEvent: (event: ExtendedFundEvent) => void;
  onDeleteEvent: (event: ExtendedFundEvent) => void;
}

const ActionButtons: React.FC<ActionButtonsProps> = ({
  event,
  onEditEvent,
  onDeleteEvent
}) => {
  // Only show edit/delete for user-editable events
  const isEditableEvent = !['TAX_PAYMENT', 'DAILY_RISK_FREE_INTEREST_CHARGE', 'EOFY_DEBT_COST', 'MANAGEMENT_FEE', 'CARRIED_INTEREST', 'OTHER'].includes(event.event_type);

  if (!isEditableEvent) {
    return null;
  }

  return (
    <Box display="flex" gap={1.5} justifyContent="flex-end" alignItems="center">
      <IconButton
        size="small"
        onClick={() => onEditEvent(event)}
        sx={{
          color: 'primary.main',
          p: 1,
          borderRadius: 1,
          transition: 'all 0.2s ease-in-out',
          '&:hover': {
            bgcolor: 'primary.light',
            transform: 'scale(1.05)',
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
          }
        }}
        title="Edit event"
      >
        <EditIcon sx={{ fontSize: 18 }} />
      </IconButton>
      <IconButton
        size="small"
        onClick={() => onDeleteEvent(event)}
        sx={{
          color: 'error.main',
          p: 1,
          borderRadius: 1,
          transition: 'all 0.2s ease-in-out',
          '&:hover': {
            bgcolor: 'error.light',
            transform: 'scale(1.05)',
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
          }
        }}
        title="Delete event"
      >
        <DeleteIcon sx={{ fontSize: 18 }} />
      </IconButton>
    </Box>
  );
};

export default ActionButtons; 