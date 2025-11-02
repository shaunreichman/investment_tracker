// ============================================================================
// EVENT TYPE CHIP TYPES
// ============================================================================

/**
 * Props for the EventTypeChip component
 */
export interface EventTypeChipProps {
  /** The event type to display (e.g., 'NAV_UPDATE', 'DISTRIBUTION') */
  eventType: string;
  /** Size of the chip */
  size?: 'small' | 'medium';
  /** Additional CSS class name */
  className?: string;
}

/**
 * Color variants for event types
 * Mapped via getEventTypeColor utility function
 */
export type EventTypeColorVariant = 
  | 'primary' 
  | 'success' 
  | 'warning' 
  | 'error' 
  | 'info' 
  | 'default';

