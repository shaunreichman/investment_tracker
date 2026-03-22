/**
 * Core API Hooks - Barrel Export
 * 
 * Exports all core API hooks for data fetching and mutations.
 * These hooks provide the foundation for all data operations in the application.
 * 
 * Design Philosophy:
 * - Simple, focused hooks that do one thing well
 * - Composable through standard React patterns (useCallback, useMemo)
 * - No "convenience" wrappers - let consumers create their own patterns
 * 
 * @module hooks/core/api
 */

// Query hooks
export {
  useQuery,
  type UseQueryOptions,
  type UseQueryResult,
} from './useQuery';

// Mutation hooks
export {
  useMutation,
  type UseMutationOptions,
  type UseMutationResult,
} from './useMutation';

