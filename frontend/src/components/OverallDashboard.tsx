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
  Button,
  Grid
} from '@mui/material';
import {
  Business,
  AccountBalance,
  TrendingUp,
  Event,
  Add as AddIcon,
  Person as PersonIcon,
  Business as BusinessIcon
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import CreateEntityModal from './CreateEntityModal';
import CreateInvestmentCompanyModal from './CreateInvestmentCompanyModal';
import { useInvestmentCompanies } from '../hooks/useInvestmentCompanies';



const OverallDashboard: React.FC = () => {
  const navigate = useNavigate();
  const [showEntityModal, setShowEntityModal] = useState(false);
  const [showCompanyModal, setShowCompanyModal] = useState(false);

  // Centralized API hook
  const { data: companies, loading, error, refetch } = useInvestmentCompanies();



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

  const handleEntityCreated = (entity: { id: number; name: string }) => {
    // Refresh the page or show a success message
    // For now, we'll just close the modal
    setShowEntityModal(false);
  };

  const handleCompanyCreated = (company: { id: number; name: string }) => {
    // Refresh the companies list using the centralized hook
    refetch();
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

      {/* Data Management Section */}
      <Box display="grid" gap={3} sx={{ gridTemplateColumns: '1fr 1fr', mb: 3 }}>
        {/* Entity Management Card */}
        <Card>
          <CardContent>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
              <Box display="flex" alignItems="center">
                <PersonIcon sx={{ mr: 1, color: 'primary.main' }} />
                <Typography variant="h6">
                  Entity Management
                </Typography>
              </Box>
              <Button
                variant="contained"
                startIcon={<AddIcon />}
                onClick={() => setShowEntityModal(true)}
                size="small"
              >
                Create Entity
              </Button>
            </Box>
            <Typography variant="body2" color="textSecondary">
              Create and manage investing entities (persons or companies) that can hold funds
            </Typography>
          </CardContent>
        </Card>

        {/* Investment Company Management Card */}
        <Card>
          <CardContent>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
              <Box display="flex" alignItems="center">
                <BusinessIcon sx={{ mr: 1, color: 'primary.main' }} />
                <Typography variant="h6">
                  Company Management
                </Typography>
              </Box>
              <Button
                variant="contained"
                startIcon={<AddIcon />}
                onClick={() => setShowCompanyModal(true)}
                size="small"
              >
                Create Company
              </Button>
            </Box>
            <Typography variant="body2" color="textSecondary">
              Create and manage investment companies and fund managers
            </Typography>
          </CardContent>
        </Card>
      </Box>

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
                {companies?.map((company) => (
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
                        label={`${company.active_funds || 0} active`}
                        size="small"
                        color={(company.active_funds || 0) > 0 ? 'success' : 'default'}
                      />
                    </TableCell>
                    <TableCell align="right">
                      <Typography variant="body2" fontWeight="bold">
                        {formatCurrency(company.total_equity_balance || 0)}
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
      {companies && companies.length > 0 && (
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
                    {companies?.reduce((sum, company) => sum + (company.fund_count || 0), 0) || 0}
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
                    {companies?.reduce((sum, company) => sum + (company.active_funds || 0), 0) || 0}
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
                    {formatCurrency(companies?.reduce((sum, company) => sum + (company.total_equity_balance || 0), 0) || 0)}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Box>
      )}

      {/* Entity Creation Modal */}
      <CreateEntityModal
        open={showEntityModal}
        onClose={() => setShowEntityModal(false)}
        onEntityCreated={handleEntityCreated}
      />

      {/* Investment Company Creation Modal */}
      <CreateInvestmentCompanyModal
        open={showCompanyModal}
        onClose={() => setShowCompanyModal(false)}
        onCompanyCreated={handleCompanyCreated}
      />
    </Box>
  );
};

export default OverallDashboard; 