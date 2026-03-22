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
import { useErrorHandler } from '@/shared/hooks/core/error';
import type { ErrorInfo } from '@/shared/types/errors';

// ============================================================================
// REQUEST DEDUPLICATION
// ============================================================================

/**
 * Global cache for in-flight requests to prevent duplicate API calls
 * Key: serialized query function (or query key if provided)
 * Value: Promise that resolves with the result
 */
const requestCache = new Map<string, Promise<any>>();

/**
 * Generate a stable key for a query function
 * Uses function stringification as a fallback, but ideally should use query keys
 */
function getQueryKey(queryFn: () => Promise<any>): string {
  // Try to extract a stable identifier from the function
  // This is a simple approach - in production, consider using explicit query keys
  return queryFn.toString();
}

/**
 * Clear a request from the cache after it completes
 */
function clearRequestCache(key: string) {
  // Use setTimeout to allow other concurrent requests to use the same promise
  setTimeout(() => {
    requestCache.delete(key);
  }, 100);
}

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
  const hasExecutedRef = useRef(false);
  const queryKeyRef = useRef<string>(getQueryKey(queryFn));

  // Update queryFn ref when it changes and reset execution flag
  useEffect(() => {
    const newKey = getQueryKey(queryFn);
    const keyChanged = queryKeyRef.current !== newKey;
    
    queryFnRef.current = queryFn;
    queryKeyRef.current = newKey;
    
    // Only reset execution flag if the query key actually changed
    // This prevents unnecessary refetches when function reference changes but logic is the same
    if (keyChanged) {
      hasExecutedRef.current = false;
    }
  }, [queryFn]);

  // Set mounted ref to true on mount (important for React Strict Mode)
  useEffect(() => {
    mountedRef.current = true;
    
    return () => {
      mountedRef.current = false;
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, []);

  // Main query execution function with request deduplication
  // Note: error is NOT in dependencies - we use withErrorHandling which manages errors internally
  // Adding error would cause infinite loops when error state changes
  const executeQuery = useCallback(async () => {
    if (!enabled) {
      setLoading(false);
      return;
    }

    const queryKey = queryKeyRef.current;
    
    // Check if there's already an in-flight request for this query
    const cachedRequest = requestCache.get(queryKey);
    if (cachedRequest) {
      try {
        setLoading(true);
        const result = await cachedRequest;
        if (result !== null && mountedRef.current) {
          setData(result);
          setIsFetched(true);
          if (onSuccess) {
            onSuccess(result);
          }
        }
      } catch (err) {
        // Error already handled by the original request
        if (onError) {
          // Error will be available from the hook's error state
        }
      } finally {
        if (mountedRef.current) {
          setLoading(false);
        }
      }
      return;
    }

    // Create new request and cache it
    try {
      setLoading(true);
      
      const requestPromise = withErrorHandling(async () => {
        return await queryFnRef.current();
      }, true, 'query');
      
      // Cache the promise so concurrent requests can share it
      requestCache.set(queryKey, requestPromise);
      
      const result = await requestPromise;
      
      // Clear from cache after completion
      clearRequestCache(queryKey);
      
      if (result !== null && mountedRef.current) {
        setData(result);
        setIsFetched(true);
        if (onSuccess) {
          onSuccess(result);
        }
      }
    } catch (err) {
      // Clear from cache on error too
      clearRequestCache(queryKey);
      
      // Error already handled by withErrorHandling
      if (onError) {
        // Access error from the hook's return value, not closure
        // This will be handled by the error handler's state
      }
    } finally {
      if (mountedRef.current) {
        setLoading(false);
      }
    }
  }, [enabled, withErrorHandling, onSuccess, onError]);

  // Initial query execution
  // Only execute once when enabled becomes true, or when queryFn changes
  useEffect(() => {
    if (enabled && !hasExecutedRef.current) {
      hasExecutedRef.current = true;
      executeQuery();
    } else if (!enabled) {
      hasExecutedRef.current = false;
    }
  }, [enabled, queryFn, executeQuery]);

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

