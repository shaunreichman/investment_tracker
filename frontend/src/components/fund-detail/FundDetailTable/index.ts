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

// Future exports will be added here as we progress through the phases:
// Phase 2B.4: FundDetailTable component
// Phase 2B.5: TableHeader and TableActions components 