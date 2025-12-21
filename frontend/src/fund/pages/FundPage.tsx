/**
 * FundPage Component
 * 
 * Main page for displaying a single fund with detail view.
 * Handles orchestration logic (useParams, state, data fetching, error handling).
 * Presentation is handled by components in fund/components/fund-detail/.
 */

import React, { useState, Suspense, useCallback, useMemo } from 'react';
import { Typography, Box, useTheme } from '@mui/material';
import { useParams, useNavigate } from 'react-router-dom';

import { ErrorDisplay, LoadingSpinner } from '@/shared/ui/feedback';
import { ConfirmDialog } from '@/shared/ui/overlays';
import { ErrorType } from '@/shared/types/errors';
import { createErrorInfo } from '@/shared/utils/errors';
import { formatCurrency, formatDate } from '@/shared/utils/formatters';
import { useSidebarState, useTableFilters } from '@/store';

// Fund domain imports
import { useFund, useFundEventsByFundId, useDeleteFundEvent } from '../hooks';
import type { FundEvent } from '../types';
import {
  EquitySection,
  ExpectedPerformanceSection,
  CompletedPerformanceSection,
  FundDetailsSection,
  TransactionSummarySection,
} from '../components/fund-detail/summary';
import { FundDetailHeader } from '../components/fund-detail';
import { TableContainer } from '../components/fund-detail/table';

// Lazy load heavy components
const CreateFundEventModal = React.lazy(() => import('../components/fund-events/CreateFundEventModal'));
const UnitPriceChartSection = React.lazy(() => import('../components/fund-detail/summary/UnitPriceChartSection'));

// ============================================================================
// COMPONENT
// ============================================================================

