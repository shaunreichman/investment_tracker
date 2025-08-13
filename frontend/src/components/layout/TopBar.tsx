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
} from '@mui/material';
import {
  Search as SearchIcon,
  Notifications as NotificationsIcon,
  AccountCircle as AccountCircleIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useSidebar } from './MainLayout';

interface TopBarProps {
  pageTitle?: string;
  breadcrumbs?: Array<{ label: string; path: string }>;
}

const TopBar: React.FC<TopBarProps> = ({ 
  pageTitle = 'Dashboard',
  breadcrumbs = [{ label: 'Dashboard', path: '/' }]
}) => {
  const theme = useTheme();
  const navigate = useNavigate();
  // We don't need sidebarOpen for now, but keeping the context for future use
  useSidebar();

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

        {/* Search Box */}
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            backgroundColor: theme.palette.background.search, // Search bar background
            borderRadius: '8px',
            padding: '8px 12px',
            marginRight: 3,
            minWidth: 200,
            '&:hover': {
              backgroundColor: theme.palette.background.searchHover, // Search bar hover
            },
          }}
        >
          <SearchIcon sx={{ color: theme.palette.text.muted, marginRight: 1, fontSize: 20 }} />
          <InputBase
            placeholder="Search..."
            sx={{
                          color: theme.palette.text.primary, // White text
            fontSize: '14px',
            '& input::placeholder': {
              color: theme.palette.text.muted, // Placeholder text color
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
