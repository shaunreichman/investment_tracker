import React from 'react';
import {
  Box,
  Paper,
  Typography,
  Button
} from '@mui/material';
import {
  AccountBalance,
  Add as AddIcon,
  TrendingUp,
  MonetizationOn,
  Receipt
} from '@mui/icons-material';

// Types
export type EventType = 'CAPITAL_CALL' | 'DISTRIBUTION' | 'UNIT_PURCHASE' | 'UNIT_SALE' | 'NAV_UPDATE' | 'TAX_STATEMENT';

export interface EventTemplate {
  label: string;
  value: EventType | 'RETURN_OF_CAPITAL';
  description: string;
  icon: React.ReactNode;
  trackingType: 'nav_based' | 'cost_based' | 'both';
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
  { label: 'Capital Call', value: 'CAPITAL_CALL', description: 'Add a capital call (cost-based funds)', icon: <AccountBalance color="primary" />, trackingType: 'cost_based' },
  { label: 'Capital Return', value: 'RETURN_OF_CAPITAL', description: 'Return capital to investors (cost-based funds)', icon: <AccountBalance color="warning" />, trackingType: 'cost_based' },
  { label: 'Unit Purchase', value: 'UNIT_PURCHASE', description: 'Buy units (NAV-based funds)', icon: <AddIcon color="primary" />, trackingType: 'nav_based' },
  { label: 'Unit Sale', value: 'UNIT_SALE', description: 'Sell units (NAV-based funds)', icon: <TrendingUp color="warning" />, trackingType: 'nav_based' },
  { label: 'NAV Update', value: 'NAV_UPDATE', description: 'Update NAV per share (NAV-based funds)', icon: <TrendingUp color="info" />, trackingType: 'nav_based' },
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
  fundTrackingType: 'nav_based' | 'cost_based';
  eventType: EventType | 'RETURN_OF_CAPITAL' | '';
  distributionType: string;
  subDistributionType: string;
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
  onEventTypeSelect,
  onDistributionTypeSelect,
  onSubDistributionTypeSelect,
  onBack
}) => {
  // Filter templates based on fund tracking type
  const filteredTemplates = EVENT_TEMPLATES.filter(
    template => template.trackingType === fundTrackingType || template.trackingType === 'both'
  );

  return (
    <Box>
      {/* Event Type Cards */}
      <Box display="flex" gap={2} mb={2}>
        {filteredTemplates.map(template => {
          const isSelected = eventType === template.value;
          const isDisabled = eventType && eventType !== template.value && !(eventType === 'DISTRIBUTION' && template.value === 'DISTRIBUTION');
          
          return (
            <Paper
              key={template.value}
              elevation={isSelected ? 6 : 1}
              sx={{
                p: 2,
                minWidth: 120,
                border: isSelected ? '2px solid #1976d2' : '1px solid #ccc',
                background: isSelected ? '#e3f2fd' : '#fff',
                opacity: isDisabled ? 0.5 : 1,
                cursor: isDisabled ? 'not-allowed' : 'pointer',
                transition: 'all 0.2s',
                position: 'relative',
              }}
              onClick={() => {
                if (isDisabled) return;
                if (isSelected) {
                  onEventTypeSelect('' as EventType | 'RETURN_OF_CAPITAL');
                  onDistributionTypeSelect('');
                  onSubDistributionTypeSelect('');
                } else {
                  onEventTypeSelect(template.value);
                  onDistributionTypeSelect('');
                  onSubDistributionTypeSelect('');
                }
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
        <Box mb={2}>
          <Typography variant="subtitle1" mb={1} color="primary">Select Distribution Type</Typography>
          <Box display="flex" gap={2}>
            {DISTRIBUTION_TEMPLATES.map(dt => {
              const isSelected = distributionType === dt.value;
              return (
                <Paper
                  key={dt.value}
                  elevation={isSelected ? 6 : 2}
                  sx={{
                    p: 2,
                    minWidth: 120,
                    border: isSelected ? '2px solid #1976d2' : '1px solid #ccc',
                    background: isSelected ? '#e3f2fd' : '#f3f6fa',
                    cursor: 'pointer',
                    transition: 'all 0.2s',
                  }}
                  onClick={() => {
                    if (isSelected) {
                      onDistributionTypeSelect('');
                      onSubDistributionTypeSelect('');
                    } else {
                      onDistributionTypeSelect(dt.value);
                      onSubDistributionTypeSelect('');
                    }
                  }}
                >
                  <Box display="flex" flexDirection="column" alignItems="center">
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
        <Box mb={2}>
          <Typography variant="subtitle1" mb={1} color="primary">Select Dividend Type</Typography>
          <Box display="flex" gap={2}>
            {DIVIDEND_SUB_TEMPLATES.map(sub => (
              <Button
                key={sub.value}
                variant={subDistributionType === sub.value ? 'contained' : 'outlined'}
                color={sub.value === 'DIVIDEND_FRANKED' ? 'success' : 'warning'}
                onClick={() => onSubDistributionTypeSelect(sub.value)}
                startIcon={sub.icon}
              >
                {sub.label}
              </Button>
            ))}
          </Box>
        </Box>
      )}

      {/* Interest Sub-Distribution Type Options (inline, below Distribution Type, only visible when Interest is selected) */}
      {distributionType === 'INTEREST' && (
        <Box mb={2}>
          <Typography variant="subtitle1" mb={1} color="primary">Select Interest Sub-Distribution Type</Typography>
          <Box display="flex" gap={2}>
            {INTEREST_SUB_TEMPLATES.map(subDt => {
              const isSelected = subDistributionType === subDt.value;
              return (
                <Paper
                  key={subDt.value}
                  elevation={isSelected ? 6 : 2}
                  sx={{
                    p: 2,
                    minWidth: 120,
                    border: isSelected ? '2px solid #1976d2' : '1px solid #ccc',
                    background: isSelected ? '#e3f2fd' : '#f3f6fa',
                    cursor: 'pointer',
                    transition: 'all 0.2s',
                  }}
                  onClick={() => {
                    if (isSelected) {
                      onSubDistributionTypeSelect('');
                    } else {
                      onSubDistributionTypeSelect(subDt.value);
                    }
                  }}
                >
                  <Box display="flex" flexDirection="column" alignItems="center">
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
        <Box mt={2}>
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