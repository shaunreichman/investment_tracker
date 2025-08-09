import React, { useState, Suspense, useCallback } from 'react';
import { Typography, Box } from '@mui/material';
import { useParams, useNavigate } from 'react-router-dom';
import { ErrorDisplay } from '../../ErrorDisplay';
import { ConfirmDialog } from '../../ui/ConfirmDialog';
import { LoadingSpinner } from '../../ui/LoadingSpinner';
import { ExtendedFundEvent } from '../../../types/api';
import { useFundDetail, useDeleteFundEvent } from '../../../hooks/useFunds';
import { formatCurrency, formatDate } from '../../../utils/formatters';

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
  
  // Modal state management
  const [eventModalOpen, setEventModalOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [selectedEvent, setSelectedEvent] = useState<ExtendedFundEvent | null>(null);
  const [deletingEvent, setDeletingEvent] = useState(false);

  // Table filter state
  const [showTaxEvents, setShowTaxEvents] = useState(true);
  const [showNavUpdates, setShowNavUpdates] = useState(true);

  // Sidebar toggle state with localStorage persistence
  const [sidebarVisible, setSidebarVisible] = useState(() => {
    const saved = localStorage.getItem('fundDetailSidebarVisible');
    return saved !== null ? JSON.parse(saved) : true;
  });

  const toggleSidebar = () => {
    const newState = !sidebarVisible;
    setSidebarVisible(newState);
    localStorage.setItem('fundDetailSidebarVisible', JSON.stringify(newState));
  };

  // Centralized API hooks
  const { data: fundData, loading, error, refetch } = useFundDetail(Number(fundId));
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
      <Box p={3}>
        <LoadingSpinner label="Loading fund details..." />
      </Box>
    );
  }

  // Error state
  if (error) {
    return (
      <Box p={3}>
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
      <Box p={3}>
        <Box sx={{ p: 2, bgcolor: 'warning.light', borderRadius: 1, display: 'flex', alignItems: 'center' }}>
          <Typography variant="body1" fontWeight="medium" color="warning.main">
            No fund data available
          </Typography>
        </Box>
      </Box>
    );
  }

  const { fund, events } = fundData;

  return (
    <Box p={3}>
      <FundDetailHeader fund={fund} sidebarVisible={sidebarVisible} onToggleSidebar={toggleSidebar} />

      {/* Main Layout */}
      <Box sx={{ 
        display: 'flex', 
        flexDirection: { xs: 'column', sm: 'row' },
        gap: { xs: 2, sm: 3 },
        minHeight: { xs: 'auto', sm: 'calc(100vh - 200px)' },
        height: { xs: 'auto', sm: 'calc(100vh - 200px)' },
        alignItems: 'stretch',
        transition: 'all 0.3s ease-in-out',
        '& > *:first-of-type': {
          borderRight: { sm: '1px solid' },
          borderColor: { sm: 'divider' },
          pr: { sm: 2 }
        }
      }}>
        {/* Left Sidebar - Summary Sections */}
        <Box sx={{ 
          width: sidebarVisible ? { xs: '100%', sm: '322px', md: '368px', lg: '414px' } : 0,
          flexShrink: 0,
          position: { xs: 'static', sm: 'relative' },
          height: { xs: 'auto', sm: '100%' },
          overflowY: { xs: 'visible', sm: 'auto' },
          transition: 'all 0.3s ease-in-out',
          overflow: 'hidden',
          order: { xs: 1, sm: 0 },
          mb: { xs: 2, sm: 0 },
          bgcolor: 'background.paper',
          borderRadius: { sm: 2 },
          boxShadow: { sm: '0 4px 16px rgba(0,0,0,0.08), 0 2px 6px rgba(0,0,0,0.12)' },
          display: 'flex',
          flexDirection: 'column',
          opacity: sidebarVisible ? 1 : 0,
          visibility: sidebarVisible ? 'visible' : 'hidden',
          transform: sidebarVisible ? 'translateX(0)' : 'translateX(-100%)'
        }}>
          {/* Summary Section Header */}
          <Box sx={{ 
            p: 3, 
            borderBottom: 1, 
            borderColor: 'divider',
            bgcolor: 'grey.50'
          }}>
            <Typography 
              variant="h6"
              sx={{ 
                fontWeight: 600,
                color: 'text.primary',
                letterSpacing: '-0.01em'
              }}
            >
              Summary
            </Typography>
          </Box>
          
          {/* Summary Sections */}
          <EquitySection fund={fund} formatCurrency={formatCurrency} formatDate={formatDate} />
          <ExpectedPerformanceSection fund={fund} formatCurrency={formatCurrency} formatDate={formatDate} />
          <CompletedPerformanceSection fund={fund} formatCurrency={formatCurrency} formatDate={formatDate} />
          <FundDetailsSection fund={fund} formatCurrency={formatCurrency} formatDate={formatDate} />
          <TransactionSummarySection fund={fund} formatCurrency={formatCurrency} formatDate={formatDate} />
          <Suspense fallback={null}>
            <UnitPriceChartSection fund={fund} formatCurrency={formatCurrency} formatDate={formatDate} events={events} />
          </Suspense>
        </Box>

        {/* Right Main Area - Events Table */}
        <Box sx={{ 
          flex: 1,
          minWidth: 0,
          height: { xs: 'auto', sm: '100%' },
          overflow: 'hidden',
          order: { xs: 2, sm: 1 },
          width: { xs: '100%', sm: 'auto' },
          bgcolor: 'background.paper',
          borderRadius: { sm: 2 },
          boxShadow: { sm: '0 4px 16px rgba(0,0,0,0.08), 0 2px 6px rgba(0,0,0,0.12)' },
          pl: { sm: 2 },
          display: 'flex',
          flexDirection: 'column'
        }}>
          {/* Use the extracted TableContainer component */}
          <TableContainer
            fund={fund}
            events={events}
            showTaxEvents={showTaxEvents}
            showNavUpdates={showNavUpdates}
            onShowTaxEventsChange={setShowTaxEvents}
            onShowNavUpdatesChange={setShowNavUpdates}
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