export const FundPage: React.FC = () => {
  const { fundId } = useParams<{ fundId: string }>();
  const navigate = useNavigate();
  const theme = useTheme();
  
  const fundIdNum = Number(fundId || '0');
  
  // Modal state management
  const [eventModalOpen, setEventModalOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [selectedEvent, setSelectedEvent] = useState<FundEvent | null>(null);
  const [deletingEvent, setDeletingEvent] = useState(false);
  const [isUpdatingSummary, setIsUpdatingSummary] = useState(false);
  const [showUpdateSuccess, setShowUpdateSuccess] = useState(false);
  
  // Granular loading states for individual sections
  const [sectionLoadingStates, setSectionLoadingStates] = useState({
    equity: false,
    expectedPerformance: false,
    completedPerformance: false,
    fundDetails: false,
    transactionSummary: false,
    unitPriceChart: false
  });

  // Centralized state management using Zustand store
  const { isVisible: sidebarVisible, toggle: toggleSidebar } = useSidebarState('fundDetail');
  const { filters: tableFilters, updateFilters } = useTableFilters();

  // Data fetching - using new domain hooks
  const { data: fund, loading: fundLoading, refetch: refetchFund } = useFund(fundIdNum);
  const { data: eventsData, loading: eventsLoading, refetch: refetchEvents } = useFundEventsByFundId(fundIdNum);
  
  const deleteFundEvent = useDeleteFundEvent(fundIdNum, selectedEvent?.id || 0);

  // Helper functions for granular loading state management
  const setAllSectionsLoading = useCallback((isLoading: boolean) => {
    setSectionLoadingStates({
      equity: isLoading,
      expectedPerformance: isLoading,
      completedPerformance: isLoading,
      fundDetails: isLoading,
      transactionSummary: isLoading,
      unitPriceChart: isLoading
    });
  }, []);

  // Extract events from API response
  const events: FundEvent[] = useMemo(() => 
    (eventsData || []) as FundEvent[], 
    [eventsData]
  );

  // Memoized props for summary sections
  const equitySectionProps = useMemo(() => ({
    fund: fund!,
    formatCurrency,
    formatDate,
    isLoading: sectionLoadingStates.equity
  }), [fund, sectionLoadingStates.equity]);

  const expectedPerformanceSectionProps = useMemo(() => ({
    fund: fund!,
    formatCurrency,
    formatDate,
    isLoading: sectionLoadingStates.expectedPerformance
  }), [fund, sectionLoadingStates.expectedPerformance]);

  const completedPerformanceSectionProps = useMemo(() => ({
    fund: fund!,
    formatCurrency,
    formatDate,
    isLoading: sectionLoadingStates.completedPerformance
  }), [fund, sectionLoadingStates.completedPerformance]);

  const fundDetailsSectionProps = useMemo(() => ({
    fund: fund!,
    formatCurrency,
    formatDate,
    isLoading: sectionLoadingStates.fundDetails
  }), [fund, sectionLoadingStates.fundDetails]);

  const transactionSummarySectionProps = useMemo(() => ({
    fund: fund!,
    formatCurrency,
    formatDate,
    isLoading: sectionLoadingStates.transactionSummary
  }), [fund, sectionLoadingStates.transactionSummary]);

  const unitPriceChartSectionProps = useMemo(() => ({
    fund: fund!,
    formatCurrency,
    formatDate,
    events,
    isLoading: sectionLoadingStates.unitPriceChart
  }), [fund, events, sectionLoadingStates.unitPriceChart]);

  // Targeted refresh handlers using separate data streams
  const handleEventCreated = useCallback(() => {
    setEventModalOpen(false);
    
    // Immediate refresh of events table
    refetchEvents();
    
    // Targeted refresh of summary sections
    setAllSectionsLoading(true);
    setIsUpdatingSummary(true);
    
    const refreshDelay = 3000; // 3 seconds for visual assessment
    setTimeout(() => {
      refetchFund().finally(() => {
        setAllSectionsLoading(false);
        setIsUpdatingSummary(false);
        setShowUpdateSuccess(true);
        setTimeout(() => setShowUpdateSuccess(false), 2000);
      });
    }, refreshDelay);
  }, [refetchEvents, refetchFund, setAllSectionsLoading]);

  const openEventModal = useCallback(() => {
    setEventModalOpen(true);
  }, []);

  const handleDeleteEvent = useCallback((event: FundEvent) => {
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
      
      // Targeted refresh for deletion using separate data streams
      // Immediate refresh of events table
      refetchEvents();
      
      // Targeted refresh of summary sections
      setAllSectionsLoading(true);
      setIsUpdatingSummary(true);
      
      const refreshDelay = 3000; // 3 seconds for visual assessment
      setTimeout(() => {
        refetchFund().finally(() => {
          setAllSectionsLoading(false);
          setIsUpdatingSummary(false);
          setShowUpdateSuccess(true);
          setTimeout(() => setShowUpdateSuccess(false), 2000);
        });
      }, refreshDelay);
    } catch (err) {
      console.error('Failed to delete event:', err);
    } finally {
      setDeletingEvent(false);
    }
  }, [selectedEvent, deleteFundEvent, refetchEvents, refetchFund, setAllSectionsLoading]);

  // Only show full-page loading for initial loads, not refreshes
  if (fundLoading || eventsLoading) {
    return (
      <Box sx={{ p: 3 }}>
        <LoadingSpinner label="Loading fund details..." />
      </Box>
    );
  }

  // Error state handling for separate data streams
  const hasError = (fund === null && !fundLoading) || (eventsData === null && !eventsLoading);
  
  if (hasError) {
    return (
      <Box sx={{ p: 3 }}>
        <ErrorDisplay
          error={createErrorInfo(
            'Failed to load fund data',
            ErrorType.NETWORK
          )}
          onRetry={() => {
            // Retry all data streams
            refetchEvents();
            refetchFund();
          }}
          onDismiss={() => navigate('/')}
        />
      </Box>
    );
  }

  // No data state check
  if (!fund) {
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

  return (
    <Box sx={{ 
      p: 0, 
      height: '100%', // Inherit height from parent container (not viewport)
      display: 'grid',
      gridTemplateRows: 'auto 1fr', // Header takes what it needs, content takes remaining
      minHeight: 0, // Allow grid item to shrink below content size
      overflow: 'hidden' // Prevent page-level scrollbar
    }}>
      <FundDetailHeader 
        fund={fund} 
        sidebarVisible={sidebarVisible} 
        onToggleSidebar={toggleSidebar} 
      />

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
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
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
              {isUpdatingSummary && (
                <Box sx={{ 
                  display: 'flex', 
                  alignItems: 'center', 
                  gap: 1,
                  color: theme.palette.primary.main,
                  fontSize: '12px'
                }}>
                  <Box sx={{ 
                    width: 12, 
                    height: 12, 
                    border: `2px solid ${theme.palette.primary.main}`,
                    borderTop: '2px solid transparent',
                    borderRadius: '50%',
                    animation: 'spin 1s linear infinite',
                    '@keyframes spin': {
                      '0%': { transform: 'rotate(0deg)' },
                      '100%': { transform: 'rotate(360deg)' }
                    }
                  }} />
                  <Typography variant="caption" sx={{ color: theme.palette.primary.main }}>
                    Updating...
                  </Typography>
                </Box>
              )}
              {showUpdateSuccess && !isUpdatingSummary && (
                <Box sx={{ 
                  display: 'flex', 
                  alignItems: 'center', 
                  gap: 1,
                  color: theme.palette.success.main,
                  fontSize: '12px'
                }}>
                  <Typography variant="caption" sx={{ color: theme.palette.success.main }}>
                    ✓ Updated
                  </Typography>
                </Box>
              )}
            </Box>
          </Box>
          
          {/* Summary Sections - Scrollable container */}
          <Box sx={{ 
            flex: 1, 
            overflowY: 'auto',
            minHeight: 0 // Allow flex item to shrink
          }}>
            {/* Use memoized props to prevent unnecessary re-renders */}
            <EquitySection {...equitySectionProps} />
            <ExpectedPerformanceSection {...expectedPerformanceSectionProps} />
            <CompletedPerformanceSection {...completedPerformanceSectionProps} />
            <FundDetailsSection {...fundDetailsSectionProps} />
            <TransactionSummarySection {...transactionSummarySectionProps} />
            <Suspense fallback={null}>
              {/* @ts-ignore - Lazy component type inference issue */}
              <UnitPriceChartSection {...unitPriceChartSectionProps} />
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
          fundId={fundIdNum}
          fundTrackingType={fund.tracking_type}
        />
      </Suspense>

      <ConfirmDialog
        open={deleteDialogOpen}
        title="Delete Event"
        description="Are you sure you want to delete this event? This action cannot be undone."
        confirmAction={{
          label: 'Delete',
          variant: 'error',
          onClick: confirmDeleteEvent,
          loading: deletingEvent
        }}
        cancelAction={{
          label: 'Cancel',
          variant: 'outlined',
          onClick: () => setDeleteDialogOpen(false)
        }}
      />
    </Box>
  );
};

