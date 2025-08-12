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
  InputBase,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  Search as SearchIcon,
  Settings as SettingsIcon,
  Help as HelpIcon,
  AccountCircle as AccountIcon,
} from '@mui/icons-material';
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
        width: '100%', // Full width
        marginLeft: 0, // No left margin - extends to left edge
        background: 'linear-gradient(90deg, #051B51 0%, #00298B 100%)', // TopBar gradient background
        borderBottom: '1px solid #303234', // Updated border color
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
            color: '#FFFFFF', // White text as per spec
            fontWeight: 600,
            marginRight: 3,
          }}
        >
          {pageTitle}
        </Typography>

        {/* Search Box */}
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            backgroundColor: '#1b3d89', // Search bar background
            borderRadius: '8px',
            padding: '8px 12px',
            marginRight: 3,
            minWidth: 200,
            '&:hover': {
              backgroundColor: '#345397', // Search bar hover
            },
          }}
        >
          <SearchIcon sx={{ color: '#8B949E', marginRight: 1, fontSize: 20 }} />
          <InputBase
            placeholder="Search..."
            sx={{
              color: '#FFFFFF', // White text
              fontSize: '14px',
              '& input::placeholder': {
                color: '#8B949E', // Placeholder text color
                opacity: 1,
              },
            }}
          />
        </Box>

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
                  color={isLast ? 'inherit' : '#2496ED'} // Docker blue for links
                  underline="hover"
                  onClick={() => !isLast && navigate(breadcrumb.path)}
                  sx={{
                    cursor: isLast ? 'default' : 'pointer',
                    '&:hover': {
                      color: isLast ? '#8B949E' : '#1B7FC4', // Darker blue on hover
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

        {/* Action Buttons Area */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Tooltip title="Settings">
            <IconButton
              sx={{
                color: '#C9D1D9', // Light grey by default
                '&:hover': {
                  backgroundColor: '#19222a', // Dashboard hover row
                  color: '#FFFFFF', // White on hover
                },
              }}
            >
              <SettingsIcon />
            </IconButton>
          </Tooltip>
          
          <Tooltip title="Help">
            <IconButton
              sx={{
                color: '#C9D1D9', // Light grey by default
                '&:hover': {
                  backgroundColor: '#19222a', // Dashboard hover row
                  color: '#FFFFFF', // White on hover
                },
              }}
            >
              <HelpIcon />
            </IconButton>
          </Tooltip>
          
          <Tooltip title="User Profile">
            <IconButton
              sx={{
                color: '#C9D1D9', // Light grey by default
                '&:hover': {
                  backgroundColor: '#19222a', // Dashboard hover row
                  color: '#FFFFFF', // White on hover
                },
              }}
            >
              <AccountIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default TopBar;
