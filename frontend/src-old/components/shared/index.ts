// ============================================================================
// SHARED COMPONENTS - BARREL EXPORTS
// ============================================================================

// Data Display
export { 
  StatCard,
  DataCard,
  SummaryCard,
  StatusChip,
  EventTypeChip,
  TrackingTypeChip
} from './data-display';
export type {
  StatCardProps,
  TrendIndicator,
  DataCardProps,
  DataRow,
  SummaryCardProps,
  SummarySection,
  SummarySectionRow,
  StatusChipProps,
  StatusValue,
  EventTypeChipProps,
  EventTypeColorVariant,
  TrackingTypeChipProps,
  TrackingType
} from './data-display';

// Navigation
export { TabNavigation, Breadcrumbs } from './navigation';
export type { Tab, TabNavigationProps, BreadcrumbItem, BreadcrumbsProps } from './navigation';

// Feedback
export { ErrorDisplay } from './feedback';
export { ErrorToast } from './feedback';
export { DomainErrorBoundary } from './feedback';
export { LoadingSpinner } from './feedback';
export { SuccessBanner } from './feedback';
export type { DomainErrorBoundaryProps, Domain } from './feedback';

// Forms
export {
  FormTextField,
  FormTextArea,
  FormNumberField,
  FormDateField,
  FormSelectField,
  FormRadioGroup,
  FormCheckbox,
  FormSwitch
} from './forms';
export type { SelectOption, RadioOption } from './forms';

// Overlays
export { ConfirmDialog, FormModal } from './overlays';
export type { ConfirmDialogProps, FormModalProps } from './overlays';
