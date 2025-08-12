// Main Layout - Phase 2 Implementation
// Combines sidebar, top bar, and main content area

import React, { useState } from 'react';
import { Box, CssBaseline } from '@mui/material';
import MainSidebar from './MainSidebar';
import TopBar from './TopBar';

interface MainLayoutProps {
  children: React.ReactNode;
}

const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const handleSidebarToggle = () => {
    setSidebarOpen(!sidebarOpen);
  };

  return (
    <Box sx={{ display: 'flex' }}>
      <CssBaseline />
      
      {/* Main Sidebar */}
      <MainSidebar open={sidebarOpen} onToggle={handleSidebarToggle} />
      
      {/* Main Content Area */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          width: `calc(100% - ${sidebarOpen ? 280 : 64}px)`,
          transition: 'width 0.2s ease-in-out',
        }}
      >
        {/* Top Bar */}
        <TopBar sidebarOpen={sidebarOpen} />
        
        {/* Content Area with proper spacing */}
        <Box
          sx={{
            marginTop: '64px', // Account for fixed top bar
            padding: '24px', // 24px outer padding as per spec
            minHeight: 'calc(100vh - 64px)',
            backgroundColor: '#0D1117', // Docker main background
          }}
        >
          {children}
        </Box>
      </Box>
    </Box>
  );
};

export default MainLayout;
