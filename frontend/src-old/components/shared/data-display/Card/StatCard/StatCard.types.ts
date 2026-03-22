// ============================================================================
// STAT CARD TYPES
// ============================================================================

import type { ReactNode } from 'react';

/**
 * Props for the StatCard component
 */
export interface StatCardProps {
  /** Title/label for the statistic */
  title: string;
  /** The main value to display (can be string, number, or formatted value) */
  value: string | number;
  /** Optional subtitle text */
  subtitle?: string;
  /** Optional icon to display */
  icon?: ReactNode;
  /** Color theme for the card */
  color?: 'primary' | 'success' | 'error' | 'warning' | 'info' | 'default';
  /** Optional trend indicator */
  trend?: TrendIndicator;
  /** Click handler for interactive cards */
  onClick?: () => void;
  /** Additional CSS class name */
  className?: string;
}

/**
 * Trend indicator configuration
 */
export interface TrendIndicator {
  /** Numeric value of the trend */
  value: number;
  /** Direction of the trend */
  direction: 'up' | 'down';
  /** Whether this trend direction is positive (green) or negative (red) */
  isPositive?: boolean;
  /** Optional label for the trend */
  label?: string;
}

