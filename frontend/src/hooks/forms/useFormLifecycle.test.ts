import { renderHook, act } from '@testing-library/react';
import { useFormLifecycle } from './useFormLifecycle';

describe('useFormLifecycle', () => {
  it('should initialize with idle state', () => {
    const { result } = renderHook(() => useFormLifecycle());
    
    expect(result.current.currentState).toBe('idle');
    expect(result.current.progress).toBe(0);
    expect(result.current.canSubmit).toBe(false);
    expect(result.current.canCancel).toBe(false);
    expect(result.current.isInProgress).toBe(false);
  });

  it('should transition to editing state when startEditing is called', () => {
    const { result } = renderHook(() => useFormLifecycle());
    
    act(() => {
      result.current.startEditing();
    });
    
    expect(result.current.currentState).toBe('editing');
    expect(result.current.canSubmit).toBe(true);
    expect(result.current.canCancel).toBe(true);
  });

  it('should transition to validating state when startValidation is called', () => {
    const { result } = renderHook(() => useFormLifecycle());
    
    act(() => {
      result.current.startValidation();
    });
    
    expect(result.current.currentState).toBe('validating');
    expect(result.current.progress).toBe(25);
    expect(result.current.isInProgress).toBe(true);
  });

  it('should transition to editing state when validation completes successfully', () => {
    const { result } = renderHook(() => useFormLifecycle());
    
    act(() => {
      result.current.startValidation();
      result.current.completeValidation(true);
    });
    
    expect(result.current.currentState).toBe('editing');
    expect(result.current.progress).toBe(50);
  });

  it('should transition to submitting state when startSubmission is called', () => {
    const { result } = renderHook(() => useFormLifecycle());
    
    act(() => {
      result.current.startSubmission();
    });
    
    expect(result.current.currentState).toBe('submitting');
    expect(result.current.progress).toBe(75);
    expect(result.current.isInProgress).toBe(true);
  });

  it('should transition to success state when submission completes successfully', () => {
    const { result } = renderHook(() => useFormLifecycle());
    
    act(() => {
      result.current.startSubmission();
      result.current.completeSubmission(true);
    });
    
    expect(result.current.currentState).toBe('success');
    expect(result.current.progress).toBe(100);
    expect(result.current.isInProgress).toBe(false);
  });

  it('should transition to error state when submission fails', () => {
    const { result } = renderHook(() => useFormLifecycle());
    
    act(() => {
      result.current.startSubmission();
      result.current.completeSubmission(false, 'Network error');
    });
    
    expect(result.current.currentState).toBe('error');
    expect(result.current.progress).toBe(75);
    expect(result.current.isInProgress).toBe(false);
  });

  it('should transition to cancelled state when cancelForm is called', () => {
    const { result } = renderHook(() => useFormLifecycle());
    
    act(() => {
      result.current.startEditing();
      result.current.cancelForm();
    });
    
    expect(result.current.currentState).toBe('cancelled');
    expect(result.current.progress).toBe(0);
  });

  it('should reset to idle state when resetForm is called', () => {
    const { result } = renderHook(() => useFormLifecycle());
    
    act(() => {
      result.current.startEditing();
    });
    
    expect(result.current.currentState).toBe('editing');
    
    act(() => {
      result.current.resetForm();
    });
    
    expect(result.current.currentState).toBe('idle');
    expect(result.current.progress).toBe(0);
    expect(result.current.canSubmit).toBe(false);
    expect(result.current.canCancel).toBe(false);
  });

  it('should track previous state correctly', () => {
    const { result } = renderHook(() => useFormLifecycle());
    
    act(() => {
      result.current.startEditing();
    });
    
    expect(result.current.previousState).toBe('idle');
    
    act(() => {
      result.current.startValidation();
    });
    
    expect(result.current.previousState).toBe('editing');
  });

  it('should set progress correctly', () => {
    const { result } = renderHook(() => useFormLifecycle());
    
    act(() => {
      result.current.setProgress(50);
    });
    
    expect(result.current.progress).toBe(50);
  });

  it('should clamp progress between 0 and 100', () => {
    const { result } = renderHook(() => useFormLifecycle());
    
    act(() => {
      result.current.setProgress(150);
    });
    
    expect(result.current.progress).toBe(100);
    
    act(() => {
      result.current.setProgress(-50);
    });
    
    expect(result.current.progress).toBe(0);
  });

  it('should track analytics events when enabled', () => {
    const mockAnalyticsHandler = jest.fn();
    const { result } = renderHook(() => 
      useFormLifecycle({ 
        enableAnalytics: true, 
        onAnalyticsEvent: mockAnalyticsHandler 
      })
    );
    
    act(() => {
      result.current.startEditing();
    });
    
    expect(mockAnalyticsHandler).toHaveBeenCalledWith('state_changed', {
      from: 'idle',
      to: 'editing'
    });
  });

  it('should not track analytics events when disabled', () => {
    const mockAnalyticsHandler = jest.fn();
    const { result } = renderHook(() => 
      useFormLifecycle({ 
        enableAnalytics: false, 
        onAnalyticsEvent: mockAnalyticsHandler 
      })
    );
    
    act(() => {
      result.current.startEditing();
    });
    
    expect(mockAnalyticsHandler).not.toHaveBeenCalled();
  });
});
