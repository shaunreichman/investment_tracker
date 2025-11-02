// ============================================================================
// DATA CARD TYPES
// ============================================================================

import type { ReactNode } from 'react';

/**
 * Props for the DataCard component
 */
export interface DataCardProps {
  /** Optional title for the card */
  title?: string;
  /** Array of data rows to display */
  data: DataRow[];
  /** Click handler for individual rows */
  onItemClick?: (index: number) => void;
  /** Additional CSS class name */
  className?: string;
}

/**
 * Individual data row configuration
 */
export interface DataRow {
  /** Label for the data row */
  label: string;
  /** Value to display (can be string, number, or React node) */
  value: ReactNode;
  /** Optional icon to display before the label */
  icon?: ReactNode;
  /** Optional color for the value */
  color?: string;
  /** Optional helper text below the row */
  helperText?: string;
  /** Whether this row should be highlighted */
  highlighted?: boolean;
}

