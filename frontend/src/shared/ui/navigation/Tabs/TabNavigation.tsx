// ============================================================================
// TAB NAVIGATION - SHARED COMPONENT
// ============================================================================
// Generic, reusable tab navigation component with:
// - Standard keyboard navigation (Tab key for focus management)
// - Accessibility (ARIA roles, labels, keyboard focus management)
// - Responsive design (mobile-friendly with breakpoint detection)
// - Icon support
// - Disabled tab support
// - Theme integration
//
// Usage:
//   <TabNavigation
//     tabs={[
//       { id: 'overview', label: 'Overview', icon: <HomeIcon /> },
//       { id: 'details', label: 'Details', disabled: true }
//     ]}
//     activeTab={activeTab}
//     onTabChange={setActiveTab}
//     ariaLabel="Company navigation tabs"
//   />
// ============================================================================

import React, { useCallback } from 'react';
import { Box, Button, Typography, useMediaQuery, useTheme } from '@mui/material';
import { styled } from '@mui/material/styles';
import type { TabNavigationProps } from './TabNavigation.types';

// ============================================================================
// STYLED COMPONENTS
// ============================================================================

const TabContainer = styled(Box)(({ theme }) => ({
  display: 'flex',
  borderBottom: `1px solid ${theme.palette.divider}`,
  backgroundColor: theme.palette.background.paper,
  borderRadius: '8px 8px 0 0', // Rounded top corners
  overflow: 'hidden',
  '&.tab-navigation': {
    // Additional custom styles if needed
  },
  [theme.breakpoints.down('md')]: {
    flexDirection: 'column',
    borderBottom: 'none',
    borderRight: `1px solid ${theme.palette.divider}`,
    borderRadius: '8px 0 0 8px', // Rounded left corners on mobile
  },
}));

const TabButton = styled(Button, {
  shouldForwardProp: (prop) => prop !== 'active' && prop !== 'isMobile',
})<{ active: boolean; isMobile: boolean }>(({ theme, active, isMobile }) => ({
  minHeight: 56, // Increased height for better touch targets
  padding: '16px 24px', // Docker-style generous padding
  borderRadius: 0,
  textTransform: 'none',
  fontWeight: active ? 600 : 500,
  fontSize: '14px',
  color: active ? theme.palette.text.primary : theme.palette.text.muted,
  backgroundColor: active ? theme.palette.background.sidebar : 'transparent',
  borderBottom: active ? `3px solid ${theme.palette.primary.main}` : 'none',
  borderRight: isMobile && active ? `3px solid ${theme.palette.primary.main}` : 'none',
  transition: 'all 0.2s ease-in-out',
  '&:hover': {
    backgroundColor: active ? theme.palette.background.sidebar : theme.palette.background.sidebarHover,
    color: active ? theme.palette.text.primary : theme.palette.text.secondary,
  },
  '&:disabled': {
    color: theme.palette.text.disabled,
    backgroundColor: 'transparent',
  },
  [theme.breakpoints.down('md')]: {
    justifyContent: 'flex-start',
    borderBottom: 'none',
    borderRight: active ? `3px solid ${theme.palette.primary.main}` : 'none',
  },
}));

// ============================================================================
// COMPONENT
// ============================================================================

export const TabNavigation: React.FC<TabNavigationProps> = ({
  tabs,
  activeTab,
  onTabChange,
  ariaLabel = 'Navigation tabs', // Default generic label
}) => {
  const theme = useTheme();
  // Detect mobile breakpoint (md breakpoint = 900px)
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  // Handle tab click - prevent calling onTabChange if already active
  const handleTabClick = useCallback((tabId: string) => {
    if (tabId !== activeTab) {
      onTabChange(tabId);
    }
  }, [activeTab, onTabChange]);

  return (
    <TabContainer role="tablist" aria-label={ariaLabel} className="tab-navigation">
      {tabs.map((tab) => (
        <TabButton
          key={tab.id}
          active={activeTab === tab.id}
          isMobile={isMobile}
          disabled={tab.disabled || false}
          onClick={() => handleTabClick(tab.id)}
          startIcon={tab.icon}
          aria-label={tab.label}
          aria-selected={activeTab === tab.id}
          role="tab"
          tabIndex={activeTab === tab.id ? 0 : -1}
          id={`${tab.id}-tab`}
        >
          <Typography 
            variant="body2" 
            component="span"
            sx={{
              fontWeight: 'inherit',
              fontSize: '14px',
              lineHeight: 1.4
            }}
          >
            {tab.label}
          </Typography>
        </TabButton>
      ))}
    </TabContainer>
  );
};

