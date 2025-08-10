import React from 'react';
import { TableBody as MuiTableBody } from '@mui/material';
import { ExtendedFundEvent, ExtendedFund } from '../../../../types/api';
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

  onDeleteEvent: (event: ExtendedFundEvent) => void;
}

/**
 * Component to render the table body with integrated event grouping logic
 * Extracted from FundDetail.tsx lines 650-1084 for reusability and testing
 * 
 * This component:
 * 1. Uses useEventGrouping hook to process events with flag-based grouping
 * 2. Renders GroupedEventRow for grouped events (interest + withholding, tax statements)
 * 3. Renders EventRow for individual events
 * 4. Maintains all existing styling and responsive behavior
 */
export const TableBody: React.FC<TableBodyProps> = ({
  events,
  fund,
  showTaxEvents,
  showNavUpdates,

  onDeleteEvent
}) => {
  // CALCULATED: Use the new flag-based event grouping hook
  const groupedEvents = useEventGrouping(events);

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
      {/* Render grouped events and individual events */}
      {groupedEvents.map((item) => {
        // CALCULATED: Check if this is a grouped event or individual event
        if (item.isGrouped) {
          // This is a GroupedEvent (interest + withholding, tax statement, etc.)
          return (
            <GroupedEventRow
              key={`group-${item.groupId}-${item.displayDate}`}
              groupedEvent={item}
              fund={fund}
              showTaxEvents={showTaxEvents}
              showNavUpdates={showNavUpdates}
              onDeleteEvent={onDeleteEvent}
            />
          );
        } else {
          // This is an individual ExtendedFundEvent
          const firstEvent = item.events[0];
          if (firstEvent) {
            return (
              <EventRow
                key={firstEvent.id}
                event={firstEvent as ExtendedFundEvent}
                fund={fund}
                showTaxEvents={showTaxEvents}
                showNavUpdates={showNavUpdates}
                onDeleteEvent={onDeleteEvent}
              />
            );
          }
          // Return null if no valid event found (shouldn't happen in practice)
          return null;
        }
      })}
    </MuiTableBody>
  );
};

export default TableBody; 