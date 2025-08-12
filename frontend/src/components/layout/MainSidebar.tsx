// Main Sidebar Navigation - Phase 4 Implementation
// Dynamic, contextual sidebar that adapts based on current page context

import React, { useMemo } from 'react';
import {
  Box,
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  IconButton,
  Tooltip,
  useTheme,
  Divider,
  Typography,
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  Business as CompanyIcon,
  AccountBalance as FundIcon,
  ChevronLeft as ChevronLeftIcon,
  ChevronRight as ChevronRightIcon,
} from '@mui/icons-material';
import { useNavigate, useParams } from 'react-router-dom';
import { useInvestmentCompanies } from '../../hooks/useInvestmentCompanies';
import { useFunds } from '../../hooks/useFunds';
import { DashboardFund } from '../../types/api';

interface MainSidebarProps {
  open: boolean;
  onToggle: () => void;
}

const MainSidebar: React.FC<MainSidebarProps> = ({ open, onToggle }) => {
  const theme = useTheme();
  const navigate = useNavigate();
  const params = useParams();

  // API hooks for dynamic content
  const { data: companiesData } = useInvestmentCompanies();
  const { data: allFundsData } = useFunds();

  // Get current company and fund IDs
  const currentCompanyId = useMemo(() => {
    console.log('Sidebar Debug - params:', params);
    console.log('Sidebar Debug - allFundsData:', allFundsData);
    
    if (params.companyId) {
      console.log('Sidebar Debug - Found companyId in params:', params.companyId);
      return parseInt(params.companyId);
    }
    if (params.fundId && allFundsData) {
      const fund = allFundsData.find(f => f.id === parseInt(params.fundId || '0'));
      console.log('Sidebar Debug - Found fund in params, fund:', fund);
      return fund?.investment_company_id;
    }
    console.log('Sidebar Debug - No current company ID found');
    return null;
  }, [params, allFundsData]);

  const currentFundId = useMemo(() => {
    if (params.fundId) return parseInt(params.fundId);
    return null;
  }, [params.fundId]);

  // Group funds by company for sidebar display
  const fundsByCompany = useMemo(() => {
    if (!allFundsData) return new Map();
    
    console.log('Sidebar Debug - allFundsData:', allFundsData);
    console.log('Sidebar Debug - companiesData:', companiesData);
    
    const grouped = new Map<number, DashboardFund[]>();
    allFundsData.forEach((fund: DashboardFund) => {
      console.log('Sidebar Debug - Processing fund:', fund);
      if (!grouped.has(fund.investment_company_id)) {
        grouped.set(fund.investment_company_id, []);
      }
      grouped.get(fund.investment_company_id)!.push(fund);
    });
    
    console.log('Sidebar Debug - Grouped funds:', grouped);
    return grouped;
  }, [allFundsData, companiesData]);

  // Handle navigation
  const handleNavigation = (path: string) => {
    navigate(path);
  };

  // Handle company navigation
  const handleCompanyClick = (companyId: number) => {
    navigate(`/companies/${companyId}`);
  };

  // Handle fund navigation
  const handleFundClick = (fundId: number) => {
    navigate(`/funds/${fundId}`);
  };

  // Check if item is active using route params (proper React Router pattern)
  const isActive = (path: string) => {
    if (path === '/') {
      return !params.companyId && !params.fundId; // Dashboard is active when no company or fund is selected
    }
    if (path === '/companies') {
      return !!params.companyId; // Companies section is active when viewing a company
    }
    return false;
  };

  // Check if company is active
  const isCompanyActive = (companyId: number) => {
    return currentCompanyId === companyId;
  };

  // Check if fund is active
  const isFundActive = (fundId: number) => {
    return currentFundId === fundId;
  };

  return (
    <Drawer
      variant="permanent"
      sx={{
        width: open ? 280 : 72, // Increased width to accommodate dynamic content
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: open ? 280 : 72,
          backgroundColor: '#070b0d', // Navigation sidebar background
          borderRight: '1px solid #303234',
          transition: theme.transitions.create('width', {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.enteringScreen,
          }),
          overflowX: 'hidden',
        },
      }}
    >
      {/* Toggle Button */}
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: open ? 'flex-end' : 'center',
          padding: 2,
          borderBottom: '1px solid #303234',
        }}
      >
        <Tooltip title={open ? 'Collapse Sidebar' : 'Expand Sidebar'}>
          <IconButton
            onClick={onToggle}
            sx={{
              color: '#C9D1D9',
              '&:hover': {
                backgroundColor: '#19222a',
                color: '#2496ED',
              },
            }}
          >
            {open ? <ChevronLeftIcon /> : <ChevronRightIcon />}
          </IconButton>
        </Tooltip>
      </Box>

      {/* Navigation Content */}
      <Box sx={{ 
        height: 'calc(100vh - 80px)', // Account for toggle button
        overflow: 'hidden',
        display: 'flex',
        flexDirection: 'column'
      }}>
        {/* Dashboard - Always Fixed at Top */}
        <Box sx={{ flexShrink: 0 }}>
          <List sx={{ padding: 1 }}>
            <ListItem disablePadding sx={{ mb: 1 }}>
              <ListItemButton
                onClick={() => handleNavigation('/')}
                sx={{
                  borderRadius: 1,
                  backgroundColor: isActive('/') ? '#303234' : 'transparent',
                  border: 'none',
                  position: 'relative',
                  '&:hover': {
                    backgroundColor: isActive('/') ? '#303234' : '#19222a',
                    cursor: 'pointer',
                  },
                  minHeight: 36,
                  padding: '8px 12px',
                  paddingLeft: open ? '12px' : '8px',
                  paddingRight: open ? '12px' : '8px',
                }}
              >
                {/* Active Link Indicator */}
                {isActive('/') && (
                  <Box
                    sx={{
                      position: 'absolute',
                      left: 0,
                      top: 0,
                      bottom: 0,
                      width: '3px',
                      backgroundColor: '#2496ED',
                      borderRadius: '0 2px 2px 0',
                    }}
                  />
                )}
                
                <ListItemIcon
                  sx={{
                    color: isActive('/') ? '#FFFFFF' : '#C9D1D9',
                    minWidth: open ? 40 : 32,
                    '& .MuiSvgIcon-root': {
                      fontSize: '24px',
                    },
                    '&:hover': {
                      color: '#2496ED',
                    },
                  }}
                >
                  <DashboardIcon />
                </ListItemIcon>
                {open && (
                  <ListItemText
                    primary="Dashboard"
                    sx={{
                      color: isActive('/') ? '#FFFFFF' : '#C9D1D9',
                      fontWeight: isActive('/') ? 600 : 400,
                    }}
                  />
                )}
              </ListItemButton>
            </ListItem>
          </List>
        </Box>

        {/* Divider */}
        <Divider sx={{ backgroundColor: '#303234', mx: 2 }} />

        {/* Dynamic Content - Scrollable */}
        <Box sx={{ 
          flex: 1,
          overflowY: 'auto',
          padding: 1
        }}>
          {/* Companies Section */}
          {open && companiesData && (
            <Box sx={{ mb: 2 }}>
              <Typography
                variant="caption"
                sx={{
                  color: '#8B949E',
                  fontSize: '11px',
                  textTransform: 'uppercase',
                  letterSpacing: '0.5px',
                  px: 2,
                  py: 1,
                  display: 'block'
                }}
              >
                Companies
              </Typography>
              
              <List sx={{ p: 0 }}>
                {companiesData.map((company) => {
                  const companyActive = isCompanyActive(company.id);
                  const companyFunds = fundsByCompany.get(company.id) || [];
                  
                  console.log(`Sidebar Debug - Company ${company.name} (ID: ${company.id}):`, {
                    companyActive,
                    companyFundsCount: companyFunds.length,
                    companyFunds
                  });
                  
                  return (
                    <Box key={company.id}>
                      {/* Company Item */}
                      <ListItem disablePadding sx={{ mb: 0.5 }}>
                        <ListItemButton
                          onClick={() => handleCompanyClick(company.id)}
                          sx={{
                            borderRadius: 1,
                            backgroundColor: companyActive ? '#19222a' : 'transparent',
                            border: companyActive ? '1px solid #2496ED' : '1px solid transparent',
                            '&:hover': {
                              backgroundColor: companyActive ? '#19222a' : '#1F2937',
                            },
                            minHeight: 32,
                            padding: '6px 12px',
                            paddingLeft: open ? '28px' : '8px', // 16px indentation
                            paddingRight: open ? '12px' : '8px',
                          }}
                        >
                          <ListItemIcon
                            sx={{
                              color: companyActive ? '#2496ED' : '#8B949E',
                              minWidth: open ? 32 : 24,
                              '& .MuiSvgIcon-root': {
                                fontSize: '20px',
                              },
                            }}
                          >
                            <CompanyIcon />
                          </ListItemIcon>
                          {open && (
                            <ListItemText
                              primary={company.name}
                              sx={{
                                color: companyActive ? '#FFFFFF' : '#C9D1D9',
                                fontWeight: companyActive ? 600 : 400,
                                fontSize: '14px',
                              }}
                            />
                          )}
                        </ListItemButton>
                      </ListItem>

                      {/* Company Funds - Show when company is active */}
                      {companyActive && open && companyFunds.length > 0 && (
                        <List sx={{ p: 0, pl: 2 }}>
                          {companyFunds.map((fund: DashboardFund) => {
                            const fundActive = isFundActive(fund.id);
                            
                            return (
                              <ListItem key={fund.id} disablePadding sx={{ mb: 0.5 }}>
                                <ListItemButton
                                  onClick={() => handleFundClick(fund.id)}
                                  sx={{
                                    borderRadius: 1,
                                    backgroundColor: fundActive ? '#19222a' : 'transparent',
                                    border: fundActive ? '1px solid #2496ED' : '1px solid transparent',
                                    '&:hover': {
                                      backgroundColor: fundActive ? '#19222a' : '#1F2937',
                                    },
                                    minHeight: 28,
                                    padding: '4px 12px',
                                    paddingLeft: open ? '44px' : '8px', // 32px indentation
                                    paddingRight: open ? '12px' : '8px',
                                  }}
                                >
                                  <ListItemIcon
                                    sx={{
                                      color: fundActive ? '#2496ED' : '#8B949E',
                                      minWidth: open ? 24 : 20,
                                      '& .MuiSvgIcon-root': {
                                        fontSize: '16px',
                                      },
                                    }}
                                  >
                                    <FundIcon />
                                  </ListItemIcon>
                                  {open && (
                                    <ListItemText
                                      primary={fund.name}
                                      sx={{
                                        color: fundActive ? '#FFFFFF' : '#C9D1D9',
                                        fontWeight: fundActive ? 600 : 400,
                                        fontSize: '13px',
                                      }}
                                    />
                                  )}
                                </ListItemButton>
                              </ListItem>
                            );
                          })}
                        </List>
                      )}
                    </Box>
                  );
                })}
              </List>
            </Box>
          )}
        </Box>
      </Box>
    </Drawer>
  );
};

export default MainSidebar;
