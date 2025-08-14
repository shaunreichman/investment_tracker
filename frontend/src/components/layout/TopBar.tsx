// Top Bar - Phase 2 Implementation
// Fixed position header with page context and actions
// Now route-aware for dynamic content updates

import React from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Box,
  Breadcrumbs,
  Link,
  useTheme,
  InputBase,
} from '@mui/material';
import {
  Search as SearchIcon,
  Notifications as NotificationsIcon,
  AccountCircle as AccountCircleIcon,
} from '@mui/icons-material';
import { useNavigate, useLocation, useParams } from 'react-router-dom';
import { useSidebar } from './MainLayout';

// Route-based page title and breadcrumb configuration
const getRouteInfo = (pathname: string, params: any) => {
  if (pathname === '/') {
    return {
      pageTitle: 'Investment Dashboard',
      breadcrumbs: [{ label: 'Investment Dashboard', path: '/' }]
    };
  }
  
  if (pathname.startsWith('/companies/')) {
    const companyId = params.companyId;
    return {
      pageTitle: `Company ${companyId}`,
      breadcrumbs: [
        { label: 'Investment Dashboard', path: '/' },
        { label: 'Companies', path: '/companies' },
        { label: `Company ${companyId}`, path: `/companies/${companyId}` }
      ]
    };
  }
  
  if (pathname.startsWith('/funds/')) {
    const fundId = params.fundId;
    return {
      pageTitle: `Fund ${fundId}`,
      breadcrumbs: [
        { label: 'Investment Dashboard', path: '/' },
        { label: 'Funds', path: '/funds' },
        { label: `Fund ${fundId}`, path: `/funds/${fundId}` }
      ]
    };
  }
  
  // Default fallback
  return {
    pageTitle: 'Investment Dashboard',
    breadcrumbs: [{ label: 'Investment Dashboard', path: '/' }]
  };
};

const TopBar: React.FC = () => {
  const theme = useTheme();
  const navigate = useNavigate();
  const location = useLocation();
  const params = useParams();
  // We don't need sidebarOpen for now, but keeping the context for future use
  useSidebar();

  // Get dynamic route information
  const { pageTitle, breadcrumbs } = getRouteInfo(location.pathname, params);

  const handleBreadcrumbClick = (path: string) => {
    navigate(path);
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
        {/* Page Title */}
        <Typography
          variant="h6"
          sx={{
            color: theme.palette.text.primary, // White text as per spec
            fontWeight: 600,
            marginRight: 3,
          }}
        >
          {pageTitle}
        </Typography>

        {/* Breadcrumbs */}
        <Box sx={{ flexGrow: 1 }}>
          <Breadcrumbs
            aria-label="breadcrumb"
            sx={{
              '& .MuiBreadcrumbs-ol': {
                alignItems: 'center',
              },
                              '& .MuiBreadcrumbs-li': {
                  '&:last-child .MuiTypography-root': {
                    color: theme.palette.text.muted, // Muted color for current page
                    fontWeight: 400,
                  },
                },
            }}
          >
            {breadcrumbs.map((breadcrumb, index) => {
              const isLast = index === breadcrumbs.length - 1;
              
              return (
                <Link
                  key={breadcrumb.path}
                  color={isLast ? 'inherit' : theme.palette.primary.main} // Docker blue for links
                  underline="hover"
                  onClick={() => !isLast && handleBreadcrumbClick(breadcrumb.path)}
                  sx={{
                    cursor: isLast ? 'default' : 'pointer',
                    '&:hover': {
                      color: isLast ? theme.palette.text.muted : theme.palette.text.hover, // Darker blue on hover
                    },
                  }}
                >
                  <Typography
                    variant="body2"
                    sx={{
                      color: 'inherit',
                      fontWeight: isLast ? 400 : 500,
                    }}
                  >
                    {breadcrumb.label}
                  </Typography>
                </Link>
              );
            })}
          </Breadcrumbs>
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
