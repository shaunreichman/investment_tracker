// Main Sidebar Navigation - Phase 2 Implementation
// Docker-style collapsible left sidebar with navigation items

import React from 'react';
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
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  Business as CompaniesIcon,
  AccountBalance as FundsIcon,
  ChevronLeft as ChevronLeftIcon,
  ChevronRight as ChevronRightIcon,
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';

interface MainSidebarProps {
  open: boolean;
  onToggle: () => void;
}

const MainSidebar: React.FC<MainSidebarProps> = ({ open, onToggle }) => {
  const theme = useTheme();
  const navigate = useNavigate();
  const location = useLocation();

  // Navigation items configuration
  const navigationItems = [
    {
      id: 'dashboard',
      label: 'Dashboard',
      icon: <DashboardIcon />,
      path: '/',
    },
    {
      id: 'companies',
      label: 'Companies',
      icon: <CompaniesIcon />,
      path: '/companies',
    },
    {
      id: 'funds',
      label: 'Funds',
      icon: <FundsIcon />,
      path: '/funds',
    },
  ];

  // Check if item is active
  const isActive = (path: string) => {
    if (path === '/') {
      return location.pathname === '/';
    }
    return location.pathname.startsWith(path);
  };

  // Handle navigation
  const handleNavigation = (path: string) => {
    navigate(path);
  };

  return (
    <Drawer
      variant="permanent"
      sx={{
        width: open ? 240 : 72,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: open ? 240 : 72,
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
                backgroundColor: '#19222a', // Dashboard hover row
                color: '#2496ED',
              },
            }}
          >
            {open ? <ChevronLeftIcon /> : <ChevronRightIcon />}
          </IconButton>
        </Tooltip>
      </Box>

      {/* Navigation List */}
      <List sx={{ padding: 1 }}>
        {navigationItems.map((item) => {
          const active = isActive(item.path);
          return (
            <ListItem key={item.id} disablePadding sx={{ mb: 1 }}>
              <ListItemButton
                onClick={() => handleNavigation(item.path)}
                sx={{
                  borderRadius: 1,
                  backgroundColor: active ? '#303234' : 'transparent', // Navigation selection color
                  border: 'none',
                  position: 'relative',
                  '&:hover': {
                    backgroundColor: active 
                      ? '#303234' 
                      : '#19222a', // Dashboard hover row
                    cursor: 'pointer',
                  },
                  minHeight: 36, // Reduced from 48px
                  padding: '8px 12px', // Reduced from 16px
                  paddingLeft: open ? '12px' : '8px', // Reduced padding
                  paddingRight: open ? '12px' : '8px', // Reduced padding
                }}
              >
                {/* Active Link Indicator - 3px solid bar on the left */}
                {active && (
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
                    color: active ? '#FFFFFF' : '#C9D1D9',
                    minWidth: open ? 40 : 32,
                    '& .MuiSvgIcon-root': {
                      fontSize: '24px', // 24px icon size as per spec
                    },
                    '&:hover': {
                      color: '#2496ED',
                    },
                  }}
                >
                  {item.icon}
                </ListItemIcon>
                {open && (
                  <ListItemText
                    primary={item.label}
                    sx={{
                      color: active ? '#FFFFFF' : '#C9D1D9',
                      fontWeight: active ? 600 : 400,
                    }}
                  />
                )}
              </ListItemButton>
            </ListItem>
          );
        })}
      </List>
    </Drawer>
  );
};

export default MainSidebar;
