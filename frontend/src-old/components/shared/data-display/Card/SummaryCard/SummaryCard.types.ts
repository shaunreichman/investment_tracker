// ============================================================================
// SUMMARY CARD TYPES
// ============================================================================

import type { ReactNode } from 'react';

/**
 * Props for the SummaryCard component
 */
export interface SummaryCardProps {
  /** Title for the summary card */
  title: string;
  /** Optional icon to display with the title */
  icon?: ReactNode;
  /** Array of sections to display */
  sections: SummarySection[];
  /** Optional footer content */
  footer?: ReactNode;
  /** Additional CSS class name */
  className?: string;
}

/**
 * Individual section within a summary card
 */
export interface SummarySection {
  /** Optional section title */
  title?: string;
  /** Content for this section (can be any React node or data rows) */
  content: ReactNode | SummarySectionRow[];
  /** Whether to show a divider after this section */
  showDivider?: boolean;
}

/**
 * Data row within a summary section
 */
export interface SummarySectionRow {
  /** Label for the row */
  label: string;
  /** Value to display */
  value: ReactNode;
  /** Optional icon */
  icon?: ReactNode;
  /** Optional color for the value */
  color?: string;
  /** Whether to emphasize this row */
  emphasized?: boolean;
}

