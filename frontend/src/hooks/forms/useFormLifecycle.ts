import { useCallback, useEffect, useMemo, useRef, useState } from 'react';

/**
 * Form lifecycle states
 */
export type FormLifecycleState = 
  | 'idle'           // Form is ready for user input
  | 'editing'        // User is actively editing the form
  | 'validating'     // Form validation is in progress
  | 'submitting'     // Form submission is in progress
  | 'success'        // Form submission was successful
  | 'error'          // Form submission encountered an error
  | 'cancelled';     // Form was cancelled by user

/**
 * Form lifecycle events
 */
export type FormLifecycleEvent = 
  | 'start_editing'
  | 'field_changed'
  | 'validation_started'
  | 'validation_completed'
  | 'submission_started'
  | 'submission_succeeded'
  | 'submission_failed'
  | 'form_cancelled'
  | 'form_reset'
  | 'state_changed'
  | 'auto_save_started'
  | 'auto_save_completed';

/**
 * Configuration for the form lifecycle hook
 */
export interface UseFormLifecycleConfig {
  /** Whether to enable analytics tracking */
  enableAnalytics?: boolean;
  /** Whether to show progress indicators */
  showProgress?: boolean;
  /** Custom analytics event handler */
  onAnalyticsEvent?: (event: FormLifecycleEvent, data?: any) => void;
  /** Whether to auto-save form state */
  enableAutoSave?: boolean;
  /** Auto-save interval in milliseconds */
  autoSaveInterval?: number;
}

/**
 * Return type for the form lifecycle hook
 */
export interface UseFormLifecycleReturn {
  // Current state
  currentState: FormLifecycleState;
  previousState: FormLifecycleState | null;
  
  // State transitions
  transitionTo: (newState: FormLifecycleState) => void;
  startEditing: () => void;
  startValidation: () => void;
  completeValidation: (isValid: boolean) => void;
  startSubmission: () => void;
  completeSubmission: (success: boolean, error?: string) => void;
  cancelForm: () => void;
  resetForm: () => void;
  
  // Progress tracking
  progress: number;
  setProgress: (progress: number) => void;
  
  // Analytics
  trackEvent: (event: FormLifecycleEvent, data?: any) => void;
  
  // Auto-save
  lastAutoSave: Date | null;
  isAutoSaving: boolean;
  
  // State queries
  canSubmit: boolean;
  canCancel: boolean;
  hasUnsavedChanges: boolean;
  isInProgress: boolean;
}

/**
 * Form lifecycle management hook that provides predictable state machine
 * and lifecycle events for enterprise-grade form management.
 * 
 * @param config - Configuration object for the form lifecycle
 * @returns Form lifecycle state and actions
 */
