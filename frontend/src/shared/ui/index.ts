// ============================================================================
// SHARED UI COMPONENTS - BARREL EXPORT
// ============================================================================

// Data Display components
export {
  StatusChip,
  EventTypeChip,
  TrackingTypeChip,
  StatCard,
  SummaryCard,
} from './data-display';

export type {
  StatusChipProps,
  StatusValue,
  EventTypeChipProps,
  EventTypeColorVariant,
  TrackingTypeChipProps,
  TrackingType,
  StatCardProps,
  TrendIndicator,
  SummaryCardProps,
  SummarySection,
  SummarySectionRow,
} from './data-display';

// Feedback components
export {
  LoadingSpinner,
  SuccessBanner,
  DomainErrorBoundary,
  ErrorDisplay,
  ErrorHeader,
  ErrorMessage,
  ErrorDetails,
  ErrorMetadata,
  ErrorRetry,
} from './feedback';

export type {
  LoadingSpinnerProps,
  SuccessBannerProps,
  DomainErrorBoundaryProps,
  Domain,
  ErrorDisplayProps,
  ErrorHeaderProps,
  ErrorMessageProps,
  ErrorDetailsProps,
  ErrorMetadataProps,
  ErrorRetryProps,
} from './feedback';

// Form components
export {
  NumberInputField,
} from './forms';

export type {
  NumberInputFieldProps,
} from './forms';

// Navigation components
export {
  TabNavigation,
  Breadcrumbs,
} from './navigation';

export type {
  Tab,
  TabNavigationProps,
  BreadcrumbItem,
  BreadcrumbsProps,
  BreadcrumbItemRenderProps,
  BreadcrumbSegmentMeta,
} from './navigation';

// Overlay components
export {
  ConfirmDialog,
  FormModal,
} from './overlays';

export type {
  ConfirmDialogProps,
  ActionDescriptor,
  OverlayEvent,
  FormModalProps,
} from './overlays';

// Layout components
export {
  RouteLayout,
  SidebarContext,
  useSidebar,
  MainSidebar,
  TopBar,
} from './layout';

