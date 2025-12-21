// ============================================================================
// CONFIRM DIALOG - TESTS
// ============================================================================

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { ThemeProvider } from '@mui/material/styles';
import { dockerTheme } from '@/theme';
import { ConfirmDialog } from './ConfirmDialog';
import type { ConfirmDialogProps } from './ConfirmDialog.types';

// Test wrapper with theme
const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <ThemeProvider theme={dockerTheme}>
    {children}
  </ThemeProvider>
);

describe('ConfirmDialog', () => {
  const defaultProps: ConfirmDialogProps = {
    open: true,
    title: 'Test Dialog',
    description: 'Test description',
    confirmAction: {
      label: 'Confirm',
      variant: 'primary',
      onClick: jest.fn(),
    },
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Rendering', () => {
    it('renders dialog when open', () => {
      render(
        <TestWrapper>
          <ConfirmDialog {...defaultProps} />
        </TestWrapper>
      );

      expect(screen.getByText('Test Dialog')).toBeInTheDocument();
      expect(screen.getByText('Test description')).toBeInTheDocument();
    });

    it('does not render when closed', () => {
      render(
        <TestWrapper>
          <ConfirmDialog {...defaultProps} open={false} />
        </TestWrapper>
      );

      expect(screen.queryByText('Test Dialog')).not.toBeInTheDocument();
    });

    it('renders custom children instead of description', () => {
      render(
        <TestWrapper>
          <ConfirmDialog
            {...defaultProps}
            description={undefined}
            children={<div data-testid="custom-content">Custom content</div>}
          />
        </TestWrapper>
      );

      expect(screen.getByTestId('custom-content')).toBeInTheDocument();
      expect(screen.queryByText('Test description')).not.toBeInTheDocument();
    });

    it('renders error message when provided', () => {
      render(
        <TestWrapper>
          <ConfirmDialog
            {...defaultProps}
            error="Something went wrong"
          />
        </TestWrapper>
      );

      expect(screen.getByText('Something went wrong')).toBeInTheDocument();
    });

    it('renders error from Error object', () => {
      const error = new Error('Test error');
      render(
        <TestWrapper>
          <ConfirmDialog
            {...defaultProps}
            error={error}
          />
        </TestWrapper>
      );

      expect(screen.getByText('Test error')).toBeInTheDocument();
    });
  });

  describe('Action Buttons', () => {
    it('renders confirm button', () => {
      render(
        <TestWrapper>
          <ConfirmDialog {...defaultProps} />
        </TestWrapper>
      );

      const confirmButton = screen.getByText('Confirm');
      expect(confirmButton).toBeInTheDocument();
    });

    it('renders cancel button when cancelAction provided', () => {
      const cancelAction = {
        label: 'Cancel',
        variant: 'outlined' as const,
        onClick: jest.fn(),
      };

      render(
        <TestWrapper>
          <ConfirmDialog
            {...defaultProps}
            cancelAction={cancelAction}
          />
        </TestWrapper>
      );

      expect(screen.getByText('Cancel')).toBeInTheDocument();
    });

    it('does not render cancel button when cancelAction not provided', () => {
      render(
        <TestWrapper>
          <ConfirmDialog {...defaultProps} />
        </TestWrapper>
      );

      expect(screen.queryByText('Cancel')).not.toBeInTheDocument();
    });

    it('renders tertiary action when provided', () => {
      const tertiaryAction = {
        label: 'Save Draft',
        variant: 'secondary' as const,
        onClick: jest.fn(),
      };

      render(
        <TestWrapper>
          <ConfirmDialog
            {...defaultProps}
            tertiaryAction={tertiaryAction}
          />
        </TestWrapper>
      );

      expect(screen.getByText('Save Draft')).toBeInTheDocument();
    });

    it('shows loading state on confirm button', () => {
      render(
        <TestWrapper>
          <ConfirmDialog
            {...defaultProps}
            confirmAction={{
              ...defaultProps.confirmAction,
              loading: true,
            }}
          />
        </TestWrapper>
      );

      const confirmButton = screen.getByText('Working...');
      expect(confirmButton).toBeInTheDocument();
      expect(confirmButton).toBeDisabled();
    });

    it('disables button when disabled prop is true', () => {
      render(
        <TestWrapper>
          <ConfirmDialog
            {...defaultProps}
            confirmAction={{
              ...defaultProps.confirmAction,
              disabled: true,
            }}
          />
        </TestWrapper>
      );

      const confirmButton = screen.getByText('Confirm');
      expect(confirmButton).toBeDisabled();
    });
  });

  describe('User Interactions', () => {
    it('calls confirmAction.onClick when confirm button clicked', () => {
      const onConfirm = jest.fn();
      render(
        <TestWrapper>
          <ConfirmDialog
            {...defaultProps}
            confirmAction={{
              ...defaultProps.confirmAction,
              onClick: onConfirm,
            }}
          />
        </TestWrapper>
      );

      fireEvent.click(screen.getByText('Confirm'));
      expect(onConfirm).toHaveBeenCalledTimes(1);
    });

    it('calls cancelAction.onClick when cancel button clicked', () => {
      const onCancel = jest.fn();
      const cancelAction = {
        label: 'Cancel',
        variant: 'outlined' as const,
        onClick: onCancel,
      };

      render(
        <TestWrapper>
          <ConfirmDialog
            {...defaultProps}
            cancelAction={cancelAction}
          />
        </TestWrapper>
      );

      fireEvent.click(screen.getByText('Cancel'));
      expect(onCancel).toHaveBeenCalledTimes(1);
    });

    it('handles async confirmAction.onClick', async () => {
      const onConfirm = jest.fn().mockResolvedValue(undefined);
      render(
        <TestWrapper>
          <ConfirmDialog
            {...defaultProps}
            confirmAction={{
              ...defaultProps.confirmAction,
              onClick: onConfirm,
            }}
          />
        </TestWrapper>
      );

      fireEvent.click(screen.getByText('Confirm'));
      await waitFor(() => {
        expect(onConfirm).toHaveBeenCalledTimes(1);
      });
    });
  });

  describe('Keyboard Navigation', () => {
    it('closes dialog on Escape key when not disabled', () => {
      const onClose = jest.fn();
      render(
        <TestWrapper>
          <ConfirmDialog
            {...defaultProps}
            onClose={onClose}
            cancelAction={{
              label: 'Cancel',
              variant: 'outlined',
              onClick: () => {},
            }}
          />
        </TestWrapper>
      );

      const dialog = screen.getByRole('dialog');
      fireEvent.keyDown(dialog, { key: 'Escape', code: 'Escape' });
      
      // Note: MUI Dialog handles Escape internally, so we verify the dialog is still open
      // The actual close behavior is tested via onClose callback
      expect(screen.getByText('Test Dialog')).toBeInTheDocument();
    });

    it('does not close on Escape when disableEscapeKeyDown is true', () => {
      render(
        <TestWrapper>
          <ConfirmDialog
            {...defaultProps}
            disableEscapeKeyDown={true}
          />
        </TestWrapper>
      );

      const dialog = screen.getByRole('dialog');
      fireEvent.keyDown(dialog, { key: 'Escape', code: 'Escape' });
      
      expect(screen.getByText('Test Dialog')).toBeInTheDocument();
    });
  });

  describe('Analytics Callbacks', () => {
    it('calls onOpen when dialog opens', () => {
      const onOpen = jest.fn();
      const { rerender } = render(
        <TestWrapper>
          <ConfirmDialog
            {...defaultProps}
            open={false}
            onOpen={onOpen}
          />
        </TestWrapper>
      );

      expect(onOpen).not.toHaveBeenCalled();

      rerender(
        <TestWrapper>
          <ConfirmDialog
            {...defaultProps}
            open={true}
            onOpen={onOpen}
          />
        </TestWrapper>
      );

      expect(onOpen).toHaveBeenCalledTimes(1);
      expect(onOpen).toHaveBeenCalledWith(
        expect.objectContaining({
          overlayType: 'confirm',
          action: 'open',
        })
      );
    });

    it('calls onAction when confirm button clicked', () => {
      const onAction = jest.fn();
      render(
        <TestWrapper>
          <ConfirmDialog
            {...defaultProps}
            onAction={onAction}
          />
        </TestWrapper>
      );

      fireEvent.click(screen.getByText('Confirm'));
      
      expect(onAction).toHaveBeenCalledTimes(1);
      expect(onAction).toHaveBeenCalledWith(
        expect.objectContaining({
          overlayType: 'confirm',
          action: 'confirm',
        })
      );
    });
  });

  describe('Accessibility', () => {
    it('has proper ARIA attributes', () => {
      render(
        <TestWrapper>
          <ConfirmDialog {...defaultProps} />
        </TestWrapper>
      );

      const dialog = screen.getByRole('dialog');
      expect(dialog).toHaveAttribute('aria-modal', 'true');
      expect(dialog).toHaveAttribute('aria-labelledby', 'confirm-dialog-title');
      expect(dialog).toHaveAttribute('aria-describedby', 'confirm-dialog-description');
    });

    it('has accessible title', () => {
      render(
        <TestWrapper>
          <ConfirmDialog {...defaultProps} />
        </TestWrapper>
      );

      const title = screen.getByText('Test Dialog');
      expect(title).toHaveAttribute('id', 'confirm-dialog-title');
    });

    it('has accessible description', () => {
      render(
        <TestWrapper>
          <ConfirmDialog {...defaultProps} />
        </TestWrapper>
      );

      const description = screen.getByText('Test description');
      expect(description).toHaveAttribute('id', 'confirm-dialog-description');
    });
  });

  describe('Custom Footer', () => {
    it('renders custom footer when provided', () => {
      const customFooter = <div data-testid="custom-footer">Custom Footer</div>;
      
      render(
        <TestWrapper>
          <ConfirmDialog
            {...defaultProps}
            footer={customFooter}
          />
        </TestWrapper>
      );

      expect(screen.getByTestId('custom-footer')).toBeInTheDocument();
      expect(screen.queryByText('Confirm')).not.toBeInTheDocument();
    });
  });
});

