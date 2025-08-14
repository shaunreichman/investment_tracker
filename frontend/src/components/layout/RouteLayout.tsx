// Route Layout - Phase 4 Implementation (Clean Solution)
// Combines sidebar and main content, allowing sidebar to access route parameters
// Now includes persistent TopBar for consistent navigation

import React, { useState, createContext, useContext } from 'react';
import { Box, useTheme } from '@mui/material';
import MainSidebar from './MainSidebar';
import TopBar from './TopBar';

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

interface RouteLayoutProps {
  children: React.ReactNode;
}

const RouteLayout: React.FC<RouteLayoutProps> = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const theme = useTheme();

  const handleSidebarToggle = () => {
    setSidebarOpen(!sidebarOpen);
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      {/* Persistent TopBar - Now part of layout structure */}
      <TopBar />
      
      {/* Main Content and Sidebar Container */}
      <Box sx={{ display: 'flex', flex: 1 }}>
        {/* Main Sidebar - Now has access to route parameters */}
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
