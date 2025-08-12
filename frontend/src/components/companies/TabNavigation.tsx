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
  borderBottom: '1px solid #303234', // Docker border color
  backgroundColor: '#1F2937', // Docker panel background
  borderRadius: '8px 8px 0 0', // Rounded top corners
  overflow: 'hidden',
  '&.tab-navigation': {
    // Additional custom styles if needed
  },
  [theme.breakpoints.down('md')]: {
    flexDirection: 'column',
    borderBottom: 'none',
    borderRight: '1px solid #303234',
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
  color: active ? '#FFFFFF' : '#8B949E', // Docker text colors
  backgroundColor: active ? '#070b0d' : 'transparent', // Docker active background
  borderBottom: active ? '3px solid #2496ED' : 'none', // Docker blue indicator
  borderRight: isMobile && active ? '3px solid #2496ED' : 'none',
  transition: 'all 0.2s ease-in-out',
  '&:hover': {
    backgroundColor: active ? '#070b0d' : '#19222a', // Docker hover colors
    color: active ? '#FFFFFF' : '#C9D1D9',
  },
  '&:disabled': {
    color: '#6B7280',
    backgroundColor: 'transparent',
  },
  [theme.breakpoints.down('md')]: {
    justifyContent: 'flex-start',
    borderBottom: 'none',
    borderRight: active ? '3px solid #2496ED' : 'none',
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
