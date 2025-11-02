/**
 * Error Logging and Reporting Infrastructure
 * 
 * Centralized error logging system that:
 * - Logs errors to the console in development
 * - Reports errors to monitoring services in production
 * - Tracks error frequency and patterns
 * - Supports integration with services like Sentry, LogRocket, etc.
 * 
 * Usage:
 *   import { errorLogger } from '@/utils/errorLogger';
 *   errorLogger.logError(error, { context: 'fund_creation', userId: '123' });
 */

import { ErrorInfo, ErrorType, ErrorSeverity, createErrorInfo } from '../types/errors';
import { ApiResponseCode } from '../types/dto';

// ============================================================================
// ERROR LOGGING CONFIGURATION
// ============================================================================

interface ErrorLoggerConfig {
  /** Whether to log errors to console */
  consoleEnabled: boolean;
  /** Whether to send errors to remote monitoring service */
  remoteEnabled: boolean;
  /** Whether to track error frequency */
  trackingEnabled: boolean;
  /** Environment (development, production, etc.) */
  environment: string;
}

const config: ErrorLoggerConfig = {
  consoleEnabled: process.env.NODE_ENV === 'development',
  remoteEnabled: process.env.NODE_ENV === 'production',
  trackingEnabled: true,
  environment: process.env.NODE_ENV || 'development'
};

// ============================================================================
// ERROR CONTEXT
// ============================================================================

interface ErrorContext {
  /** Component or feature where error occurred */
  context?: string;
  /** User ID (if available) */
  userId?: string;
  /** Additional metadata */
  metadata?: Record<string, any>;
  /** API endpoint (if applicable) */
  endpoint?: string;
  /** Request ID (if available) */
  requestId?: string;
  /** Browser/user agent info */
  userAgent?: string;
}

// ============================================================================
// ERROR TRACKING
// ============================================================================

interface ErrorTrackingEntry {
  errorInfo: ErrorInfo;
  context: ErrorContext;
  timestamp: Date;
}

// In-memory error tracking (could be replaced with IndexedDB for persistence)
const errorTrackingLog: ErrorTrackingEntry[] = [];
const MAX_TRACKED_ERRORS = 100; // Limit memory usage

// ============================================================================
// ERROR LOGGER CLASS
// ============================================================================

class ErrorLogger {
  /**
   * Log an error with context
   */
  logError(error: Error | string | ErrorInfo, context: ErrorContext = {}): ErrorInfo {
    let errorInfo: ErrorInfo;
    
    // Convert to ErrorInfo if needed
    if (this.isErrorInfo(error)) {
      errorInfo = error;
    } else {
      errorInfo = createErrorInfo(error);
    }
    
    // Add context to error info
    if (context.metadata) {
      errorInfo.details = { ...errorInfo.details, ...context.metadata };
    }
    
    // Log to console in development
    if (config.consoleEnabled) {
      this.logToConsole(errorInfo, context);
    }
    
    // Track error
    if (config.trackingEnabled) {
      this.trackError(errorInfo, context);
    }
    
    // Send to remote monitoring (Sentry, etc.)
    if (config.remoteEnabled) {
      this.sendToRemoteMonitoring(errorInfo, context);
    }
    
    return errorInfo;
  }
  
  /**
   * Log an API error with response code
   */
  logApiError(
    responseCode: ApiResponseCode,
    error: Error | string,
    context: ErrorContext = {}
  ): ErrorInfo {
    const errorType = this.mapResponseCodeToErrorType(responseCode);
    const errorInfo = createErrorInfo(error, errorType);
    
    return this.logError(errorInfo, {
      ...context,
      metadata: {
        ...context.metadata,
        responseCode
      }
    });
  }
  
  /**
   * Log a warning (non-critical error)
   */
  logWarning(message: string, context: ErrorContext = {}): void {
    if (config.consoleEnabled) {
      console.warn(`[WARNING] ${message}`, context);
    }
    
    // Could send warnings to a different channel in monitoring service
  }
  
  /**
   * Get recent error history
   */
  getErrorHistory(): ErrorTrackingEntry[] {
    return [...errorTrackingLog];
  }
  
  /**
   * Get error frequency by type
   */
  getErrorFrequency(): Record<ErrorType, number> {
    const frequency: Record<string, number> = {};
    
    errorTrackingLog.forEach(entry => {
      const type = entry.errorInfo.type;
      frequency[type] = (frequency[type] || 0) + 1;
    });
    
    return frequency as Record<ErrorType, number>;
  }
  
  /**
   * Clear error history
   */
  clearHistory(): void {
    errorTrackingLog.length = 0;
  }
  
  // ==========================================================================
  // PRIVATE METHODS
  // ==========================================================================
  
  private isErrorInfo(error: any): error is ErrorInfo {
    return (
      error &&
      typeof error === 'object' &&
      'message' in error &&
      'type' in error &&
      'severity' in error
    );
  }
  
