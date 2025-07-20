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
  Link
} from '@mui/material';
import {
  Business,
  AccountBalance,
  TrendingUp,
  Event
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

interface InvestmentCompany {
  id: number;
  name: string;
  description: string;
  website: string;
  contact_email: string;
  fund_count: number;
  active_funds: number;
  total_equity_balance: number;
  created_at: string;
  updated_at: string;
}

const OverallDashboard: React.FC = () => {
  const navigate = useNavigate();
  const [companies, setCompanies] = useState<InvestmentCompany[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:5001';

  useEffect(() => {
    const fetchCompanies = async () => {
      try {
        setLoading(true);
        setError(null);

        const response = await fetch(`${API_BASE_URL}/api/investment-companies`);
        
        if (!response.ok) {
          throw new Error('Failed to fetch investment companies');
        }

        const data = await response.json();
        setCompanies(data.companies);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred');
      } finally {
        setLoading(false);
      }
    };

    fetchCompanies();
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
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    const day = date.getDate();
    const month = date.toLocaleDateString('en-AU', { month: 'short' });
    const year = date.getFullYear().toString().slice(-2);
    return `${day}-${month}-${year}`;
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
        Investment Companies
      </Typography>
      
      <Typography variant="body1" color="textSecondary" mb={3}>
        Overview of all investment companies and their managed funds
      </Typography>

      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            <Business sx={{ mr: 1, verticalAlign: 'middle' }} />
            Investment Companies Portfolio
          </Typography>
          
          <TableContainer component={Paper} variant="outlined">
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Company Name</TableCell>
                  <TableCell>Description</TableCell>
                  <TableCell align="right">Total Funds</TableCell>
                  <TableCell align="right">Active Funds</TableCell>
                  <TableCell align="right">Total Equity</TableCell>
                  <TableCell align="right">Contact</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {companies.map((company) => (
                  <TableRow key={company.id}>
                    <TableCell>
                      <Box>
                        <Link
                          component="button"
                          variant="subtitle2"
                          onClick={() => navigate(`/companies/${company.id}`)}
                          sx={{ textDecoration: 'none', cursor: 'pointer' }}
                        >
                          {company.name}
                        </Link>
                        {company.website && (
                          <Typography variant="caption" color="textSecondary" display="block">
                            <a href={company.website} target="_blank" rel="noopener noreferrer" style={{ textDecoration: 'none' }}>
                              {company.website}
                            </a>
                          </Typography>
                        )}
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" color="textSecondary">
                        {company.description || 'No description available'}
                      </Typography>
                    </TableCell>
                    <TableCell align="right">
                      <Chip
                        label={`${company.fund_count} funds`}
                        size="small"
                        color="primary"
                      />
                    </TableCell>
                    <TableCell align="right">
                      <Chip
                        label={`${company.active_funds} active`}
                        size="small"
                        color={company.active_funds > 0 ? 'success' : 'default'}
                      />
                    </TableCell>
                    <TableCell align="right">
                      <Typography variant="body2" fontWeight="bold">
                        {formatCurrency(company.total_equity_balance)}
                      </Typography>
                    </TableCell>
                    <TableCell align="right">
                      {company.contact_email && (
                        <Typography variant="caption" color="textSecondary">
                          {company.contact_email}
                        </Typography>
                      )}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Summary Cards */}
      {companies.length > 0 && (
        <Box 
          display="flex" 
          flexWrap="wrap" 
          gap={3} 
          mt={4}
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
                <Business color="primary" sx={{ mr: 2 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Total Companies
                  </Typography>
                  <Typography variant="h5">
                    {companies.length}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>

          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <AccountBalance color="success" sx={{ mr: 2 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Total Funds
                  </Typography>
                  <Typography variant="h5">
                    {companies.reduce((sum, company) => sum + company.fund_count, 0)}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>

          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <TrendingUp color="info" sx={{ mr: 2 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Active Funds
                  </Typography>
                  <Typography variant="h5">
                    {companies.reduce((sum, company) => sum + company.active_funds, 0)}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>

          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <Event color="secondary" sx={{ mr: 2 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Total Equity
                  </Typography>
                  <Typography variant="h5">
                    {formatCurrency(companies.reduce((sum, company) => sum + company.total_equity_balance, 0))}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Box>
      )}
    </Box>
  );
};

export default OverallDashboard; 