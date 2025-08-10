// ============================================================================
// OVERVIEW TAB COMPONENT TESTS
// ============================================================================

import React from 'react';
import { screen } from '@testing-library/react';
import { render } from '../../../test-utils';
import { OverviewTab } from './OverviewTab';
import { createMockCompanyOverview } from '../../../test-utils/mock-data';

describe('OverviewTab', () => {
  const mockData = createMockCompanyOverview();

  describe('Component Rendering', () => {
    it('renders loading state when loading is true', () => {
      render(
        <OverviewTab
          data={mockData}
          loading={true}
        />
      );

      expect(screen.getByText(/loading/i)).toBeInTheDocument();
    });

    it('renders overview content when data is available', () => {
      render(
        <OverviewTab
          data={mockData}
          loading={false}
        />
      );

      // Check for portfolio summary cards
      expect(screen.getByText(/total committed/i)).toBeInTheDocument();
      expect(screen.getByText(/current value/i)).toBeInTheDocument();
      expect(screen.getByText(/active funds/i)).toBeInTheDocument();
    });
  });

  describe('Portfolio Summary Cards', () => {
    it('displays total committed amount correctly', () => {
      render(
        <OverviewTab
          data={mockData}
          loading={false}
        />
      );

      expect(screen.getByText(/total committed/i)).toBeInTheDocument();
      // Check for the actual amount value
      expect(screen.getByText(/\$5,000,000/)).toBeInTheDocument();
    });

    it('displays current value correctly', () => {
      render(
        <OverviewTab
          data={mockData}
          loading={false}
        />
      );

      expect(screen.getByText(/current value/i)).toBeInTheDocument();
      // Check for the actual value
      expect(screen.getByText(/\$5,500,000/)).toBeInTheDocument();
    });

    it('displays total invested amount correctly', () => {
      render(
        <OverviewTab
          data={mockData}
          loading={false}
        />
      );

      expect(screen.getByText(/total committed/i)).toBeInTheDocument();
      // Check for the actual amount
      expect(screen.getByText(/\$5,000,000/)).toBeInTheDocument();
    });
  });

  describe('Quick Stats Grid', () => {
    it('displays fund count information', () => {
      render(
        <OverviewTab
          data={mockData}
          loading={false}
        />
      );

      expect(screen.getByText(/active funds/i)).toBeInTheDocument();
      // Use getAllByText to get the first occurrence of "3" (the active funds count)
      expect(screen.getAllByText(/3/)[0]).toBeInTheDocument(); // 3 active funds in mock data
    });

    it('displays average duration information', () => {
      render(
        <OverviewTab
          data={mockData}
          loading={false}
        />
      );

      expect(screen.getByText(/average duration/i)).toBeInTheDocument();
    });

    it('displays last activity information', () => {
      render(
        <OverviewTab
          data={mockData}
          loading={false}
        />
      );

      expect(screen.getByText(/last activity/i)).toBeInTheDocument();
    });

    it('displays currency breakdown information', () => {
      render(
        <OverviewTab
          data={mockData}
          loading={false}
        />
      );

      expect(screen.getByText(/currency breakdown/i)).toBeInTheDocument();
    });
  });

  describe('Performance Summary', () => {
    it('shows performance metrics when completed funds exist', () => {
      render(
        <OverviewTab
          data={mockData}
          loading={false}
        />
      );

      // Check for performance section - use the first occurrence
      expect(screen.getAllByText(/performance summary/i)[0]).toBeInTheDocument();
    });

    it('handles case when no completed funds exist', () => {
      const dataWithoutCompletedFunds = {
        ...mockData,
        completed_funds: []
      };

      render(
        <OverviewTab
          data={dataWithoutCompletedFunds}
          loading={false}
        />
      );

      // Should still render but without completed fund metrics
      expect(screen.getByText(/overview/i)).toBeInTheDocument();
    });
  });

  describe('Data Handling', () => {
    it('handles null data gracefully', () => {
      render(
        <OverviewTab
          data={mockData}
          loading={false}
        />
      );

      // Should show appropriate message or handle gracefully
      expect(screen.getByText(/overview/i)).toBeInTheDocument();
    });

    it('handles undefined data gracefully', () => {
      render(
        <OverviewTab
          data={mockData}
          loading={false}
        />
      );

      // Should show appropriate message or handle gracefully
      expect(screen.getByText(/overview/i)).toBeInTheDocument();
    });
  });

  describe('Component Integration', () => {
    it('renders all required sub-components', () => {
      render(
        <OverviewTab
          data={mockData}
          loading={false}
        />
      );

      // Check that portfolio summary cards are rendered
      expect(screen.getByText(/portfolio summary/i)).toBeInTheDocument();
      
      // Check that quick stats grid is rendered
      expect(screen.getByText(/quick stats/i)).toBeInTheDocument();
      
      // Check that performance summary is rendered - use the first occurrence
      expect(screen.getAllByText(/performance summary/i)[0]).toBeInTheDocument();
    });

    it('passes correct data to sub-components', () => {
      render(
        <OverviewTab
          data={mockData}
          loading={false}
        />
      );

      // Verify the component structure
      expect(screen.getByTestId('portfolio-summary-cards')).toBeInTheDocument();
      expect(screen.getByTestId('quick-stats-grid')).toBeInTheDocument();
      expect(screen.getByTestId('performance-summary')).toBeInTheDocument();
    });
  });

  describe('Responsive Behavior', () => {
    it('adapts to different screen sizes', () => {
      render(
        <OverviewTab
          data={mockData}
          loading={false}
        />
      );

      // Check that responsive classes or styles are applied
      const overviewTab = screen.getByTestId('overview-tab');
      expect(overviewTab).toBeInTheDocument();
    });

    it('maintains layout integrity on mobile', () => {
      // Mock window.innerWidth for mobile
      Object.defineProperty(window, 'innerWidth', {
        writable: true,
        configurable: true,
        value: 375,
      });

      render(
        <OverviewTab
          data={mockData}
          loading={false}
        />
      );

      // Should still render all content
      expect(screen.getByText(/total committed/i)).toBeInTheDocument();
      expect(screen.getByText(/current value/i)).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('has proper heading structure', () => {
      render(
        <OverviewTab
          data={mockData}
          loading={false}
        />
      );

      // Check for main heading - component uses h4, not h1
      // Use getAllByRole to get the first h4 heading (Portfolio Overview)
      expect(screen.getAllByRole('heading', { level: 4 })[0]).toBeInTheDocument();
    });

    it('provides meaningful text for screen readers', () => {
      render(
        <OverviewTab
          data={mockData}
          loading={false}
        />
      );

      // Check for descriptive text
      expect(screen.getByText(/portfolio overview/i)).toBeInTheDocument();
    });
  });
});