  private logToConsole(errorInfo: ErrorInfo, context: ErrorContext): void {
    const style = this.getConsoleStyle(errorInfo.severity);
    const timestamp = errorInfo.timestamp.toISOString();
    
    console.group(`%c[${errorInfo.type.toUpperCase()}] ${errorInfo.message}`, style);
    console.log('Timestamp:', timestamp);
    console.log('Severity:', errorInfo.severity);
    console.log('User Message:', errorInfo.userMessage);
    console.log('Error ID:', errorInfo.id);
    
    if (context.context) {
      console.log('Context:', context.context);
    }
    
    if (context.endpoint) {
      console.log('Endpoint:', context.endpoint);
    }
    
    if (errorInfo.code) {
      console.log('Status Code:', errorInfo.code);
    }
    
    if (errorInfo.details) {
      console.log('Details:', errorInfo.details);
    }
    
    if (context.metadata) {
      console.log('Metadata:', context.metadata);
    }
    
    if (errorInfo.stack) {
      console.log('Stack Trace:', errorInfo.stack);
    }
    
    console.groupEnd();
  }
  
  private getConsoleStyle(severity: ErrorSeverity): string {
    switch (severity) {
      case ErrorSeverity.CRITICAL:
        return 'color: white; background-color: #d32f2f; font-weight: bold; padding: 2px 4px;';
      case ErrorSeverity.HIGH:
        return 'color: white; background-color: #f57c00; font-weight: bold; padding: 2px 4px;';
      case ErrorSeverity.MEDIUM:
        return 'color: black; background-color: #ffa726; padding: 2px 4px;';
      case ErrorSeverity.LOW:
        return 'color: black; background-color: #ffeb3b; padding: 2px 4px;';
      default:
        return 'color: black; background-color: #e0e0e0; padding: 2px 4px;';
    }
  }
  
  private trackError(errorInfo: ErrorInfo, context: ErrorContext): void {
    // Add to tracking log
    errorTrackingLog.push({
      errorInfo,
      context,
      timestamp: new Date()
    });
    
    // Limit log size
    if (errorTrackingLog.length > MAX_TRACKED_ERRORS) {
      errorTrackingLog.shift(); // Remove oldest error
    }
  }
  
  private sendToRemoteMonitoring(errorInfo: ErrorInfo, context: ErrorContext): void {
    // This is where you would integrate with Sentry, LogRocket, etc.
    // Example Sentry integration:
    /*
    if (window.Sentry) {
      window.Sentry.captureException(new Error(errorInfo.message), {
        level: this.mapSeverityToSentryLevel(errorInfo.severity),
        tags: {
          errorType: errorInfo.type,
          context: context.context,
        },
        extra: {
          errorInfo,
          context,
          userAgent: context.userAgent || navigator.userAgent,
        },
      });
    }
    */
    
    // For now, just log that we would send to remote monitoring
    if (config.consoleEnabled) {
      console.log('[MONITORING] Would send error to remote monitoring:', {
        errorId: errorInfo.id,
        type: errorInfo.type,
        severity: errorInfo.severity,
        context: context.context
      });
    }
  }
  
  private mapResponseCodeToErrorType(responseCode: ApiResponseCode): ErrorType {
    // Map DTO response codes to error types
    switch (responseCode) {
      case ApiResponseCode.VALIDATION_ERROR:
        return ErrorType.VALIDATION;
      case ApiResponseCode.RESOURCE_NOT_FOUND:
        return ErrorType.NOT_FOUND;
      case ApiResponseCode.UNAUTHORIZED:
      case ApiResponseCode.AUTHENTICATION_ERROR:
        return ErrorType.AUTHENTICATION;
      case ApiResponseCode.FORBIDDEN:
      case ApiResponseCode.AUTHORIZATION_ERROR:
        return ErrorType.AUTHORIZATION;
      case ApiResponseCode.CONFLICT_ERROR:
      case ApiResponseCode.DUPLICATE_ENTRY:
        return ErrorType.CONFLICT;
      case ApiResponseCode.TOO_MANY_REQUESTS:
      case ApiResponseCode.RATE_LIMIT_EXCEEDED:
        return ErrorType.RATE_LIMIT;
      case ApiResponseCode.REQUEST_TIMEOUT:
      case ApiResponseCode.GATEWAY_TIMEOUT:
        return ErrorType.TIMEOUT;
      case ApiResponseCode.INTERNAL_SERVER_ERROR:
      case ApiResponseCode.DATABASE_ERROR:
      case ApiResponseCode.SERVICE_UNAVAILABLE:
      case ApiResponseCode.BAD_GATEWAY:
        return ErrorType.SERVER;
      default:
        return ErrorType.UNKNOWN;
    }
  }
  
  private mapSeverityToSentryLevel(severity: ErrorSeverity): string {
    switch (severity) {
      case ErrorSeverity.CRITICAL:
        return 'fatal';
      case ErrorSeverity.HIGH:
        return 'error';
      case ErrorSeverity.MEDIUM:
        return 'warning';
      case ErrorSeverity.LOW:
        return 'info';
      default:
        return 'error';
    }
  }
}

// ============================================================================
// SINGLETON EXPORT
// ============================================================================

export const errorLogger = new ErrorLogger();

// ============================================================================
// CONVENIENCE EXPORTS
// ============================================================================

export type { ErrorContext, ErrorLoggerConfig };

