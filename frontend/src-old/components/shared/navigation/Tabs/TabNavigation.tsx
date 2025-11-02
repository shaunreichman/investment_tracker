// ============================================================================
// TAB NAVIGATION - SHARED COMPONENT
// ============================================================================
// Generic, reusable tab navigation component with:
// - Full keyboard navigation (Arrow keys, Home, End)
// - Accessibility (ARIA roles, labels, keyboard focus management)
// - Responsive design (mobile-friendly)
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

import React, { useCallback, useRef } from 'react';
import { Box, Button, Typography } from '@mui/material';
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
  const isMobile = false; // TODO: Implement responsive breakpoint detection
  const tabRefs = useRef<(HTMLButtonElement | null)[]>([]);

  // Handle tab click - prevent calling onTabChange if already active
  const handleTabClick = useCallback((tabId: string) => {
    if (tabId !== activeTab) {
      onTabChange(tabId);
    }
  }, [activeTab, onTabChange]);

  // Handle keyboard navigation
  const handleKeyDown = useCallback((event: React.KeyboardEvent, tabIndex: number) => {
    let nextTabIndex = tabIndex;
    
    switch (event.key) {
      case 'ArrowRight':
        nextTabIndex = (tabIndex + 1) % tabs.length;
        break;
      case 'ArrowLeft':
        nextTabIndex = tabIndex === 0 ? tabs.length - 1 : tabIndex - 1;
        break;
      case 'Home':
        nextTabIndex = 0;
        break;
      case 'End':
        nextTabIndex = tabs.length - 1;
        break;
      default:
        return;
    }
    
    event.preventDefault();
    const nextTab = tabs[nextTabIndex];
    if (nextTab && !nextTab.disabled) {
      onTabChange(nextTab.id);
      tabRefs.current[nextTabIndex]?.focus();
    }
  }, [tabs, onTabChange]);

  // Set up tab refs array
  React.useEffect(() => {
    tabRefs.current = tabRefs.current.slice(0, tabs.length);
  }, [tabs.length]);

  return (
    <TabContainer role="tablist" aria-label={ariaLabel} className="tab-navigation">
      {tabs.map((tab, index) => (
        <TabButton
          key={tab.id}
          ref={(el) => {
            tabRefs.current[index] = el;
          }}
          active={activeTab === tab.id}
          isMobile={isMobile}
          disabled={tab.disabled || false}
          onClick={() => handleTabClick(tab.id)}
          onKeyDown={(e) => handleKeyDown(e, index)}
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

