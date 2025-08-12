// Main Layout - Phase 4 Implementation (Clean Solution)
// Handles content area and TopBar positioning, sidebar now rendered inside routes

import React, { createContext, useContext } from 'react';
import { Box, CssBaseline } from '@mui/material';

// Create context for sidebar state (shared across all routes)
interface SidebarContextType {
  sidebarOpen: boolean;
  onSidebarToggle: () => void;
}

export const SidebarContext = createContext<SidebarContextType>({
  sidebarOpen: true,
  onSidebarToggle: () => {},
});

export const useSidebar = () => useContext(SidebarContext);

interface MainLayoutProps {
  children: React.ReactNode;
}

const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
  // Removed unused theme variable
  
  return (
    <Box sx={{ display: 'flex' }}>
      <CssBaseline />
      
      {/* Main Content Area - Sidebar will be rendered by children */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          width: '100%', // Full width since sidebar is handled by children
          minHeight: '100vh',
          backgroundColor: '#10151a', // Main dashboard background
        }}
      >
        {/* Content Area with proper spacing */}
        <Box
          sx={{
            padding: '24px', // 24px outer padding as per spec
            minHeight: '100vh',
          }}
        >
          {children}
        </Box>
      </Box>
    </Box>
  );
};

export default MainLayout;
