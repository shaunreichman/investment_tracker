// Main Layout - Phase 2 Implementation
// Combines sidebar, top bar, and main content area

import React, { useState } from 'react';
import { Box, CssBaseline, useTheme } from '@mui/material';
import MainSidebar from './MainSidebar';
import TopBar from './TopBar';

interface MainLayoutProps {
  children: React.ReactNode;
}

const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const theme = useTheme();

  const handleSidebarToggle = () => {
    setSidebarOpen(!sidebarOpen);
  };

  return (
    <Box sx={{ display: 'flex' }}>
      <CssBaseline />
      
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
          width: `calc(100% - ${sidebarOpen ? 240 : 72}px)`, // Updated sidebar dimensions
          marginLeft: `${sidebarOpen ? 240 : 72}px`, // Offset for sidebar
          transition: 'width 0.2s ease-in-out, margin-left 0.2s ease-in-out',
        }}
      >
        {/* Top Bar */}
        <TopBar sidebarOpen={sidebarOpen} />
        
        {/* Content Area with proper spacing */}
        <Box
          sx={{
            marginTop: '56px', // Account for 56px fixed top bar
            padding: '24px', // 24px outer padding as per spec
            minHeight: 'calc(100vh - 56px)',
            backgroundColor: '#10151a', // Main dashboard background
          }}
        >
          {children}
        </Box>
      </Box>
    </Box>
  );
};

export default MainLayout;
