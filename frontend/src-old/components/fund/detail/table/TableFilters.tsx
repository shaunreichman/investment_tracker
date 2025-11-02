import React, { useCallback } from 'react';
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
  // Stabilize onChange callbacks to prevent unnecessary re-renders
  const handleTaxEventsChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    onShowTaxEventsChange(e.target.checked);
  }, [onShowTaxEventsChange]);

  const handleNavUpdatesChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    onShowNavUpdatesChange(e.target.checked);
  }, [onShowNavUpdatesChange]);

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
            onChange={handleTaxEventsChange}
            size="small"
            sx={{
              '& .MuiSwitch-switchBase': {
                color: 'divider',
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
              onChange={handleNavUpdatesChange}
              size="small"
              sx={{
                '& .MuiSwitch-switchBase': {
                  color: 'divider',
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

/**
 * Custom comparator for React.memo to only compare fields that affect rendering
 * This prevents unnecessary re-renders when irrelevant fields change
 */
const tableFiltersPropsAreEqual = (prevProps: TableFiltersProps, nextProps: TableFiltersProps): boolean => {
  return (
    prevProps.showTaxEvents === nextProps.showTaxEvents &&
    prevProps.showNavUpdates === nextProps.showNavUpdates &&
    prevProps.isNavBasedFund === nextProps.isNavBasedFund &&
    prevProps.onShowTaxEventsChange === nextProps.onShowTaxEventsChange &&
    prevProps.onShowNavUpdatesChange === nextProps.onShowNavUpdatesChange &&
    prevProps.onAddEventClick === nextProps.onAddEventClick
  );
};

export default React.memo(TableFiltersComponent, tableFiltersPropsAreEqual);