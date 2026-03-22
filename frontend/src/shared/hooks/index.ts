/**
 * Shared Hooks - Main Barrel Export
 * 
 * Exports all shared hooks that form the foundation of the hooks system.
 * These hooks are cross-cutting concerns used by all domain-specific hooks.
 * 
 * Shared hooks are:
 * - Generic and reusable across domains
 * - Domain-agnostic (no business logic)
 * - Well-tested and stable
 * - Central to the application's hook architecture
 * 
 * @module shared/hooks
 */

// Re-export all core hooks (API, error handling)
export * from './core';

// Re-export error UI hooks
export * from './errors';

// Re-export form management hooks
export * from './forms';

// Re-export shared form validation schemas
export * from './schemas';

// Re-export UI hooks (debounced search, responsive view, table sorting)
export * from './ui';

