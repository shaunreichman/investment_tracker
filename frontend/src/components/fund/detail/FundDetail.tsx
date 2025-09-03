import React, { useState, Suspense, useCallback } from 'react';
import { Typography, Box, useTheme } from '@mui/material';
import { useParams, useNavigate } from 'react-router-dom';

import { ErrorDisplay } from '../../ErrorDisplay';
import { ConfirmDialog } from '../../ui/ConfirmDialog';
import { LoadingSpinner } from '../../ui/LoadingSpinner';
import { ExtendedFundEvent } from '../../../types/api';
import { useCentralizedFundDetail, useDeleteFundEvent, useFundEvents, useFundSummary, useFundMetadata } from '../../../hooks/useFunds';
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
  const [isUpdatingSummary, setIsUpdatingSummary] = useState(false);
  const [showUpdateSuccess, setShowUpdateSuccess] = useState(false);
  
  // ENTERPRISE: Granular loading states for individual sections
  const [sectionLoadingStates, setSectionLoadingStates] = useState({
    equity: false,
    expectedPerformance: false,
    completedPerformance: false,
    fundDetails: false,
    transactionSummary: false,
    unitPriceChart: false
  });

  // ENTERPRISE: Removed smooth transition logic - using proper memoization instead

  // Centralized state management using Zustand store
  const { isVisible: sidebarVisible, toggle: toggleSidebar } = useSidebarState('fundDetail');
  const { filters: tableFilters, updateFilters } = useTableFilters();

  // PHASE 1: Separate data streams for independent refresh
  // Events data - refreshes immediately (fast)
  const { data: eventsData, loading: eventsLoading, refetch: refetchEvents } = useFundEvents(Number(fundId));
  
  // Summary data - refreshes with delay (computational sections)
  const { data: summaryData, loading: summaryLoading, refetch: refetchSummary } = useFundSummary(Number(fundId));
  
  // Metadata - static data that rarely changes
  const { data: fundMetadata, loading: metadataLoading } = useFundMetadata(Number(fundId));
  
  // Legacy hook for backward compatibility (will be removed in Phase 2)
  const { data: fundData, loading, error, refetch: refetchFundDetail } = useCentralizedFundDetail(Number(fundId));
  
  const deleteFundEvent = useDeleteFundEvent(Number(fundId), selectedEvent?.id || 0);

  // ENTERPRISE: Removed smooth transition effects - using proper memoization instead

  // ENTERPRISE: Helper functions for granular loading state management
  // Note: setSectionLoading removed as it's not currently used

  const setAllSectionsLoading = useCallback((isLoading: boolean) => {
    console.log(`🔄 [DEBUG] All sections loading state: ${isLoading ? 'STARTING' : 'COMPLETED'}`);
    console.log(`🔄 [DEBUG] Current section states:`, sectionLoadingStates);
    setSectionLoadingStates({
      equity: isLoading,
      expectedPerformance: isLoading,
      completedPerformance: isLoading,
      fundDetails: isLoading,
      transactionSummary: isLoading,
      unitPriceChart: isLoading
    });
  }, [sectionLoadingStates]);

  // PHASE 1: Extract data from separate streams
  // Use new data streams when available, fallback to legacy for backward compatibility
  const fund = React.useMemo(() => 
    summaryData?.fund || fundData?.fund, 
    [summaryData?.fund, fundData?.fund]
  );
  
  const events: ExtendedFundEvent[] = React.useMemo(() => 
    (eventsData as ExtendedFundEvent[]) || fundData?.events || [], 
    [eventsData, fundData?.events]
  );
  
  const statistics = React.useMemo(() => 
    summaryData?.statistics || fundData?.statistics, 
    [summaryData?.statistics, fundData?.statistics]
  );

  const equitySectionProps = React.useMemo(() => ({
    fund: fund!,
    formatCurrency,
    formatDate,
    isLoading: sectionLoadingStates.equity
  }), [fund, sectionLoadingStates.equity]);

  const expectedPerformanceSectionProps = React.useMemo(() => ({
    fund: fund!,
    formatCurrency,
    formatDate,
    isLoading: sectionLoadingStates.expectedPerformance
  }), [fund, sectionLoadingStates.expectedPerformance]);

  const completedPerformanceSectionProps = React.useMemo(() => ({
    fund: fund!,
    formatCurrency,
    formatDate,
    isLoading: sectionLoadingStates.completedPerformance
  }), [fund, sectionLoadingStates.completedPerformance]);

  const fundDetailsSectionProps = React.useMemo(() => ({
    fund: fund!,
    formatCurrency,
    formatDate,
    isLoading: sectionLoadingStates.fundDetails
  }), [fund, sectionLoadingStates.fundDetails]);

  const transactionSummarySectionProps = React.useMemo(() => ({
    fund: fund!,
    formatCurrency,
    formatDate,
    isLoading: sectionLoadingStates.transactionSummary
  }), [fund, sectionLoadingStates.transactionSummary]);

  const unitPriceChartSectionProps = React.useMemo(() => ({
    fund: fund!,
    formatCurrency,
    formatDate,
    events,
    isLoading: sectionLoadingStates.unitPriceChart
  }), [fund, events, sectionLoadingStates.unitPriceChart]);

  // PHASE 1: Targeted refresh handlers using separate data streams
  const handleEventCreated = useCallback(() => {
    console.log('🚀 [PHASE 1] Event created - starting targeted refresh');
    setEventModalOpen(false);
    
    // Phase 1: Immediate refresh of events table (fast)
    console.log('⚡ [PHASE 1] Refreshing events table immediately');
    refetchEvents();
    
    // Phase 2: Targeted refresh of summary sections only
    console.log('🔄 [PHASE 1] Setting summary sections to loading state');
    setAllSectionsLoading(true);
    setIsUpdatingSummary(true);
    
    // Use the new targeted refresh instead of full page refresh
    const refreshDelay = 3000; // 3 seconds for visual assessment of refresh behavior
    console.log(`⏱️ [PHASE 1] Starting ${refreshDelay}ms delay before summary refresh`);
    setTimeout(() => {
      console.log('🔄 [PHASE 1] Starting summary refresh after delay');
      refetchSummary().finally(() => {
        console.log('✅ [PHASE 1] Summary refresh completed - clearing loading states');
        // Clear all loading states when complete
        setAllSectionsLoading(false);
        setIsUpdatingSummary(false);
        setShowUpdateSuccess(true);
        // Hide success message after 2 seconds
        setTimeout(() => setShowUpdateSuccess(false), 2000);
      });
    }, refreshDelay);
  }, [refetchEvents, refetchSummary, setAllSectionsLoading]);

  const openEventModal = useCallback(() => {
    setEventModalOpen(true);
  }, []);

  const handleDeleteEvent = useCallback((event: ExtendedFundEvent) => {
    setSelectedEvent(event);
    setDeleteDialogOpen(true);
  }, []);

  const confirmDeleteEvent = useCallback(async () => {
    if (!selectedEvent) return;
    
    console.log('🗑️ [PHASE 1] Event deletion started');
    setDeletingEvent(true);
    try {
      await deleteFundEvent.mutate();
      console.log('✅ [PHASE 1] Event deletion completed - starting targeted refresh');
      setDeleteDialogOpen(false);
      setSelectedEvent(null);
      
      // PHASE 1: Targeted refresh for deletion using separate data streams
      // Phase 1: Immediate refresh of events table (fast)
      console.log('⚡ [PHASE 1] Refreshing events table immediately');
      refetchEvents();
      
      // Phase 2: Targeted refresh of summary sections only
      console.log('🔄 [PHASE 1] Setting summary sections to loading state');
      setAllSectionsLoading(true);
      setIsUpdatingSummary(true);
      
      // Use the new targeted refresh instead of full page refresh
      const refreshDelay = 3000; // 3 seconds for visual assessment of refresh behavior
      console.log(`⏱️ [PHASE 1] Starting ${refreshDelay}ms delay before summary refresh`);
      setTimeout(() => {
        console.log('🔄 [PHASE 1] Starting summary refresh after delay');
        refetchSummary().finally(() => {
          console.log('✅ [PHASE 1] Summary refresh completed - clearing loading states');
          // Clear all loading states when complete
          setAllSectionsLoading(false);
          setIsUpdatingSummary(false);
          setShowUpdateSuccess(true);
          // Hide success message after 2 seconds
          setTimeout(() => setShowUpdateSuccess(false), 2000);
        });
      }, refreshDelay);
    } catch (err) {
      console.error('❌ [PHASE 1] Failed to delete event:', err);
    } finally {
      setDeletingEvent(false);
    }
  }, [selectedEvent, deleteFundEvent, refetchEvents, refetchSummary, setAllSectionsLoading]);

  // PHASE 1: Only show full-page loading for initial loads, not refreshes
  // This prevents the "whole page reset" issue during targeted refreshes
  if (loading || eventsLoading || summaryLoading || metadataLoading) {
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
          onRetry={() => refetchFundDetail()}
          onDismiss={() => navigate('/')}
          variant="inline"
        />
      </Box>
    );
  }

  // ENTERPRISE: Data and props are now memoized above, before any early returns

  // No data state
  if (!fundData || !fund) {
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
            
            {/* ENTERPRISE: Debug panel for testing loading states */}
            {process.env.NODE_ENV === 'development' && (
              <Box sx={{ 
                mt: 2, 
                p: 1, 
                backgroundColor: theme.palette.grey[100], 
                borderRadius: 1,
                fontSize: '10px',
                fontFamily: 'monospace'
              }}>
                <Typography variant="caption" sx={{ fontWeight: 'bold', color: theme.palette.primary.main }}>
                  🔍 DEBUG - Section Loading States (Memoized):
                </Typography>
                <Box sx={{ mt: 0.5 }}>
                  {Object.entries(sectionLoadingStates).map(([section, loading]) => (
                    <Box key={section} sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                      <Box sx={{ 
                        width: 8, 
                        height: 8, 
                        borderRadius: '50%', 
                        backgroundColor: loading ? theme.palette.primary.main : theme.palette.grey[400]
                      }} />
                      <Typography variant="caption" sx={{ fontSize: '9px' }}>
                        {section}: {loading ? 'LOADING' : 'READY'}
                      </Typography>
                    </Box>
                  ))}
                </Box>
              </Box>
            )}
          </Box>
          
          {/* Summary Sections - Scrollable container */}
          <Box sx={{ 
            flex: 1, 
            overflowY: 'auto',
            minHeight: 0 // Allow flex item to shrink
          }}>
            {/* ENTERPRISE: Use memoized props to prevent unnecessary re-renders */}
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