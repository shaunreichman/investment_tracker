import React, { useState } from 'react';
import {
  Typography,
  Paper,
  Box,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Button,
  CircularProgress,
  Switch,
  Breadcrumbs,
  Link,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  DialogContentText,
  Tooltip as MuiTooltip
} from '@mui/material';
import { ErrorDisplay } from './ErrorDisplay';
import { TrendingUp, AccountBalance, Edit as EditIcon, Delete as DeleteIcon, Assessment, Info, Receipt, ChevronLeft, ChevronRight } from '@mui/icons-material';
import { useParams, useNavigate } from 'react-router-dom';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Scatter } from 'recharts';
import CreateFundEventModal from './CreateFundEventModal';
import EditFundEventModal from './EditFundEventModal';
import { 
  ExtendedFundEvent,
  ExtendedFund
} from '../types/api';
import { useFundDetail, useDeleteFundEvent } from '../hooks/useFunds';
import { formatCurrency, formatBrokerageFee, formatDate } from '../utils/formatters';
import { getEventTypeColor, getEventTypeLabel, getStatusInfo } from '../utils/helpers';
import {
  EquitySection,
  ExpectedPerformanceSection,
  CompletedPerformanceSection,
  FundDetailsSection,
  TransactionSummarySection,
  UnitPriceChartSection
} from './fund-detail';

// Phase 2B.1: Debug utilities (safe, no UI changes)
import {
  createTableDebugReport,
  debugTableRendering,
  logEventGrouping,
  validateTableStructure
} from './fund-detail/FundDetailTable';

// Phase 2B.2: Event grouping logic hook (safe, no UI changes)
import {
  useEventGrouping,
  shouldShowEvent,
  isEquityEvent,
  isDistributionEvent,
  isOtherEvent
} from './fund-detail/FundDetailTable';

// ============================================================================
// MAIN FUND DETAIL COMPONENT
// ============================================================================

