// ============================================================================
// BREADCRUMBS - TYPE DEFINITIONS
// ============================================================================

export interface BreadcrumbItem {
  label: string;
  path: string;
  icon?: React.ReactNode;
}

export interface BreadcrumbsProps {
  items: BreadcrumbItem[];
  onNavigate: (path: string) => void;
  separator?: React.ReactNode; // Optional custom separator
  maxItems?: number; // For collapsing long breadcrumb trails
  ariaLabel?: string; // Optional, defaults to "breadcrumb"
}

