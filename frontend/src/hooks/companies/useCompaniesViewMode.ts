// ============================================================================
// COMPANIES VIEW MODE HOOK
// ============================================================================

import { useState, useCallback } from 'react';
import { ViewMode } from '../shared/useResponsiveView';

interface UseCompaniesViewModeProps {
  defaultView?: ViewMode;
  onViewModeChange?: (mode: ViewMode) => void;
}

export const useCompaniesViewMode = ({
  defaultView = 'table',
  onViewModeChange,
}: UseCompaniesViewModeProps = {}) => {
  const [viewMode, setViewMode] = useState<ViewMode>(defaultView);

  const handleViewModeChange = useCallback((mode: ViewMode) => {
    setViewMode(mode);
    onViewModeChange?.(mode);
  }, [onViewModeChange]);

  const toggleViewMode = useCallback(() => {
    const newMode = viewMode === 'table' ? 'cards' : 'table';
    handleViewModeChange(newMode);
  }, [viewMode, handleViewModeChange]);

  return {
    viewMode,
    handleViewModeChange,
    toggleViewMode,
    isTable: viewMode === 'table',
    isCards: viewMode === 'cards',
  };
};
