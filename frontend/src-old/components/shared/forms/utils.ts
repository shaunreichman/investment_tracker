/**
 * Form Field Utilities
 * 
 * Shared utilities for consistent validation display and field rendering
 * across all form components. Eliminates duplication and enforces
 * enterprise-grade UX standards.
 */

import * as React from 'react';
import { ControllerFieldState } from 'react-hook-form';

/**
 * Determines if a field error should be displayed to the user
 * 
 * Enterprise UX Rule: Only show errors AFTER the user has interacted with the field.
 * This prevents showing errors on page load and provides a better user experience.
 * 
 * @param fieldState - React Hook Form field state
 * @returns true if error should be shown, false otherwise
 * 
 * @example
 * ```typescript
 * const showError = shouldShowError(fieldState);
 * <TextField error={showError} />
 * ```
 */
export function shouldShowError(fieldState: ControllerFieldState): boolean {
  return !!fieldState.error && fieldState.isTouched;
}

/**
 * Generates a form label with optional required indicator
 * 
 * Enterprise UX Rule: Required fields show a red asterisk (*) to indicate
 * to users that the field must be completed.
 * 
 * @param label - The field label text
 * @param required - Whether the field is required
 * @returns React element with label and optional asterisk
 * 
 * @example
 * ```typescript
 * <TextField label={getFieldLabel('Fund Name', true)} />
 * // Renders: "Fund Name *" (with red asterisk)
 * ```
 */
export function getFieldLabel(label: string, required: boolean = false): React.ReactElement {
  return React.createElement(
    'span',
    null,
    label,
    required && React.createElement('span', { style: { color: 'red' } }, ' *')
  );
}

/**
 * Gets the appropriate helper text for a field based on validation state
 * 
 * Enterprise UX Rule: Error messages take priority over helper text.
 * Only show helper text when there's no error OR the field hasn't been touched.
 * 
 * @param fieldState - React Hook Form field state
 * @param helperText - Optional helper text to show when no error
 * @returns Error message if error should be shown, otherwise helper text
 * 
 * @example
 * ```typescript
 * const helperText = getHelperText(fieldState, 'Enter your full name');
 * <TextField helperText={helperText} />
 * ```
 */
export function getHelperText(
  fieldState: ControllerFieldState, 
  helperText?: string
): string | undefined {
  if (shouldShowError(fieldState)) {
    return fieldState.error?.message;
  }
  return helperText;
}

/**
 * Gets the appropriate border color for a field based on validation state
 * 
 * Enterprise UX Rule - Visual Priority Hierarchy:
 * 1. RED: Error state (touched + invalid) - Immediate attention needed
 * 2. BLUE: Required indicator (required + empty) - User should complete this
 * 3. DEFAULT: Normal state - No special attention needed
 * 
 * This provides immediate visual feedback about field importance and state
 * without being overwhelming or showing "errors" before user interaction.
 * 
 * @param fieldState - React Hook Form field state
 * @param required - Whether the field is required
 * @returns Material-UI color prop value
 * 
 * @example
 * ```typescript
 * <TextField
 *   color={getFieldColor(fieldState, true)}
 *   error={shouldShowError(fieldState)}
 * />
 * ```
 */
export function getFieldColor(
  fieldState: ControllerFieldState,
  required: boolean = false
): 'primary' | 'info' | 'error' {
  // Priority 1: Show error color if touched and invalid (RED)
  if (shouldShowError(fieldState)) {
    return 'error';
  }
  
  // Priority 2: Show info color for required empty fields (BLUE)
  // Note: This shows immediately to help users understand what's required
  if (required && !fieldState.isDirty) {
    return 'info';
  }
  
  // Priority 3: Normal state (DEFAULT GRAY)
  return 'primary';
}

/**
 * Bundle of field state utilities for use in form components
 * Provides all validation display logic in a single hook
 * 
 * @param fieldState - React Hook Form field state
 * @param label - Field label text
 * @param required - Whether field is required
 * @param helperText - Optional helper text
 * @returns Object with all field display logic
 * 
 * @example
 * ```typescript
 * const { showError, displayLabel, displayHelperText, fieldColor } = useFieldState(
 *   fieldState,
 *   'Fund Name',
 *   true,
 *   'Enter a unique name'
 * );
 * 
 * <TextField
 *   label={displayLabel}
 *   color={fieldColor}
 *   error={showError}
 *   helperText={displayHelperText}
 * />
 * ```
 */
export function useFieldState(
  fieldState: ControllerFieldState,
  label: string,
  required: boolean = false,
  helperText?: string
) {
  return {
    showError: shouldShowError(fieldState),
    fieldColor: getFieldColor(fieldState, required),
    displayLabel: getFieldLabel(label, required),
    displayHelperText: getHelperText(fieldState, helperText)
  };
}