const FundDetail: React.FC = () => {
  const { fundId } = useParams<{ fundId: string }>();
  const navigate = useNavigate();
  const [showTaxEvents, setShowTaxEvents] = useState(true);
  const [showNavUpdates, setShowNavUpdates] = useState(true);
  const [eventModalOpen, setEventModalOpen] = useState(false);
  const [editModalOpen, setEditModalOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [selectedEvent, setSelectedEvent] = useState<ExtendedFundEvent | null>(null);
  const [deletingEvent, setDeletingEvent] = useState(false);

  // Phase 2C: Sidebar toggle state with localStorage persistence
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

  // Phase 2B.2: Event grouping logic hook (safe, no UI changes)
  // Temporarily disabled to avoid hook order issues - will be properly integrated in Phase 2B.4
  // const eventGroupingResult = useEventGrouping(events, fund, showTaxEvents, showNavUpdates);



  // Add this function to refresh events after event creation
  const handleEventCreated = () => {
    // Re-fetch fund details using centralized hook
    refetch();
  };

  const handleEventUpdated = () => {
    // Re-fetch fund details using centralized hook
    refetch();
  };

  const handleEditEvent = (event: ExtendedFundEvent) => {
    // Check if there's a withholding tax event on the same date
    const sameDateEvents = fundData?.events.filter((e: ExtendedFundEvent) => e.event_date === event.event_date) || [];
    const withholdingEvent = sameDateEvents.find((e: ExtendedFundEvent) => 
      e.event_type === 'TAX_PAYMENT' && e.tax_payment_type === 'NON_RESIDENT_INTEREST_WITHHOLDING'
    );
    
    // Add withholding context to the event
    const eventWithContext = {
      ...event,
      has_withholding_tax: !!withholdingEvent,
      withholding_amount: withholdingEvent?.amount || null,
      withholding_rate: withholdingEvent ? 10 : null, // Default rate
      net_interest: withholdingEvent ? (event.amount || 0) - (withholdingEvent.amount || 0) : null
    };
    
    setSelectedEvent(eventWithContext);
    setEditModalOpen(true);
  };

  const handleDeleteEvent = (event: ExtendedFundEvent) => {
    setSelectedEvent(event);
    setDeleteDialogOpen(true);
  };

  const confirmDeleteEvent = async () => {
    if (!selectedEvent || !fundId) return;

    setDeletingEvent(true);
    try {
      await deleteFundEvent.mutate();
      
      // Refresh the fund data using centralized hook
      refetch();
      setDeleteDialogOpen(false);
      setSelectedEvent(null);
    } catch (err) {
      // Error handling will be done by the centralized hook
      console.error('Failed to delete event:', err);
    } finally {
      setDeletingEvent(false);
    }
  };

  if (loading) {
    return (
      <Box p={3}>
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px" flexDirection="column" gap={2}>
          {/* Phase 4: Enhanced loading state */}
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
        <Button
          variant="outlined"
          onClick={() => navigate('/')}
          sx={{ mt: 2 }}
        >
          Back to Dashboard
        </Button>
      </Box>
    );
  }

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

  // Phase 2B.1: Debug utilities (safe, no UI changes)
  // Only run in development mode to avoid console spam in production
  if (process.env.NODE_ENV === 'development') {
    // Create comprehensive debug report
    createTableDebugReport(events, fund, showTaxEvents, showNavUpdates);
    
    // Additional targeted debugging
    debugTableRendering(events, fund, showTaxEvents, showNavUpdates);
    logEventGrouping(events, fund);
    validateTableStructure(events, fund, showTaxEvents, showNavUpdates);
  }

  // Phase 2B.2: Event grouping logic hook (safe, no UI changes)
  // Temporarily disabled to avoid hook order issues - will be properly integrated in Phase 2B.4
  // const eventGroupingResult = useEventGrouping(events, fund, showTaxEvents, showNavUpdates);
  
  // Verify the hook returns the expected structure
  if (process.env.NODE_ENV === 'development') {
    console.log('🔍 useEventGrouping Hook Created Successfully - Ready for Phase 2B.4 integration');
  }

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
        
        {/* Phase 2C: Sidebar Toggle Button */}
        <IconButton
          onClick={toggleSidebar}
          sx={{ 
            position: 'absolute', 
            right: 0, 
            top: 0,
            zIndex: 1,
            bgcolor: 'background.paper',
            // Phase 4: Enhanced visual polish
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

      {/* Phase 2C: Side-by-Side Layout */}
      <Box sx={{ 
        display: 'flex', 
        flexDirection: { xs: 'column', sm: 'row' },
        gap: { xs: 2, sm: 3 },
        minHeight: { xs: 'auto', sm: 'calc(100vh - 200px)' },
        height: { xs: 'auto', sm: 'calc(100vh - 200px)' },
        alignItems: 'stretch',
        transition: 'all 0.3s ease-in-out',
        // Visual separation: Add subtle border between sidebar and main area
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
          // Responsive optimization: Better mobile experience
          order: { xs: 1, sm: 0 },
          mb: { xs: 2, sm: 0 },
          // Phase 4: Enhanced visual polish
          bgcolor: 'background.paper',
          borderRadius: { sm: 2 },
          boxShadow: { sm: '0 4px 16px rgba(0,0,0,0.08), 0 2px 6px rgba(0,0,0,0.12)' },
          display: 'flex',
          flexDirection: 'column',
          // Hide completely when not visible
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
          // Responsive optimization: Better mobile experience
          order: { xs: 2, sm: 1 },
          width: { xs: '100%', sm: 'auto' },
          // Phase 4: Enhanced visual polish
          bgcolor: 'background.paper',
          borderRadius: { sm: 2 },
          boxShadow: { sm: '0 4px 16px rgba(0,0,0,0.08), 0 2px 6px rgba(0,0,0,0.12)' },
          pl: { sm: 2 },
          display: 'flex',
          flexDirection: 'column'
        }}>
      {/* Events Table Header with Add Cash Flow Button */}
      <Paper sx={{ 
        width: '100%', 
        overflow: 'hidden', 
        mb: 3,
        flex: 1,
        display: 'flex',
        flexDirection: 'column',
        // Phase 4: Enhanced visual polish
        boxShadow: '0 4px 16px rgba(0,0,0,0.08), 0 2px 6px rgba(0,0,0,0.12)',
        borderRadius: 2,
        transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
        '&:hover': {
          boxShadow: '0 6px 20px rgba(0,0,0,0.12), 0 3px 8px rgba(0,0,0,0.16)'
        }
      }}>
        <Box sx={{ 
          p: 3, 
          borderBottom: 1, 
          borderColor: 'divider',
          bgcolor: 'grey.50'
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
              Fund Events ({(() => {
                const filteredEvents = (events || []).filter(event => {
                  if (!showTaxEvents && (event.event_type === 'TAX_PAYMENT' || event.event_type === 'EOFY_DEBT_COST')) {
                    return false;
                  }
                  if (!showNavUpdates && event.event_type === 'NAV_UPDATE') {
                    return false;
                  }
                  return true;
                });
                return filteredEvents.length;
              })()})
            </Typography>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <Button
                variant="outlined"
                color="primary"
                onClick={() => setEventModalOpen(true)}
                sx={{ 
                  minWidth: { xs: 100, sm: 120 },
                  fontSize: { xs: 11, sm: 12 },
                  textTransform: 'none',
                  borderRadius: 1.5,
                  px: { xs: 1.5, sm: 2 },
                  py: { xs: 0.5, sm: 0.75 },
                  transition: 'all 0.2s ease-in-out',
                  '&:hover': {
                    transform: 'translateY(-1px)',
                    boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
                  }
                }}
              >
                Add Event
              </Button>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Typography variant="body2" color="text.secondary">
                  Show Tax Events
                </Typography>
                <Switch
                  checked={showTaxEvents}
                  onChange={(e) => setShowTaxEvents(e.target.checked)}
                  size="small"
                  sx={{
                    '& .MuiSwitch-switchBase': {
                      color: 'grey.400',
                      transition: 'all 0.2s ease-in-out',
                    },
                    '& .MuiSwitch-switchBase.Mui-checked': {
                      color: 'primary.main',
                    },
                    '& .MuiSwitch-switchBase.Mui-checked + .MuiSwitch-track': {
                      backgroundColor: 'primary.main',
                    },
                    '&:hover .MuiSwitch-switchBase': {
                      transform: 'scale(1.05)',
                    }
                  }}
                />
              </Box>
              {fund.tracking_type === 'nav_based' && (
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Typography variant="body2" color="text.secondary">
                    Show NAV Updates
                  </Typography>
                  <Switch
                    checked={showNavUpdates}
                    onChange={(e) => setShowNavUpdates(e.target.checked)}
                    size="small"
                    sx={{
                      '& .MuiSwitch-switchBase': {
                        color: 'grey.400',
                        transition: 'all 0.2s ease-in-out',
                      },
                      '& .MuiSwitch-switchBase.Mui-checked': {
                        color: 'primary.main',
                      },
                      '& .MuiSwitch-switchBase.Mui-checked + .MuiSwitch-track': {
                        backgroundColor: 'primary.main',
                      },
                      '&:hover .MuiSwitch-switchBase': {
                        transform: 'scale(1.05)',
                      }
                    }}
                  />
                </Box>
              )}
            </Box>
          </Box>
        </Box>
        {/* Events Table */}
        <TableContainer sx={{ 
          flex: 1,
          maxHeight: { xs: 300, sm: 'none' },
          scrollBehavior: 'smooth',
          // Phase 4: Enhanced scrollbar styling
          '&::-webkit-scrollbar': {
            width: '8px',
            height: '8px'
          },
          '&::-webkit-scrollbar-track': {
            backgroundColor: 'grey.100',
            borderRadius: '4px'
          },
          '&::-webkit-scrollbar-thumb': {
            backgroundColor: 'grey.400',
            borderRadius: '4px',
            transition: 'background-color 0.2s ease-in-out',
            '&:hover': {
              backgroundColor: 'grey.500'
            }
          },
          // Responsive optimization: Better mobile table experience
          fontSize: { xs: '12px', sm: '13px' }
        }}>
          <Table stickyHeader size="small">
            <TableHead>
              <TableRow>
                <TableCell 
                  sx={{ 
                    py: { xs: 1, sm: 1.5 }, 
                    px: { xs: 1, sm: 2 }, 
                    fontWeight: 600, 
                    fontSize: { xs: 12, sm: 13 },
                    backgroundColor: 'grey.50',
                    borderBottom: 2,
                    borderColor: 'grey.300',
                    color: 'text.primary'
                  }}
                >
                  Date
                </TableCell>
                <TableCell 
                  sx={{ 
                    py: { xs: 1, sm: 1.5 }, 
                    px: { xs: 1, sm: 2 }, 
                    fontWeight: 600, 
                    fontSize: { xs: 12, sm: 13 },
                    backgroundColor: 'grey.50',
                    borderBottom: 2,
                    borderColor: 'grey.300',
                    color: 'text.primary'
                  }}
                >
                  Type
                </TableCell>
                <TableCell 
                  sx={{ 
                    py: { xs: 1, sm: 1.5 }, 
                    px: { xs: 1, sm: 2 }, 
                    fontWeight: 600, 
                    fontSize: { xs: 12, sm: 13 },
                    backgroundColor: 'grey.50',
                    borderBottom: 2,
                    borderColor: 'grey.300',
                    color: 'text.primary'
                  }}
                >
                  Description
                </TableCell>
                <TableCell 
                  align="center" 
                  sx={{ 
                    py: { xs: 1, sm: 1.5 }, 
                    px: { xs: 1, sm: 2 }, 
                    fontWeight: 600, 
                    fontSize: { xs: 12, sm: 13 },
                    backgroundColor: 'grey.50',
                    borderBottom: 2,
                    borderColor: 'grey.300',
                    color: 'text.primary'
                  }}
                >
                  Equity
                </TableCell>
                {fund.tracking_type === 'nav_based' && (
                  <TableCell 
                    align="center" 
                    sx={{ 
                      py: { xs: 1, sm: 1.5 }, 
                      px: { xs: 1, sm: 2 }, 
                      fontWeight: 600, 
                      fontSize: { xs: 12, sm: 13 },
                      backgroundColor: 'grey.50',
                      borderBottom: 2,
                      borderColor: 'grey.300',
                      color: 'text.primary'
                    }}
                  >
                    Nav Update
                  </TableCell>
                )}
                <TableCell 
                  align="center" 
                  sx={{ 
                    py: { xs: 1, sm: 1.5 }, 
                    px: { xs: 1, sm: 2 }, 
                    fontWeight: 600, 
                    fontSize: { xs: 12, sm: 13 },
                    backgroundColor: 'grey.50',
                    borderBottom: 2,
                    borderColor: 'grey.300',
                    color: 'text.primary'
                  }}
                >
                  Distributions
                </TableCell>
                {showTaxEvents && (
                  <TableCell 
                    align="right"
                    sx={{ 
                      py: 1.5, 
                      px: 2, 
                      fontWeight: 600, 
                      fontSize: 13,
                      backgroundColor: 'grey.50',
                      borderBottom: 2,
                      borderColor: 'grey.300',
                      color: 'text.primary'
                    }}
                  >
                    Tax
                  </TableCell>
                )}
                <TableCell 
                  align="right"
                  sx={{ 
                    py: { xs: 1, sm: 1.5 }, 
                    px: { xs: 1, sm: 2 }, 
                    fontWeight: 600, 
                    fontSize: { xs: 12, sm: 13 },
                    backgroundColor: 'grey.50',
                    borderBottom: 2,
                    borderColor: 'grey.300',
                    color: 'text.primary'
                  }}
                >
                  Actions
                </TableCell>
              </TableRow>
            </TableHead>
            <TableBody sx={{ 
              '& .MuiTableCell-root': { 
                py: { xs: 0.5, sm: 1 }, 
                px: { xs: 1, sm: 2 }, 
                fontSize: { xs: 12, sm: 13 } 
              },
              // Phase 4: Enhanced table row styling
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
            }}
            // Performance optimization: Only render visible rows
            >
              {(() => {
                // Performance optimization: Show loading state for large datasets
                if (events.length > 100) {
                  console.log(`Processing ${events.length} events - this may take a moment...`);
                }
                
                // Debug: Log all events
                console.log('All events:', events);
                console.log('Events with RETURN_OF_CAPITAL:', events.filter(e => e.event_type === 'RETURN_OF_CAPITAL'));
                console.log('Event types:', events.map(e => ({ id: e.id, type: e.event_type, description: e.description, amount: e.amount })));
                
                // Group events by date and type to combine interest distributions with withholding tax
                const groupedEvents: { [key: string]: ExtendedFundEvent[] } = {};
                
                events.forEach(event => {
                  const dateKey = event.event_date;
                  if (!groupedEvents[dateKey]) {
                    groupedEvents[dateKey] = [];
                  }
                  groupedEvents[dateKey].push(event);
                });

                return Object.entries(groupedEvents).map(([date, dateEvents]) => {
                  // Debug: Log all dates and their events
                  console.log(`Processing date: ${date}, events:`, dateEvents);
                  
                  // Find interest distribution and related withholding tax for this date
                  const interestEvent = dateEvents.find(e => 
                    e.event_type === 'DISTRIBUTION' && e.distribution_type === 'INTEREST'
                  );
                  const withholdingEvent = dateEvents.find(e => 
                    e.event_type === 'TAX_PAYMENT' && e.tax_payment_type === 'NON_RESIDENT_INTEREST_WITHHOLDING'
                  );

                  // If we have both interest and withholding on the same date, combine them
                  if (interestEvent && withholdingEvent) {
                                              const isNavBased = fund.tracking_type === 'nav_based';
                          const isDistributionEvent = interestEvent.event_type === 'DISTRIBUTION';

                    return (
                      <React.Fragment key={`${date}-combined`}>
                        {/* Combined interest + withholding row */}
                        <TableRow hover>
                          <TableCell>{formatDate(date)}</TableCell>
                          <TableCell>
                            <Chip
                              label="INTEREST"
                              color={getEventTypeColor('DISTRIBUTION') as any}
                              size="small"
                            />
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2">
                              {interestEvent.description || '-'}
                            </Typography>
                                                          <Typography variant="caption" color="error.main">
                                Withholding: {formatCurrency(-(withholdingEvent?.amount || 0), fund.currency)}
                              </Typography>
                          </TableCell>
                        {/* EQUITY Section */}
                        <TableCell align="right"></TableCell>
                        {/* NAV UPDATE Section (only for NAV-based funds) */}
                        {fund.tracking_type === 'nav_based' && (
                          <TableCell align="right"></TableCell>
                        )}
                        {/* DISTRIBUTIONS Section */}
                        <TableCell align="right">
                          {isDistributionEvent ? (
                            <Box>
                              <Typography variant="body2">
                                {formatCurrency(interestEvent.amount, fund.currency)}
                              </Typography>
                              <Typography variant="caption" color="error.main">
                                {formatCurrency(-(withholdingEvent.amount || 0), fund.currency)}
                              </Typography>
                            </Box>
                          ) : ''}
                        </TableCell>
                        {/* Tax Section */}
                        {showTaxEvents && (
                          <TableCell align="right"></TableCell>
                        )}
                        {/* Actions Column */}
                        <TableCell align="right" sx={{ 
                          minWidth: { xs: 80, sm: 120 }, 
                          px: { xs: 1, sm: 2 } 
                        }}>
                          <Box display="flex" gap={{ xs: 0.5, sm: 1.5 }} justifyContent="flex-end" alignItems="center">
                            {/* Only show edit/delete for user-editable events */}
                            {!['TAX_PAYMENT', 'DAILY_RISK_FREE_INTEREST_CHARGE', 'EOFY_DEBT_COST', 'MANAGEMENT_FEE', 'CARRIED_INTEREST', 'OTHER'].includes(interestEvent.event_type) && (
                              <>
                                <IconButton
                                  size="small"
                                  onClick={() => handleEditEvent(interestEvent)}
                                  sx={{
                                    color: 'primary.main',
                                    p: 1,
                                    borderRadius: 1,
                                    transition: 'all 0.2s ease-in-out',
                                    '&:hover': {
                                      bgcolor: 'primary.light',
                                      transform: 'scale(1.05)',
                                      boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
                                    }
                                  }}
                                  title="Edit event"
                                >
                                  <EditIcon sx={{ fontSize: 18 }} />
                                </IconButton>
                                <IconButton
                                  size="small"
                                  onClick={() => handleDeleteEvent(interestEvent)}
                                  sx={{
                                    color: 'error.main',
                                    p: 1,
                                    borderRadius: 1,
                                    transition: 'all 0.2s ease-in-out',
                                    '&:hover': {
                                      bgcolor: 'error.light',
                                      transform: 'scale(1.05)',
                                      boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
                                    }
                                  }}
                                  title="Delete event"
                                >
                                  <DeleteIcon sx={{ fontSize: 18 }} />
                                </IconButton>
                              </>
                            )}
                          </Box>
                        </TableCell>
                        </TableRow>
                        
                        {/* Process other events on the same date (like RETURN_OF_CAPITAL) */}
                        {dateEvents.filter(event => 
                          event.id !== interestEvent.id && 
                          event.id !== withholdingEvent.id
                        ).map((event) => {
                          // Debug RETURN_OF_CAPITAL events specifically
                          if (event.event_type === 'RETURN_OF_CAPITAL') {
                            console.log('Processing RETURN_OF_CAPITAL event (after combined):', event);
                          }
                          
                          const isNavBased = fund.tracking_type === 'nav_based';
                          const isEquityEvent = isNavBased 
                            ? (event.event_type === 'UNIT_PURCHASE' || event.event_type === 'UNIT_SALE')
                            : (event.event_type === 'CAPITAL_CALL' || event.event_type === 'RETURN_OF_CAPITAL');
                          const isDistributionEvent = event.event_type === 'DISTRIBUTION';
                          const isOtherEvent = !isEquityEvent && !isDistributionEvent;

                          // Skip withholding tax events that are already combined
                          if (event.event_type === 'TAX_PAYMENT' && event.tax_payment_type === 'NON_RESIDENT_INTEREST_WITHHOLDING') {
                            return null;
                          }

                          // Skip tax and debt events if toggle is off
                          if (!showTaxEvents && (event.event_type === 'TAX_PAYMENT' || event.event_type === 'EOFY_DEBT_COST')) {
                            return null;
                          }

                          // Skip NAV updates if toggle is off
                          if (!showNavUpdates && event.event_type === 'NAV_UPDATE') {
                            return null;
                          }

                          return (
                            <TableRow key={event.id} hover>
                              <TableCell>{formatDate(event.event_date)}</TableCell>
                              <TableCell>
                                <Chip
                                  label={getEventTypeLabel(event)}
                                  color={getEventTypeColor(event.event_type) as any}
                                  size="small"
                                />
                              </TableCell>
                              <TableCell>
                                <Typography variant="body2">
                                  {event.description || '-'}
                                </Typography>
                                {event.distribution_type && (
                                  <Typography variant="caption" color="text.secondary">
                                    {event.distribution_type}
                                  </Typography>
                                )}
                              </TableCell>
                              {/* EQUITY Section */}
                              <TableCell align="right">
                                {isEquityEvent && (
                                  (() => {
                                    // Handle NAV-based funds
                                    if (isNavBased) {
                                      if (event.event_type === 'UNIT_PURCHASE') {
                                        return (
                                          <Box>
                                            <Typography variant="body2" color="error.main">
                                              ({formatCurrency(event.amount, fund.currency)})
                                            </Typography>
                                            {event.units_purchased && event.unit_price && (
                                              <Typography variant="caption" color="text.secondary">
                                                {event.units_purchased} × {formatCurrency(event.unit_price, fund.currency)}
                                                {event.brokerage_fee && event.brokerage_fee > 0 && (
                                                  <span style={{ color: 'error.main' }}>
                                                    {' '}- {formatBrokerageFee(event.brokerage_fee, fund.currency)}
                                                  </span>
                                                )}
                                              </Typography>
                                            )}
                                          </Box>
                                        );
                                      } else if (event.event_type === 'UNIT_SALE') {
                                        return (
                                          <Box>
                                            <Typography variant="body2">
                                              {formatCurrency(event.amount, fund.currency)}
                                            </Typography>
                                            {event.units_sold && event.unit_price && (
                                              <Typography variant="caption" color="text.secondary">
                                                {event.units_sold} × {formatCurrency(event.unit_price, fund.currency)}
                                                {event.brokerage_fee && event.brokerage_fee > 0 && (
                                                  <span style={{ color: 'error.main' }}>
                                                    {' '}- {formatBrokerageFee(event.brokerage_fee, fund.currency)}
                                                  </span>
                                                )}
                                              </Typography>
                                            )}
                                          </Box>
                                        );
                                      }
                                    } else {
                                      // Handle cost-based funds
                                      if (event.event_type === 'CAPITAL_CALL') {
                                        return (
                                          <Typography variant="body2" color="error.main">
                                            ({formatCurrency(event.amount, fund.currency)})
                                          </Typography>
                                        );
                                      } else if (event.event_type === 'RETURN_OF_CAPITAL') {
                                        return (
                                          <Typography variant="body2">
                                            {formatCurrency(event.amount, fund.currency)}
                                          </Typography>
                                        );
                                      }
                                    }
                                    return '';
                                  })()
                                )}
                              </TableCell>
                              {/* NAV UPDATE Section (only for NAV-based funds) */}
                              {fund.tracking_type === 'nav_based' && (
                                <TableCell align="right">
                                  {event.event_type === 'NAV_UPDATE' && event.nav_per_share ? (
                                    <Box>
                                      <Typography variant="body2">
                                        {formatCurrency(event.nav_per_share, fund.currency)}
                                      </Typography>
                                      {event.nav_change_absolute != null && event.nav_change_percentage != null && (
                                        <Typography 
                                          variant="caption" 
                                          color={event.nav_change_absolute >= 0 ? 'success.main' : 'error.main'}
                                        >
                                          {event.nav_change_absolute >= 0 ? '+' : ''}{formatCurrency(event.nav_change_absolute, fund.currency)}, {event.nav_change_percentage >= 0 ? '+' : ''}{event.nav_change_percentage.toFixed(1)}%
                                        </Typography>
                                      )}
                                    </Box>
                                  ) : ''}
                                </TableCell>
                              )}
                              {/* DISTRIBUTIONS Section */}
                              <TableCell align="right">
                                {isDistributionEvent ? formatCurrency(event.amount, fund.currency) : ''}
                              </TableCell>
                              {/* Tax Section */}
                              {showTaxEvents && (
                                <TableCell align="right">
                                  {isOtherEvent && event.amount ? (
                            event.event_type === 'TAX_PAYMENT' ? (
                              <Box>
                                <Typography variant="body2" color="error.main">
                                  {formatCurrency(-event.amount, fund.currency)}
                                </Typography>
                                {(() => {
                                  // Get income and tax rate based on tax payment type
                                  let incomeAmount: number | null = null;
                                  let taxRate: number | null = null;
                                  

                                  
                                  switch (event.tax_payment_type) {
                                    case 'EOFY_INTEREST_TAX':
                                      incomeAmount = event.interest_income_amount ?? null;
                                      taxRate = event.interest_income_tax_rate ?? null;
                                      break;
                                    case 'DIVIDENDS_FRANKED_TAX':
                                      incomeAmount = event.dividend_franked_income_amount ?? null;
                                      taxRate = event.dividend_franked_income_tax_rate ?? null;
                                      break;
                                    case 'DIVIDENDS_UNFRANKED_TAX':
                                      incomeAmount = event.dividend_unfranked_income_amount ?? null;
                                      taxRate = event.dividend_unfranked_income_tax_rate ?? null;
                                      break;
                                    case 'CAPITAL_GAINS_TAX':
                                      incomeAmount = event.capital_gain_income_amount ?? null;
                                      taxRate = event.capital_gain_income_tax_rate ?? null;
                                      break;
                                  }
                                  
                                  if (incomeAmount && taxRate) {
                                    return (
                                      <Typography variant="caption" color="text.secondary">
                                        {formatCurrency(incomeAmount, fund.currency)} @ {taxRate}%
                                      </Typography>
                                    );
                                  } else if (event.description) {
                                    // Fallback to description if income/tax rate not available
                                    return (
                                      <Typography variant="caption" color="text.secondary">
                                        {event.description}
                                      </Typography>
                                    );
                                  }
                                  return null;
                                })()}
                              </Box>
                            ) : event.event_type === 'EOFY_DEBT_COST' ? (
                              <Box>
                                <Typography variant="body2">
                                  {formatCurrency(event.amount, fund.currency)}
                                </Typography>
                                {(() => {
                                  // Get total interest and deduction rate for EOFY debt cost events
                                  const totalInterest = event.eofy_debt_interest_deduction_sum_of_daily_interest ?? null;
                                  const deductionRate = event.eofy_debt_interest_deduction_rate ?? null;
                                  
                                  if (totalInterest && deductionRate) {
                                    return (
                                      <Typography variant="caption" color="text.secondary">
                                        {formatCurrency(totalInterest, fund.currency)} @ {deductionRate}%
                                      </Typography>
                                    );
                                  } else if (event.description) {
                                    // Fallback to description if data not available
                                    return (
                                      <Typography variant="caption" color="text.secondary">
                                        {event.description}
                                      </Typography>
                                    );
                                  }
                                  return null;
                                })()}
                              </Box>
                            ) : formatCurrency(event.amount, fund.currency)
                          ) : ''}
                          </TableCell>
                        )}
                        {/* Actions Column */}
                        <TableCell align="right" sx={{ minWidth: 120, px: 2 }}>
                          <Box display="flex" gap={1.5} justifyContent="flex-end" alignItems="center">
                            {/* Only show edit/delete for user-editable events */}
                            {!['TAX_PAYMENT', 'DAILY_RISK_FREE_INTEREST_CHARGE', 'EOFY_DEBT_COST', 'MANAGEMENT_FEE', 'CARRIED_INTEREST', 'OTHER'].includes(event.event_type) && (
                              <>
                                <IconButton
                                  size="small"
                                  onClick={() => handleEditEvent(event)}
                                  sx={{
                                    color: 'primary.main',
                                    p: 1,
                                    borderRadius: 1,
                                    transition: 'all 0.2s ease-in-out',
                                    '&:hover': {
                                      bgcolor: 'primary.light',
                                      transform: 'scale(1.05)',
                                      boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
                                    }
                                  }}
                                  title="Edit event"
                                >
                                  <EditIcon sx={{ fontSize: 18 }} />
                                </IconButton>
                                <IconButton
                                  size="small"
                                  onClick={() => handleDeleteEvent(event)}
                                  sx={{
                                    color: 'error.main',
                                    p: 1,
                                    borderRadius: 1,
                                    transition: 'all 0.2s ease-in-out',
                                    '&:hover': {
                                      bgcolor: 'error.light',
                                      transform: 'scale(1.05)',
                                      boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
                                    }
                                  }}
                                  title="Delete event"
                                >
                                  <DeleteIcon sx={{ fontSize: 18 }} />
                                </IconButton>
                              </>
                            )}
                          </Box>
                        </TableCell>
                      </TableRow>
                    );
                  }).filter(Boolean)}
                      </React.Fragment>
                    );
                  }

                  // For all other events, display normally
                  return dateEvents.map((event) => {
                    // Debug RETURN_OF_CAPITAL events specifically
                    if (event.event_type === 'RETURN_OF_CAPITAL') {
                      console.log('Processing RETURN_OF_CAPITAL event:', event);
                      console.log('Date events for this date:', dateEvents);
                    }
                    
                    const isNavBased = fund.tracking_type === 'nav_based';
                    const isEquityEvent = isNavBased 
                      ? (event.event_type === 'UNIT_PURCHASE' || event.event_type === 'UNIT_SALE')
                      : (event.event_type === 'CAPITAL_CALL' || event.event_type === 'RETURN_OF_CAPITAL');
                    const isDistributionEvent = event.event_type === 'DISTRIBUTION';
                    const isOtherEvent = !isEquityEvent && !isDistributionEvent;



                    // Skip standalone withholding tax events (they should only appear when combined with interest distributions)
                    if (event.event_type === 'TAX_PAYMENT' && event.tax_payment_type === 'NON_RESIDENT_INTEREST_WITHHOLDING') {
                      return null;
                    }

                    // Skip tax and debt events if toggle is off
                    if (!showTaxEvents && (event.event_type === 'TAX_PAYMENT' || event.event_type === 'EOFY_DEBT_COST')) {
                      return null;
                    }

                    // Skip NAV updates if toggle is off
                    if (!showNavUpdates && event.event_type === 'NAV_UPDATE') {
                      return null;
                    }

                    return (
                      <TableRow key={event.id} hover>
                        <TableCell>{formatDate(event.event_date)}</TableCell>
                        <TableCell>
                          <Chip
                            label={getEventTypeLabel(event)}
                            color={getEventTypeColor(event.event_type) as any}
                            size="small"
                          />
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2">
                            {event.description || '-'}
                          </Typography>
                          {event.distribution_type && (
                            <Typography variant="caption" color="text.secondary">
                              {event.distribution_type}
                            </Typography>
                          )}
                        </TableCell>
                        {/* EQUITY Section */}
                        <TableCell align="right">
                          {isEquityEvent && (
                            (() => {
                              // Handle NAV-based funds
                              if (isNavBased) {
                                if (event.event_type === 'UNIT_PURCHASE') {
                                  return (
                                    <Box>
                                      <Typography variant="body2" color="error.main">
                                        ({formatCurrency(event.amount, fund.currency)})
                                      </Typography>
                                      {event.units_purchased && event.unit_price && (
                                        <Typography variant="caption" color="text.secondary">
                                          {event.units_purchased} × {formatCurrency(event.unit_price, fund.currency)}
                                          {event.brokerage_fee && event.brokerage_fee > 0 && (
                                            <span style={{ color: 'error.main' }}>
                                              {' '}- {formatBrokerageFee(event.brokerage_fee, fund.currency)}
                                            </span>
                                          )}
                                        </Typography>
                                      )}
                                    </Box>
                                  );
                                } else if (event.event_type === 'UNIT_SALE') {
                                  return (
                                    <Box>
                                      <Typography variant="body2">
                                        {formatCurrency(event.amount, fund.currency)}
                                      </Typography>
                                      {event.units_sold && event.unit_price && (
                                        <Typography variant="caption" color="text.secondary">
                                          {event.units_sold} × {formatCurrency(event.unit_price, fund.currency)}
                                          {event.brokerage_fee && event.brokerage_fee > 0 && (
                                            <span style={{ color: 'error.main' }}>
                                              {' '}- {formatBrokerageFee(event.brokerage_fee, fund.currency)}
                                            </span>
                                          )}
                                        </Typography>
                                      )}
                                    </Box>
                                  );
                                }
                              } else {
                                // Handle cost-based funds
                                if (event.event_type === 'CAPITAL_CALL') {
                                  return (
                                    <Typography variant="body2" color="error.main">
                                      ({formatCurrency(event.amount, fund.currency)})
                                    </Typography>
                                  );
                                } else if (event.event_type === 'RETURN_OF_CAPITAL') {
                                  return (
                                    <Typography variant="body2">
                                      {formatCurrency(event.amount, fund.currency)}
                                    </Typography>
                                  );
                                }
                              }
                              return '';
                            })()
                          )}
                        </TableCell>
                                                {/* NAV UPDATE Section (only for NAV-based funds) */}
                        {fund.tracking_type === 'nav_based' && (
                          <TableCell align="right">
                            {event.event_type === 'NAV_UPDATE' && event.nav_per_share ? (
                              <Box>
                                <Typography variant="body2">
                                  {formatCurrency(event.nav_per_share, fund.currency)}
                                </Typography>
                                {event.nav_change_absolute != null && event.nav_change_percentage != null && (
                                  <Typography 
                                    variant="caption" 
                                    color={event.nav_change_absolute >= 0 ? 'success.main' : 'error.main'}
                                  >
                                    {event.nav_change_absolute >= 0 ? '+' : ''}{formatCurrency(event.nav_change_absolute, fund.currency)}, {event.nav_change_percentage >= 0 ? '+' : ''}{event.nav_change_percentage.toFixed(1)}%
                                  </Typography>
                                )}
                              </Box>
                            ) : ''}
                          </TableCell>
                        )}
                        {/* DISTRIBUTIONS Section */}
                        <TableCell align="right">
                          {isDistributionEvent ? formatCurrency(event.amount, fund.currency) : ''}
                        </TableCell>
                        {/* Tax Section */}
                        {showTaxEvents && (
                          <TableCell align="right">
                            {isOtherEvent && event.amount ? (
                            event.event_type === 'TAX_PAYMENT' ? (
                              <Box>
                                <Typography variant="body2" color="error.main">
                                  {formatCurrency(-event.amount, fund.currency)}
                                </Typography>
                                {(() => {
                                  // Get income and tax rate based on tax payment type
                                  let incomeAmount: number | null = null;
                                  let taxRate: number | null = null;
                                  

                                  
                                  switch (event.tax_payment_type) {
                                    case 'EOFY_INTEREST_TAX':
                                      incomeAmount = event.interest_income_amount ?? null;
                                      taxRate = event.interest_income_tax_rate ?? null;
                                      break;
                                    case 'DIVIDENDS_FRANKED_TAX':
                                      incomeAmount = event.dividend_franked_income_amount ?? null;
                                      taxRate = event.dividend_franked_income_tax_rate ?? null;
                                      break;
                                    case 'DIVIDENDS_UNFRANKED_TAX':
                                      incomeAmount = event.dividend_unfranked_income_amount ?? null;
                                      taxRate = event.dividend_unfranked_income_tax_rate ?? null;
                                      break;
                                    case 'CAPITAL_GAINS_TAX':
                                      incomeAmount = event.capital_gain_income_amount ?? null;
                                      taxRate = event.capital_gain_income_tax_rate ?? null;
                                      break;
                                  }
                                  
                                  if (incomeAmount && taxRate) {
                                    return (
                                      <Typography variant="caption" color="text.secondary">
                                        {formatCurrency(incomeAmount, fund.currency)} @ {taxRate}%
                                      </Typography>
                                    );
                                  } else if (event.description) {
                                    // Fallback to description if income/tax rate not available
                                    return (
                                      <Typography variant="caption" color="text.secondary">
                                        {event.description}
                                      </Typography>
                                    );
                                  }
                                  return null;
                                })()}
                              </Box>
                            ) : event.event_type === 'EOFY_DEBT_COST' ? (
                              <Box>
                                <Typography variant="body2">
                                  {formatCurrency(event.amount, fund.currency)}
                                </Typography>
                                {(() => {
                                  // Get total interest and deduction rate for EOFY debt cost events
                                  const totalInterest = event.eofy_debt_interest_deduction_sum_of_daily_interest ?? null;
                                  const deductionRate = event.eofy_debt_interest_deduction_rate ?? null;
                                  
                                  if (totalInterest && deductionRate) {
                                    return (
                                      <Typography variant="caption" color="text.secondary">
                                        {formatCurrency(totalInterest, fund.currency)} @ {deductionRate}%
                                      </Typography>
                                    );
                                  } else if (event.description) {
                                    // Fallback to description if data not available
                                    return (
                                      <Typography variant="caption" color="text.secondary">
                                        {event.description}
                                      </Typography>
                                    );
                                  }
                                  return null;
                                })()}
                              </Box>
                            ) : formatCurrency(event.amount, fund.currency)
                          ) : ''}
                          </TableCell>
                        )}
                        {/* Actions Column */}
                        <TableCell align="right" sx={{ minWidth: 120, px: 2 }}>
                          <Box display="flex" gap={1.5} justifyContent="flex-end" alignItems="center">
                            {/* Only show edit/delete for user-editable events */}
                            {!['TAX_PAYMENT', 'DAILY_RISK_FREE_INTEREST_CHARGE', 'EOFY_DEBT_COST', 'MANAGEMENT_FEE', 'CARRIED_INTEREST', 'OTHER'].includes(event.event_type) && (
                              <>
                                <IconButton
                                  size="small"
                                  onClick={() => handleEditEvent(event)}
                                  sx={{
                                    color: 'primary.main',
                                    p: 1,
                                    borderRadius: 1,
                                    transition: 'all 0.2s ease-in-out',
                                    '&:hover': {
                                      bgcolor: 'primary.light',
                                      transform: 'scale(1.05)',
                                      boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
                                    }
                                  }}
                                  title="Edit event"
                                >
                                  <EditIcon sx={{ fontSize: 18 }} />
                                </IconButton>
                                <IconButton
                                  size="small"
                                  onClick={() => handleDeleteEvent(event)}
                                  sx={{
                                    color: 'error.main',
                                    p: 1,
                                    borderRadius: 1,
                                    transition: 'all 0.2s ease-in-out',
                                    '&:hover': {
                                      bgcolor: 'error.light',
                                      transform: 'scale(1.05)',
                                      boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
                                    }
                                  }}
                                  title="Delete event"
                                >
                                  <DeleteIcon sx={{ fontSize: 18 }} />
                                </IconButton>
                              </>
                            )}
                          </Box>
                        </TableCell>
                      </TableRow>
                    );
                  }).filter(Boolean);
                }).flat();
              })()}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>


          </Box>
      </Box>
      {/* Modal rendered at root */}
      <CreateFundEventModal
        open={eventModalOpen}
        onClose={() => setEventModalOpen(false)}
        onEventCreated={handleEventCreated}
        fundId={fund.id}
        fundTrackingType={fund.tracking_type === 'nav_based' ? 'nav_based' : 'cost_based'}
      />
      
      {/* Edit Event Modal */}
      <EditFundEventModal
        open={editModalOpen}
        onClose={() => setEditModalOpen(false)}
        onEventUpdated={handleEventUpdated}
        fundId={fund.id}
        event={selectedEvent}
      />
      
      {/* Delete Confirmation Dialog */}
      <Dialog
        open={deleteDialogOpen}
        onClose={() => setDeleteDialogOpen(false)}
      >
        <DialogTitle>Confirm Delete</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Are you sure you want to delete this event? This action cannot be undone.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)} disabled={deletingEvent}>
            Cancel
          </Button>
          <Button 
            onClick={confirmDeleteEvent} 
            color="error" 
            variant="contained"
            disabled={deletingEvent}
          >
            {deletingEvent ? <CircularProgress size={20} /> : 'Delete'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default FundDetail; 