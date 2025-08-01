import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Paper,
  Box,
  Card,
  CardContent,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Button,
  CircularProgress,
  Alert,
  Switch,
  Breadcrumbs,
  Link,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  DialogContentText
} from '@mui/material';
import { TrendingUp, AccountBalance, Event, Edit as EditIcon, Delete as DeleteIcon } from '@mui/icons-material';
import { useParams, useNavigate } from 'react-router-dom';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Scatter } from 'recharts';
import CreateFundEventModal from './CreateFundEventModal';
import EditFundEventModal from './EditFundEventModal';
import { 
  FundDetailData, 
  ExtendedFundEvent, 
  ExtendedFund, 
  ExtendedFundStatistics,
  EventType,
  FundType
} from '../types/api';
import { useFundDetail } from '../hooks/useFunds';

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

  // Centralized API hooks
  const { data: fundData, loading, error, refetch } = useFundDetail(Number(fundId));

  const formatCurrency = (amount: number | null, currency: string = 'AUD') => {
    if (amount === null) return '-';
    
    // Excel accounting format: parentheses for negatives, no minus sign
    const absAmount = Math.abs(amount);
    const formatted = new Intl.NumberFormat('en-AU', {
      style: 'currency',
      currency: currency,
    }).format(absAmount);
    
    return amount < 0 ? `(${formatted})` : formatted;
  };

  const formatBrokerageFee = (amount: number | null, currency: string = 'AUD') => {
    if (amount === null) return '-';
    const rounded = Math.round(amount);
    const formatted = new Intl.NumberFormat('en-AU', {
      style: 'currency',
      currency: currency,
    }).format(rounded);
    
    // Remove .00 for whole numbers
    return formatted.replace(/\.00$/, '');
  };

  const formatDate = (dateString: string | null) => {
    if (!dateString) return '-';
    const date = new Date(dateString);
    const day = date.getDate();
    const month = date.toLocaleDateString('en-AU', { month: 'short' });
    const year = date.getFullYear().toString().slice(-2);
    return `${day}-${month}-${year}`;
  };

  const getEventTypeColor = (eventType: string) => {
    switch (eventType) {
      case 'CAPITAL_CALL':
        return 'primary';
      case 'DISTRIBUTION':
        return 'success';
      case 'RETURN_OF_CAPITAL':
        return 'warning';
      case 'NAV_UPDATE':
        return 'info';
      case 'UNIT_PURCHASE':
        return 'primary';
      case 'UNIT_SALE':
        return 'warning';
      case 'TAX_PAYMENT':
        return 'error';
      default:
        return 'default';
    }
  };

  const getEventTypeLabel = (event: ExtendedFundEvent) => {
    // Show only subtype if available, otherwise show the main type
    if (event.distribution_type) {
      // Format distribution type to be consistent (uppercase)
      return event.distribution_type.toUpperCase();
    }
    if (event.tax_payment_type) {
      return event.tax_payment_type;
    }
    
    // For events without subtypes, show the main type
    return event.event_type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

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
      const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:5001';
      const response = await fetch(`${API_BASE_URL}/api/funds/${fundId}/events/${selectedEvent.id}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `HTTP ${response.status}: ${response.statusText}`);
      }

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
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
        <Button
          variant="outlined"
          onClick={() => navigate('/')}
        >
          Back to Dashboard
        </Button>
      </Container>
    );
  }

  if (!fundData) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Alert severity="warning">No fund data available</Alert>
      </Container>
    );
  }

  const { fund, events, statistics } = fundData;

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
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
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          {fund.name}
        </Typography>
        <Typography variant="subtitle1" color="text.secondary" gutterBottom>
          {fund.fund_type} • {fund.entity} • {fund.investment_company}
        </Typography>
      </Box>

      {/* Fund Overview Cards */}
      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 3, mb: 4 }}>
        <Box sx={{ flex: '1 1 250px', minWidth: '250px' }}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={1}>
                <AccountBalance color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6">Current Balance</Typography>
              </Box>
              <Typography variant="h4" color="primary">
                {formatCurrency(fund.current_equity_balance, fund.currency)}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Average: {formatCurrency(fund.average_equity_balance, fund.currency)}
              </Typography>
            </CardContent>
          </Card>
        </Box>

        <Box sx={{ flex: '1 1 250px', minWidth: '250px' }}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={1}>
                <TrendingUp color="success" sx={{ mr: 1 }} />
                <Typography variant="h6">Expected IRR</Typography>
              </Box>
              <Typography variant="h4" color="success.main">
                {fund.expected_irr ? `${fund.expected_irr}%` : 'N/A'}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Duration: {fund.expected_duration_months || 'N/A'} months
              </Typography>
            </CardContent>
          </Card>
        </Box>

        <Box sx={{ flex: '1 1 250px', minWidth: '250px' }}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={1}>
                <Event color="info" sx={{ mr: 1 }} />
                <Typography variant="h6">Total Events</Typography>
              </Box>
              <Typography variant="h4" color="info.main">
                {statistics.total_events}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {statistics.capital_calls} calls • {statistics.distributions} distributions
              </Typography>
            </CardContent>
          </Card>
        </Box>

        <Box sx={{ flex: '1 1 250px', minWidth: '250px' }}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Commitment
              </Typography>
              <Typography variant="h4" color="primary">
                {formatCurrency(fund.commitment_amount || null, fund.currency)}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {fund.tracking_type.replace('_', ' ')}
              </Typography>
            </CardContent>
          </Card>
        </Box>
      </Box>

      {/* Fund Details */}
      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 3, mb: 4 }}>
        <Box sx={{ flex: '1 1 400px', minWidth: '400px' }}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Fund Details
            </Typography>
            <Box sx={{ mt: 2 }}>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2 }}>
                <Box sx={{ flex: '1 1 200px', minWidth: '200px' }}>
                  <Typography variant="body2" color="text.secondary">Fund Type</Typography>
                  <Typography variant="body1">{fund.fund_type || 'N/A'}</Typography>
                </Box>
                <Box sx={{ flex: '1 1 200px', minWidth: '200px' }}>
                  <Typography variant="body2" color="text.secondary">Currency</Typography>
                  <Typography variant="body1">{fund.currency}</Typography>
                </Box>
                <Box sx={{ flex: '1 1 200px', minWidth: '200px' }}>
                  <Typography variant="body2" color="text.secondary">Status</Typography>
                  <Chip 
                    label={fund.is_active ? 'Active' : 'Inactive'} 
                    color={fund.is_active ? 'success' : 'default'}
                    size="small"
                  />
                </Box>
                <Box sx={{ flex: '1 1 200px', minWidth: '200px' }}>
                  <Typography variant="body2" color="text.secondary">Entity</Typography>
                  <Typography variant="body1">{fund.entity}</Typography>
                </Box>
              </Box>
              {fund.description && (
                <Box sx={{ mt: 2 }}>
                  <Typography variant="body2" color="text.secondary">Description</Typography>
                  <Typography variant="body1">{fund.description}</Typography>
                </Box>
              )}
            </Box>
          </Paper>
        </Box>

        <Box sx={{ flex: '1 1 400px', minWidth: '400px' }}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Transaction Summary
            </Typography>
            <Box sx={{ mt: 2 }}>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2 }}>
                <Box sx={{ flex: '1 1 200px', minWidth: '200px' }}>
                  <Typography variant="body2" color="text.secondary">Capital Called</Typography>
                  <Typography variant="body1" color="primary">
                    {formatCurrency(statistics.total_capital_called, fund.currency)}
                  </Typography>
                </Box>
                <Box sx={{ flex: '1 1 200px', minWidth: '200px' }}>
                  <Typography variant="body2" color="text.secondary">Capital Returned</Typography>
                  <Typography variant="body1" color="warning.main">
                    {formatCurrency(statistics.total_capital_returned, fund.currency)}
                  </Typography>
                </Box>
                <Box sx={{ flex: '1 1 200px', minWidth: '200px' }}>
                  <Typography variant="body2" color="text.secondary">Total Distributions</Typography>
                  <Typography variant="body1" color="success.main">
                    {formatCurrency(statistics.total_distributions, fund.currency)}
                  </Typography>
                </Box>
                <Box sx={{ flex: '1 1 200px', minWidth: '200px' }}>
                  <Typography variant="body2" color="text.secondary">Period</Typography>
                  <Typography variant="body1">
                    {formatDate(statistics.first_event_date)} - {formatDate(statistics.last_event_date)}
                  </Typography>
                </Box>
              </Box>
            </Box>
          </Paper>
        </Box>
      </Box>

      {/* Events Table Header with Add Cash Flow Button */}
      <Paper sx={{ width: '100%', overflow: 'hidden', mb: 3 }}>
        <Box sx={{ p: 3, borderBottom: 1, borderColor: 'divider' }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="h6">
              Fund Events ({(() => {
                const filteredEvents = events.filter(event => {
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
                variant="contained"
                color="primary"
                onClick={() => setEventModalOpen(true)}
                sx={{ minWidth: 160 }}
              >
                Add Cash Flow
              </Button>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Typography variant="body2" color="text.secondary">
                  Show Tax Events
                </Typography>
                <Switch
                  checked={showTaxEvents}
                  onChange={(e) => setShowTaxEvents(e.target.checked)}
                  size="small"
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
                  />
                </Box>
              )}
            </Box>
          </Box>
        </Box>
        {/* Events Table */}
        <TableContainer sx={{ maxHeight: 600 }}>
          <Table stickyHeader>
            <TableHead>
              <TableRow>
                <TableCell>Date</TableCell>
                <TableCell>Type</TableCell>
                <TableCell>Description</TableCell>
                <TableCell align="center" sx={{ borderBottom: 1, borderColor: 'divider' }}>
                  Equity
                </TableCell>
                {fund.tracking_type === 'nav_based' && (
                  <TableCell align="center" sx={{ borderBottom: 1, borderColor: 'divider' }}>
                    Nav Update
                  </TableCell>
                )}
                <TableCell align="center" sx={{ borderBottom: 1, borderColor: 'divider' }}>
                  Distributions
                </TableCell>
                {showTaxEvents && (
                  <TableCell align="right">Tax</TableCell>
                )}
                <TableCell align="right">Actions</TableCell>
              </TableRow>

            </TableHead>
            <TableBody>
              {(() => {
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
                          const isEquityEvent = isNavBased 
                            ? (interestEvent.event_type === 'UNIT_PURCHASE' || interestEvent.event_type === 'UNIT_SALE')
                            : (interestEvent.event_type === 'CAPITAL_CALL' || interestEvent.event_type === 'RETURN_OF_CAPITAL');
                          const isDistributionEvent = interestEvent.event_type === 'DISTRIBUTION';
                          // Note: isEquityEvent is used in the JSX below

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
                        <TableCell align="right">
                          <Box display="flex" gap={1} justifyContent="flex-end">
                            {/* Only show edit/delete for user-editable events */}
                            {!['TAX_PAYMENT', 'DAILY_RISK_FREE_INTEREST_CHARGE', 'EOFY_DEBT_COST', 'MANAGEMENT_FEE', 'CARRIED_INTEREST', 'OTHER'].includes(interestEvent.event_type) && (
                              <>
                                <IconButton
                                  size="small"
                                  onClick={() => handleEditEvent(interestEvent)}
                                  color="primary"
                                  title="Edit event"
                                >
                                  <EditIcon fontSize="small" />
                                </IconButton>
                                <IconButton
                                  size="small"
                                  onClick={() => handleDeleteEvent(interestEvent)}
                                  color="error"
                                  title="Delete event"
                                >
                                  <DeleteIcon fontSize="small" />
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
                        <TableCell align="right">
                          <Box display="flex" gap={1} justifyContent="flex-end">
                            {/* Only show edit/delete for user-editable events */}
                            {!['TAX_PAYMENT', 'DAILY_RISK_FREE_INTEREST_CHARGE', 'EOFY_DEBT_COST', 'MANAGEMENT_FEE', 'CARRIED_INTEREST', 'OTHER'].includes(event.event_type) && (
                              <>
                                <IconButton
                                  size="small"
                                  onClick={() => handleEditEvent(event)}
                                  color="primary"
                                  title="Edit event"
                                >
                                  <EditIcon fontSize="small" />
                                </IconButton>
                                <IconButton
                                  size="small"
                                  onClick={() => handleDeleteEvent(event)}
                                  color="error"
                                  title="Delete event"
                                >
                                  <DeleteIcon fontSize="small" />
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
                        <TableCell align="right">
                          <Box display="flex" gap={1} justifyContent="flex-end">
                            {/* Only show edit/delete for user-editable events */}
                            {!['TAX_PAYMENT', 'DAILY_RISK_FREE_INTEREST_CHARGE', 'EOFY_DEBT_COST', 'MANAGEMENT_FEE', 'CARRIED_INTEREST', 'OTHER'].includes(event.event_type) && (
                              <>
                                <IconButton
                                  size="small"
                                  onClick={() => handleEditEvent(event)}
                                  color="primary"
                                  title="Edit event"
                                >
                                  <EditIcon fontSize="small" />
                                </IconButton>
                                <IconButton
                                  size="small"
                                  onClick={() => handleDeleteEvent(event)}
                                  color="error"
                                  title="Delete event"
                                >
                                  <DeleteIcon fontSize="small" />
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

      {/* Unit Price Chart - Only for NAV-based funds */}
      {fund.tracking_type === 'nav_based' && (
        <Paper sx={{ width: '100%', overflow: 'hidden', mt: 3 }}>
          <Box sx={{ p: 3, borderBottom: 1, borderColor: 'divider' }}>
            <Typography variant="h6">
              Unit Price Performance
            </Typography>
            <Typography variant="body2" color="text.secondary">
              NAV per share over time
            </Typography>
          </Box>
          <Box sx={{ p: 3, height: 400, position: 'relative' }}>
            {(() => {
              try {
                const events = fundData.events;
                
                // Prepare NAV data - separate for continuous line
                const navData = events
                  .filter(event => event.event_type === 'NAV_UPDATE' && event.nav_per_share)
                  .map(event => ({
                    date: new Date(event.event_date).getTime(),
                    displayDate: new Date(event.event_date).toLocaleDateString('en-AU', {
                      day: '2-digit',
                      month: 'short',
                      year: 'numeric'
                    }),
                    nav: event.nav_per_share,
                    timestamp: new Date(event.event_date).getTime()
                  }))
                  .sort((a, b) => a.timestamp - b.timestamp);

                // Prepare purchase/sale data - separate for markers
                const purchaseData = events
                  .filter(event => (event.event_type === 'UNIT_PURCHASE' || event.description?.includes('purchase')) && event.amount && event.units_purchased)
                  .map(event => ({
                    date: new Date(event.event_date).getTime(), // Use same timestamp format as NAV
                    displayDate: new Date(event.event_date).toLocaleDateString('en-AU', {
                      day: '2-digit',
                      month: 'short',
                      year: 'numeric'
                    }),
                    purchase: (event.amount || 0) / (event.units_purchased || 1), // Use 'purchase' as dataKey
                    timestamp: new Date(event.event_date).getTime(),
                    type: 'Purchase',
                    units: event.units_purchased || 0,
                    amount: event.amount || 0,
                    description: event.description
                  }));

                const saleData = events
                  .filter(event => (event.event_type === 'UNIT_SALE' || event.description?.includes('sale')) && event.amount && event.units_sold)
                  .map(event => ({
                    date: new Date(event.event_date).getTime(), // Use same timestamp format as NAV
                    displayDate: new Date(event.event_date).toLocaleDateString('en-AU', {
                      day: '2-digit',
                      month: 'short',
                      year: 'numeric'
                    }),
                    sale: (event.amount || 0) / (event.units_sold || 1), // Use 'sale' as dataKey
                    timestamp: new Date(event.event_date).getTime(),
                    type: 'Sale',
                    units: event.units_sold || 0,
                    amount: event.amount || 0,
                    description: event.description
                  }));

                console.log('NAV data count:', navData.length);
                console.log('Purchase data count:', purchaseData.length);
                console.log('Sale data count:', saleData.length);

                // Calculate shared domain from ALL data
                const allValues = [
                  ...navData.map(d => d.nav),
                  ...purchaseData.map(d => d.purchase),
                  ...saleData.map(d => d.sale)
                ].filter((v): v is number => v !== null && v !== undefined);

                const allDates = [
                  ...navData.map(d => d.timestamp),
                  ...purchaseData.map(d => d.timestamp),
                  ...saleData.map(d => d.timestamp)
                ];

                if (allValues.length === 0) {
                  return <Typography>No chart data available</Typography>;
                }

                const minValue = Math.min(...allValues);
                const maxValue = Math.max(...allValues);
                const padding = (maxValue - minValue) * 0.1;

                const minDate = Math.min(...allDates);
                const maxDate = Math.max(...allDates);
                const datePadding = (maxDate - minDate) * 0.05;

                const yDomain = [minValue - padding, maxValue + padding];
                const xDomain = [minDate - datePadding, maxDate + datePadding];

                console.log('Shared domains:', { xDomain, yDomain });
                console.log('Date range:', { min: new Date(minDate), max: new Date(maxDate) });

                return (
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={navData}>
                      <CartesianGrid 
                        strokeDasharray="3 3" 
                        vertical={true}
                        horizontal={true}
                        stroke="#f0f0f0"
                      />
                      <XAxis 
                        dataKey="date" 
                        tick={{ fontSize: 12 }}
                        angle={-45}
                        textAnchor="end"
                        height={80}
                        domain={xDomain}
                        type="number"
                        scale="time"
                        tickFormatter={(value) => new Date(value).toLocaleDateString('en-AU', {
                          day: '2-digit',
                          month: 'short',
                          year: 'numeric'
                        })}
                        ticks={(() => {
                          // Generate ticks at end of each month within the date range
                          const ticks = [];
                          const startDate = new Date(minDate);
                          const endDate = new Date(maxDate);
                          
                          // Start from the first day of the month containing the start date
                          let currentDate = new Date(startDate.getFullYear(), startDate.getMonth(), 1);
                          
                          // Add safety check to prevent infinite loops
                          let iterationCount = 0;
                          const maxIterations = 50; // Safety limit
                          
                          while (currentDate <= endDate && iterationCount < maxIterations) {
                            // Set to last day of current month
                            const lastDayOfMonth = new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 0);
                            ticks.push(lastDayOfMonth.getTime());
                            
                            // Move to first day of next month
                            currentDate.setMonth(currentDate.getMonth() + 1);
                            currentDate.setDate(1);
                            iterationCount++;
                          }
                          
                          console.log('Generated ticks:', ticks.length, 'iterations:', iterationCount);
                          console.log('Tick dates:', ticks.map(t => new Date(t).toLocaleDateString('en-AU')));
                          return ticks;
                        })()}
                      />
                      <YAxis 
                        tick={{ fontSize: 12 }}
                        tickFormatter={(value) => `$${value.toFixed(2)}`}
                        domain={yDomain}
                      />
                      <Tooltip 
                        formatter={(value, name) => {
                          if (name === 'nav') return [`$${value}`, 'NAV'];
                          if (name === 'purchase') return [`$${value}`, 'Purchase'];
                          if (name === 'sale') return [`$${value}`, 'Sale'];
                          return [value, name];
                        }}
                        labelFormatter={(label) => `Date: ${new Date(label).toLocaleDateString('en-AU', {
                          day: '2-digit',
                          month: 'short',
                          year: 'numeric'
                        })}`}
                      />
                      <Line 
                        type="linear" 
                        dataKey="nav" 
                        stroke="#1976d2" 
                        strokeWidth={2}
                        dot={{ fill: '#1976d2', strokeWidth: 2, r: 4, stroke: '#1976d2' }}
                        activeDot={{ r: 6, fill: '#1976d2', stroke: '#1976d2', strokeWidth: 2 }}
                        connectNulls={false}
                        isAnimationActive={false}
                      />
                      <Scatter 
                        dataKey="purchase" 
                        fill="#4caf50" 
                        stroke="#4caf50"
                        shape="star"
                        data={purchaseData}
                      />
                      <Scatter 
                        dataKey="sale" 
                        fill="#f44336" 
                        stroke="#f44336"
                        shape="star"
                        data={saleData}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                );
              } catch (error) {
                console.error('Chart error:', error);
                return <Typography color="error">Error loading chart: {error instanceof Error ? error.message : 'Unknown error'}</Typography>;
              }
            })()}
          </Box>
        </Paper>
      )}
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
    </Container>
  );
};

export default FundDetail; 