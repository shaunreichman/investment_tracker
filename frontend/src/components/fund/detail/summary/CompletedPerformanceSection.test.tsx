import React from 'react';
import { render, screen } from '@testing-library/react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CompletedPerformanceSection from './CompletedPerformanceSection';
import { ExtendedFund, FundTrackingType, FundStatus } from '../../../../types/api';

// Create a mock theme for testing
const theme = createTheme();

// Helper function to render component with theme
const renderWithTheme = (component: React.ReactElement) => {
  return render(
    <ThemeProvider theme={theme}>
      {component}
    </ThemeProvider>
  );
};

// Helper function to create mock fund data
const createMockFund = (overrides: Partial<ExtendedFund> = {}): ExtendedFund => ({
  id: 1,
  name: 'Test Fund',
  status: FundStatus.COMPLETED, // Changed from ACTIVE to COMPLETED
  tracking_type: FundTrackingType.NAV_BASED,
  start_date: '2020-01-01',
  end_date: '2025-01-01',
  current_nav_total: 1000000,
  total_cost_basis: 800000,
  completed_real_irr: null,
  completed_after_tax_irr: null,
  actual_duration_months: null,
  // Required ExtendedFund properties
  investment_company: 'Test Company',
  entity: 'Test Entity',
  currency: 'AUD',
  commitment_amount: 1000000,
  expected_irr: 0.15,
  expected_duration_months: 60,
  investment_company_id: 1,
  entity_id: 1,
  current_equity_balance: 1000000,
  average_equity_balance: 1000000,
  final_tax_statement_received: false,
  created_at: '2020-01-01T00:00:00Z',
  updated_at: '2020-01-01T00:00:00Z',
  ...overrides
});

