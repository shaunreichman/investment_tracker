import React, { useCallback, useRef } from 'react';
import { Box, Button, Typography } from '@mui/material';
import { styled } from '@mui/material/styles';

// ============================================================================
// TYPES
// ============================================================================

export interface Tab {
  id: string;
  label: string;
  icon?: React.ReactNode;
  disabled?: boolean;
}

interface TabNavigationProps {
  tabs: Tab[];
  activeTab: string;
  onTabChange: (tabId: string) => void;
}

// ============================================================================
// STYLED COMPONENTS
// ============================================================================

const TabContainer = styled(Box)(({ theme }) => ({
  display: 'flex',
  borderBottom: `1px solid ${theme.palette.divider}`,
  backgroundColor: theme.palette.background.paper,
  '&.tab-navigation': {
    // Additional custom styles if needed
  },
  [theme.breakpoints.down('md')]: {
    flexDirection: 'column',
    borderBottom: 'none',
    borderRight: `1px solid ${theme.palette.divider}`,
  },
}));

const TabButton = styled(Button, {
  shouldForwardProp: (prop) => prop !== 'active' && prop !== 'isMobile',
})<{ active: boolean; isMobile: boolean }>(({ theme, active, isMobile }) => ({
  minHeight: 48,
  padding: theme.spacing(1, 3),
  borderRadius: 0,
  textTransform: 'none',
  fontWeight: active ? 600 : 400,
  color: active ? theme.palette.primary.main : theme.palette.text.secondary,
  backgroundColor: active ? theme.palette.background.paper : 'transparent',
  borderBottom: active ? `2px solid ${theme.palette.primary.main}` : 'none',
  borderRight: isMobile && active ? `2px solid ${theme.palette.primary.main}` : 'none',
  '&:hover': {
    backgroundColor: theme.palette.action.hover,
    color: theme.palette.text.primary,
  },
  '&:disabled': {
    color: theme.palette.text.disabled,
    backgroundColor: 'transparent',
  },
  [theme.breakpoints.down('md')]: {
    justifyContent: 'flex-start',
    borderBottom: 'none',
    borderRight: active ? `2px solid ${theme.palette.primary.main}` : 'none',
  },
}));

// ============================================================================
// COMPONENT
// ============================================================================

export const TabNavigation: React.FC<TabNavigationProps> = ({
  tabs,
  activeTab,
  onTabChange,
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
    <TabContainer role="tablist" aria-label="Company navigation tabs" className="tab-navigation">
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
          <Typography variant="body2" component="span">
            {tab.label}
          </Typography>
        </TabButton>
      ))}
    </TabContainer>
  );
};
