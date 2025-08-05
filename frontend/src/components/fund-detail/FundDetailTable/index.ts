// ============================================================================
// FUND DETAIL TABLE COMPONENTS
// ============================================================================

// Phase 2B.1: Debug utilities (safe, no UI changes)
export {
  debugTableRendering,
  compareTableRendering,
  logEventGrouping,
  validateTableStructure,
  logTablePerformance,
  createTableDebugReport,
  type TableDebugInfo,
  type EventGroupingDebugInfo
} from './debug';

// Phase 2B.2: Event grouping logic hook
export {
  useEventGrouping,
  shouldShowEvent,
  isEquityEvent,
  isDistributionEvent,
  isOtherEvent,
  type GroupedEvent,
  type EventGroupingResult
} from './useEventGrouping';

// Phase 2B.3: Row rendering components
export {
  EventRow,
  type EventRowProps
} from './EventRow';

export {
  GroupedEventRow,
  type GroupedEventRowProps
} from './GroupedEventRow';

// Phase 2B.4: Table filters component
export {
  default as TableFilters,
  type TableFiltersProps
} from './TableFilters';

// Phase 2B.4: Table header component
export {
  default as TableHeader,
  type TableHeaderProps
} from './TableHeader';

// Phase 2B.4: Action buttons component
export {
  default as ActionButtons,
  type ActionButtonsProps
} from './ActionButtons';

// Phase 2B.4: Table body component
export {
  default as TableBody,
  type TableBodyProps
} from './TableBody';

// Phase 2B.5: Table container component
export {
  default as TableContainer,
  type TableContainerProps
} from './TableContainer';

// Future exports will be added here as we progress through the phases:
// Phase 2B.6: Complete table integration 