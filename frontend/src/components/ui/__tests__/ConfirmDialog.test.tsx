import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ConfirmDialog } from '../ConfirmDialog';

describe('ConfirmDialog', () => {
  it('calls handlers on actions', async () => {
    const onConfirm = jest.fn();
    const onCancel = jest.fn();
    
    render(
      <ConfirmDialog
        open
        title="Delete"
        description="Are you sure?"
        confirmLabel="Delete"
        onConfirm={onConfirm}
        onCancel={onCancel}
      />
    );

    // Wait for Material-UI components to fully render and stabilize
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /delete/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /cancel/i })).toBeInTheDocument();
    });

    // Use userEvent with proper async handling for Material-UI interactions
    const confirmButton = screen.getByRole('button', { name: /delete/i });
    await userEvent.click(confirmButton);
    
    // Wait for any Material-UI state updates to complete
    await waitFor(() => {
      expect(onConfirm).toHaveBeenCalledTimes(1);
    });

    const cancelButton = screen.getByRole('button', { name: /cancel/i });
    await userEvent.click(cancelButton);
    
    await waitFor(() => {
      expect(onCancel).toHaveBeenCalledTimes(1);
    });
  });
});


