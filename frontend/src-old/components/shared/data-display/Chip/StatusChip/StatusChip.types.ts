// ============================================================================
// STATUS CHIP TYPES
// ============================================================================

/**
 * Props for the StatusChip component
 */
export interface StatusChipProps {
  /** The status value to display (e.g., 'active', 'completed', 'error') */
  status: string;
  /** Size of the chip */
  size?: 'small' | 'medium';
  /** Additional CSS class name */
  className?: string;
}

/**
 * Supported status values and their color mappings:
 * - Success: 'active', 'completed', 'success'
 * - Warning: 'pending', 'processing', 'warning'
 * - Error: 'error', 'failed', 'cancelled'
 * - Info: 'info', 'draft', or any other value (default)
 */
export type StatusValue = 
  | 'active' 
  | 'completed' 
  | 'success'
  | 'pending' 
  | 'processing' 
  | 'warning'
  | 'error' 
  | 'failed' 
  | 'cancelled'
  | 'info' 
  | 'draft'
  | string; // Allow any string for flexibility

