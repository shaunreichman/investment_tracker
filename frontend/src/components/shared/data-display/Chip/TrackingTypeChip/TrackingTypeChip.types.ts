// ============================================================================
// TRACKING TYPE CHIP TYPES
// ============================================================================

/**
 * Props for the TrackingTypeChip component
 */
export interface TrackingTypeChipProps {
  /** The tracking type to display ('nav_based' or 'cost_based') */
  trackingType: string;
  /** Size of the chip */
  size?: 'small' | 'medium';
  /** Additional CSS class name */
  className?: string;
}

/**
 * Supported tracking type values
 */
export type TrackingType = 'nav_based' | 'cost_based';

