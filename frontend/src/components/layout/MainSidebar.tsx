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
        width: open ? 280 : 64,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: open ? 280 : 64,
          backgroundColor: '#161B22', // Docker sidebar background
          borderRight: '1px solid rgba(255,255,255,0.08)',
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
          borderBottom: '1px solid rgba(255,255,255,0.08)',
        }}
      >
        <Tooltip title={open ? 'Collapse Sidebar' : 'Expand Sidebar'}>
          <IconButton
            onClick={onToggle}
            sx={{
              color: '#FFFFFF',
              '&:hover': {
                backgroundColor: 'rgba(255,255,255,0.04)',
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
                  backgroundColor: active ? 'rgba(0,127,255,0.1)' : 'transparent',
                  border: active ? '1px solid rgba(0,127,255,0.3)' : 'none',
                  '&:hover': {
                    backgroundColor: active 
                      ? 'rgba(0,127,255,0.15)' 
                      : 'rgba(255,255,255,0.04)',
                  },
                  minHeight: 48,
                  padding: open ? '12px 16px' : '12px 8px',
                }}
              >
                <ListItemIcon
                  sx={{
                    color: active ? '#007FFF' : '#8B949E',
                    minWidth: open ? 40 : 32,
                  }}
                >
                  {item.icon}
                </ListItemIcon>
                {open && (
                  <ListItemText
                    primary={item.label}
                    sx={{
                      color: active ? '#FFFFFF' : '#8B949E',
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
