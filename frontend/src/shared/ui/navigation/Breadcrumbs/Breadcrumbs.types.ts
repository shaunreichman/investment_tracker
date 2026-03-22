// ============================================================================
// BREADCRUMBS - TYPE DEFINITIONS
// ============================================================================
// Enterprise-grade breadcrumb component types with full feature support

import React from 'react';

/**
 * Analytics metadata for breadcrumb segments
 * Reserved for future analytics integration
 */
export interface BreadcrumbSegmentMeta {
  category?: string;
  action?: string;
  label?: string;
  [key: string]: unknown;
}

/**
 * Individual breadcrumb item with required and optional properties
 */
export interface BreadcrumbItem {
  /** Required unique identifier for the breadcrumb item */
  id: string;
  
  /** Required display label */
  label: string;
  
  /** Optional React Router path (preferred over onNavigate) */
  to?: string;
  
  /** Optional icon element */
  icon?: React.ReactNode;
  
  /** Whether the breadcrumb is disabled (non-clickable) */
  disabled?: boolean;
  
  /** Analytics metadata (reserved for future use) */
  segmentMeta?: BreadcrumbSegmentMeta;
}

/**
 * Props for custom render function
 */
export interface BreadcrumbItemRenderProps {
  item: BreadcrumbItem;
  isLast: boolean;
  isTruncated: boolean;
  index: number;
}

/**
 * Breadcrumbs component props
 */
export interface BreadcrumbsProps {
  /** Array of breadcrumb items */
  items: BreadcrumbItem[];
  
  /** Optional React Router Link component (defaults to react-router-dom Link) */
  LinkComponent?: React.ComponentType<React.PropsWithChildren<{ to: string; [key: string]: unknown }>>;
  
  /** Optional navigation handler (fallback when `to` is not provided) */
  onNavigate?: (item: BreadcrumbItem) => void;
  
  /** Optional custom separator between items */
  separator?: React.ReactNode;
  
  /** Maximum items to display before collapsing (middle ellipsis strategy) */
  maxItems?: number;
  
  /** Custom render function for breadcrumb items */
  renderItem?: (props: BreadcrumbItemRenderProps) => React.ReactNode;
  
  /** Custom ARIA label (defaults to "Breadcrumb") */
  ariaLabel?: string;
  
  /** Density variant (future use - only expose if both variants ship) */
  density?: 'compact' | 'comfortable';
  
  /** Whether to show tooltips on truncated labels */
  showTooltips?: boolean;
  
  /** Custom className */
  className?: string;
}

