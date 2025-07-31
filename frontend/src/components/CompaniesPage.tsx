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
  Link,
  Breadcrumbs,
  Button
} from '@mui/material';
import {
  Business,
  AccountBalance,
  TrendingUp,
  Event,
  Add as AddIcon
} from '@mui/icons-material';
import { useNavigate, useParams } from 'react-router-dom';
import CreateFundModal from './CreateFundModal';
import { useCompanyFunds } from '../hooks/useInvestmentCompanies';

interface Company {
  id: number;
  name: string;
  description?: string;
  website?: string;
  contact_email?: string;
  contact_phone?: string;
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
  entity: string;
  recent_events_count: number;
  created_at: string;
}

interface CompanyFundsResponse {
  company: Company;
  funds: Fund[];
}

const CompaniesPage: React.FC = () => {
  const navigate = useNavigate();
  const { companyId } = useParams<{ companyId: string }>();
  const [company, setCompany] = useState<Company | null>(null);
  const [createModalOpen, setCreateModalOpen] = useState(false);

  // Centralized API hook
  const { data: fundsData, loading, error, refetch } = useCompanyFunds(parseInt(companyId || '0')) as {
    data: CompanyFundsResponse | null;
    loading: boolean;
    error: string | null;
    refetch: () => Promise<void>;
  };

  // Process company data when it loads
  useEffect(() => {
    if (fundsData && fundsData.company) {
      setCompany(fundsData.company);
    }
  }, [fundsData]);

  const handleFundCreated = () => {
    // Refresh the funds list using the centralized hook
    refetch();
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-AU', {
      style: 'currency',
      currency: 'AUD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount);
  };

  const getTrackingTypeColor = (trackingType: string) => {
    switch (trackingType.toLowerCase()) {
      case 'nav_based':
        return 'primary';
      case 'cost_based':
        return 'secondary';
      default:
        return 'default';
    }
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

  if (!company) {
    return (
      <Box p={3}>
        <Alert severity="warning">Company not found</Alert>
      </Box>
    );
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
        <Typography color="text.primary">{company.name}</Typography>
      </Breadcrumbs>

      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box>
          <Typography variant="h4" gutterBottom>
            {company.name}
          </Typography>
          
          <Typography variant="body1" color="textSecondary">
            Funds managed by {company.name}
          </Typography>
        </Box>

        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setCreateModalOpen(true)}
        >
          Create Fund
        </Button>
      </Box>

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
                  <TableCell>Entity</TableCell>
                  <TableCell align="right">Current Equity</TableCell>
                  <TableCell align="right">Status</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {fundsData?.funds?.map((fund) => (
                  <TableRow key={fund.id}>
                    <TableCell>
                      <Link
                        component="button"
                        variant="subtitle2"
                        onClick={() => navigate(`/funds/${fund.id}`)}
                        sx={{ textDecoration: 'none', cursor: 'pointer' }}
                      >
                        {fund.name}
                      </Link>
                    </TableCell>
                    <TableCell>{fund.fund_type}</TableCell>
                    <TableCell>
                      <Chip
                        label={fund.tracking_type}
                        size="small"
                        color={getTrackingTypeColor(fund.tracking_type)}
                      />
                    </TableCell>
                    <TableCell>{fund.entity}</TableCell>
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

      {/* Summary Cards */}
              {fundsData?.funds && fundsData.funds.length > 0 && (
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
                <AccountBalance color="primary" sx={{ mr: 2 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Total Funds
                  </Typography>
                  <Typography variant="h5">
                    {fundsData?.funds?.length || 0}
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
                    {fundsData?.funds?.filter(fund => fund.is_active).length || 0}
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
                    Total Equity
                  </Typography>
                  <Typography variant="h5">
                    {formatCurrency(fundsData?.funds?.reduce((sum, fund) => sum + fund.current_equity_balance, 0) || 0)}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>

          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <Business color="secondary" sx={{ mr: 2 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Average Equity
                  </Typography>
                  <Typography variant="h5">
                    {formatCurrency(fundsData?.funds?.reduce((sum, fund) => sum + fund.average_equity_balance, 0) || 0)}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Box>
      )}

      {/* Empty State */}
              {(!fundsData?.funds || fundsData.funds.length === 0) && (
        <Card sx={{ mt: 3 }}>
          <CardContent>
            <Box textAlign="center" py={4}>
              <Business sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
              <Typography variant="h6" color="textSecondary" gutterBottom>
                No Funds Found
              </Typography>
              <Typography variant="body2" color="textSecondary" mb={3}>
                This investment company doesn't have any funds yet.
              </Typography>
              <Button
                variant="contained"
                startIcon={<AddIcon />}
                onClick={() => setCreateModalOpen(true)}
              >
                Create Your First Fund
              </Button>
            </Box>
          </CardContent>
        </Card>
      )}

      {/* Create Fund Modal */}
      <CreateFundModal
        open={createModalOpen}
        onClose={() => setCreateModalOpen(false)}
        onFundCreated={handleFundCreated}
        companyId={parseInt(companyId!)}
        companyName={company.name}
      />
    </Box>
  );
};

export default CompaniesPage; 