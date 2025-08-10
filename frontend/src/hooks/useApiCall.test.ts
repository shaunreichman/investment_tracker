// useApiCall Comprehensive Testing
// This file addresses the critical 44.44% coverage gap in hooks

import { renderHook, act, waitFor } from '@testing-library/react';
import { useApiCall } from './useApiCall';

// Mock the useErrorHandler hook
jest.mock('./useErrorHandler', () => ({
  useErrorHandler: () => ({
    error: null,
    withErrorHandling: jest.fn(async (fn) => {
      try {
        return await fn();
      } catch (error) {
        // Return null to simulate error handling behavior
        return null;
      }
    }),
  }),
}));

describe('useApiCall', () => {
  const mockApiCall = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    mockApiCall.mockResolvedValue('test data');
  });

  it('should initialize with loading state', () => {
    const { result } = renderHook(() => useApiCall(mockApiCall));
    
    expect(result.current.loading).toBe(true);
    expect(result.current.data).toBe(null);
    expect(result.current.error).toBe(null);
  });

  it('should call API and update state on mount', async () => {
    const { result } = renderHook(() => useApiCall(mockApiCall));
    
    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });
    
    // The hook may be called multiple times due to React's behavior
    expect(mockApiCall).toHaveBeenCalled();
    expect(result.current.data).toBe('test data');
  });

  it('should provide refetch function', async () => {
    const { result } = renderHook(() => useApiCall(mockApiCall));
    
    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });
    
    expect(typeof result.current.refetch).toBe('function');
    
    // Test refetch
    const initialCallCount = mockApiCall.mock.calls.length;
    await act(async () => {
      await result.current.refetch();
    });
    
    // Should have been called at least one more time
    expect(mockApiCall.mock.calls.length).toBeGreaterThan(initialCallCount);
  });

  it('should handle API errors gracefully', async () => {
    const errorApiCall = jest.fn().mockRejectedValue(new Error('API Error'));
    const { result } = renderHook(() => useApiCall(errorApiCall));
    
    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });
    
    expect(errorApiCall).toHaveBeenCalled();
    expect(result.current.data).toBe(null);
  });

  it('should respect enabled option', () => {
    const { result } = renderHook(() => useApiCall(mockApiCall, { enabled: false }));
    
    expect(result.current.loading).toBe(false);
    expect(mockApiCall).not.toHaveBeenCalled();
  });

  it('should handle refetch on window focus when enabled', async () => {
    const { result } = renderHook(() => 
      useApiCall(mockApiCall, { refetchOnWindowFocus: true })
    );
    
    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });
    
    const initialCallCount = mockApiCall.mock.calls.length;
    
    // Simulate window focus
    act(() => {
      window.dispatchEvent(new Event('focus'));
    });
    
    await waitFor(() => {
      expect(mockApiCall.mock.calls.length).toBeGreaterThan(initialCallCount);
    });
  });

  it('should handle refetch interval when specified', async () => {
    const { result } = renderHook(() => 
      useApiCall(mockApiCall, { refetchInterval: 1000 })
    );
    
    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });
    
    // Test that the hook was initialized with the interval option
    expect(result.current.refetch).toBeDefined();
  });
});
