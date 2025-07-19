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
  Alert
} from '@mui/material';
import { ArrowBack, TrendingUp, AccountBalance, Event } from '@mui/icons-material';
import { useParams, useNavigate } from 'react-router-dom';

interface FundEvent {
  id: number;
  event_type: string;
  event_date: string;
  amount: number | null;
  description: string | null;
  reference_number: string | null;
  distribution_type: string | null;
  tax_payment_type: string | null;
  units_purchased: number | null;
  units_sold: number | null;
  unit_price: number | null;
  nav_per_share: number | null;
  brokerage_fee: number | null;
}

interface FundStatistics {
  total_events: number;
  capital_calls: number;
  distributions: number;
  nav_updates: number;
  unit_purchases: number;
  unit_sales: number;
  total_capital_called: number;
  total_capital_returned: number;
  total_distributions: number;
  first_event_date: string | null;
  last_event_date: string | null;
}

interface FundData {
  id: number;
  name: string;
  fund_type: string | null;
  tracking_type: string;
  currency: string;
  current_equity_balance: number;
  average_equity_balance: number;
  is_active: boolean;
  commitment_amount: number | null;
  expected_irr: number | null;
  expected_duration_months: number | null;
  description: string | null;
  investment_company: string;
  entity: string;
  created_at: string | null;
  updated_at: string | null;
}

interface FundDetailData {
  fund: FundData;
  events: FundEvent[];
  statistics: FundStatistics;
}

const FundDetail: React.FC = () => {
  const { fundId } = useParams<{ fundId: string }>();
  const navigate = useNavigate();
  const [fundData, setFundData] = useState<FundDetailData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchFundDetail = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const response = await fetch(`${process.env.REACT_APP_API_BASE_URL}/api/funds/${fundId}`);
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        setFundData(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch fund details');
      } finally {
        setLoading(false);
      }
    };

    if (fundId) {
      fetchFundDetail();
    }
  }, [fundId]);

  const formatCurrency = (amount: number | null, currency: string = 'AUD') => {
    if (amount === null) return '-';
    return new Intl.NumberFormat('en-AU', {
      style: 'currency',
      currency: currency,
    }).format(amount);
  };

  const formatDate = (dateString: string | null) => {
    if (!dateString) return '-';
    return new Date(dateString).toLocaleDateString('en-AU');
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

  const getEventTypeLabel = (eventType: string) => {
    return eventType.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
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
          startIcon={<ArrowBack />}
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
      {/* Header */}
      <Box sx={{ mb: 3 }}>
        <Button
          variant="outlined"
          startIcon={<ArrowBack />}
          onClick={() => navigate('/')}
          sx={{ mb: 2 }}
        >
          Back to Dashboard
        </Button>
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
                {formatCurrency(fund.commitment_amount, fund.currency)}
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
                  <Typography variant="body2" color="text.secondary">Created</Typography>
                  <Typography variant="body1">{formatDate(fund.created_at)}</Typography>
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

      {/* Events Table */}
      <Paper sx={{ width: '100%', overflow: 'hidden' }}>
        <Box sx={{ p: 3, borderBottom: 1, borderColor: 'divider' }}>
          <Typography variant="h6">
            Fund Events ({events.length})
          </Typography>
        </Box>
        <TableContainer sx={{ maxHeight: 600 }}>
          <Table stickyHeader>
            <TableHead>
              <TableRow>
                <TableCell>Date</TableCell>
                <TableCell>Type</TableCell>
                <TableCell>Description</TableCell>
                <TableCell align="right">Amount</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {events.map((event) => (
                <TableRow key={event.id} hover>
                  <TableCell>{formatDate(event.event_date)}</TableCell>
                  <TableCell>
                    <Chip
                      label={getEventTypeLabel(event.event_type)}
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
                  <TableCell align="right">
                    {event.amount ? formatCurrency(event.amount, fund.currency) : '-'}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>
    </Container>
  );
};

export default FundDetail; 