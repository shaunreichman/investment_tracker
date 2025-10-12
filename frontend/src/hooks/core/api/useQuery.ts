/**
 * Core Query Hook - Base hook for GET operations
 * 
 * This hook provides a standardized way to fetch data from APIs with:
 * - Automatic loading and error state management
 * - Refetch on window focus support
 * - Polling/refetch interval support
 * - Manual refetch capability
 * - Conditional execution (enabled flag)
 * 
 * @module hooks/core/api/useQuery
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { useErrorHandler } from '@/hooks/core/error';
import type { ErrorInfo } from '@/types/errors';

// ============================================================================
// TYPES
// ============================================================================

/**
 * Options for configuring query behavior
 */
export interface UseQueryOptions {
  /** Whether the query should execute automatically (default: true) */
  enabled?: boolean;
  /** Whether to refetch when window regains focus (default: false) */
  refetchOnWindowFocus?: boolean | undefined;
  /** Interval in milliseconds to automatically refetch (default: undefined) */
  refetchInterval?: number | undefined;
  /** Callback executed when query succeeds */
  onSuccess?: (data: any) => void;
  /** Callback executed when query fails */
  onError?: (error: ErrorInfo) => void;
}

/**
 * Return value from useQuery hook
 */
export interface UseQueryResult<T> {
  /** The fetched data, null if not yet loaded or on error */
  data: T | null;
  /** Whether the query is currently loading */
  loading: boolean;
  /** Error information if the query failed */
  error: ErrorInfo | null;
  /** Function to manually refetch the data */
  refetch: () => Promise<void>;
  /** Whether the query has been fetched at least once */
  isFetched: boolean;
}

// ============================================================================
// HOOK IMPLEMENTATION
// ============================================================================

/**
 * Base hook for fetching data (GET operations)
 * 
 * @template T - The type of data being fetched
 * @param queryFn - Async function that fetches the data
 * @param options - Configuration options for the query
 * @returns Query state and refetch function
 * 
 * @example
 * ```typescript
 * // Basic usage
 * const { data, loading, error, refetch } = useQuery<User[]>(
 *   () => api.users.getAll(),
 *   { refetchOnWindowFocus: true }
 * );
 * 
 * // With dependencies (use useCallback)
 * const queryFn = useCallback(
 *   () => api.users.get(userId),
 *   [userId]
 * );
 * const { data, loading } = useQuery(queryFn, { enabled: !!userId });
 * ```
 */
export function useQuery<T>(
  queryFn: () => Promise<T>,
  options: UseQueryOptions = {}
): UseQueryResult<T> {
  // Destructure options with defaults
  const {
    enabled = true,
    refetchOnWindowFocus = false,
    refetchInterval,
    onSuccess,
    onError
  } = options;

  // State management
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [isFetched, setIsFetched] = useState(false);
  
  // Use centralized error handler
  const { error, withErrorHandling } = useErrorHandler();

  // Refs for managing intervals and tracking mount status
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const mountedRef = useRef(true);
  const queryFnRef = useRef(queryFn);

  // Update queryFn ref when it changes
  useEffect(() => {
    queryFnRef.current = queryFn;
  }, [queryFn]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      mountedRef.current = false;
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, []);

  // Main query execution function
  const executeQuery = useCallback(async () => {
    if (!enabled) {
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      
      const result = await withErrorHandling(async () => {
        return await queryFnRef.current();
      }, true, 'query');
      
      if (result !== null && mountedRef.current) {
        setData(result);
        setIsFetched(true);
        if (onSuccess) {
          onSuccess(result);
        }
      }
    } catch (err) {
      // Error already handled by withErrorHandling
      if (onError && error) {
        onError(error);
      }
    } finally {
      if (mountedRef.current) {
        setLoading(false);
      }
    }
  }, [enabled, withErrorHandling, onSuccess, onError, error]);

  // Initial query execution
  useEffect(() => {
    if (enabled) {
      executeQuery();
    }
  }, [executeQuery, enabled]);

  // Refetch on window focus
  useEffect(() => {
    if (!refetchOnWindowFocus || !enabled) return;

    const handleFocus = () => {
      executeQuery();
    };

    window.addEventListener('focus', handleFocus);
    return () => window.removeEventListener('focus', handleFocus);
  }, [refetchOnWindowFocus, enabled, executeQuery]);

  // Refetch interval (polling)
  useEffect(() => {
    if (!refetchInterval || !enabled) return;

    intervalRef.current = setInterval(() => {
      executeQuery();
    }, refetchInterval);

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };
  }, [refetchInterval, enabled, executeQuery]);

  // Manual refetch function
  const refetch = useCallback(async () => {
    await executeQuery();
  }, [executeQuery]);

  return {
    data,
    loading,
    error,
    refetch,
    isFetched,
  };
}

