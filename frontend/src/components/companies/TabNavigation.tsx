import React from 'react';
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

  return (
    <TabContainer>
      {tabs.map((tab) => (
        <TabButton
          key={tab.id}
          active={activeTab === tab.id}
          isMobile={isMobile}
          disabled={tab.disabled || false}
          onClick={() => onTabChange(tab.id)}
          startIcon={tab.icon}
          aria-label={tab.label}
          aria-selected={activeTab === tab.id}
          role="tab"
        >
          <Typography variant="body2" component="span">
            {tab.label}
          </Typography>
        </TabButton>
      ))}
    </TabContainer>
  );
};
