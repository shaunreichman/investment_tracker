# Primitive Utilities

This directory contains generic utility functions that are cross-cutting concerns.

## Deprecation Notice

The following primitive utilities (`debounce`, `throttle`, `deepClone`, `deepEqual`) are **deprecated** and should be replaced with well-tested library alternatives:

### Recommended Replacements

- **debounce/throttle**: Use `lodash.debounce` and `lodash.throttle` from lodash, or consider React-specific hooks like `useDebounce`/`useThrottle` from `react-use` or similar libraries.

- **deepClone**: Use `structuredClone()` (native browser API, available in modern environments) or `lodash.clonedeep` for complex cases.

- **deepEqual**: Use `lodash.isequal` or consider using immutable data structures that make equality checks trivial.

## Migration Strategy

1. **For new code**: Use the recommended library alternatives directly.
2. **For existing code**: These functions remain available in `src-old/utils/helpers.ts` during the migration period. Update imports to use library alternatives as components are migrated.
3. **No shared primitives**: We are not creating shared versions of these primitives to avoid reinventing the wheel. Use established libraries instead.

## Rationale

- **Maintenance burden**: Custom implementations require ongoing maintenance and testing.
- **Edge cases**: Well-established libraries handle edge cases we may not consider.
- **Performance**: Optimized library implementations are typically more performant.
- **Standards**: Using common libraries improves code familiarity for new developers.

