import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  CircularProgress,
  Alert,
  Divider,
  Link
} from '@mui/material';
import {
  TrendingUp,
  AccountBalance,
  Event,
  Assessment,
  AttachMoney,
  Business
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

interface PortfolioSummary {
  total_funds: number;
  active_funds: number;
  total_equity_balance: number;
  total_average_equity_balance: number;
  recent_events_count: number;
  total_tax_statements: number;
  last_updated: string;
}

interface Fund {
  id: number;
  name: string;
  fund_type: string;
  tracking_type: string;
  currency: string;
  current_equity_balance: number;
  average_equity_balance: number;
  is_active: boolean;
  investment_company: string;
  entity: string;
  recent_events_count: number;
  created_at: string;
}

interface FundEvent {
  id: number;
  fund_name: string;
  event_type: string;
  event_date: string;
  amount: number | null;
  description: string;
  reference_number: string;
}

interface PerformanceData {
  fund_id: number;
  fund_name: string;
  current_equity: number;
  average_equity: number;
  total_events: number;
  last_event_date: string;
}

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const [portfolioSummary, setPortfolioSummary] = useState<PortfolioSummary | null>(null);
  const [funds, setFunds] = useState<Fund[]>([]);
  const [recentEvents, setRecentEvents] = useState<FundEvent[]>([]);
  const [performanceData, setPerformanceData] = useState<PerformanceData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:5001';

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        setError(null);

        // Fetch all dashboard data in parallel
        const [summaryRes, fundsRes, eventsRes, performanceRes] = await Promise.all([
          fetch(`${API_BASE_URL}/api/dashboard/portfolio-summary`),
          fetch(`${API_BASE_URL}/api/dashboard/funds`),
          fetch(`${API_BASE_URL}/api/dashboard/recent-events`),
          fetch(`${API_BASE_URL}/api/dashboard/performance`)
        ]);

        if (!summaryRes.ok || !fundsRes.ok || !eventsRes.ok || !performanceRes.ok) {
          throw new Error('Failed to fetch dashboard data');
        }

        const [summary, fundsData, eventsData, performanceData] = await Promise.all([
          summaryRes.json(),
          fundsRes.json(),
          eventsRes.json(),
          performanceRes.json()
        ]);

        setPortfolioSummary(summary);
        setFunds(fundsData.funds);
        setRecentEvents(eventsData.events);
        setPerformanceData(performanceData.performance);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred');
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, [API_BASE_URL]);

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-AU', {
      style: 'currency',
      currency: 'AUD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount);
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const day = date.getDate();
    const month = date.toLocaleDateString('en-AU', { month: 'short' });
    const year = date.getFullYear().toString().slice(-2);
    return `${day}-${month}-${year}`;
  };

  const getEventTypeColor = (eventType: string) => {
    switch (eventType) {
      case 'distribution':
        return 'success';
      case 'capital_call':
        return 'warning';
      case 'nav_update':
        return 'info';
      default:
        return 'default';
    }
  };

  const getTrackingTypeColor = (trackingType: string) => {
    return trackingType === 'nav_based' ? 'primary' : 'secondary';
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box p={3}>
        <Alert severity="error">{error}</Alert>
      </Box>
    );
  }

  return (
    <Box p={3}>
      <Typography variant="h4" gutterBottom>
        Investment Portfolio Dashboard
      </Typography>

      {/* Portfolio Summary Cards */}
      {portfolioSummary && (
        <Box 
          display="flex" 
          flexWrap="wrap" 
          gap={3} 
          mb={4}
          sx={{
            '& > *': {
              flex: '1 1 250px',
              minWidth: '250px'
            }
          }}
        >
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <AccountBalance color="primary" sx={{ mr: 2 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Total Equity
                  </Typography>
                  <Typography variant="h5">
                    {formatCurrency(portfolioSummary.total_equity_balance)}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>

          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <TrendingUp color="success" sx={{ mr: 2 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Active Funds
                  </Typography>
                  <Typography variant="h5">
                    {portfolioSummary.active_funds} / {portfolioSummary.total_funds}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>

          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <Event color="info" sx={{ mr: 2 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Recent Events
                  </Typography>
                  <Typography variant="h5">
                    {portfolioSummary.recent_events_count}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>

          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <Assessment color="secondary" sx={{ mr: 2 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Tax Statements
                  </Typography>
                  <Typography variant="h5">
                    {portfolioSummary.total_tax_statements}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Box>
      )}

      <Box display="flex" gap={3} flexWrap="wrap">
        {/* Funds Table */}
        <Box flex="2" minWidth="600px">
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                <Business sx={{ mr: 1, verticalAlign: 'middle' }} />
                Fund Portfolio
              </Typography>
              <TableContainer component={Paper} variant="outlined">
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Fund Name</TableCell>
                      <TableCell>Type</TableCell>
                      <TableCell>Tracking</TableCell>
                      <TableCell align="right">Current Equity</TableCell>
                      <TableCell align="right">Status</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {funds.map((fund) => (
                      <TableRow key={fund.id}>
                        <TableCell>
                          <Box>
                            <Link
                              component="button"
                              variant="subtitle2"
                              onClick={() => navigate(`/fund/${fund.id}`)}
                              sx={{ textDecoration: 'none', cursor: 'pointer' }}
                            >
                              {fund.name}
                            </Link>
                            <Typography variant="caption" color="textSecondary">
                              {fund.investment_company}
                            </Typography>
                          </Box>
                        </TableCell>
                        <TableCell>{fund.fund_type}</TableCell>
                        <TableCell>
                          <Chip
                            label={fund.tracking_type}
                            size="small"
                            color={getTrackingTypeColor(fund.tracking_type)}
                          />
                        </TableCell>
                        <TableCell align="right">
                          {formatCurrency(fund.current_equity_balance)}
                        </TableCell>
                        <TableCell align="right">
                          <Chip
                            label={fund.is_active ? 'Active' : 'Inactive'}
                            size="small"
                            color={fund.is_active ? 'success' : 'default'}
                          />
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Box>

        {/* Recent Events */}
        <Box flex="1" minWidth="300px">
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                <Event sx={{ mr: 1, verticalAlign: 'middle' }} />
                Recent Events
              </Typography>
              <Box>
                {recentEvents.map((event) => (
                  <Box key={event.id} mb={2}>
                    <Box display="flex" justifyContent="space-between" alignItems="center">
                      <Typography variant="subtitle2">{event.fund_name}</Typography>
                      <Chip
                        label={event.event_type}
                        size="small"
                        color={getEventTypeColor(event.event_type)}
                      />
                    </Box>
                    <Typography variant="body2" color="textSecondary">
                      {event.description}
                    </Typography>
                    <Box display="flex" justifyContent="space-between" alignItems="center" mt={1}>
                      <Typography variant="caption">
                        {formatDate(event.event_date)}
                      </Typography>
                      {event.amount && (
                        <Typography variant="body2" fontWeight="bold">
                          {formatCurrency(event.amount)}
                        </Typography>
                      )}
                    </Box>
                    <Divider sx={{ mt: 1 }} />
                  </Box>
                ))}
              </Box>
            </CardContent>
          </Card>
        </Box>
      </Box>

      {/* Performance Summary */}
      {performanceData.length > 0 && (
        <Card sx={{ mt: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              <AttachMoney sx={{ mr: 1, verticalAlign: 'middle' }} />
              Performance Summary
            </Typography>
            <Box display="flex" gap={2} flexWrap="wrap">
              {performanceData.map((fund) => (
                <Card key={fund.fund_name} variant="outlined" sx={{ flex: '1 1 300px', minWidth: '300px' }}>
                  <CardContent>
                    <Link
                      component="button"
                      variant="subtitle1"
                      onClick={() => navigate(`/fund/${fund.fund_id}`)}
                      sx={{ textDecoration: 'none', cursor: 'pointer', textAlign: 'left', display: 'block' }}
                    >
                      {fund.fund_name}
                    </Link>
                    <Typography variant="h6" color="primary">
                      {formatCurrency(fund.current_equity)}
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      Avg: {formatCurrency(fund.average_equity)}
                    </Typography>
                    <Typography variant="caption" display="block">
                      {fund.total_events} events • Last: {formatDate(fund.last_event_date)}
                    </Typography>
                  </CardContent>
                </Card>
              ))}
            </Box>
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

export default Dashboard; 