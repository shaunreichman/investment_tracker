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
    <Box sx={{ 
      display: 'flex', 
      flexDirection: 'column', 
      height: '100vh',
      // Define CSS custom properties for layout dimensions
      '--topbar-height': '56px',
      '--content-padding': '24px',
      '--content-top-offset': 'calc(var(--topbar-height) + var(--content-padding))',
      '--sidebar-width': sidebarOpen ? '280px' : '72px'
    } as any}>
      {/* Persistent TopBar - Clean implementation with key for route changes */}
      <TopBar key={topBarKey} />
      
      {/* Main Layout Area - CSS Grid for proper space distribution */}
      <Box sx={{ 
        display: 'grid',
        gridTemplateRows: '1fr', // Main content takes remaining space
        gridTemplateColumns: `${sidebarOpen ? 280 : 72}px 1fr`, // Sidebar + main content
        flex: 1,
        minHeight: 0 // Allow grid to shrink below content size
      }}>
        {/* Main Sidebar */}
        <Box
          sx={{
            position: 'fixed',
            top: 'var(--topbar-height)', // Use CSS custom property
            left: 0,
            height: 'calc(100vh - var(--topbar-height))', // Use CSS custom property
            zIndex: theme.zIndex.drawer,
          }}
        >
          <MainSidebar open={sidebarOpen} onToggle={handleSidebarToggle} />
        </Box>
        
        {/* Main Content Area */}
        <Box
          component="main"
          sx={{
            gridColumn: 2, // Position in second grid column
            width: '100%',
            height: '100%',
            minHeight: 0 // Allow grid item to shrink
          }}
        >
          {/* Content Area with proper spacing - account for TopBar height */}
          <Box
            sx={{
              padding: 'var(--content-padding)', // Use CSS custom property
              paddingTop: 'var(--content-top-offset)', // Use CSS custom property
              height: '100%',
              minHeight: 0, // Allow flex item to shrink
              backgroundColor: theme.palette.background.default, // Main dashboard background
              display: 'flex',
              flexDirection: 'column'
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
