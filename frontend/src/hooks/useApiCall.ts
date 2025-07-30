// Base Custom Hook for API Calls
// This file provides a generic hook for API calls with loading, error, and data state management

import { useState, useEffect, useCallback, useRef } from 'react';
import { apiClient } from '../services/api';

// ============================================================================
// TYPES
// ============================================================================

export interface ApiCallState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
}

export interface ApiCallOptions {
  enabled?: boolean;
  refetchOnWindowFocus?: boolean;
  refetchInterval?: number;
}

// ============================================================================
// BASE API CALL HOOK
// ============================================================================

export function useApiCall<T>(
  apiCall: () => Promise<T>,
  options: ApiCallOptions = {}
): ApiCallState<T> & { refetch: () => Promise<void> } {
  const [state, setState] = useState<ApiCallState<T>>({
    data: null,
    loading: true,
    error: null,
  });

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
      setState(prev => ({ ...prev, loading: false }));
      return;
    }

    try {
      setState(prev => ({ ...prev, loading: true, error: null }));
      const data = await apiCallRef.current();
      
      setState({ data, loading: false, error: null });
    } catch (error) {
      setState({
        data: null,
        loading: false,
        error: error instanceof Error ? error.message : 'An error occurred',
      });
    }
  }, [enabled]);

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
    ...state,
    refetch,
  };
}

// ============================================================================
// MUTATION HOOK
// ============================================================================

export interface MutationState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
}

export function useMutation<T, R>(
  mutationFn: (data: T) => Promise<R>,
  options: {
    onSuccess?: (data: R) => void;
    onError?: (error: string) => void;
  } = {}
): MutationState<R> & { mutate: (data: T) => Promise<R | undefined> } {
  const [state, setState] = useState<MutationState<R>>({
    data: null,
    loading: false,
    error: null,
  });

  const { onSuccess, onError } = options;

  const mutate = useCallback(async (data: T): Promise<R | undefined> => {
    try {
      setState(prev => ({ ...prev, loading: true, error: null }));
      const result = await mutationFn(data);
      
      setState({ data: result, loading: false, error: null });
      onSuccess?.(result);
      return result;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'An error occurred';
      setState({ data: null, loading: false, error: errorMessage });
      onError?.(errorMessage);
      throw error;
    }
  }, [mutationFn, onSuccess, onError]);

  return {
    ...state,
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
export function useApiCallWithDeps<T, D extends readonly any[]>(
  apiCall: (...deps: D) => Promise<T>,
  deps: D,
  options: ApiCallOptions = {}
): ApiCallState<T> & { refetch: () => Promise<void> } {
  const memoizedApiCall = useCallback(() => apiCall(...deps), deps);
  return useApiCall(memoizedApiCall, options);
}

// All types are already exported above 