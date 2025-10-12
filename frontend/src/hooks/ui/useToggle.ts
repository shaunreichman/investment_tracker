/**
 * Toggle Hook - Boolean state management with helper methods
 * 
 * Provides a cleaner API for managing boolean state (modals, dropdowns, etc.)
 * with explicit methods that improve code readability and reduce boilerplate.
 * 
 * @module hooks/ui/useToggle
 * 
 * @example
 * ```typescript
 * // Basic modal usage
 * const modal = useToggle();
 * <Button onClick={modal.setTrue}>Open Modal</Button>
 * <Modal isOpen={modal.value} onClose={modal.setFalse} />
 * 
 * // Dropdown with initial state
 * const dropdown = useToggle(false);
 * <Button onClick={dropdown.toggle}>Toggle Menu</Button>
 * 
 * // Accordion section
 * const section = useToggle(true); // Start expanded
 * <AccordionHeader onClick={section.toggle} expanded={section.value} />
 * ```
 */

import { useState, useCallback } from 'react';

// ============================================================================
// TYPES
// ============================================================================

/**
 * Return value from useToggle hook
 */
export interface UseToggleReturn {
  /** Current boolean value */
  value: boolean;
  /** Toggle between true and false */
  toggle: () => void;
  /** Set value to true */
  setTrue: () => void;
  /** Set value to false */
  setFalse: () => void;
  /** Set value to a specific boolean */
  setValue: (value: boolean) => void;
}

// ============================================================================
// HOOK IMPLEMENTATION
// ============================================================================

/**
 * Hook for managing boolean state with convenient helper methods
 * 
 * Useful for any on/off UI state: modals, dropdowns, accordions, filters,
 * expanded states, visibility toggles, etc.
 * 
 * @param initialValue - Initial boolean value (default: false)
 * @returns Object with value and methods to control it
 * 
 * @example
 * ```typescript
 * // Modal dialog
 * const modal = useToggle();
 * const handleSubmit = () => {
 *   // ... save data
 *   modal.setFalse(); // Close modal after save
 * };
 * 
 * // Filter panel
 * const filters = useToggle(false);
 * <Button onClick={filters.toggle}>
 *   {filters.value ? 'Hide' : 'Show'} Filters
 * </Button>
 * 
 * // Expandable section
 * const details = useToggle(true); // Start expanded
 * <Collapsible 
 *   expanded={details.value} 
 *   onToggle={details.toggle}
 * />
 * ```
 */
export function useToggle(initialValue: boolean = false): UseToggleReturn {
  const [value, setValue] = useState<boolean>(initialValue);

  // Toggle between true and false
  const toggle = useCallback(() => {
    setValue(prev => !prev);
  }, []);

  // Explicitly set to true
  const setTrue = useCallback(() => {
    setValue(true);
  }, []);

  // Explicitly set to false
  const setFalse = useCallback(() => {
    setValue(false);
  }, []);

  return {
    value,
    toggle,
    setTrue,
    setFalse,
    setValue,
  };
}