export function useFormLifecycle(
  config: UseFormLifecycleConfig = {}
): UseFormLifecycleReturn {
  const {
    enableAnalytics = true,
    showProgress = true,
    onAnalyticsEvent,
    enableAutoSave = false,
    autoSaveInterval = 30000 // 30 seconds
  } = config;

  // State management
  const [currentState, setCurrentState] = useState<FormLifecycleState>('idle');
  const [previousState, setPreviousState] = useState<FormLifecycleState | null>(null);
  const [progress, setProgressState] = useState(0);
  const [lastAutoSave, setLastAutoSave] = useState<Date | null>(null);
  const [isAutoSaving, setIsAutoSaving] = useState(false);

  // Refs for tracking
  const stateHistoryRef = useRef<FormLifecycleState[]>(['idle']);
  const editStartTimeRef = useRef<Date | null>(null);
  const autoSaveTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // Track analytics events
  const trackEvent = useCallback((event: FormLifecycleEvent, data?: any) => {
    if (enableAnalytics) {
      // Call custom analytics handler if provided
      onAnalyticsEvent?.(event, data);
      
      // Default analytics tracking (console for now, can be enhanced later)
      if (process.env.NODE_ENV === 'development') {
        console.log(`[Form Lifecycle] ${event}:`, data);
      }
    }
  }, [enableAnalytics, onAnalyticsEvent]);

  // State transition function
  const transitionTo = useCallback((newState: FormLifecycleState) => {
    if (newState === currentState) return;

    setPreviousState(currentState);
    setCurrentState(newState);
    
    // Track state history for debugging
    stateHistoryRef.current.push(newState);
    if (stateHistoryRef.current.length > 10) {
      stateHistoryRef.current.shift();
    }

    // Track analytics event
    if (enableAnalytics) {
      trackEvent('state_changed', { from: currentState, to: newState });
    }
  }, [currentState, enableAnalytics, trackEvent]);

  // Start editing state
  const startEditing = useCallback(() => {
    transitionTo('editing');
    editStartTimeRef.current = new Date();
  }, [transitionTo]);

  // Start validation state
  const startValidation = useCallback(() => {
    transitionTo('validating');
    setProgress(25);
  }, [transitionTo]);

  // Complete validation
  const completeValidation = useCallback((isValid: boolean) => {
    if (isValid) {
      transitionTo('editing');
      setProgress(50);
    } else {
      transitionTo('editing');
      setProgress(25);
    }
  }, [transitionTo]);

  // Start submission
  const startSubmission = useCallback(() => {
    transitionTo('submitting');
    setProgress(75);
  }, [transitionTo]);

  // Complete submission
  const completeSubmission = useCallback((success: boolean, error?: string) => {
    if (success) {
      transitionTo('success');
      setProgress(100);
      
      // Track success analytics
      if (editStartTimeRef.current) {
        const editDuration = Date.now() - editStartTimeRef.current.getTime();
        trackEvent('submission_succeeded', { editDuration });
      }
    } else {
      transitionTo('error');
      setProgress(75);
      
      // Track error analytics
      trackEvent('submission_failed', { error });
    }
  }, [transitionTo, trackEvent]);

  // Cancel form
  const cancelForm = useCallback(() => {
    transitionTo('cancelled');
    setProgress(0);
    
    // Track cancellation analytics
    if (editStartTimeRef.current) {
      const editDuration = Date.now() - editStartTimeRef.current.getTime();
      trackEvent('form_cancelled', { editDuration });
    }
  }, [transitionTo, trackEvent]);

  // Reset form
  const resetForm = useCallback(() => {
    transitionTo('idle');
    setProgress(0);
    editStartTimeRef.current = null;
    setLastAutoSave(null);
    setIsAutoSaving(false);
    
    // Clear auto-save timeout
    if (autoSaveTimeoutRef.current) {
      clearTimeout(autoSaveTimeoutRef.current);
      autoSaveTimeoutRef.current = null;
    }
    
    trackEvent('form_reset');
  }, [transitionTo, trackEvent]);

  // Set progress
  const setProgress = useCallback((newProgress: number) => {
    setProgressState(Math.max(0, Math.min(100, newProgress)));
  }, []);

  // Auto-save functionality
  const startAutoSave = useCallback(() => {
    if (autoSaveTimeoutRef.current) {
      clearTimeout(autoSaveTimeoutRef.current);
    }
    
    autoSaveTimeoutRef.current = setTimeout(() => {
      if (currentState === 'editing') {
        setIsAutoSaving(true);
        setLastAutoSave(new Date());
        
        // Track auto-save event
        trackEvent('auto_save_started');
        
        // Simulate auto-save completion
        setTimeout(() => {
          setIsAutoSaving(false);
          trackEvent('auto_save_completed');
        }, 1000);
        
        // Schedule next auto-save
        startAutoSave();
      }
    }, autoSaveInterval);
  }, [currentState, autoSaveInterval, trackEvent]);

  // Store startAutoSave in a ref to break circular dependency
  const startAutoSaveRef = useRef(startAutoSave);
  startAutoSaveRef.current = startAutoSave;

  // Effect to start auto-save when entering editing state
  useEffect(() => {
    if (currentState === 'editing' && enableAutoSave) {
      startAutoSaveRef.current();
    }
  }, [currentState, enableAutoSave]);

  // Computed properties
  const canSubmit = useMemo(() => {
    return currentState === 'editing' || currentState === 'validating';
  }, [currentState]);

  const canCancel = useMemo(() => {
    return currentState === 'editing' || currentState === 'validating';
  }, [currentState]);

  const hasUnsavedChanges = useMemo(() => {
    return currentState === 'editing' || currentState === 'validating';
  }, [currentState]);

  const isInProgress = useMemo(() => {
    return currentState === 'validating' || currentState === 'submitting';
  }, [currentState]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (autoSaveTimeoutRef.current) {
        clearTimeout(autoSaveTimeoutRef.current);
      }
    };
  }, []);

  return {
    // Current state
    currentState,
    previousState,
    
    // State transitions
    transitionTo,
    startEditing,
    startValidation,
    completeValidation,
    startSubmission,
    completeSubmission,
    cancelForm,
    resetForm,
    
    // Progress tracking
    progress,
    setProgress,
    
    // Analytics
    trackEvent,
    
    // Auto-save
    lastAutoSave,
    isAutoSaving,
    
    // State queries
    canSubmit,
    canCancel,
    hasUnsavedChanges,
    isInProgress
  };
}
