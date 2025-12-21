// Top Bar - Phase 2 Implementation
// Fixed position header with page context and actions
// Now route-aware for dynamic content updates

import React from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Box,
  useTheme,
  InputBase,
} from '@mui/material';
import {
  Search as SearchIcon,
  Notifications as NotificationsIcon,
  AccountCircle as AccountCircleIcon,
} from '@mui/icons-material';
import { useNavigate, useLocation, useParams } from 'react-router-dom';
import { useSidebar } from './RouteLayout';
import { useCompanies } from '@/company/hooks';
import { useFund } from '@/fund/hooks';
import { Breadcrumbs } from '../navigation';
import type { BreadcrumbItem } from '../navigation';

// Custom hook to get meaningful breadcrumb data
const useBreadcrumbData = () => {
  const location = useLocation();
  const params = useParams();
  
  // Get company data if we're on a company or fund route
  const companyId = params.companyId ? Number(params.companyId) : undefined;
  const fundId = params.fundId ? Number(params.fundId) : undefined;
  
  const { data: companiesResponse } = useCompanies();
  const { data: fundData } = useFund(fundId || 0, undefined, {
    refetchOnWindowFocus: false
  });
  
  // Extract companies array from response
  const companiesData = companiesResponse?.companies || null;
  
  if (location.pathname === '/') {
    return {
      breadcrumbs: [{ id: 'investments', label: 'Investments', to: '/' }]
    };
  }
  
  if (location.pathname.startsWith('/companies/') && companyId) {
    // Find the company name from the companies data
    const company = companiesData?.find((c) => c.id === companyId);
    const companyName = company?.name || `Company ${companyId}`;
    
    return {
      breadcrumbs: [
        { id: 'investments', label: 'Investments', to: '/' },
        { id: `company-${companyId}`, label: companyName, to: `/companies/${companyId}` }
      ]
    };
  }
  
  if (location.pathname.startsWith('/funds/') && fundId) {
    // Get company name from companies data using fund's company_id
    const company = fundData ? companiesData?.find((c) => c.id === fundData.company_id) : null;
    const companyName = company?.name || `Company ${fundData?.company_id || 'Unknown'}`;
    const fundName = fundData?.name || `Fund ${fundId}`;
    
    return {
      breadcrumbs: [
        { id: 'investments', label: 'Investments', to: '/' },
        { id: `company-${fundData?.company_id || 0}`, label: companyName, to: `/companies/${fundData?.company_id || 0}` },
        { id: `fund-${fundId}`, label: fundName, to: `/funds/${fundId}` }
      ]
    };
  }
  
  // Default fallback
  return {
    breadcrumbs: [{ id: 'investments', label: 'Investments', to: '/' }]
  };
};

const TopBar: React.FC = () => {
  const theme = useTheme();
  const navigate = useNavigate();
  // We don't need sidebarOpen for now, but keeping the context for future use
  useSidebar();

  // Get dynamic breadcrumb data with actual names
  const { breadcrumbs } = useBreadcrumbData();

  const handleBreadcrumbClick = (item: BreadcrumbItem) => {
    if (item.to) {
      navigate(item.to);
    }
  };

  return (
    <AppBar
      position="fixed"
      sx={{
        width: '100%', // Full width
        marginLeft: 0, // No left margin - extends to left edge
        background: `linear-gradient(90deg, ${theme.palette.background.topbar} 0%, ${theme.palette.background.topbarGradient} 100%)`, // TopBar gradient background
        borderBottom: `1px solid ${theme.palette.divider}`, // Updated border color
        boxShadow: '0px 1px 4px rgba(0,0,0,0.2)', // Subtle shadow for depth
        transition: theme.transitions.create(['width', 'margin'], {
          easing: theme.transitions.easing.sharp,
          duration: theme.transitions.duration.leavingScreen,
        }),
        zIndex: theme.zIndex.drawer + 1,
      }}
    >
      <Toolbar sx={{ minHeight: 56, padding: '0 24px' }}> {/* 56px height as per spec */}
        {/* Breadcrumbs - Now using shared navigation component */}
        <Box sx={{ flexGrow: 1 }}>
          <Breadcrumbs
            items={breadcrumbs}
            onNavigate={handleBreadcrumbClick}
            ariaLabel="Breadcrumb"
          />
        </Box>

        {/* Search Box - Moved to right side */}
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            background: `linear-gradient(90deg, ${theme.palette.background.searchGradientStart} 0%, ${theme.palette.background.searchGradientEnd} 100%)`, // Theme-based gradient
            borderRadius: '8px',
            padding: '8px 16px', // Increased horizontal padding
            marginRight: 3,
            minWidth: 300, // Increased from 200 to 300
            maxWidth: 400, // Added max width for responsiveness
            '&:hover': {
              background: `linear-gradient(90deg, ${theme.palette.background.searchGradientEnd} 0%, ${theme.palette.background.searchGradientStart} 100%)`, // Reverse gradient on hover
            },
          }}
        >
          <SearchIcon sx={{ color: theme.palette.text.primary, marginRight: 1, fontSize: 20 }} />
          <InputBase
            placeholder="Search..."
            sx={{
              color: theme.palette.text.primary, // Theme-based white text
              fontSize: '14px',
              width: '100%', // Take full width of container
              '& input': {
                color: theme.palette.text.primary, // Ensure input text uses theme color
                '&::placeholder': {
                  color: theme.palette.text.pure, // Pure white placeholder from theme
                  opacity: 1,
                },
              },
            }}
          />
        </Box>

        {/* Action Buttons Area */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <NotificationsIcon sx={{ color: theme.palette.text.secondary }} />
          
                      <AccountCircleIcon sx={{ color: theme.palette.text.secondary }} />
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default TopBar;

