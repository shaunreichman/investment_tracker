// ============================================================================
// TAB NAVIGATION - TYPE DEFINITIONS
// ============================================================================

export interface Tab {
  id: string;
  label: string;
  icon?: React.ReactNode;
  disabled?: boolean;
}

export interface TabNavigationProps {
  tabs: Tab[];
  activeTab: string;
  onTabChange: (tabId: string) => void;
  ariaLabel?: string; // Optional, defaults to "Navigation tabs"
}

