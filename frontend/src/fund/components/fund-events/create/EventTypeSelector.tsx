import React from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  useTheme
} from '@mui/material';
import {
  AccountBalance,
  Add as AddIcon,
  TrendingUp,
  MonetizationOn,
  Receipt
} from '@mui/icons-material';
import { FundTrackingType } from '@/fund/types';

// Types
export type EventType = 'CAPITAL_CALL' | 'DISTRIBUTION' | 'UNIT_PURCHASE' | 'UNIT_SALE' | 'NAV_UPDATE' | 'TAX_STATEMENT';

export interface EventTemplate {
  label: string;
  value: EventType | 'RETURN_OF_CAPITAL';
  description: string;
  icon: React.ReactNode;
  trackingType: FundTrackingType | 'both';
}

export interface DistributionTemplate {
  label: string;
  value: string;
  description: string;
  icon: React.ReactNode;
}

export interface SubDistributionTemplate {
  label: string;
  value: string;
  description: string;
  icon: React.ReactNode;
}

// Constants
export const EVENT_TEMPLATES: EventTemplate[] = [
  { label: 'Capital Call', value: 'CAPITAL_CALL', description: 'Add a capital call (cost-based funds)', icon: <AccountBalance color="primary" />, trackingType: FundTrackingType.COST_BASED },
  { label: 'Capital Return', value: 'RETURN_OF_CAPITAL', description: 'Return capital to investors (cost-based funds)', icon: <AccountBalance color="warning" />, trackingType: FundTrackingType.COST_BASED },
  { label: 'Unit Purchase', value: 'UNIT_PURCHASE', description: 'Buy units (NAV-based funds)', icon: <AddIcon color="primary" />, trackingType: FundTrackingType.NAV_BASED },
  { label: 'Unit Sale', value: 'UNIT_SALE', description: 'Sell units (NAV-based funds)', icon: <TrendingUp color="warning" />, trackingType: FundTrackingType.NAV_BASED },
  { label: 'NAV Update', value: 'NAV_UPDATE', description: 'Update NAV per share (NAV-based funds)', icon: <TrendingUp color="info" />, trackingType: FundTrackingType.NAV_BASED },
  { label: 'Distribution', value: 'DISTRIBUTION', description: 'Add a distribution (all funds)', icon: <MonetizationOn color="success" />, trackingType: 'both' },
  { label: 'Tax Statement', value: 'TAX_STATEMENT', description: 'Add a tax statement (all funds)', icon: <Receipt color="secondary" />, trackingType: 'both' },
];

export const DISTRIBUTION_TEMPLATES: DistributionTemplate[] = [
  { label: 'Interest', value: 'INTEREST', description: 'Interest distribution', icon: <MonetizationOn color="primary" /> },
  { label: 'Dividend', value: 'DIVIDEND', description: 'Dividend distribution', icon: <MonetizationOn color="success" /> },
  { label: 'Other', value: 'OTHER', description: 'Other distribution', icon: <MonetizationOn color="warning" /> },
];

export const DIVIDEND_SUB_TEMPLATES: SubDistributionTemplate[] = [
  { label: 'Franked', value: 'DIVIDEND_FRANKED', description: 'Franked dividend', icon: <MonetizationOn color="success" /> },
  { label: 'Unfranked', value: 'DIVIDEND_UNFRANKED', description: 'Unfranked dividend', icon: <MonetizationOn color="warning" /> },
];

export const INTEREST_SUB_TEMPLATES: SubDistributionTemplate[] = [
  { label: 'Regular', value: 'REGULAR', description: 'Regular interest', icon: <MonetizationOn color="primary" /> },
  { label: 'Withholding Tax', value: 'WITHHOLDING_TAX', description: 'Interest with withholding tax', icon: <MonetizationOn color="warning" /> },
];

// Props interface
export interface EventTypeSelectorProps {
  fundTrackingType: FundTrackingType;
  eventType: EventType | 'RETURN_OF_CAPITAL' | '';
  distributionType: string;
  subDistributionType: string;
  mode?: 'create' | 'edit'; // New prop for edit mode
  onEventTypeSelect: (value: EventType | 'RETURN_OF_CAPITAL') => void;
  onDistributionTypeSelect: (value: string) => void;
  onSubDistributionTypeSelect: (value: string) => void;
  onBack: () => void;
}

/**
 * EventTypeSelector Component
 * 
 * Extracted from CreateFundEventModal.tsx for reusability and testing
 * Handles event type selection with filtering based on fund tracking type
 * Includes distribution type and sub-distribution type selection
 */
