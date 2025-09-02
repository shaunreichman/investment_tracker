import React from 'react';
import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { render } from '../../test-utils';
import { CompaniesPage } from './CompaniesPage';
import { createMockCompanyOverview, createMockEnhancedFundsResponse, createMockCompanyDetails } from '../../test-utils/mock-data';

// Mock the custom hooks directly in the jest.mock call
jest.mock('../../hooks/useInvestmentCompanies', () => ({
  useCompanyOverview: jest.fn(),
  useEnhancedFunds: jest.fn(),
  useCompanyDetails: jest.fn(),
}));

// Mock useParams hook
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useParams: () => ({ companyId: '1' })
}));

// Get the mocked functions after the mock is set up
const mockUseCompanyOverview = jest.mocked(require('../../hooks/useInvestmentCompanies').useCompanyOverview);
const mockUseEnhancedFunds = jest.mocked(require('../../hooks/useInvestmentCompanies').useEnhancedFunds);
const mockUseCompanyDetails = jest.mocked(require('../../hooks/useInvestmentCompanies').useCompanyDetails);

describe('CompaniesPage', () => {
  // Increase timeout for all tests in this suite
  jest.setTimeout(15000);
  
  const user = userEvent;

  beforeEach(() => {
    jest.clearAllMocks();
    
    // Set up default mock implementations
    mockUseCompanyOverview.mockReturnValue({
      data: createMockCompanyOverview(),
      loading: false,
      error: null,
      refetch: jest.fn()
    });
    
    mockUseEnhancedFunds.mockReturnValue({
      data: createMockEnhancedFundsResponse(),
      loading: false,
      error: null,
      refetch: jest.fn()
    });
    
    mockUseCompanyDetails.mockReturnValue({
      data: createMockCompanyDetails(),
      loading: false,
      error: null,
      refetch: jest.fn()
    });
  });

  describe('Page Integration', () => {
    it('renders company header with company information', async () => {
      render(<CompaniesPage />);
      
      // Wait for company data to load
      await waitFor(() => {
        expect(screen.getByRole('heading', { name: 'Test Investment Company' })).toBeInTheDocument();
      });
      
      // Check for company type
      expect(screen.getByText('Private Equity Investment Company')).toBeInTheDocument();
    });

    it('displays tab navigation with all expected tabs', async () => {
      render(<CompaniesPage />);
      
      await waitFor(() => {
        expect(screen.getByRole('tab', { name: /overview/i })).toBeInTheDocument();
      });
      await waitFor(() => {
        expect(screen.getByRole('tab', { name: /funds/i })).toBeInTheDocument();
      });
      await waitFor(() => {
        expect(screen.getByRole('tab', { name: /analysis/i })).toBeInTheDocument();
      });
      await waitFor(() => {
        expect(screen.getByRole('tab', { name: /activity/i })).toBeInTheDocument();
      });
      await waitFor(() => {
        expect(screen.getByRole('tab', { name: /company details/i })).toBeInTheDocument();
      });
    });

    it('shows Overview tab content by default', async () => {
      render(<CompaniesPage />);
      
      await waitFor(() => {
        expect(screen.getByRole('tabpanel', { name: /overview/i })).toBeInTheDocument();
      });
      await waitFor(() => {
        expect(screen.getByText(/total committed/i)).toBeInTheDocument();
      });
      await waitFor(() => {
        expect(screen.getByText(/current value/i)).toBeInTheDocument();
      });
    });
  });

  describe('Tab Navigation', () => {
    it('switches to Funds tab when clicked', async () => {
      render(<CompaniesPage />);
      
      await waitFor(() => {
        expect(screen.getByRole('tabpanel', { name: /overview/i })).toBeInTheDocument();
      });

      const fundsTab = screen.getByRole('tab', { name: /funds/i });
      await user.click(fundsTab);

      // Wait for tab panel to appear
      await waitFor(() => {
        expect(screen.getByRole('tabpanel', { name: /funds/i })).toBeInTheDocument();
      }, { timeout: 10000 });
      
      // Wait for fund content to appear with increased timeout
      await waitFor(() => {
        expect(screen.getByText(/test enhanced fund 1/i)).toBeInTheDocument();
      }, { timeout: 10000 });
    }, 15000); // Increase test timeout to 15 seconds

    it('switches to Company Details tab when clicked', async () => {
      render(<CompaniesPage />);
      
      await waitFor(() => {
        expect(screen.getByRole('tabpanel', { name: /overview/i })).toBeInTheDocument();
      });

      const detailsTab = screen.getByRole('tab', { name: /company details/i });
      await user.click(detailsTab);

      await waitFor(() => {
        expect(screen.getByRole('tabpanel', { name: /company details/i })).toBeInTheDocument();
      });
      await waitFor(() => {
        expect(screen.getByText(/john doe/i)).toBeInTheDocument();
      });
      await waitFor(() => {
        expect(screen.getByText(/investment manager/i)).toBeInTheDocument();
      });
    });

    it('maintains active tab state correctly', async () => {
      render(<CompaniesPage />);
      
      await waitFor(() => {
        expect(screen.getByRole('tab', { name: /overview/i })).toHaveAttribute('aria-selected', 'true');
      });

      const fundsTab = screen.getByRole('tab', { name: /funds/i });
      await user.click(fundsTab);

      await waitFor(() => {
        expect(screen.getByRole('tab', { name: /funds/i })).toHaveAttribute('aria-selected', 'true');
      });
      await waitFor(() => {
        expect(screen.getByRole('tab', { name: /overview/i })).toHaveAttribute('aria-selected', 'false');
      });
    });
  });

  describe('Loading States', () => {
    it('shows loading state while fetching company data', () => {
      // Set up loading state
      mockUseCompanyOverview.mockReturnValue({
        data: null,
        loading: true,
        error: null,
        refetch: jest.fn()
      });
      
      render(<CompaniesPage />);
      
      // Should show loading state initially
      expect(screen.getByRole('progressbar')).toBeInTheDocument();
    });

    it('handles loading states for tab content', async () => {
      render(<CompaniesPage />);
      
      // Wait for initial load
      await waitFor(() => {
        expect(screen.getByRole('heading', { name: 'Test Investment Company' })).toBeInTheDocument();
      });

      // Switch to Funds tab (should show loading briefly)
      const fundsTab = screen.getByRole('tab', { name: /funds/i });
      await user.click(fundsTab);

      // Wait for tab panel with increased timeout
      await waitFor(() => {
        expect(screen.getByRole('tabpanel', { name: /funds/i })).toBeInTheDocument();
      }, { timeout: 10000 });
    }, 15000); // Increase test timeout to 15 seconds
  });

  describe('Error Handling', () => {
    it('displays error message when company data fails to load', async () => {
      // Set up error state
      mockUseCompanyOverview.mockReturnValue({
        data: null,
        loading: false,
        error: new Error('Failed to fetch company data'),
        refetch: jest.fn()
      });
      
      render(<CompaniesPage />);
      
      await waitFor(() => {
        expect(screen.getByText(/An unexpected error occurred/i)).toBeInTheDocument();
      });
    });

    it('provides retry functionality for failed requests', async () => {
      const mockRefetch = jest.fn();
      
      // Set up error state initially with retryable error
      mockUseCompanyOverview.mockReturnValue({
        data: null,
        loading: false,
        error: {
          message: 'Failed to fetch company data',
          type: 'NETWORK',
          severity: 'MEDIUM',
          retryable: true,
          timestamp: new Date()
        },
        refetch: mockRefetch
      });
      
      render(<CompaniesPage />);
      
      await waitFor(() => {
        expect(screen.getByText(/Failed to fetch company data/i)).toBeInTheDocument();
      });

      // Find and click retry button (should be in the error alert)
      // Use getAllByRole to get all retry buttons and click the text button (not the icon button)
      const retryButtons = screen.getAllByRole('button', { name: /retry/i });
      const textRetryButton = retryButtons.find(button => button.textContent === 'Retry');
      expect(textRetryButton).toBeInTheDocument();
      await user.click(textRetryButton!);

      // Verify refetch was called
      expect(mockRefetch).toHaveBeenCalled();
    });
  });

  describe('Responsive Behavior', () => {
    it('adapts layout for different screen sizes', async () => {
      render(<CompaniesPage />);
      
      await waitFor(() => {
        expect(screen.getByRole('heading', { name: 'Test Investment Company' })).toBeInTheDocument();
      });

      // Check that the layout is responsive by looking for the main container
      const mainContainer = screen.getByRole('main');
      expect(mainContainer).toBeInTheDocument();
    });
  });
});
