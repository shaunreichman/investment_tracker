/**
 * Shared Form Component Types
 * 
 * Common interfaces and types used across form components.
 */

/**
 * Option for select dropdowns
 */
export interface SelectOption {
  /** The value to be stored when this option is selected */
  value: string | number;
  /** Display label shown to the user */
  label: string;
}

/**
 * Option for radio buttons with optional disabled state
 */
export interface RadioOption {
  /** The value to be stored when this option is selected */
  value: string | number | boolean;
  /** Display label shown to the user */
  label: string;
  /** Whether this option is disabled */
  disabled?: boolean;
}
