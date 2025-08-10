import React from 'react';
import { Box, Button, Paper, Typography } from '@mui/material';

interface ErrorBoundaryProps {
  fallbackText?: string;
  onReset?: () => void;
  children: React.ReactNode;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error): void {
    // Optionally log error to monitoring here
    // eslint-disable-next-line no-console
    console.error('ErrorBoundary caught error', error);
  }

  private handleReset = () => {
    this.setState({ hasError: false, error: null });
    this.props.onReset?.();
  };

  render(): React.ReactNode {
    if (this.state.hasError) {
      return (
        <Paper role="alert" aria-live="assertive" sx={{ p: 3 }}>
          <Box display="flex" flexDirection="column" gap={2} alignItems="flex-start">
            <Typography variant="h6">Something went wrong.</Typography>
            <Typography variant="body2" color="text.secondary">
              {this.props.fallbackText || 'An unexpected error occurred. Please try again.'}
            </Typography>
            <Button variant="outlined" onClick={this.handleReset}>Try again</Button>
          </Box>
        </Paper>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;


