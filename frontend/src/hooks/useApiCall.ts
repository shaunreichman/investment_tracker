// Base Custom Hook for API Calls
// This file provides a generic hook for API calls with loading, error, and data state management

import { useState, useEffect, useCallback, useRef } from 'react';
import { useErrorHandler } from './useErrorHandler';
import { ErrorInfo } from '../types/errors';

// ============================================================================
// TYPES
// ============================================================================

export interface ApiCallState<T> {
  data: T | null;
  loading: boolean;
  error: ErrorInfo | null;
}

export interface ApiCallOptions {
  enabled?: boolean;
  refetchOnWindowFocus?: boolean | undefined;
  refetchInterval?: number;
}

// ============================================================================
// BASE API CALL HOOK
// ============================================================================

export function useApiCall<T>(
  apiCall: () => Promise<T>,
  options: ApiCallOptions = {}
): ApiCallState<T> & { refetch: () => Promise<void> } {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  
  // Use centralized error handler
  const { error, withErrorHandling } = useErrorHandler();

  const { enabled = true, refetchOnWindowFocus = false, refetchInterval } = options;
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const mountedRef = useRef(true);
  const apiCallRef = useRef(apiCall);

  // Update the ref when apiCall changes
  useEffect(() => {
    apiCallRef.current = apiCall;
  }, [apiCall]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      mountedRef.current = false;
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, []);

  // Main API call function
  const executeApiCall = useCallback(async () => {
    if (!enabled) {
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      const data = await withErrorHandling(async () => {
        const result = await apiCallRef.current();
        return result;
      }, true, 'api_call');
      
      if (data !== null) {
        setData(data);
      }
    } finally {
      setLoading(false);
    }
  }, [enabled, withErrorHandling]);

  // Initial API call
  useEffect(() => {
    executeApiCall();
  }, [executeApiCall]);

  // Refetch on window focus
  useEffect(() => {
    if (!refetchOnWindowFocus) return;

    const handleFocus = () => {
      executeApiCall();
    };

    window.addEventListener('focus', handleFocus);
    return () => window.removeEventListener('focus', handleFocus);
  }, [refetchOnWindowFocus, executeApiCall]);

  // Refetch interval
  useEffect(() => {
    if (!refetchInterval) return;

    intervalRef.current = setInterval(() => {
      executeApiCall();
    }, refetchInterval);

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [refetchInterval, executeApiCall]);

  // Manual refetch function
  const refetch = useCallback(async () => {
    await executeApiCall();
  }, [executeApiCall]);

  return {
    data,
    loading,
    error,
    refetch,
  };
}

// ============================================================================
// MUTATION HOOK
// ============================================================================

export interface MutationState<T> {
  data: T | null;
  loading: boolean;
  error: ErrorInfo | null;
}

export function useMutation<T, R>(
  mutationFn: (data: T) => Promise<R>,
  options: {
    onSuccess?: (data: R) => void;
  } = {}
): MutationState<R> & { mutate: (data: T) => Promise<R | undefined> } {
  // Use centralized error handler
  const { error, withErrorHandling } = useErrorHandler();

  const { onSuccess } = options;
  const [data, setData] = useState<R | null>(null);
  const [loading, setLoading] = useState(false);

  const mutate = useCallback(async (data: T): Promise<R | undefined> => {
    try {
      setLoading(true);
      setData(null);
      
      const result = await withErrorHandling(async () => {
        return await mutationFn(data);
      }, true, 'api_mutation');
      
      // Check if the result is valid (not null/undefined)
      if (result !== null && result !== undefined) {
        setData(result);
        if (onSuccess) {
          onSuccess(result);
        }
        return result;
      } else {
        // If result is null/undefined, it might be an error
        // The error should be handled by withErrorHandling
        return undefined;
      }
    } catch (error) {
      return undefined;
    } finally {
      setLoading(false);
    }
  }, [mutationFn, onSuccess, withErrorHandling]);

  return {
    data,
    loading,
    error,
    mutate,
  };
}

// ============================================================================
// UTILITY HOOKS
// ============================================================================

// Hook for conditional API calls
export function useConditionalApiCall<T>(
  apiCall: () => Promise<T>,
  condition: boolean,
  options: ApiCallOptions = {}
): ApiCallState<T> & { refetch: () => Promise<void> } {
  return useApiCall(apiCall, { ...options, enabled: condition });
}

// Hook for API calls with dependencies
export function useApiCallWithDeps<T, D extends readonly unknown[]>(
  apiCall: (...deps: D) => Promise<T>,
  deps: D,
  options: ApiCallOptions = {}
): ApiCallState<T> & { refetch: () => Promise<void> } {
  // Use a ref to store the latest deps and apiCall
  const depsRef = useRef(deps);
  const apiCallRef = useRef(apiCall);
  
  // Update refs when deps or apiCall change
  useEffect(() => {
    depsRef.current = deps;
    apiCallRef.current = apiCall;
  }, [deps, apiCall]);
  
  // Create a stable callback that uses the refs
  const memoizedApiCall = useCallback(async () => {
    // eslint-disable-next-line @typescript-eslint/no-unsafe-return
    return await apiCallRef.current(...depsRef.current);
  }, []); // No dependencies needed since we use refs for latest values
  
  return useApiCall(memoizedApiCall, options);
}

// All types are already exported above 
// All types are already exported above 