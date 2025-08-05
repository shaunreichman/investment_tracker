import React from 'react';
import { TableBody as MuiTableBody } from '@mui/material';
import { ExtendedFundEvent, ExtendedFund } from '../../../types/api';
import { useEventGrouping } from './useEventGrouping';
import { EventRow } from './EventRow';
import { GroupedEventRow } from './GroupedEventRow';

// ============================================================================
// TABLE BODY COMPONENT
// ============================================================================

export interface TableBodyProps {
  events: ExtendedFundEvent[];
  fund: ExtendedFund;
  showTaxEvents: boolean;
  showNavUpdates: boolean;
  onEditEvent: (event: ExtendedFundEvent) => void;
  onDeleteEvent: (event: ExtendedFundEvent) => void;
}

/**
 * Component to render the table body with integrated event grouping logic
 * Extracted from FundDetail.tsx lines 650-1084 for reusability and testing
 * 
 * This component:
 * 1. Uses useEventGrouping hook to process events
 * 2. Renders GroupedEventRow for interest + withholding combinations
 * 3. Renders EventRow for individual events
 * 4. Maintains all existing styling and responsive behavior
 */
export const TableBody: React.FC<TableBodyProps> = ({
  events,
  fund,
  showTaxEvents,
  showNavUpdates,
  onEditEvent,
  onDeleteEvent
}) => {
  // Use the event grouping hook to process events
  const { sortedEvents } = useEventGrouping(
    events,
    fund,
    showTaxEvents,
    showNavUpdates
  );

  return (
    <MuiTableBody sx={{ 
      '& .MuiTableCell-root': { 
        py: { xs: 0.5, sm: 1 }, 
        px: { xs: 1, sm: 2 }, 
        fontSize: { xs: 12, sm: 13 } 
      },
      // Enhanced table row styling
      '& .MuiTableRow-root': {
        transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
        borderRadius: 1,
        '&:hover': {
          backgroundColor: 'action.hover',
          transform: 'translateY(-2px)',
          boxShadow: '0 4px 12px rgba(0,0,0,0.15), 0 2px 4px rgba(0,0,0,0.1)',
          '& .MuiTableCell-root': {
            borderBottom: '1px solid',
            borderColor: 'divider'
          }
        }
      }
    }}>
      {/* Render events in chronological order */}
      {sortedEvents.map((item) => {
        // Check if this is a grouped event or individual event
        if ('hasInterestWithholdingPair' in item) {
          // This is a GroupedEvent
          return (
            <GroupedEventRow
              key={`${item.date}-combined`}
              groupedEvent={item}
              fund={fund}
              showTaxEvents={showTaxEvents}
              showNavUpdates={showNavUpdates}
              onEditEvent={onEditEvent}
              onDeleteEvent={onDeleteEvent}
            />
          );
        } else {
          // This is an ExtendedFundEvent
          return (
            <EventRow
              key={item.id}
              event={item}
              fund={fund}
              showTaxEvents={showTaxEvents}
              showNavUpdates={showNavUpdates}
              onEditEvent={onEditEvent}
              onDeleteEvent={onDeleteEvent}
            />
          );
        }
      })}
    </MuiTableBody>
  );
};

export default TableBody; 