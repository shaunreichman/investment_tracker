import React, { useState, Suspense, useCallback } from 'react';
import { Typography, Box, useTheme } from '@mui/material';
import { useParams, useNavigate } from 'react-router-dom';

import { ErrorDisplay } from '../../ErrorDisplay';
import { ConfirmDialog } from '../../ui/ConfirmDialog';
import { LoadingSpinner } from '../../ui/LoadingSpinner';
import { ExtendedFundEvent, FundType } from '../../../types/api';
import { useCentralizedFundDetail, useDeleteFundEvent } from '../../../hooks/useFunds';
import { formatCurrency, formatDate } from '../../../utils/formatters';
import { useSidebarState, useTableFilters } from '../../../store';

// Import all the extracted section components
import {
  EquitySection,
  ExpectedPerformanceSection,
  CompletedPerformanceSection,
  FundDetailsSection,
  TransactionSummarySection,
} from './';
import FundDetailHeader from './FundDetailHeader';

// Import the extracted table components
import TableContainer from './table/TableContainer';

const CreateFundEventModal = React.lazy(() => import('../events/CreateFundEventModal'));
const UnitPriceChartSection = React.lazy(() => import('./summary/UnitPriceChartSection'));

// ============================================================================
// MAIN FUND DETAIL COMPONENT
// ============================================================================

