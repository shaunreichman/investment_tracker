import React, { useState } from 'react';
import {
  Typography,
  Box,
  CircularProgress,
  Breadcrumbs,
  Link,
  IconButton,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  DialogContentText
} from '@mui/material';
import { ChevronLeft, ChevronRight } from '@mui/icons-material';
import { useParams, useNavigate } from 'react-router-dom';
import { ErrorDisplay } from './ErrorDisplay';
import CreateFundEventModal from './CreateFundEventModal';
import EditFundEventModal from './EditFundEventModal';
import { 
  ExtendedFundEvent,
  ExtendedFund
} from '../types/api';
import { useFundDetail, useDeleteFundEvent } from '../hooks/useFunds';
import { formatCurrency, formatDate } from '../utils/formatters';

// Import all the extracted section components
import {
  EquitySection,
  ExpectedPerformanceSection,
  CompletedPerformanceSection,
  FundDetailsSection,
  TransactionSummarySection,
  UnitPriceChartSection
} from './fund-detail';

// Import the extracted table components
import { TableContainer } from './fund-detail/FundDetailTable';

// ============================================================================
// MAIN FUND DETAIL COMPONENT
// ============================================================================

const FundDetail: React.FC = () => {
  const { fundId } = useParams<{ fundId: string }>();
  const navigate = useNavigate();
  
  // Modal state management
  const [eventModalOpen, setEventModalOpen] = useState(false);
  const [editModalOpen, setEditModalOpen] = useState(false);
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
  const handleEventCreated = () => {
    setEventModalOpen(false);
    refetch();
  };

  const handleEventUpdated = () => {
    setEditModalOpen(false);
    setSelectedEvent(null);
    refetch();
  };

  const handleEditEvent = (event: ExtendedFundEvent) => {
    setSelectedEvent(event);
    setEditModalOpen(true);
  };

  const handleDeleteEvent = (event: ExtendedFundEvent) => {
    setSelectedEvent(event);
    setDeleteDialogOpen(true);
  };

  const confirmDeleteEvent = async () => {
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
  };

  // Loading state
  if (loading) {
    return (
      <Box p={3}>
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px" flexDirection="column" gap={2}>
          <CircularProgress 
            size={40} 
            sx={{ 
              color: 'primary.main',
              '& .MuiCircularProgress-circle': {
                strokeLinecap: 'round',
              }
            }} 
          />
          <Typography variant="body2" color="text.secondary" sx={{ opacity: 0.8 }}>
            Loading fund details...
          </Typography>
        </Box>
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
      {/* Breadcrumb Navigation */}
      <Breadcrumbs aria-label="breadcrumb" sx={{ mb: 2 }}>
        <Link
          component="button"
          variant="body2"
          onClick={() => navigate('/')}
          sx={{ textDecoration: 'none', cursor: 'pointer' }}
        >
          Investment Companies
        </Link>
        <Link
          component="button"
          variant="body2"
          onClick={() => navigate(`/companies/${fund.investment_company_id}`)}
          sx={{ textDecoration: 'none', cursor: 'pointer' }}
        >
          {fund.investment_company}
        </Link>
        <Typography color="text.primary">{fund.name}</Typography>
      </Breadcrumbs>

      {/* Header */}
      <Box sx={{ mb: 3, position: 'relative' }}>
        <Typography 
          variant="h4" 
          component="h1" 
          gutterBottom
          sx={{ 
            fontWeight: 600,
            color: 'text.primary',
            letterSpacing: '-0.02em'
          }}
        >
          {fund.name}
        </Typography>
        <Typography 
          variant="subtitle1" 
          color="text.secondary" 
          gutterBottom
          sx={{ 
            fontWeight: 400,
            opacity: 0.8
          }}
        >
          {fund.fund_type} • {fund.entity} • {fund.investment_company}
        </Typography>
        
        {/* Sidebar Toggle Button */}
        <IconButton
          onClick={toggleSidebar}
          sx={{ 
            position: 'absolute', 
            right: 0, 
            top: 0,
            zIndex: 1,
            bgcolor: 'background.paper',
            boxShadow: '0 4px 16px rgba(0,0,0,0.08), 0 2px 6px rgba(0,0,0,0.12)',
            borderRadius: 2,
            transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
            '&:hover': {
              bgcolor: 'action.hover',
              transform: 'translateY(-2px)',
              boxShadow: '0 6px 20px rgba(0,0,0,0.12), 0 3px 8px rgba(0,0,0,0.16)'
            }
          }}
        >
          {sidebarVisible ? <ChevronLeft /> : <ChevronRight />}
        </IconButton>
      </Box>

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
          <UnitPriceChartSection fund={fund} formatCurrency={formatCurrency} formatDate={formatDate} events={events} />
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
            onAddEvent={() => setEventModalOpen(true)}
            onEditEvent={handleEditEvent}
            onDeleteEvent={handleDeleteEvent}
          />
        </Box>
      </Box>

      {/* Modals */}
      <CreateFundEventModal
        open={eventModalOpen}
        onClose={() => setEventModalOpen(false)}
        onEventCreated={handleEventCreated}
        fundId={Number(fundId)}
        fundTrackingType={fund.tracking_type}
      />

      <EditFundEventModal
        open={editModalOpen}
        onClose={() => {
          setEditModalOpen(false);
          setSelectedEvent(null);
        }}
        onEventUpdated={handleEventUpdated}
        event={selectedEvent}
        fundId={Number(fundId)}
      />

      {/* Delete Confirmation Dialog */}
      <Dialog
        open={deleteDialogOpen}
        onClose={() => setDeleteDialogOpen(false)}
        aria-labelledby="delete-dialog-title"
        aria-describedby="delete-dialog-description"
      >
        <DialogTitle id="delete-dialog-title">
          Delete Event
        </DialogTitle>
        <DialogContent>
          <DialogContentText id="delete-dialog-description">
            Are you sure you want to delete this event? This action cannot be undone.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>
            Cancel
          </Button>
          <Button 
            onClick={confirmDeleteEvent} 
            color="error" 
            disabled={deletingEvent}
          >
            {deletingEvent ? 'Deleting...' : 'Delete'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default FundDetail; 