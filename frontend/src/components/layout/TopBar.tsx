// Top Bar - Phase 2 Implementation
// Fixed position header with page context and actions

import React from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Box,
  Breadcrumbs,
  Link,
  useTheme,
} from '@mui/material';
import { useLocation, useNavigate } from 'react-router-dom';

interface TopBarProps {
  sidebarOpen: boolean;
}

const TopBar: React.FC<TopBarProps> = ({ sidebarOpen }) => {
  const theme = useTheme();
  const location = useLocation();
  const navigate = useNavigate();

  // Generate breadcrumbs based on current location
  const generateBreadcrumbs = () => {
    const pathSegments = location.pathname.split('/').filter(Boolean);
    
    if (pathSegments.length === 0) {
      return [{ label: 'Dashboard', path: '/' }];
    }

    const breadcrumbs = [{ label: 'Dashboard', path: '/' }];
    
    pathSegments.forEach((segment, index) => {
      const path = `/${pathSegments.slice(0, index + 1).join('/')}`;
      const label = segment.charAt(0).toUpperCase() + segment.slice(1);
      breadcrumbs.push({ label, path });
    });

    return breadcrumbs;
  };

  // Get page title
  const getPageTitle = () => {
    const pathSegments = location.pathname.split('/').filter(Boolean);
    
    if (pathSegments.length === 0) {
      return 'Dashboard';
    }
    
    if (pathSegments[0] === 'companies' && pathSegments[1]) {
      return 'Company Details';
    }
    
    if (pathSegments[0] === 'funds' && pathSegments[1]) {
      return 'Fund Details';
    }
    
    // Safe access with null check
    const firstSegment = pathSegments[0];
    if (firstSegment) {
      return firstSegment.charAt(0).toUpperCase() + firstSegment.slice(1);
    }
    
    return 'Dashboard';
  };

  const breadcrumbs = generateBreadcrumbs();
  const pageTitle = getPageTitle();

  return (
    <AppBar
      position="fixed"
      sx={{
        width: `calc(100% - ${sidebarOpen ? 280 : 64}px)`,
        marginLeft: `${sidebarOpen ? 280 : 64}px`,
        backgroundColor: '#0D1117', // Docker header background
        borderBottom: '1px solid rgba(255,255,255,0.08)',
        boxShadow: 'none',
        transition: theme.transitions.create(['width', 'margin'], {
          easing: theme.transitions.easing.sharp,
          duration: theme.transitions.duration.leavingScreen,
        }),
        zIndex: theme.zIndex.drawer + 1,
      }}
    >
      <Toolbar sx={{ minHeight: 64, padding: '0 24px' }}>
        {/* Page Title */}
        <Typography
          variant="h6"
          sx={{
            color: '#FFFFFF',
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
                  color: '#8B949E', // Muted color for current page
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
                  color={isLast ? 'inherit' : '#007FFF'}
                  underline="hover"
                  onClick={() => !isLast && navigate(breadcrumb.path)}
                  sx={{
                    cursor: isLast ? 'default' : 'pointer',
                    '&:hover': {
                      color: isLast ? '#8B949E' : '#1E90FF',
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

        {/* Action Buttons Area - Placeholder for future actions */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          {/* Future: Add search, notifications, user menu, etc. */}
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default TopBar;
