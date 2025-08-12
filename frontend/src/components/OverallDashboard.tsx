import React, { useState } from 'react';
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
  Link,
  Button,
  
} from '@mui/material';
import { ErrorDisplay } from './ErrorDisplay';
import { createErrorInfo } from '../types/errors';
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
import { formatCurrency } from '../utils/formatters';
import { LoadingSpinner } from './ui/LoadingSpinner';


const OverallDashboard: React.FC = () => {
  const navigate = useNavigate();
  const [showEntityModal, setShowEntityModal] = useState(false);
  const [showCompanyModal, setShowCompanyModal] = useState(false);

  // Centralized API hook
  const { data: companies, loading, error, refetch } = useInvestmentCompanies();


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
      <Box sx={{ p: 3 }}>
        <LoadingSpinner label="Loading companies..." />
      </Box>
    );
  }

  if (error) {
    // Handle both string and ErrorInfo error types
    const errorInfo = typeof error === 'string' ? createErrorInfo(error) : error;
    return (
      <Box sx={{ p: 3 }}>
        <ErrorDisplay
          error={errorInfo}
          canRetry={errorInfo.retryable}
          onRetry={refetch}
          onDismiss={() => window.location.reload()}
        />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 0 }}>
      {/* Page Header Section */}
      <Box sx={{ mb: 4 }}>
        <Typography 
          variant="h3" 
          sx={{ 
            color: '#FFFFFF',
            fontWeight: 600,
            mb: 1,
            letterSpacing: '-0.02em'
          }}
        >
          Investment Companies
        </Typography>
        
        <Typography 
          variant="body1" 
          sx={{ 
            color: '#8B949E',
            fontSize: '16px',
            lineHeight: 1.5
          }}
        >
          Overview of all investment companies and their managed funds
        </Typography>
      </Box>

      {/* Data Management Section */}
      <Box 
        sx={{ 
          display: 'grid', 
          gap: 3, 
          gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, 
          mb: 4 
        }}
      >
        {/* Entity Management Card */}
        <Card sx={{ 
          backgroundColor: '#1F2937',
          border: '1px solid #303234',
          '&:hover': {
            boxShadow: '0px 8px 24px rgba(0,0,0,0.3)',
            transform: 'translateY(-2px)',
            transition: 'all 0.2s ease-in-out'
          }
        }}>
          <CardContent sx={{ p: 3 }}>
            <Box sx={{ 
              display: 'flex', 
              justifyContent: 'space-between', 
              alignItems: 'center', 
              mb: 2 
            }}>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <PersonIcon sx={{ 
                  mr: 2, 
                  color: '#2496ED',
                  fontSize: '28px'
                }} />
                <Typography 
                  variant="h5" 
                  sx={{ 
                    color: '#FFFFFF',
                    fontWeight: 600
                  }}
                >
                  Entity Management
                </Typography>
              </Box>
              <Button
                variant="contained"
                startIcon={<AddIcon />}
                onClick={() => setShowEntityModal(true)}
                size="medium"
                sx={{
                  backgroundColor: '#2496ED',
                  '&:hover': {
                    backgroundColor: '#1B7FC4'
                  },
                  px: 3,
                  py: 1
                }}
              >
                Create Entity
              </Button>
            </Box>
            <Typography 
              variant="body1" 
              sx={{ 
                color: '#8B949E',
                lineHeight: 1.6
              }}
            >
              Create and manage investing entities (persons or companies) that can hold funds
            </Typography>
          </CardContent>
        </Card>

        {/* Investment Company Management Card */}
        <Card sx={{ 
          backgroundColor: '#1F2937',
          border: '1px solid #303234',
          '&:hover': {
            boxShadow: '0px 8px 24px rgba(0,0,0,0.3)',
            transform: 'translateY(-2px)',
            transition: 'all 0.2s ease-in-out'
          }
        }}>
          <CardContent sx={{ p: 3 }}>
            <Box sx={{ 
              display: 'flex', 
              justifyContent: 'space-between', 
              alignItems: 'center', 
              mb: 2 
            }}>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <BusinessIcon sx={{ 
                  mr: 2, 
                  color: '#2496ED',
                  fontSize: '28px'
                }} />
                <Typography 
                  variant="h5" 
                  sx={{ 
                    color: '#FFFFFF',
                    fontWeight: 600
                  }}
                >
                  Company Management
                </Typography>
              </Box>
              <Button
                variant="contained"
                startIcon={<AddIcon />}
                onClick={() => setShowCompanyModal(true)}
                size="medium"
                sx={{
                  backgroundColor: '#2496ED',
                  '&:hover': {
                    backgroundColor: '#1B7FC4'
                  },
                  px: 3,
                  py: 1
                }}
              >
                Create Company
              </Button>
            </Box>
            <Typography 
              variant="body1" 
              sx={{ 
                color: '#8B949E',
                lineHeight: 1.6
              }}
            >
              Create and manage investment companies and fund managers
            </Typography>
          </CardContent>
        </Card>
      </Box>

      {/* Companies Portfolio Table */}
      <Card sx={{ 
        backgroundColor: '#1F2937',
        border: '1px solid #303234',
        mb: 4
      }}>
        <CardContent sx={{ p: 3 }}>
          <Typography 
            variant="h5" 
            sx={{ 
              color: '#FFFFFF',
              fontWeight: 600,
              mb: 3,
              display: 'flex',
              alignItems: 'center'
            }}
          >
            <Business sx={{ mr: 2, color: '#2496ED', fontSize: '28px' }} />
            Investment Companies Portfolio
          </Typography>
          
          <TableContainer 
            component={Paper} 
            variant="outlined"
            sx={{
              backgroundColor: '#10151a',
              border: '1px solid #303234',
              borderRadius: '8px',
              overflow: 'hidden'
            }}
          >
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell sx={{ 
                    color: '#FFFFFF',
                    fontWeight: 600,
                    fontSize: '14px',
                    borderBottom: '1px solid #303234'
                  }}>
                    Company Name
                  </TableCell>
                  <TableCell sx={{ 
                    color: '#FFFFFF',
                    fontWeight: 600,
                    fontSize: '14px',
                    borderBottom: '1px solid #303234'
                  }}>
                    Description
                  </TableCell>
                  <TableCell align="right" sx={{ 
                    color: '#FFFFFF',
                    fontWeight: 600,
                    fontSize: '14px',
                    borderBottom: '1px solid #303234'
                  }}>
                    Total Funds
                  </TableCell>
                  <TableCell align="right" sx={{ 
                    color: '#FFFFFF',
                    fontWeight: 600,
                    fontSize: '14px',
                    borderBottom: '1px solid #303234'
                  }}>
                    Active Funds
                  </TableCell>
                  <TableCell align="right" sx={{ 
                    color: '#FFFFFF',
                    fontWeight: 600,
                    fontSize: '14px',
                    borderBottom: '1px solid #303234'
                  }}>
                    Total Equity
                  </TableCell>
                  <TableCell align="right" sx={{ 
                    color: '#FFFFFF',
                    fontWeight: 600,
                    fontSize: '14px',
                    borderBottom: '1px solid #303234'
                  }}>
                    Contact
                  </TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {companies?.map((company, index) => (
                  <TableRow 
                    key={company.id}
                    sx={{
                      backgroundColor: index % 2 === 0 ? 'transparent' : 'rgba(255,255,255,0.02)',
                      '&:hover': {
                        backgroundColor: '#19222a'
                      }
                    }}
                  >
                    <TableCell sx={{ 
                      borderBottom: '1px solid #303234',
                      padding: '16px'
                    }}>
                      <Box>
                        <Link
                          component="button"
                          variant="subtitle2"
                          onClick={() => navigate(`/companies/${company.id}`)}
                          sx={{ 
                            textDecoration: 'none', 
                            cursor: 'pointer',
                            color: '#2496ED',
                            fontWeight: 500,
                            '&:hover': {
                              color: '#1B7FC4'
                            }
                          }}
                        >
                          {company.name}
                        </Link>
                        {company.website && (
                          <Typography 
                            variant="caption" 
                            sx={{ 
                              color: '#8B949E',
                              display: 'block',
                              mt: 0.5
                            }}
                          >
                            <a 
                              href={company.website} 
                              target="_blank" 
                              rel="noopener noreferrer" 
                              style={{ 
                                textDecoration: 'none',
                                color: '#8B949E'
                              }}
                            >
                              {company.website}
                            </a>
                          </Typography>
                        )}
                      </Box>
                    </TableCell>
                    <TableCell sx={{ 
                      borderBottom: '1px solid #303234',
                      padding: '16px'
                    }}>
                      <Typography 
                        variant="body2" 
                        sx={{ 
                          color: '#8B949E',
                          lineHeight: 1.5
                        }}
                      >
                        {company.description || 'No description available'}
                      </Typography>
                    </TableCell>
                    <TableCell align="right" sx={{ 
                      borderBottom: '1px solid #303234',
                      padding: '16px'
                    }}>
                      <Chip
                        label={`${company.fund_count} funds`}
                        size="small"
                        sx={{
                          backgroundColor: '#2496ED',
                          color: '#FFFFFF',
                          fontWeight: 500,
                          fontSize: '12px'
                        }}
                      />
                    </TableCell>
                    <TableCell align="right" sx={{ 
                      borderBottom: '1px solid #303234',
                      padding: '16px'
                    }}>
                      <Chip
                        label={`${company.active_funds || 0} active`}
                        size="small"
                        sx={{
                          backgroundColor: (company.active_funds || 0) > 0 ? '#06a58c' : '#6B7280',
                          color: '#FFFFFF',
                          fontWeight: 500,
                          fontSize: '12px'
                        }}
                      />
                    </TableCell>
                    <TableCell align="right" sx={{ 
                      borderBottom: '1px solid #303234',
                      padding: '16px'
                    }}>
                      <Typography 
                        variant="body2" 
                        sx={{ 
                          fontWeight: 600,
                          color: '#FFFFFF',
                          fontSize: '14px'
                        }}
                      >
                        {formatCurrency(company.total_equity_balance || 0)}
                      </Typography>
                    </TableCell>
                    <TableCell align="right" sx={{ 
                      borderBottom: '1px solid #303234',
                      padding: '16px'
                    }}>
                      {company.contact_email && (
                        <Typography 
                          variant="caption" 
                          sx={{ 
                            color: '#8B949E',
                            fontSize: '12px'
                          }}
                        >
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
          sx={{
            display: 'flex', 
            flexWrap: 'wrap', 
            gap: 3, 
            mt: 4,
            '& > *': {
              flex: '1 1 280px',
              minWidth: '280px'
            }
          }}
        >
          <Card sx={{ 
            backgroundColor: '#1F2937',
            border: '1px solid #303234',
            '&:hover': {
              boxShadow: '0px 8px 24px rgba(0,0,0,0.3)',
              transform: 'translateY(-2px)',
              transition: 'all 0.2s ease-in-out'
            }
          }}>
            <CardContent sx={{ p: 3 }}>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <Business sx={{ 
                  color: '#2496ED', 
                  mr: 3,
                  fontSize: '32px'
                }} />
                <Box>
                  <Typography 
                    sx={{ 
                      color: '#8B949E', 
                      fontSize: '14px',
                      fontWeight: 500
                    }}
                    gutterBottom
                  >
                    Total Companies
                  </Typography>
                  <Typography variant="h4" sx={{ 
                    color: '#FFFFFF',
                    fontWeight: 600
                  }}>
                    {companies.length}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>

          <Card sx={{ 
            backgroundColor: '#1F2937',
            border: '1px solid #303234',
            '&:hover': {
              boxShadow: '0px 8px 24px rgba(0,0,0,0.3)',
              transform: 'translateY(-2px)',
              transition: 'all 0.2s ease-in-out'
            }
          }}>
            <CardContent sx={{ p: 3 }}>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <AccountBalance sx={{ 
                  color: '#06a58c', 
                  mr: 3,
                  fontSize: '32px'
                }} />
                <Box>
                  <Typography 
                    sx={{ 
                      color: '#8B949E', 
                      fontSize: '14px',
                      fontWeight: 500
                    }}
                    gutterBottom
                  >
                    Total Funds
                  </Typography>
                  <Typography variant="h4" sx={{ 
                    color: '#FFFFFF',
                    fontWeight: 600
                  }}>
                    {companies?.reduce((sum, company) => sum + (company.fund_count || 0), 0) || 0}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>

          <Card sx={{ 
            backgroundColor: '#1F2937',
            border: '1px solid #303234',
            '&:hover': {
              boxShadow: '0px 8px 24px rgba(0,0,0,0.3)',
              transform: 'translateY(-2px)',
              transition: 'all 0.2s ease-in-out'
            }
          }}>
            <CardContent sx={{ p: 3 }}>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <TrendingUp sx={{ 
                  color: '#4ca2fa', 
                  mr: 3,
                  fontSize: '32px'
                }} />
                <Box>
                  <Typography 
                    sx={{ 
                      color: '#8B949E', 
                      fontSize: '14px',
                      fontWeight: 500
                    }}
                    gutterBottom
                  >
                    Active Funds
                  </Typography>
                  <Typography variant="h4" sx={{ 
                    color: '#FFFFFF',
                    fontWeight: 600
                  }}>
                    {companies?.reduce((sum, company) => sum + (company.active_funds || 0), 0) || 0}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>

          <Card sx={{ 
            backgroundColor: '#1F2937',
            border: '1px solid #303234',
            '&:hover': {
              boxShadow: '0px 8px 24px rgba(0,0,0,0.3)',
              transform: 'translateY(-2px)',
              transition: 'all 0.2s ease-in-out'
            }
          }}>
            <CardContent sx={{ p: 3 }}>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <Event sx={{ 
                  color: '#06a58c', 
                  mr: 3,
                  fontSize: '32px'
                }} />
                <Box>
                  <Typography 
                    sx={{ 
                      color: '#8B949E', 
                      fontSize: '14px',
                      fontWeight: 500
                    }}
                    gutterBottom
                  >
                    Total Equity
                  </Typography>
                  <Typography variant="h4" sx={{ 
                    color: '#FFFFFF',
                    fontWeight: 600
                  }}>
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