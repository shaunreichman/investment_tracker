import React from 'react';
import {
  Box,
  Button,
  Switch,
  Typography
} from '@mui/material';
import { Add as AddIcon } from '@mui/icons-material';

export interface TableFiltersProps {
  showTaxEvents: boolean;
  showNavUpdates: boolean;
  isNavBasedFund: boolean;
  onShowTaxEventsChange: (checked: boolean) => void;
  onShowNavUpdatesChange: (checked: boolean) => void;
  onAddEventClick: () => void;
}

const TableFiltersComponent: React.FC<TableFiltersProps> = ({
  showTaxEvents,
  showNavUpdates,
  isNavBasedFund,
  onShowTaxEventsChange,
  onShowNavUpdatesChange,
  onAddEventClick
}) => {
  return (
    <Box sx={{ 
      display: 'flex', 
      alignItems: 'center', 
      gap: 2, 
      mb: 2,
      flexWrap: 'wrap',
      justifyContent: 'space-between'
    }}>
      <Box sx={{ 
        display: 'flex', 
        alignItems: 'center', 
        gap: 2,
        flexWrap: 'wrap'
      }}>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={onAddEventClick}
          sx={{
            backgroundColor: 'primary.main',
            color: 'white',
            '&:hover': {
              backgroundColor: 'primary.dark',
              transform: 'translateY(-1px)',
              boxShadow: '0 4px 8px rgba(0,0,0,0.2)'
            },
            transition: 'all 0.2s ease-in-out',
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
          }}
        >
          Add Event
        </Button>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Typography variant="body2" color="text.secondary">
            Show Tax Events
          </Typography>
          <Switch
            checked={showTaxEvents}
            onChange={(e) => onShowTaxEventsChange(e.target.checked)}
            size="small"
            sx={{
              '& .MuiSwitch-switchBase': {
                color: 'grey.400',
                transition: 'all 0.2s ease-in-out',
              },
              '& .MuiSwitch-switchBase.Mui-checked': {
                color: 'primary.main',
              },
              '& .MuiSwitch-switchBase.Mui-checked + .MuiSwitch-track': {
                backgroundColor: 'primary.main',
              },
              '&:hover .MuiSwitch-switchBase': {
                transform: 'scale(1.05)',
              }
            }}
          />
        </Box>
        {isNavBasedFund && (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Typography variant="body2" color="text.secondary">
              Show NAV Updates
            </Typography>
            <Switch
              checked={showNavUpdates}
              onChange={(e) => onShowNavUpdatesChange(e.target.checked)}
              size="small"
              sx={{
                '& .MuiSwitch-switchBase': {
                  color: 'grey.400',
                  transition: 'all 0.2s ease-in-out',
                },
                '& .MuiSwitch-switchBase.Mui-checked': {
                  color: 'primary.main',
                },
                '& .MuiSwitch-switchBase.Mui-checked + .MuiSwitch-track': {
                  backgroundColor: 'primary.main',
                },
                '&:hover .MuiSwitch-switchBase': {
                  transform: 'scale(1.05)',
                }
              }}
            />
          </Box>
        )}
      </Box>
    </Box>
  );
};

export default React.memo(TableFiltersComponent);