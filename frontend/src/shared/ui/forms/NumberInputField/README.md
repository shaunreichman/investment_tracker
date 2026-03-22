# NumberInputField Component

## Status

✅ **Migrated**: Component has been migrated from `src-old/components/shared/forms/primitives/NumberInputField.tsx` to `shared/ui/forms/NumberInputField.tsx`.

⚠️ **Note**: This component is currently in "legacy" mode and is preserved for existing fund/event workflows. Before general reuse across the application, the following hardening tasks should be completed.

## Follow-Up Hardening Tasks

Before using this component in new contexts or making it a general-purpose shared component, address the following areas:

### 1. Controlled Value Sync

**Current State**: The component uses a hybrid approach with internal state management via `useNumberInput` hook while maintaining external control via `value` prop.

**Issues**:
- Potential race conditions between internal state (`useNumberInput.value`) and external `value` prop
- Value sync logic in `handleValueChange` may not handle all edge cases
- The component compares `rawValue !== value` to decide when to call `onInputChange`, which could miss some update scenarios

**Tasks**:
- [ ] Review and improve synchronization between internal formatted state and external raw value
- [ ] Add proper `useEffect` to sync external `value` prop changes to internal state
- [ ] Consider making the component fully controlled (no internal state) or fully uncontrolled with proper initialization
- [ ] Add tests for value sync edge cases (rapid typing, programmatic value changes, etc.)

### 2. Precision Handling

**Current State**: Component uses `parseFloat` and `toString()` which may lose precision for very large numbers or specific decimal places.

**Issues**:
- No explicit precision/decimal place handling
- `toString()` may not preserve intended decimal places
- No configuration for minimum/maximum decimal places

**Tasks**:
- [ ] Add `minDecimals` and `maxDecimals` options to control precision
- [ ] Consider using `Number.toFixed()` or custom formatting for precision control
- [ ] Document precision behavior for different number ranges
- [ ] Add tests for precision edge cases (very large numbers, many decimal places, scientific notation)

### 3. Accessibility

**Current State**: Component uses MUI `TextField` which provides basic accessibility, but lacks specific enhancements.

**Issues**:
- No explicit ARIA labels or descriptions for number formatting behavior
- Screen readers may not announce formatting changes (thousand separators)
- No keyboard navigation enhancements for numeric input

**Tasks**:
- [ ] Add `aria-label` or `aria-describedby` to explain formatting behavior
- [ ] Ensure screen readers announce when formatting is applied/removed
- [ ] Add keyboard shortcuts documentation (if any)
- [ ] Test with screen readers (NVDA, JAWS, VoiceOver)
- [ ] Add proper `role` attributes if needed
- [ ] Ensure error states are properly announced

### 4. Automated Coverage

**Current State**: Component has no automated tests.

**Tasks**:
- [ ] Create unit tests for `NumberInputField` component
- [ ] Test `useNumberInput` hook in isolation
- [ ] Test integration between hook and component
- [ ] Add tests for:
  - Value formatting (thousand separators)
  - Decimal input handling
  - Negative number handling
  - Locale formatting
  - Edge cases (empty values, invalid input, very large numbers)
  - Value sync between internal and external state
- [ ] Achieve minimum 80% code coverage
- [ ] Add visual regression tests if applicable

### 5. Locale Strategy

**Current State**: Component accepts a `locale` prop (default: 'en-AU') but uses basic `Intl.NumberFormat`.

**Issues**:
- No validation of locale string
- No handling of locale-specific number formats (decimal separators, thousand separators)
- Hard-coded comma separator removal (`replace(/,/g, '')`) may not work for all locales
- No alignment with application-wide locale strategy

**Tasks**:
- [ ] Define application-wide locale strategy (context provider, config, etc.)
- [ ] Align component with application locale configuration
- [ ] Add locale validation
- [ ] Handle locale-specific separators (e.g., period vs comma for decimals)
- [ ] Update separator removal logic to be locale-aware
- [ ] Add tests for different locales
- [ ] Document locale behavior and limitations

## Integration with New Form System

**Note**: This component uses the legacy form pattern (`onInputChange` callback). Consider:

- [ ] Evaluate integration with React Hook Form (via `Controller` or custom wrapper)
- [ ] Consider creating a `FormNumberField` wrapper for React Hook Form integration
- [ ] Document migration path from legacy usage to new form system
- [ ] Provide examples for both legacy and new form patterns

## Usage

### Legacy Pattern (Current)

```typescript
<NumberInputField
  label="Amount"
  value={formData.amount}
  onInputChange={onInputChange}
  fieldName="amount"
  allowDecimals={true}
  allowNegative={false}
  required
  fullWidth
/>
```

### Future React Hook Form Integration

```typescript
// Example (to be implemented)
<Controller
  name="amount"
  control={control}
  render={({ field }) => (
    <NumberInputField
      {...field}
      label="Amount"
      allowDecimals={true}
      allowNegative={false}
      required
      fullWidth
    />
  )}
/>
```

