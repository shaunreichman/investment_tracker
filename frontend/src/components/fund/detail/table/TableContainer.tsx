import React from 'react';
import {
  TableContainer,
  Table,
  Box,
  Typography
} from '@mui/material';
import { ExtendedFundEvent, ExtendedFund } from '../../../../types/api';
import TableFilters from './TableFilters';
import TableHeader from './TableHeader';
import TableBody from './TableBody';

// ============================================================================
// TABLE CONTAINER COMPONENT
// ============================================================================

export interface TableContainerProps {
  events: ExtendedFundEvent[];
  fund: ExtendedFund;
  showTaxEvents: boolean;
  showNavUpdates: boolean;
  onShowTaxEventsChange: (show: boolean) => void;
  onShowNavUpdatesChange: (show: boolean) => void;
  onAddEvent: () => void;

  onDeleteEvent: (event: ExtendedFundEvent) => void;
}

/**
 * Complete table container that combines all extracted table components
 * Extracted from FundDetail.tsx lines 400-1084 for reusability and testing
 * 
 * This component:
 * 1. Combines TableFilters, TableHeader, and TableBody
 * 2. Handles all table state management
 * 3. Maintains all existing styling and responsive behavior
 * 4. Provides clean interface for parent components
 */
const TableContainerComponent: React.FC<TableContainerProps> = ({
  events,
  fund,
  showTaxEvents,
  showNavUpdates,
  onShowTaxEventsChange,
  onShowNavUpdatesChange,
  onAddEvent,

  onDeleteEvent
}) => {
  // Calculate filtered event count for header display
  const filteredEventCount = events.filter(event => {
    if (!showTaxEvents && (event.event_type === 'TAX_PAYMENT' || event.event_type === 'EOFY_DEBT_COST')) {
      return false;
    }
    if (!showNavUpdates && event.event_type === 'NAV_UPDATE') {
      return false;
    }
    return true;
  }).length;

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      {/* Table Header with Filters */}
      <Box sx={{ 
        p: 3, 
        borderBottom: 1, 
        borderColor: 'divider',
        bgcolor: 'background.sidebar',
        flexShrink: 0 // Prevent header from shrinking
      }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography 
            variant="h6"
            sx={{ 
              fontWeight: 600,
              color: 'text.primary',
              letterSpacing: '-0.01em'
            }}
          >
            Fund Events ({filteredEventCount})
          </Typography>
          
          {/* Table Filters */}
          <TableFilters
            showTaxEvents={showTaxEvents}
            showNavUpdates={showNavUpdates}
            isNavBasedFund={fund.tracking_type === 'nav_based'}
            onShowTaxEventsChange={onShowTaxEventsChange}
            onShowNavUpdatesChange={onShowNavUpdatesChange}
            onAddEventClick={onAddEvent}
          />
        </Box>
      </Box>

      {/* Table Container - Scrollable when content exceeds height */}
      <TableContainer sx={{ 
        flex: 1,
        maxHeight: { xs: 300, sm: 'none' },
        scrollBehavior: 'smooth',
        overflow: 'auto', // Allow internal scrolling
        // Phase 4: Enhanced scrollbar styling with theme colors
        '&::-webkit-scrollbar': {
          width: '8px',
          height: '8px'
        },
        '&::-webkit-scrollbar-track': {
          backgroundColor: 'background.sidebar',
          borderRadius: '4px'
        },
        '&::-webkit-scrollbar-thumb': {
          backgroundColor: 'divider',
          borderRadius: '4px',
          transition: 'background-color 0.2s ease-in-out',
          '&:hover': {
            backgroundColor: 'primary.main'
          }
        },
        // Responsive optimization: Better mobile table experience
        fontSize: { xs: '12px', sm: '13px' }
      }}>
        <Table stickyHeader size="small">
          {/* Table Header */}
          <TableHeader
            isNavBasedFund={fund.tracking_type === 'nav_based'}
            showTaxEvents={showTaxEvents}
          />
          
          {/* Table Body */}
          <TableBody
            events={events}
            fund={fund}
            showTaxEvents={showTaxEvents}
            showNavUpdates={showNavUpdates}

            onDeleteEvent={onDeleteEvent}
          />
        </Table>
      </TableContainer>
    </Box>
  );
};

export default TableContainerComponent; 