const FundDetail: React.FC = () => {
  const { fundId } = useParams<{ fundId: string }>();
  const navigate = useNavigate();
  const theme = useTheme();
  
  // Modal state management
  const [eventModalOpen, setEventModalOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [selectedEvent, setSelectedEvent] = useState<ExtendedFundEvent | null>(null);
  const [deletingEvent, setDeletingEvent] = useState(false);

  // Centralized state management using Zustand store
  const { isVisible: sidebarVisible, toggle: toggleSidebar } = useSidebarState('fundDetail');
  const { filters: tableFilters, updateFilters } = useTableFilters();

  // Centralized API hooks
  const { data: fundData, loading, error, refetch } = useCentralizedFundDetail(Number(fundId));
  const deleteFundEvent = useDeleteFundEvent(Number(fundId), selectedEvent?.id || 0);

  // Event handlers
  const handleEventCreated = useCallback(() => {
    setEventModalOpen(false);
    refetch();
  }, [refetch]);

  const openEventModal = useCallback(() => {
    setEventModalOpen(true);
  }, []);

  const handleDeleteEvent = useCallback((event: ExtendedFundEvent) => {
    setSelectedEvent(event);
    setDeleteDialogOpen(true);
  }, []);

  const confirmDeleteEvent = useCallback(async () => {
    if (!selectedEvent) return;
    
    setDeletingEvent(true);
    try {
      await deleteFundEvent.mutate();
      setDeleteDialogOpen(false);
      setSelectedEvent(null);
      refetch();
    } catch (err) {
      console.error('Failed to delete event:', err);
    } finally {
      setDeletingEvent(false);
    }
  }, [selectedEvent, deleteFundEvent, refetch]);

  // Loading state
  if (loading) {
    return (
      <Box sx={{ p: 3 }}>
        <LoadingSpinner label="Loading fund details..." />
      </Box>
    );
  }

  // Error state
  if (error) {
    return (
      <Box sx={{ p: 3 }}>
        <ErrorDisplay
          error={error}
          canRetry={error.retryable}
          onRetry={() => refetch()}
          onDismiss={() => navigate('/')}
          variant="inline"
        />
      </Box>
    );
  }

  // No data state
  if (!fundData) {
    return (
      <Box sx={{ p: 3 }}>
        <Box sx={{ 
          p: 3, 
          backgroundColor: theme.palette.background.paper,
          border: `1px solid ${theme.palette.divider}`,
          borderRadius: '8px',
          display: 'flex', 
          alignItems: 'center',
          borderLeft: `4px solid ${theme.palette.warning.main}`
        }}>
          <Typography 
            variant="body1" 
            sx={{ 
              fontWeight: 500, 
              color: theme.palette.warning.main
            }}
          >
            No fund data available
          </Typography>
        </Box>
      </Box>
    );
  }

  const { fund, events } = fundData;

  return (
    <Box sx={{ 
      p: 0, 
      height: '100%', // Inherit height from parent container (not viewport)
      display: 'grid',
      gridTemplateRows: 'auto 1fr', // Header takes what it needs, content takes remaining
      minHeight: 0, // Allow grid item to shrink below content size
      overflow: 'hidden' // Prevent page-level scrollbar
    }}>
      <FundDetailHeader fund={fund} sidebarVisible={sidebarVisible} onToggleSidebar={toggleSidebar} />

      {/* Main Layout - Grid item that fills remaining space */}
      <Box sx={{ 
        display: 'flex', 
        flexDirection: { xs: 'column', sm: 'row' },
        gap: { xs: 2, sm: 3 },
        minHeight: 0, // Critical: allow grid item to shrink below content size
        alignItems: 'stretch',
        transition: 'all 0.3s ease-in-out',
        overflow: 'hidden', // Prevent page-level scrollbar
        '& > *:first-of-type': {
          borderRight: { sm: `1px solid ${theme.palette.divider}` },
          pr: { sm: 3 }
        }
      }}>
        {/* Left Sidebar - Summary Sections */}
        <Box sx={{ 
          width: sidebarVisible ? { xs: '100%', sm: '322px', md: '368px', lg: '414px' } : 0,
          flexShrink: 0,
          position: { xs: 'static', sm: 'relative' },
          height: '100%', // Use full height from grid parent
          minHeight: 0, // Allow flex item to shrink
          display: 'flex',
          flexDirection: 'column',
          transition: 'all 0.3s ease-in-out',
          order: { xs: 1, sm: 0 },
          mb: { xs: 2, sm: 0 },
          backgroundColor: theme.palette.background.paper,
          border: `1px solid ${theme.palette.divider}`,
          borderRadius: { sm: '8px' },
          boxShadow: '0px 4px 16px rgba(0,0,0,0.2)',
          opacity: sidebarVisible ? 1 : 0,
          visibility: sidebarVisible ? 'visible' : 'hidden',
          transform: sidebarVisible ? 'translateX(0)' : 'translateX(-100%)'
        }}>
          {/* Summary Section Header */}
          <Box sx={{ 
            p: 3, 
            borderBottom: `1px solid ${theme.palette.divider}`,
            backgroundColor: theme.palette.background.sidebar,
            flexShrink: 0 // Prevent header from shrinking
          }}>
            <Typography 
              variant="h5"
              sx={{ 
                fontWeight: 600,
                color: theme.palette.text.primary,
                letterSpacing: '-0.01em',
                fontSize: '20px'
              }}
            >
              Summary
            </Typography>
          </Box>
          
          {/* Summary Sections - Scrollable container */}
          <Box sx={{ 
            flex: 1, 
            overflowY: 'auto',
            minHeight: 0 // Allow flex item to shrink
          }}>
            <EquitySection fund={fund} formatCurrency={formatCurrency} formatDate={formatDate} />
            <ExpectedPerformanceSection fund={fund} formatCurrency={formatCurrency} formatDate={formatDate} />
            <CompletedPerformanceSection fund={fund} formatCurrency={formatCurrency} formatDate={formatDate} />
            <FundDetailsSection fund={fund} formatCurrency={formatCurrency} formatDate={formatDate} />
            <TransactionSummarySection fund={fund} formatCurrency={formatCurrency} formatDate={formatDate} />
            <Suspense fallback={null}>
              <UnitPriceChartSection fund={fund} formatCurrency={formatCurrency} formatDate={formatDate} events={events} />
            </Suspense>
          </Box>
        </Box>

        {/* Right Main Area - Events Table */}
        <Box sx={{ 
          flex: 1,
          minWidth: 0,
          height: '100%', // Use full height from grid parent
          minHeight: 0, // Allow flex item to shrink
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden', // Container overflow hidden, but table can scroll internally
          order: { xs: 2, sm: 1 },
          width: { xs: '100%', sm: 'auto' },
          backgroundColor: theme.palette.background.paper,
          border: `1px solid ${theme.palette.divider}`,
          borderRadius: { sm: '8px' },
          boxShadow: '0px 4px 16px rgba(0,0,0,0.2)',
          pl: { sm: 3 }
        }}>
          {/* Use the extracted TableContainer component */}
          <TableContainer
            fund={fund}
            events={events}
            showTaxEvents={tableFilters.showTaxEvents}
            showNavUpdates={tableFilters.showNavUpdates}
            onShowTaxEventsChange={(value) => updateFilters({ showTaxEvents: value })}
            onShowNavUpdatesChange={(value) => updateFilters({ showNavUpdates: value })}
            onAddEvent={openEventModal}
            onDeleteEvent={handleDeleteEvent}
          />
        </Box>
      </Box>

      {/* Modals */}
      <Suspense fallback={null}>
        <CreateFundEventModal
          open={eventModalOpen}
          onClose={() => setEventModalOpen(false)}
          onSuccess={handleEventCreated}
          fundId={Number(fundId)}
          fundTrackingType={fund.tracking_type}
        />
      </Suspense>

      <ConfirmDialog
        open={deleteDialogOpen}
        title="Delete Event"
        description="Are you sure you want to delete this event? This action cannot be undone."
        confirmLabel="Delete"
        loading={deletingEvent}
        onCancel={() => setDeleteDialogOpen(false)}
        onConfirm={confirmDeleteEvent}
      />
    </Box>
  );
};

export default FundDetail; 