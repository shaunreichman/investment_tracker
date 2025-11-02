/**
 * Core Mutation Hook - Base hook for write operations (POST, PUT, DELETE)
 * 
 * This hook provides a standardized way to perform data mutations with:
 * - Automatic loading and error state management
 * - Success and error callbacks
 * - Optimistic updates support
 * - Last successful mutation data tracking
 * 
 * @module hooks/core/api/useMutation
 */

import { useState, useCallback } from 'react';
import { useErrorHandler } from '@/hooks/core/error';
import type { ErrorInfo } from '@/types/errors';

// ============================================================================
// TYPES
// ============================================================================

/**
 * Options for configuring mutation behavior
 */
export interface UseMutationOptions<TData, TVariables> {
  /** Callback executed when mutation succeeds */
  onSuccess?: (data: TData, variables: TVariables) => void;
  /** Callback executed when mutation fails */
  onError?: (error: ErrorInfo, variables: TVariables) => void;
  /** Callback executed when mutation starts */
  onMutate?: (variables: TVariables) => void | Promise<void>;
  /** Callback executed when mutation completes (success or failure) */
  onSettled?: (data: TData | null, error: ErrorInfo | null, variables: TVariables) => void;
}

/**
 * Return value from useMutation hook
 */
export interface UseMutationResult<TData, TVariables> {
  /** The data from the last successful mutation */
  data: TData | null;
  /** Whether a mutation is currently in progress */
  loading: boolean;
  /** Error information if the mutation failed */
  error: ErrorInfo | null;
  /** Function to trigger the mutation */
  mutate: (variables: TVariables) => Promise<TData | undefined>;
  /** Function to trigger the mutation (async version that throws on error) */
  mutateAsync: (variables: TVariables) => Promise<TData>;
  /** Function to reset mutation state */
  reset: () => void;
  /** Whether a mutation has been executed at least once */
  isExecuted: boolean;
  /** Whether the last mutation was successful */
  isSuccess: boolean;
  /** Whether the last mutation failed */
  isError: boolean;
}

// ============================================================================
// HOOK IMPLEMENTATION
// ============================================================================

/**
 * Base hook for data mutations (POST, PUT, DELETE operations)
 * 
 * @template TData - The type of data returned by the mutation
 * @template TVariables - The type of variables passed to the mutation
 * @param mutationFn - Async function that performs the mutation
 * @param options - Configuration options for the mutation
 * @returns Mutation state and trigger functions
 * 
 * @example
 * ```typescript
 * // Mutation with variables
 * const { mutate, loading, error } = useMutation<User, CreateUserData>(
 *   (data) => api.users.create(data),
 *   {
 *     onSuccess: (user) => console.log('User created:', user),
 *     onError: (error) => console.error('Failed to create user:', error)
 *   }
 * );
 * mutate({ name: 'John', email: 'john@example.com' });
 * 
 * // Mutation without variables (use void type)
 * const { mutate: logout } = useMutation<void, void>(
 *   () => api.auth.logout()
 * );
 * logout(undefined);
 * ```
 */
export function useMutation<TData, TVariables = void>(
  mutationFn: (variables: TVariables) => Promise<TData>,
  options: UseMutationOptions<TData, TVariables> = {}
): UseMutationResult<TData, TVariables> {
  // Destructure options
  const { onSuccess, onError, onMutate, onSettled } = options;

  // State management
  const [data, setData] = useState<TData | null>(null);
  const [loading, setLoading] = useState(false);
  const [isExecuted, setIsExecuted] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);
  const [isError, setIsError] = useState(false);
  
  // Use centralized error handler
  const { error, withErrorHandling, clearError } = useErrorHandler();

  /**
   * Trigger the mutation (returns undefined on error)
   */
  const mutate = useCallback(async (variables: TVariables): Promise<TData | undefined> => {
    try {
      // Clear previous error
      clearError();
      setIsError(false);
      setIsSuccess(false);
      setLoading(true);
      setIsExecuted(true);
      
      // Execute onMutate callback
      if (onMutate) {
        await onMutate(variables);
      }

      // Execute mutation with error handling
      const result = await withErrorHandling(async () => {
        return await mutationFn(variables);
      }, false, 'mutation');

      // Check if result is valid (not null/undefined from error)
      if (result !== null && result !== undefined) {
        setData(result);
        setIsSuccess(true);
        
        // Execute onSuccess callback
        if (onSuccess) {
          onSuccess(result, variables);
        }

        // Execute onSettled callback
        if (onSettled) {
          onSettled(result, null, variables);
        }

        return result;
      } else {
        // Mutation failed (error handled by withErrorHandling)
        setIsError(true);
        
        // Execute onError callback
        if (onError && error) {
          onError(error, variables);
        }

        // Execute onSettled callback
        if (onSettled) {
          onSettled(null, error, variables);
        }

        return undefined;
      }
    } catch (err) {
      // Catch any synchronous errors
      setIsError(true);
      
      if (onError && error) {
        onError(error, variables);
      }

      if (onSettled) {
        onSettled(null, error, variables);
      }

      return undefined;
    } finally {
      setLoading(false);
    }
  }, [mutationFn, onSuccess, onError, onMutate, onSettled, withErrorHandling, clearError, error]);

  /**
   * Trigger the mutation (async version that throws on error)
   * Use this when you need to handle errors in a try-catch block
   */
  const mutateAsync = useCallback(async (variables: TVariables): Promise<TData> => {
    const result = await mutate(variables);
    
    if (result === undefined) {
      // Mutation failed, throw error
      throw error || new Error('Mutation failed');
    }
    
    return result;
  }, [mutate, error]);

  /**
   * Reset mutation state
   */
  const reset = useCallback(() => {
    setData(null);
    setLoading(false);
    setIsExecuted(false);
    setIsSuccess(false);
    setIsError(false);
    clearError();
  }, [clearError]);

  return {
    data,
    loading,
    error,
    mutate,
    mutateAsync,
    reset,
    isExecuted,
    isSuccess,
    isError,
  };
}

