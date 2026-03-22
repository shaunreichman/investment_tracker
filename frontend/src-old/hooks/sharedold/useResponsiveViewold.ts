// ============================================================================
// RESPONSIVE VIEW HOOK
// ============================================================================

import { useState, useEffect, useCallback } from 'react';

export type ViewMode = 'table' | 'cards';

interface UseResponsiveViewProps {
  defaultView?: ViewMode;
  mobileBreakpoint?: number;
}

export const useResponsiveView = ({
  defaultView = 'table',
  mobileBreakpoint = 768,
}: UseResponsiveViewProps = {}) => {
  const [viewMode, setViewMode] = useState<ViewMode>(defaultView);

  // Auto-switch to card view on mobile devices
  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth < mobileBreakpoint) {
        setViewMode('cards');
      } else {
        setViewMode('table');
      }
    };

    // Set initial view mode
    handleResize();

    // Add event listener
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [mobileBreakpoint]);

  // Manual view mode change
  const handleViewModeChange = useCallback((mode: ViewMode) => {
    setViewMode(mode);
  }, []);

  return {
    viewMode,
    handleViewModeChange,
    isMobile: viewMode === 'cards',
  };
};
