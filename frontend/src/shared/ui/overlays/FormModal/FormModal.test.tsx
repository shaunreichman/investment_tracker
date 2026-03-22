// ============================================================================
// FORM MODAL - TESTS
// ============================================================================

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { ThemeProvider } from '@mui/material/styles';
import { FormProvider, useForm } from 'react-hook-form';
import { dockerTheme } from '@/theme';
import { FormModal } from './FormModal';
import type { FormModalProps } from './FormModal.types';

// Test wrapper with theme and form context
const TestWrapper: React.FC<{ 
  children: React.ReactNode;
  form?: ReturnType<typeof useForm>;
}> = ({ children, form }) => {
  const defaultForm = useForm({
    defaultValues: { name: '' },
  });
  const formInstance = form || defaultForm;

  return (
    <ThemeProvider theme={dockerTheme}>
      <FormProvider {...(formInstance as any)}>
        {children}
      </FormProvider>
    </ThemeProvider>
  );
};

describe('FormModal', () => {
  const defaultProps: FormModalProps = {
    open: true,
    title: 'Test Form',
    onClose: jest.fn(),
    onSubmit: jest.fn(),
    children: <input data-testid="form-input" />,
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Rendering', () => {
    it('renders modal when open', () => {
      render(
        <TestWrapper>
          <FormModal {...defaultProps} />
        </TestWrapper>
      );

      expect(screen.getByText('Test Form')).toBeInTheDocument();
      expect(screen.getByTestId('form-input')).toBeInTheDocument();
    });

    it('does not render when closed', () => {
      render(
        <TestWrapper>
          <FormModal {...defaultProps} open={false} />
        </TestWrapper>
      );

      expect(screen.queryByText('Test Form')).not.toBeInTheDocument();
    });

    it('renders subtitle when provided', () => {
      render(
        <TestWrapper>
          <FormModal
            {...defaultProps}
            subtitle="Test subtitle"
          />
        </TestWrapper>
      );

      expect(screen.getByText('Test subtitle')).toBeInTheDocument();
    });

    it('renders error message when provided', () => {
      render(
        <TestWrapper>
          <FormModal
            {...defaultProps}
            error="Form error occurred"
          />
        </TestWrapper>
      );

      expect(screen.getByText('Form error occurred')).toBeInTheDocument();
    });
  });

  describe('Form Submission', () => {
    it('calls onSubmit when submit button clicked', () => {
      const onSubmit = jest.fn();
      render(
        <TestWrapper>
          <FormModal
            {...defaultProps}
            onSubmit={onSubmit}
          />
        </TestWrapper>
      );

      fireEvent.click(screen.getByText('Submit'));
      expect(onSubmit).toHaveBeenCalledTimes(1);
    });

    it('handles async onSubmit', async () => {
      const onSubmit = jest.fn().mockResolvedValue(undefined);
      render(
        <TestWrapper>
          <FormModal
            {...defaultProps}
            onSubmit={onSubmit}
          />
        </TestWrapper>
      );

      fireEvent.click(screen.getByText('Submit'));
      await waitFor(() => {
        expect(onSubmit).toHaveBeenCalledTimes(1);
      });
    });

    it('disables submit button when isSubmitting is true', () => {
      render(
        <TestWrapper>
          <FormModal
            {...defaultProps}
            isSubmitting={true}
          />
        </TestWrapper>
      );

      const submitButton = screen.getByText('Submitting...');
      expect(submitButton).toBeDisabled();
    });

    it('disables submit button when isValid is false', () => {
      render(
        <TestWrapper>
          <FormModal
            {...defaultProps}
            isValid={false}
          />
        </TestWrapper>
      );

      const submitButton = screen.getByText('Submit');
      expect(submitButton).toBeDisabled();
    });
  });

  describe('Dirty State Guard', () => {
    it('shows confirmation dialog when closing with unsaved changes', () => {
      const onClose = jest.fn();
      render(
        <TestWrapper>
          <FormModal
            {...defaultProps}
            onClose={onClose}
            isDirty={true}
            showCloseConfirmation={true}
          />
        </TestWrapper>
      );

      fireEvent.click(screen.getByText('Cancel'));
      
      // Should show confirmation dialog
      expect(screen.getByText('Unsaved Changes')).toBeInTheDocument();
      expect(onClose).not.toHaveBeenCalled();
    });

    it('closes without confirmation when not dirty', () => {
      const onClose = jest.fn();
      render(
        <TestWrapper>
          <FormModal
            {...defaultProps}
            onClose={onClose}
            isDirty={false}
          />
        </TestWrapper>
      );

      fireEvent.click(screen.getByText('Cancel'));
      
      expect(onClose).toHaveBeenCalledTimes(1);
      expect(screen.queryByText('Unsaved Changes')).not.toBeInTheDocument();
    });

    it('closes when confirmation is dismissed', () => {
      const onClose = jest.fn();
      render(
        <TestWrapper>
          <FormModal
            {...defaultProps}
            onClose={onClose}
            isDirty={true}
            showCloseConfirmation={true}
          />
        </TestWrapper>
      );

      // Click cancel to trigger confirmation
      fireEvent.click(screen.getByText('Cancel'));
      
      // Click discard in confirmation
      fireEvent.click(screen.getByText('Discard Changes'));
      
      expect(onClose).toHaveBeenCalledTimes(1);
    });

    it('does not show confirmation when showCloseConfirmation is false', () => {
      const onClose = jest.fn();
      render(
        <TestWrapper>
          <FormModal
            {...defaultProps}
            onClose={onClose}
            isDirty={true}
            showCloseConfirmation={false}
          />
        </TestWrapper>
      );

      fireEvent.click(screen.getByText('Cancel'));
      
      expect(onClose).toHaveBeenCalledTimes(1);
      expect(screen.queryByText('Unsaved Changes')).not.toBeInTheDocument();
    });

    it('uses custom confirmation message', () => {
      render(
        <TestWrapper>
          <FormModal
            {...defaultProps}
            isDirty={true}
            showCloseConfirmation={true}
            closeConfirmationMessage="Custom confirmation message"
          />
        </TestWrapper>
      );

      fireEvent.click(screen.getByText('Cancel'));
      
      expect(screen.getByText('Custom confirmation message')).toBeInTheDocument();
    });
  });

  describe('Analytics Callbacks', () => {
    it('calls onOpen when modal opens', () => {
      const onOpen = jest.fn();
      const { rerender } = render(
        <TestWrapper>
          <FormModal
            {...defaultProps}
            open={false}
            onOpen={onOpen}
          />
        </TestWrapper>
      );

      expect(onOpen).not.toHaveBeenCalled();

      rerender(
        <TestWrapper>
          <FormModal
            {...defaultProps}
            open={true}
            onOpen={onOpen}
          />
        </TestWrapper>
      );

      expect(onOpen).toHaveBeenCalledTimes(1);
      expect(onOpen).toHaveBeenCalledWith(
        expect.objectContaining({
          overlayType: 'form',
          action: 'open',
        })
      );
    });

    it('calls onSubmitEvent when form is submitted', () => {
      const onSubmitEvent = jest.fn();
      render(
        <TestWrapper>
          <FormModal
            {...defaultProps}
            onSubmitEvent={onSubmitEvent}
          />
        </TestWrapper>
      );

      fireEvent.click(screen.getByText('Submit'));
      
      expect(onSubmitEvent).toHaveBeenCalledTimes(1);
      expect(onSubmitEvent).toHaveBeenCalledWith(
        expect.objectContaining({
          overlayType: 'form',
          action: 'submit',
        })
      );
    });

    it('calls onError when onSubmit throws', async () => {
      const error = new Error('Submission failed');
      const onSubmit = jest.fn().mockRejectedValue(error);
      const onError = jest.fn();
      
      render(
        <TestWrapper>
          <FormModal
            {...defaultProps}
            onSubmit={onSubmit}
            onError={onError}
          />
        </TestWrapper>
      );

      fireEvent.click(screen.getByText('Submit'));
      
      await waitFor(() => {
        expect(onError).toHaveBeenCalledTimes(1);
        expect(onError).toHaveBeenCalledWith(
          expect.objectContaining({
            overlayType: 'form',
            action: 'error',
            error: error,
          })
        );
      });
    });
  });

  describe('Accessibility', () => {
    it('has proper ARIA attributes', () => {
      render(
        <TestWrapper>
          <FormModal {...defaultProps} />
        </TestWrapper>
      );

      const dialog = screen.getByRole('dialog');
      expect(dialog).toHaveAttribute('aria-modal', 'true');
      expect(dialog).toHaveAttribute('aria-labelledby', 'form-modal-title');
    });

    it('has accessible title', () => {
      render(
        <TestWrapper>
          <FormModal {...defaultProps} />
        </TestWrapper>
      );

      const title = screen.getByText('Test Form');
      expect(title).toHaveAttribute('id', 'form-modal-title');
    });

    it('has accessible subtitle when provided', () => {
      render(
        <TestWrapper>
          <FormModal
            {...defaultProps}
            subtitle="Test subtitle"
          />
        </TestWrapper>
      );

      const subtitle = screen.getByText('Test subtitle');
      expect(subtitle).toHaveAttribute('id', 'form-modal-subtitle');
    });
  });

  describe('Custom Actions', () => {
    it('renders custom actions when provided', () => {
      const customActions = (
        <>
          <button data-testid="custom-action-1">Custom 1</button>
          <button data-testid="custom-action-2">Custom 2</button>
        </>
      );

      render(
        <TestWrapper>
          <FormModal
            {...defaultProps}
            actions={customActions}
          />
        </TestWrapper>
      );

      expect(screen.getByTestId('custom-action-1')).toBeInTheDocument();
      expect(screen.getByTestId('custom-action-2')).toBeInTheDocument();
      expect(screen.queryByText('Submit')).not.toBeInTheDocument();
    });
  });
});