describe('CompletedPerformanceSection', () => {
  describe('Rendering Logic', () => {
    it('should render when performance metrics are available', () => {
      const fund = createMockFund({
        completed_real_irr: 0.15,
        completed_after_tax_irr: 0.12,
        actual_duration_months: 24
      });
      
      renderWithTheme(<CompletedPerformanceSection fund={fund} formatCurrency={() => ''} formatDate={() => ''} />);
      
      expect(screen.getByText('Completed Performance')).toBeInTheDocument();
      expect(screen.getByText('Net-tax IRR')).toBeInTheDocument();
      expect(screen.getByText('Gross IRR')).toBeInTheDocument();
      expect(screen.getByText('Actual Duration')).toBeInTheDocument();
    });

    it('should not render when no performance metrics are available', () => {
      const fund = createMockFund({
        completed_real_irr: null,
        completed_after_tax_irr: null,
        actual_duration_months: null
      });
      
      renderWithTheme(
        <CompletedPerformanceSection fund={fund} formatCurrency={() => ''} formatDate={() => ''} />
      );
      
      expect(screen.queryByText('Completed Performance')).not.toBeInTheDocument();
    });

    it('should render partial metrics when only some are available', () => {
      const fund = createMockFund({
        completed_real_irr: 0.15,
        completed_after_tax_irr: null,
        actual_duration_months: 24
      });
      
      renderWithTheme(<CompletedPerformanceSection fund={fund} formatCurrency={() => ''} formatDate={() => ''} />);
      
      expect(screen.getByText('Completed Performance')).toBeInTheDocument();
      expect(screen.getByText('Gross IRR')).toBeInTheDocument();
      expect(screen.getByText('Actual Duration')).toBeInTheDocument();
      expect(screen.queryByText('Net-tax IRR')).not.toBeInTheDocument();
    });
  });

  describe('Metric Display', () => {
    it('should display IRR values as percentages with 2 decimal places', () => {
      const fund = createMockFund({
        completed_real_irr: 0.1567,
        completed_after_tax_irr: 0.1234
      });
      
      renderWithTheme(<CompletedPerformanceSection fund={fund} formatCurrency={() => ''} formatDate={() => ''} />);
      
      expect(screen.getByText('15.67%')).toBeInTheDocument();
      expect(screen.getByText('12.34%')).toBeInTheDocument();
    });

    it('should display duration with months unit', () => {
      const fund = createMockFund({
        actual_duration_months: 18
      });
      
      renderWithTheme(<CompletedPerformanceSection fund={fund} formatCurrency={() => ''} formatDate={() => ''} />);
      
      expect(screen.getByText('18 months')).toBeInTheDocument();
    });

    it('should handle zero values correctly', () => {
      const fund = createMockFund({
        completed_real_irr: 0,
        completed_after_tax_irr: 0
      });
      
      renderWithTheme(<CompletedPerformanceSection fund={fund} formatCurrency={() => ''} formatDate={() => ''} />);
      
      // Check that both zero values are displayed
      const zeroElements = screen.getAllByText('0.00%');
      expect(zeroElements).toHaveLength(2);
    });

    it('should handle very small values correctly', () => {
      const fund = createMockFund({
        completed_real_irr: 0.001,
        completed_after_tax_irr: 0.0001
      });
      
      renderWithTheme(<CompletedPerformanceSection fund={fund} formatCurrency={() => ''} formatDate={() => ''} />);
      
      expect(screen.getByText('0.10%')).toBeInTheDocument();
      expect(screen.getByText('0.01%')).toBeInTheDocument();
    });
  });

  describe('Visual Elements', () => {
    it('should display correct icons for each metric', () => {
      const fund = createMockFund({
        completed_real_irr: 0.15,
        completed_after_tax_irr: 0.12,
        actual_duration_months: 24
      });
      
      renderWithTheme(<CompletedPerformanceSection fund={fund} formatCurrency={() => ''} formatDate={() => ''} />);
      
      // Check that icons are present (emoji characters)
      // Note: The component shows 'IRR' with 📊 icon, 'Net-tax IRR' with 💰 icon, and 'Gross IRR' with 📈 icon
      expect(screen.getByText('💰')).toBeInTheDocument(); // Net-tax IRR
      expect(screen.getByText('📈')).toBeInTheDocument(); // Gross IRR  
      expect(screen.getByText('⏱️')).toBeInTheDocument(); // Actual Duration
    });

    it('should display section header with correct icon', () => {
      const fund = createMockFund({
        completed_real_irr: 0.15
      });
      
      renderWithTheme(<CompletedPerformanceSection fund={fund} formatCurrency={() => ''} formatDate={() => ''} />);
      
      expect(screen.getByText('Completed Performance')).toBeInTheDocument();
      // Assessment icon should be present
      expect(screen.getByTestId('AssessmentIcon')).toBeInTheDocument();
    });
  });

  describe('Edge Cases', () => {
    it('should handle undefined values gracefully', () => {
      const fund = createMockFund({
        completed_real_irr: null,
        completed_after_tax_irr: null,
        actual_duration_months: null
      });
      
      renderWithTheme(
        <CompletedPerformanceSection fund={fund} formatCurrency={() => ''} formatDate={() => ''} />
      );
      
      expect(screen.queryByText('Completed Performance')).not.toBeInTheDocument();
    });

    it('should filter out null and undefined metrics', () => {
      const fund = createMockFund({
        completed_real_irr: 0.15,
        completed_after_tax_irr: null,
        actual_duration_months: null
      });
      
      renderWithTheme(<CompletedPerformanceSection fund={fund} formatCurrency={() => ''} formatDate={() => ''} />);
      
      expect(screen.getByText('Gross IRR')).toBeInTheDocument();
      expect(screen.queryByText('Net-tax IRR')).not.toBeInTheDocument();
      expect(screen.queryByText('Actual Duration')).not.toBeInTheDocument();
    });

    it('should handle negative IRR values', () => {
      const fund = createMockFund({
        completed_real_irr: -0.05,
        completed_after_tax_irr: -0.03
      });
      
      renderWithTheme(<CompletedPerformanceSection fund={fund} formatCurrency={() => ''} formatDate={() => ''} />);
      
      expect(screen.getByText('-5.00%')).toBeInTheDocument();
      expect(screen.getByText('-3.00%')).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('should have proper heading structure', () => {
      const fund = createMockFund({
        completed_real_irr: 0.15
      });
      
      renderWithTheme(<CompletedPerformanceSection fund={fund} formatCurrency={() => ''} formatDate={() => ''} />);
      
      const heading = screen.getByRole('heading', { level: 6 });
      expect(heading).toBeInTheDocument();
      expect(heading).toHaveTextContent('Completed Performance');
    });

    it('should display metric labels clearly', () => {
      const fund = createMockFund({
        completed_real_irr: 0.15,
        completed_after_tax_irr: 0.12
      });
      
      renderWithTheme(<CompletedPerformanceSection fund={fund} formatCurrency={() => ''} formatDate={() => ''} />);
      
      expect(screen.getByText('Net-tax IRR')).toBeInTheDocument();
      expect(screen.getByText('Gross IRR')).toBeInTheDocument();
    });
  });
});
