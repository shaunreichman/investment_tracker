// ============================================================================
// FUND DETAIL TABLE COMPONENTS
// ============================================================================

// Phase 2B.1: Debug utilities (safe, no UI changes)
export {
  createTableDebugReport,
  debugTableRendering,
  compareTableRendering,
  logEventGrouping,
  validateTableStructure,
  logTablePerformance,
  type TableDebugInfo,
  type EventGroupingDebugInfo
} from './debug';

// Phase 2B.2: Event grouping logic hook (safe, isolated logic)
export {
  useEventGrouping,
  shouldShowEvent,
  isEquityEvent,
  isDistributionEvent,
  isOtherEvent,
  type GroupedEvent,
  type EventGroupingResult
} from './useEventGrouping';

// Phase 2B.3: Row rendering components (safe, isolated components)
export { EventRow, type EventRowProps } from './EventRow';
export { GroupedEventRow, type GroupedEventRowProps } from './GroupedEventRow';

// Phase 2B.4: Granular table extraction components
export { default as TableFilters } from './TableFilters';
export { default as TableHeader } from './TableHeader';
export { default as ActionButtons } from './ActionButtons';
export { default as TableBody } from './TableBody';
export { default as TableContainer } from './TableContainer';

// Future exports will be added here as we progress through the phases:
// Phase 2B.6: Complete table integration 