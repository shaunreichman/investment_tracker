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
  useTheme,
} from '@mui/material';

import { ErrorDisplay } from './ErrorDisplay';
import { createErrorInfo } from '../types/errors';
import { LoadingSpinner } from './ui/LoadingSpinner';
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


const OverallDashboard: React.FC = () => {
  const theme = useTheme();
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
      {/* Page Header Section - Add top margin to account for fixed TopBar */}
      <Box sx={{ mb: 4 }}> {/* Removed manual top margin since RouteLayout handles it */}
        <Typography 
          variant="h3" 
          sx={{ 
            color: theme.palette.text.primary,
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
            color: theme.palette.text.muted,
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
          backgroundColor: theme.palette.background.paper,
          border: `1px solid ${theme.palette.divider}`,
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
                  color: theme.palette.primary.main,
                  fontSize: '28px'
                }} />
                <Typography 
                  variant="h5" 
                  sx={{ 
                    color: theme.palette.text.primary,
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
                  backgroundColor: theme.palette.primary.main,
                  '&:hover': {
                    backgroundColor: theme.palette.primary.dark
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
                color: theme.palette.text.muted,
                lineHeight: 1.6
              }}
            >
              Create and manage investing entities (persons or companies) that can hold funds
            </Typography>
          </CardContent>
        </Card>

        {/* Investment Company Management Card */}
        <Card sx={{ 
          backgroundColor: theme.palette.background.paper,
          border: `1px solid ${theme.palette.divider}`,
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
              alignItems: 'flex-start', 
              mb: 2,
              flexWrap: 'wrap',
              gap: 2
            }}>
              <Box sx={{ display: 'flex', alignItems: 'center', flex: 1, minWidth: 0 }}>
                <BusinessIcon sx={{ 
                  mr: 2, 
                  color: theme.palette.primary.main,
                  fontSize: '28px',
                  flexShrink: 0
                }} />
                <Typography 
                  variant="h5" 
                  sx={{ 
                    color: theme.palette.text.primary,
                    fontWeight: 600,
                    minWidth: 0
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
                  backgroundColor: theme.palette.primary.main,
                  '&:hover': {
                    backgroundColor: theme.palette.primary.dark
                  },
                  px: 3,
                  py: 1,
                  flexShrink: 0
                }}
              >
                Create Company
              </Button>
            </Box>
            <Typography 
              variant="body1" 
              sx={{ 
                color: theme.palette.text.muted,
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
        backgroundColor: theme.palette.background.paper,
        border: `1px solid ${theme.palette.divider}`,
        mb: 4
      }}>
        <CardContent sx={{ p: 3 }}>
          <Typography 
            variant="h5" 
            sx={{ 
              color: theme.palette.text.primary,
              fontWeight: 600,
              mb: 3,
              display: 'flex',
              alignItems: 'center'
            }}
          >
            <Business sx={{ mr: 2, color: theme.palette.primary.main, fontSize: '28px' }} />
            Investment Companies Portfolio
          </Typography>
          
          <TableContainer 
            component={Paper} 
            variant="outlined"
            sx={{
              backgroundColor: theme.palette.background.default,
              border: `1px solid ${theme.palette.divider}`,
              borderRadius: '8px',
              overflow: 'hidden'
            }}
          >
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell sx={{ 
                    color: theme.palette.text.primary,
                    fontWeight: 600,
                    fontSize: '14px',
                    borderBottom: `1px solid ${theme.palette.divider}`
                  }}>
                    Company Name
                  </TableCell>
                  <TableCell sx={{ 
                    color: theme.palette.text.primary,
                    fontWeight: 600,
                    fontSize: '14px',
                    borderBottom: `1px solid ${theme.palette.divider}`
                  }}>
                    Description
                  </TableCell>
                  <TableCell align="right" sx={{ 
                    color: theme.palette.text.primary,
                    fontWeight: 600,
                    fontSize: '14px',
                    borderBottom: `1px solid ${theme.palette.divider}`
                  }}>
                    Total Funds
                  </TableCell>
                  <TableCell align="right" sx={{ 
                    color: theme.palette.text.primary,
                    fontWeight: 600,
                    fontSize: '14px',
                    borderBottom: `1px solid ${theme.palette.divider}`
                  }}>
                    Active Funds
                  </TableCell>
                  <TableCell align="right" sx={{ 
                    color: theme.palette.text.primary,
                    fontWeight: 600,
                    fontSize: '14px',
                    borderBottom: `1px solid ${theme.palette.divider}`
                  }}>
                    Total Equity
                  </TableCell>
                  <TableCell align="right" sx={{ 
                    color: theme.palette.text.primary,
                    fontWeight: 600,
                    fontSize: '14px',
                    borderBottom: `1px solid ${theme.palette.divider}`
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
                        backgroundColor: theme.palette.background.sidebarHover
                      }
                    }}
                  >
                    <TableCell sx={{ 
                      borderBottom: `1px solid ${theme.palette.divider}`,
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
                            color: theme.palette.primary.main,
                            fontWeight: 500,
                            '&:hover': {
                              color: theme.palette.primary.dark
                            }
                          }}
                        >
                          {company.name}
                        </Link>
                        {company.website && (
                          <Typography 
                            variant="caption" 
                            sx={{ 
                              color: theme.palette.text.muted,
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
                                color: theme.palette.text.muted
                              }}
                            >
                              {company.website}
                            </a>
                          </Typography>
                        )}
                      </Box>
                    </TableCell>
                    <TableCell sx={{ 
                      borderBottom: `1px solid ${theme.palette.divider}`,
                      padding: '16px'
                    }}>
                      <Typography 
                        variant="body2" 
                        sx={{ 
                          color: theme.palette.text.muted,
                          lineHeight: 1.5
                        }}
                      >
                        {company.description || 'No description available'}
                      </Typography>
                    </TableCell>
                    <TableCell align="right" sx={{ 
                      borderBottom: `1px solid ${theme.palette.divider}`,
                      padding: '16px'
                    }}>
                      <Chip
                        label={`${company.fund_count} funds`}
                        size="small"
                        sx={{
                          backgroundColor: theme.palette.primary.main,
                          color: theme.palette.text.primary,
                          fontWeight: 500,
                          fontSize: '12px'
                        }}
                      />
                    </TableCell>
                    <TableCell align="right" sx={{ 
                      borderBottom: `1px solid ${theme.palette.divider}`,
                      padding: '16px'
                    }}>
                      <Chip
                        label={`${company.active_funds || 0} active`}
                        size="small"
                        sx={{
                          backgroundColor: (company.active_funds || 0) > 0 ? theme.palette.secondary.main : theme.palette.text.muted,
                          color: theme.palette.text.primary,
                          fontWeight: 500,
                          fontSize: '12px'
                        }}
                      />
                    </TableCell>
                    <TableCell align="right" sx={{ 
                      borderBottom: `1px solid ${theme.palette.divider}`,
                      padding: '16px'
                    }}>
                      <Typography 
                        variant="body2" 
                        sx={{ 
                          fontWeight: 600,
                          color: theme.palette.text.primary,
                          fontSize: '14px'
                        }}
                      >
                        {formatCurrency(company.total_equity_balance || 0)}
                      </Typography>
                    </TableCell>
                    <TableCell align="right" sx={{ 
                      borderBottom: `1px solid ${theme.palette.divider}`,
                      padding: '16px'
                    }}>
                      {company.contact_email && (
                        <Typography 
                          variant="caption" 
                          sx={{ 
                            color: theme.palette.text.muted,
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
            backgroundColor: theme.palette.background.paper,
            border: `1px solid ${theme.palette.divider}`,
            '&:hover': {
              boxShadow: '0px 8px 24px rgba(0,0,0,0.3)',
              transform: 'translateY(-2px)',
              transition: 'all 0.2s ease-in-out'
            }
          }}>
            <CardContent sx={{ p: 3 }}>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <Business sx={{ 
                  color: theme.palette.primary.main, 
                  mr: 3,
                  fontSize: '32px'
                }} />
                <Box>
                  <Typography 
                    sx={{ 
                      color: theme.palette.text.muted, 
                      fontSize: '14px',
                      fontWeight: 500
                    }}
                    gutterBottom
                  >
                    Total Companies
                  </Typography>
                  <Typography variant="h4" sx={{ 
                    color: theme.palette.text.primary,
                    fontWeight: 600
                  }}>
                    {companies.length}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>

          <Card sx={{ 
            backgroundColor: theme.palette.background.paper,
            border: `1px solid ${theme.palette.divider}`,
            '&:hover': {
              boxShadow: '0px 8px 24px rgba(0,0,0,0.3)',
              transform: 'translateY(-2px)',
              transition: 'all 0.2s ease-in-out'
            }
          }}>
            <CardContent sx={{ p: 3 }}>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <AccountBalance sx={{ 
                  color: theme.palette.secondary.main, 
                  mr: 3,
                  fontSize: '32px'
                }} />
                <Box>
                  <Typography 
                    sx={{ 
                      color: theme.palette.text.muted, 
                      fontSize: '14px',
                      fontWeight: 500
                    }}
                    gutterBottom
                  >
                    Total Funds
                  </Typography>
                  <Typography variant="h4" sx={{ 
                    color: theme.palette.text.primary,
                    fontWeight: 600
                  }}>
                    {companies?.reduce((sum, company) => sum + (company.fund_count || 0), 0) || 0}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>

          <Card sx={{ 
            backgroundColor: theme.palette.background.paper,
            border: `1px solid ${theme.palette.divider}`,
            '&:hover': {
              boxShadow: '0px 8px 24px rgba(0,0,0,0.3)',
              transform: 'translateY(-2px)',
              transition: 'all 0.2s ease-in-out'
            }
          }}>
            <CardContent sx={{ p: 3 }}>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <TrendingUp sx={{ 
                  color: theme.palette.info.main, 
                  mr: 3,
                  fontSize: '32px'
                }} />
                <Box>
                  <Typography 
                    sx={{ 
                      color: theme.palette.text.muted, 
                      fontSize: '14px',
                      fontWeight: 500
                    }}
                    gutterBottom
                  >
                    Active Funds
                  </Typography>
                  <Typography variant="h4" sx={{ 
                    color: theme.palette.text.primary,
                    fontWeight: 600
                  }}>
                    {companies?.reduce((sum, company) => sum + (company.active_funds || 0), 0) || 0}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>

          <Card sx={{ 
            backgroundColor: theme.palette.background.paper,
            border: `1px solid ${theme.palette.divider}`,
            '&:hover': {
              boxShadow: '0px 8px 24px rgba(0,0,0,0.3)',
              transform: 'translateY(-2px)',
              transition: 'all 0.2s ease-in-out'
            }
          }}>
            <CardContent sx={{ p: 3 }}>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <Event sx={{ 
                  color: theme.palette.secondary.main, 
                  mr: 3,
                  fontSize: '32px'
                }} />
                <Box>
                  <Typography 
                    sx={{ 
                      color: theme.palette.text.muted, 
                      fontSize: '14px',
                      fontWeight: 500
                    }}
                    gutterBottom
                  >
                    Total Equity
                  </Typography>
                  <Typography variant="h4" sx={{ 
                    color: theme.palette.text.primary,
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