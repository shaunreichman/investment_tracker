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

  // Get current company and fund IDs from route params
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
      return !params.companyId && !params.fundId; // Investments is active when no company or fund is selected
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
          backgroundColor: theme.palette.background.sidebar, // Navigation sidebar background
          borderRight: `1px solid ${theme.palette.divider}`,
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
          // Removed borderBottom to eliminate line above Investments button
        }}
      >
        <Tooltip title={open ? 'Collapse Sidebar' : 'Expand Sidebar'}>
          <IconButton
            onClick={onToggle}
            sx={{
              color: '#ffffff', // White icon for striking appearance
              '&:hover': {
                backgroundColor: theme.palette.background.sidebarHover,
                color: theme.palette.primary.main,
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
        {/* Investments - Always Fixed at Top */}
        <Box sx={{ flexShrink: 0 }}>
          <List sx={{ padding: 1, paddingBottom: 0 }}> {/* Added paddingBottom: 2 for symmetric spacing */}
            <ListItem disablePadding sx={{ mb: 1 }}>
              <ListItemButton
                onClick={() => handleNavigation('/')}
                sx={{
                  borderRadius: 1,
                  backgroundColor: isActive('/') ? theme.palette.divider : 'transparent',
                  border: 'none',
                  position: 'relative',
                  '&:hover': {
                    backgroundColor: isActive('/') ? theme.palette.divider : theme.palette.background.sidebarHover,
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
                      backgroundColor: theme.palette.primary.main,
                      borderRadius: '0 2px 2px 0',
                    }}
                  />
                )}
                
                <ListItemIcon
                  sx={{
                    color: '#ffffff', // White icon for striking appearance
                    minWidth: open ? 40 : 32,
                    '& .MuiSvgIcon-root': {
                      fontSize: '24px',
                    },
                    '&:hover': {
                      color: theme.palette.primary.main,
                    },
                  }}
                >
                  <DashboardIcon />
                </ListItemIcon>
                {open && (
                  <Typography
                    sx={{
                      color: '#ffffff', // White text for striking appearance
                      fontWeight: isActive('/') ? 600 : 400,
                      fontSize: '18px',
                      marginLeft: 1,
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      whiteSpace: 'nowrap',
                    }}
                  >
                    Investments
                  </Typography>
                )}
              </ListItemButton>
            </ListItem>
          </List>
        </Box>

        {/* Removed divider for sleeker appearance */}

        {/* Dynamic Content - Scrollable */}
        <Box sx={{ 
          flex: 1,
          overflowY: 'auto',
          padding: 1
        }}>
          {/* Companies Section */}
          {open && companiesData && (
            <Box sx={{ mb: 2 }}>
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
                            backgroundColor: companyActive ? theme.palette.background.sidebarHover : 'transparent',
                            border: companyActive ? `1px solid ${theme.palette.primary.main}` : '1px solid transparent',
                            '&:hover': {
                              backgroundColor: companyActive ? theme.palette.background.sidebarHover : theme.palette.background.paper,
                            },
                            minHeight: 28, // Reduced height from 32
                            padding: '4px 12px', // Reduced padding from 6px 12px
                            paddingLeft: open ? '12px' : '8px', // No indentation for companies
                            paddingRight: open ? '12px' : '8px',
                          }}
                        >
                          <ListItemIcon
                            sx={{
                              color: '#ffffff', // White icon for striking appearance
                              minWidth: open ? 32 : 24,
                              '& .MuiSvgIcon-root': {
                                fontSize: '18px', // Reduced from 20px
                              },
                            }}
                          >
                            <CompanyIcon />
                          </ListItemIcon>
                          {open && (
                            <Typography
                              sx={{
                                color: '#ffffff', // White text for striking appearance
                                fontWeight: companyActive ? 600 : 400,
                                fontSize: '16px',
                                marginLeft: 1,
                                overflow: 'hidden',
                                textOverflow: 'ellipsis',
                                whiteSpace: 'nowrap',
                              }}
                            >
                              {company.name}
                            </Typography>
                          )}
                        </ListItemButton>
                      </ListItem>

                      {/* Company Funds - Show when company is active */}
                      {companyActive && open && companyFunds.length > 0 && (
                        <List sx={{ p: 0, pl: 1 }}> {/* Reduced left padding from pl: 2 */}
                          {companyFunds.map((fund: DashboardFund) => {
                            const fundActive = isFundActive(fund.id);
                            
                            return (
                              <ListItem key={fund.id} disablePadding sx={{ mb: 0.5 }}>
                                <ListItemButton
                                  onClick={() => handleFundClick(fund.id)}
                                  sx={{
                                    borderRadius: 1,
                                    backgroundColor: fundActive ? theme.palette.background.sidebarHover : 'transparent',
                                    border: fundActive ? `1px solid ${theme.palette.primary.main}` : '1px solid transparent',
                                    '&:hover': {
                                      backgroundColor: fundActive ? theme.palette.background.sidebarHover : theme.palette.background.paper,
                                    },
                                    minHeight: 18, // Reduced from 20
                                    padding: '1px 12px', // Reduced from 2px 12px
                                    paddingLeft: open ? '20px' : '8px', // Small indent from companies (20px vs 12px)
                                    paddingRight: open ? '12px' : '8px',
                                  }}
                                >
                                  <ListItemIcon
                                    sx={{
                                      color: '#ffffff', // White icon for striking appearance
                                      minWidth: open ? 20 : 16, // Reduced from 24:20
                                      '& .MuiSvgIcon-root': {
                                        fontSize: '14px', // Reduced from 16px
                                      },
                                    }}
                                  >
                                    <FundIcon />
                                  </ListItemIcon>
                                  {open && (
                                    <Typography
                                      sx={{
                                        color: '#ffffff', // White text for striking appearance
                                        fontWeight: fundActive ? 600 : 400,
                                        fontSize: '14px',
                                        marginLeft: 1,
                                        overflow: 'hidden',
                                        textOverflow: 'ellipsis',
                                        whiteSpace: 'nowrap',
                                      }}
                                    >
                                      {fund.name}
                                    </Typography>
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