const EventTypeSelector: React.FC<EventTypeSelectorProps> = ({
  fundTrackingType,
  eventType,
  distributionType,
  subDistributionType,
  mode = 'create', // Default to create mode
  onEventTypeSelect,
  onDistributionTypeSelect,
  onSubDistributionTypeSelect,
  onBack
}) => {
  const theme = useTheme();
  
  // Filter templates based on fund tracking type
  const filteredTemplates = EVENT_TEMPLATES.filter(
    template => template.trackingType === fundTrackingType || template.trackingType === 'both'
  );

  return (
    <Box>
      {/* Edit Mode Info */}
      {mode === 'edit' && (
        <Box mb={1.5} p={1.5} bgcolor="info.light" borderRadius={1}>
          <Typography variant="body2" color="info.contrastText">
            Event type cannot be changed in edit mode. To change the event type, delete this event and create a new one.
          </Typography>
        </Box>
      )}
      
      {/* Event Type Cards */}
      <Box display="flex" gap={2} mb={1.5}>
        {filteredTemplates.map(template => {
          const isSelected = eventType === template.value;
          const isDisabled = mode === 'edit' || (eventType && eventType !== template.value && !(eventType === 'DISTRIBUTION' && template.value === 'DISTRIBUTION'));
          
          return (
            <Paper
              key={template.value}
              elevation={isSelected ? 6 : 1}
              sx={{
                p: 1.5,
                minWidth: 130,
                border: isSelected ? `2px solid ${theme.palette.primary.main}` : `1px solid ${theme.palette.divider}`,
                background: isSelected ? theme.palette.primary.light : theme.palette.background.paper,
                opacity: isDisabled ? 0.5 : 1,
                cursor: isDisabled ? 'not-allowed' : 'pointer',
                transition: 'all 0.2s',
                position: 'relative',
                transform: isSelected ? 'scale(1.02)' : 'scale(1)',
                '&:hover': {
                  elevation: isSelected ? 6 : 2,
                  transform: isSelected ? 'scale(1.02)' : 'scale(1.05)',
                  boxShadow: isSelected ? theme.shadows[6] : theme.shadows[2],
                  background: isSelected ? theme.palette.primary.light : theme.palette.action.hover,
                  borderColor: isSelected ? theme.palette.primary.main : theme.palette.primary.light,
                }
              }}
              onClick={() => {
                if (isDisabled) return;
                if (isSelected && mode === 'create') {
                  onEventTypeSelect('' as EventType | 'RETURN_OF_CAPITAL');
                  onDistributionTypeSelect('');
                  onSubDistributionTypeSelect('');
                } else if (mode === 'create') {
                  onEventTypeSelect(template.value);
                  onDistributionTypeSelect('');
                  onSubDistributionTypeSelect('');
                }
                // In edit mode, no action on click
              }}
            >
              <Box display="flex" flexDirection="column" alignItems="center">
                {template.icon}
                <Typography variant="subtitle1" fontWeight={isSelected ? 'bold' : 'normal'}>
                  {template.label}
                </Typography>

              </Box>
              {/* Expand indicator for Distribution */}
              {template.value === 'DISTRIBUTION' && isSelected && (
                <Box position="absolute" top={8} right={8}>
                  <AddIcon color="primary" />
                </Box>
              )}
            </Paper>
          );
        })}
      </Box>

      {/* Distribution Type Options (inline, below cards, always visible when Distribution is selected) */}
      {eventType === 'DISTRIBUTION' && (
        <Box mb={1.5}>
          <Typography variant="subtitle1" mb={1} color="primary">
            {mode === 'edit' ? 'Distribution Type (Fixed)' : 'Select Distribution Type'}
          </Typography>
          <Box display="flex" gap={2}>
            {DISTRIBUTION_TEMPLATES.map(dt => {
              const isSelected = distributionType === dt.value;
              const isDisabled = mode === 'edit';
              return (
                <Paper
                  key={dt.value}
                  elevation={isSelected ? 6 : 2}
                  sx={{
                    p: 1.5,
                    minWidth: 130,
                    border: isSelected ? `2px solid ${theme.palette.primary.main}` : `1px solid ${theme.palette.divider}`,
                    background: isSelected ? theme.palette.primary.light : theme.palette.background.paper,
                    opacity: isDisabled ? 0.5 : 1,
                    cursor: isDisabled ? 'not-allowed' : 'pointer',
                    transition: 'all 0.2s',
                    position: 'relative',
                    transform: isSelected ? 'scale(1.02)' : 'scale(1)',
                    '&:hover': {
                      elevation: isSelected ? 6 : 2,
                      transform: isSelected ? 'scale(1.02)' : 'scale(1.05)',
                      boxShadow: isSelected ? theme.shadows[6] : theme.shadows[2],
                      background: isSelected ? theme.palette.primary.light : theme.palette.action.hover,
                      borderColor: isSelected ? theme.palette.primary.main : theme.palette.primary.light,
                    }
                  }}
                  onClick={() => {
                    if (isDisabled) return;
                    if (isSelected && mode === 'create') {
                      onDistributionTypeSelect('');
                      onSubDistributionTypeSelect('');
                    } else if (mode === 'create') {
                      onDistributionTypeSelect(dt.value);
                      onSubDistributionTypeSelect('');
                    }
                    // In edit mode, no action on click
                  }}
                >
                  <Box display="flex" flexDirection="row" alignItems="center" gap={1}>
                    {dt.icon}
                    <Typography variant="subtitle2" fontWeight={isSelected ? 'bold' : 'normal'}>
                      {dt.label}
                    </Typography>
                  </Box>
                </Paper>
              );
            })}
          </Box>
        </Box>
      )}

      {/* Sub-Distribution Type Options (inline, below Distribution Type, only visible when Dividend is selected) */}
      {distributionType === 'DIVIDEND' && (
        <Box mb={1}>
          <Typography variant="subtitle1" mb={1} color="primary">
            {mode === 'edit' ? 'Dividend Type (Fixed)' : 'Select Dividend Type'}
          </Typography>
          <Box display="flex" gap={2}>
            {DIVIDEND_SUB_TEMPLATES.map(sub => {
              const isSelected = subDistributionType === sub.value;
              const isDisabled = mode === 'edit';
              return (
                <Paper
                  key={sub.value}
                  elevation={isSelected ? 6 : 2}
                  sx={{
                    p: 1.5,
                    minWidth: 130,
                    border: isSelected ? `2px solid ${theme.palette.primary.main}` : `1px solid ${theme.palette.divider}`,
                    background: isSelected ? theme.palette.primary.light : theme.palette.background.paper,
                    opacity: isDisabled ? 0.5 : 1,
                    cursor: isDisabled ? 'not-allowed' : 'pointer',
                    transition: 'all 0.2s',
                    position: 'relative',
                    transform: isSelected ? 'scale(1.02)' : 'scale(1)',
                    '&:hover': {
                      elevation: isSelected ? 6 : 2,
                      transform: isSelected ? 'scale(1.02)' : 'scale(1.05)',
                      boxShadow: isSelected ? theme.shadows[6] : theme.shadows[2],
                      background: isSelected ? theme.palette.primary.light : theme.palette.action.hover,
                      borderColor: isSelected ? theme.palette.primary.main : theme.palette.primary.light,
                    }
                  }}
                  onClick={() => {
                    if (isDisabled) return;
                    if (isSelected && mode === 'create') {
                      onSubDistributionTypeSelect('');
                    } else if (mode === 'create') {
                      onSubDistributionTypeSelect(sub.value);
                    }
                    // In edit mode, no action on click
                  }}
                >
                  <Box display="flex" flexDirection="row" alignItems="center" gap={1}>
                    {sub.icon}
                    <Typography variant="subtitle2" fontWeight={isSelected ? 'bold' : 'normal'}>
                      {sub.label}
                    </Typography>
                  </Box>
                </Paper>
              );
            })}
          </Box>
        </Box>
      )}

      {/* Interest Sub-Distribution Type Options (inline, below Distribution Type, only visible when Interest is selected) */}
      {distributionType === 'INTEREST' && (
        <Box mb={1}>
          <Typography variant="subtitle1" mb={1} color="primary">
            {mode === 'edit' ? 'Interest Type (Fixed)' : 'Select Interest Sub-Distribution Type'}
          </Typography>
          <Box display="flex" gap={2}>
            {INTEREST_SUB_TEMPLATES.map(subDt => {
              const isSelected = subDistributionType === subDt.value;
              const isDisabled = mode === 'edit';
              return (
                <Paper
                  key={subDt.value}
                  elevation={isSelected ? 6 : 2}
                  sx={{
                    p: 1.5,
                    minWidth: 130,
                    border: isSelected ? `2px solid ${theme.palette.primary.main}` : `1px solid ${theme.palette.divider}`,
                    background: isSelected ? theme.palette.primary.light : theme.palette.background.paper,
                    opacity: isDisabled ? 0.5 : 1,
                    cursor: isDisabled ? 'not-allowed' : 'pointer',
                    transition: 'all 0.2s',
                    position: 'relative',
                    transform: isSelected ? 'scale(1.02)' : 'scale(1)',
                    '&:hover': {
                      elevation: isSelected ? 6 : 2,
                      transform: isSelected ? 'scale(1.02)' : 'scale(1.05)',
                      boxShadow: isSelected ? theme.shadows[6] : theme.shadows[2],
                      background: isSelected ? theme.palette.primary.light : theme.palette.action.hover,
                      borderColor: isSelected ? theme.palette.primary.main : theme.palette.primary.light,
                    }
                  }}
                  onClick={() => {
                    if (isDisabled) return;
                    if (isSelected && mode === 'create') {
                      onSubDistributionTypeSelect('');
                    } else if (mode === 'create') {
                      onSubDistributionTypeSelect(subDt.value);
                    }
                    // In edit mode, no action on click
                  }}
                >
                  <Box display="flex" flexDirection="row" alignItems="center" gap={1}>
                    {subDt.icon}
                    <Typography variant="subtitle2" fontWeight={isSelected ? 'bold' : 'normal'}>
                      {subDt.label}
                    </Typography>
                  </Box>
                </Paper>
              );
            })}
          </Box>
        </Box>
      )}

      {/* Back Button */}
      {(distributionType || eventType) && (
        <Box mt={1.5}>
          <Button
            variant="outlined"
            onClick={onBack}
            sx={{ mr: 1 }}
          >
            Back
          </Button>
        </Box>
      )}
    </Box>
  );
};

export default EventTypeSelector;

