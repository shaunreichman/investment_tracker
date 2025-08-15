// Route Layout - Phase 4 Implementation (Clean Solution)
// Combines sidebar and main content, allowing sidebar to access route parameters
// Now includes persistent TopBar for consistent navigation

import React, { useState, createContext, useContext } from 'react';
import { Box, useTheme } from '@mui/material';
import { useLocation } from 'react-router-dom';
import TopBar from './TopBar';
import MainSidebar from './MainSidebar';

// Create context for sidebar state
interface SidebarContextType {
  sidebarOpen: boolean;
  onSidebarToggle: () => void;
}

export const SidebarContext = createContext<SidebarContextType>({
  sidebarOpen: true,
  onSidebarToggle: () => {},
});

export const useSidebar = () => useContext(SidebarContext);

const RouteLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const theme = useTheme();
  const location = useLocation();

  const handleSidebarToggle = () => {
    setSidebarOpen(!sidebarOpen);
  };

  // Create a key for TopBar based on the current route to force re-render on navigation
  const topBarKey = location.pathname;

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
      {/* Persistent TopBar - Clean implementation with key for route changes */}
      <TopBar key={topBarKey} />
      <Box sx={{ display: 'flex', flex: 1 }}>
        {/* Main Sidebar */}
        <Box
          sx={{
            position: 'fixed',
            top: '56px', // Start below the TopBar
            left: 0,
            height: 'calc(100vh - 56px)', // Full height minus TopBar
            zIndex: theme.zIndex.drawer,
          }}
        >
          <MainSidebar open={sidebarOpen} onToggle={handleSidebarToggle} />
        </Box>
        
        {/* Main Content Area */}
        <Box
          component="main"
          sx={{
            flexGrow: 1,
            width: `calc(100% - ${sidebarOpen ? 280 : 72}px)`, // Updated sidebar dimensions
            marginLeft: `${sidebarOpen ? 280 : 72}px`, // Offset for sidebar
            transition: 'width 0.2s ease-in-out, margin-left 0.2s ease-in-out',
          }}
        >
          {/* Content Area with proper spacing - account for TopBar height */}
          <Box
            sx={{
              padding: '24px', // 24px outer padding as per spec
              paddingTop: '80px', // 56px TopBar height + 24px spacing
              minHeight: 'calc(100vh - 56px)',
              backgroundColor: theme.palette.background.default, // Main dashboard background
            }}
          >
            <SidebarContext.Provider value={{ sidebarOpen, onSidebarToggle: handleSidebarToggle }}>
              {children}
            </SidebarContext.Provider>
          </Box>
        </Box>
      </Box>
    </Box>
  );
};

export default RouteLayout;
