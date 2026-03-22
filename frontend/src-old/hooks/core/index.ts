/**
 * Core Hooks - Main Barrel Export
 * 
 * Exports all core infrastructure hooks that form the foundation of the hooks system.
 * These hooks should be used by all domain-specific and UI hooks.
 * 
 * Core hooks are:
 * - Generic and reusable across domains
 * - Domain-agnostic (no business logic)
 * - Well-tested and stable
 * - Rarely change once established
 * 
 * @module hooks/core
 */

// Re-export all API hooks
export * from './api';

// Re-export all error hooks
export * from './error';

