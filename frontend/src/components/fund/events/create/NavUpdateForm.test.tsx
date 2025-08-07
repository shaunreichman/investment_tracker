import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import NavUpdateForm from './NavUpdateForm';

const theme = createTheme();

const defaultProps = {
  formData: {
    nav_per_share: '',
  },
  validationErrors: {
    nav_per_share: '',
  },
  onInputChange: jest.fn(),
};

const renderWithTheme = (component: React.ReactElement) => {
  return render(
    <ThemeProvider theme={theme}>
      {component}
    </ThemeProvider>
  );
};

describe('NavUpdateForm', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Component Rendering', () => {
    it('renders without errors', () => {
      renderWithTheme(
        <NavUpdateForm
          {...defaultProps}
        />
      );

      // Test that component renders without throwing errors
      expect(screen.getByText('NAV Update Details')).toBeInTheDocument();
      expect(screen.getByLabelText(/NAV Per Share/)).toBeInTheDocument();
    });
  });

  describe('Event Handlers', () => {
    it('calls onInputChange when NAV per share field changes', () => {
      const onInputChange = jest.fn();
      renderWithTheme(
        <NavUpdateForm
          {...defaultProps}
          onInputChange={onInputChange}
        />
      );

      const navField = screen.getByLabelText(/NAV Per Share/);
      fireEvent.change(navField, { target: { value: '25.50' } });

      expect(onInputChange).toHaveBeenCalledWith('nav_per_share', '25.50');
    });

    it('calls onInputChange with decimal values', () => {
      const onInputChange = jest.fn();
      renderWithTheme(
        <NavUpdateForm
          {...defaultProps}
          onInputChange={onInputChange}
        />
      );

      const navField = screen.getByLabelText(/NAV Per Share/);
      fireEvent.change(navField, { target: { value: '123.456' } });

      expect(onInputChange).toHaveBeenCalledWith('nav_per_share', '123.456');
    });

    it('calls onInputChange with whole numbers', () => {
      const onInputChange = jest.fn();
      renderWithTheme(
        <NavUpdateForm
          {...defaultProps}
          onInputChange={onInputChange}
        />
      );

      const navField = screen.getByLabelText(/NAV Per Share/);
      fireEvent.change(navField, { target: { value: '100' } });

      expect(onInputChange).toHaveBeenCalledWith('nav_per_share', '100');
    });
  });

  describe('Form Validation', () => {
    it('displays validation errors for NAV per share field', () => {
      const propsWithErrors = {
        ...defaultProps,
        validationErrors: {
          nav_per_share: 'NAV per share is required',
        },
      };

      renderWithTheme(
        <NavUpdateForm
          {...propsWithErrors}
        />
      );

      expect(screen.getByText('NAV per share is required')).toBeInTheDocument();
    });

    it('applies proper input constraints', () => {
      renderWithTheme(
        <NavUpdateForm
          {...defaultProps}
        />
      );

      const navField = screen.getByLabelText(/NAV Per Share/);

      // Test that number input has proper constraints
      expect(navField).toHaveAttribute('type', 'number');
      expect(navField).toHaveAttribute('min', '0');
      expect(navField).toHaveAttribute('step', 'any');
    });

    it('shows required field indicator', () => {
      renderWithTheme(
        <NavUpdateForm
          {...defaultProps}
        />
      );

      expect(screen.getByLabelText(/NAV Per Share \*/)).toBeInTheDocument();
    });
  });

  describe('State Management', () => {
    it('displays current NAV per share value', () => {
      const formData = {
        nav_per_share: '25.75',
      };

      renderWithTheme(
        <NavUpdateForm
          {...defaultProps}
          formData={formData}
        />
      );

      const navField = screen.getByLabelText(/NAV Per Share/);
      expect(navField).toHaveValue(25.75);
    });

    it('handles empty value correctly', () => {
      const formData = {
        nav_per_share: '',
      };

      renderWithTheme(
        <NavUpdateForm
          {...defaultProps}
          formData={formData}
        />
      );

      const navField = screen.getByLabelText(/NAV Per Share/);
      expect(navField).toHaveValue(null);
    });
  });

  describe('Business Logic', () => {
    it('handles very large NAV values', () => {
      const onInputChange = jest.fn();
      renderWithTheme(
        <NavUpdateForm
          {...defaultProps}
          onInputChange={onInputChange}
        />
      );

      const navField = screen.getByLabelText(/NAV Per Share/);
      fireEvent.change(navField, { target: { value: '999999.99' } });

      expect(onInputChange).toHaveBeenCalledWith('nav_per_share', '999999.99');
    });

    it('handles very small NAV values', () => {
      const onInputChange = jest.fn();
      renderWithTheme(
        <NavUpdateForm
          {...defaultProps}
          onInputChange={onInputChange}
        />
      );

      const navField = screen.getByLabelText(/NAV Per Share/);
      fireEvent.change(navField, { target: { value: '0.001' } });

      expect(onInputChange).toHaveBeenCalledWith('nav_per_share', '0.001');
    });

    it('handles zero value', () => {
      const onInputChange = jest.fn();
      renderWithTheme(
        <NavUpdateForm
          {...defaultProps}
          onInputChange={onInputChange}
        />
      );

      const navField = screen.getByLabelText(/NAV Per Share/);
      fireEvent.change(navField, { target: { value: '0' } });

      expect(onInputChange).toHaveBeenCalledWith('nav_per_share', '0');
    });
  });

  describe('Edge Cases', () => {
    it('handles negative values (should be prevented by min attribute)', () => {
      const onInputChange = jest.fn();
      renderWithTheme(
        <NavUpdateForm
          {...defaultProps}
          onInputChange={onInputChange}
        />
      );

      const navField = screen.getByLabelText(/NAV Per Share/);
      fireEvent.change(navField, { target: { value: '-5' } });

      // Should still call onInputChange even with negative value
      // The min attribute will prevent it in the UI
      expect(onInputChange).toHaveBeenCalledWith('nav_per_share', '-5');
    });

    it('handles very long decimal values', () => {
      const onInputChange = jest.fn();
      renderWithTheme(
        <NavUpdateForm
          {...defaultProps}
          onInputChange={onInputChange}
        />
      );

      const navField = screen.getByLabelText(/NAV Per Share/);
      fireEvent.change(navField, { target: { value: '123.456789012345' } });

      expect(onInputChange).toHaveBeenCalledWith('nav_per_share', '123.456789012345');
    });
  });

  describe('Accessibility', () => {
    it('has proper labels and required field indicators', () => {
      renderWithTheme(
        <NavUpdateForm
          {...defaultProps}
        />
      );

      expect(screen.getByLabelText(/NAV Per Share \*/)).toBeInTheDocument();
    });

    it('has proper error states', () => {
      const propsWithErrors = {
        ...defaultProps,
        validationErrors: {
          nav_per_share: 'Invalid NAV value',
        },
      };

      renderWithTheme(
        <NavUpdateForm
          {...propsWithErrors}
        />
      );

      const navField = screen.getByLabelText(/NAV Per Share/);
      expect(navField).toHaveAttribute('aria-invalid', 'true');
    });
  });
}); 