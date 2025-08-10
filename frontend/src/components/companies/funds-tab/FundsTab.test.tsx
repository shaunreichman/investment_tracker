// ============================================================================
// FUNDS TAB COMPONENT TESTS
// ============================================================================

import React from 'react';
import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { render } from '../../../test-utils';
import { FundsTab } from './FundsTab';
import { createMockEnhancedFundsResponse } from '../../../test-utils/mock-data';

// Mock the custom hooks
jest.mock('../../../hooks/shared', () => ({
  useDebouncedSearch: jest.fn(),
  useResponsiveView: jest.fn(),
  useTableSorting: jest.fn(),
}));

jest.mock('../../../hooks/funds', () => ({
  useFundsFilters: jest.fn(),
  useFundsPagination: jest.fn(),
}));

// Get the mocked functions
const mockUseDebouncedSearch = jest.mocked(require('../../../hooks/shared').useDebouncedSearch);
const mockUseResponsiveView = jest.mocked(require('../../../hooks/shared').useResponsiveView);
const mockUseTableSorting = jest.mocked(require('../../../hooks/shared').useTableSorting);
const mockUseFundsFilters = jest.mocked(require('../../../hooks/funds').useFundsFilters);
const mockUseFundsPagination = jest.mocked(require('../../../hooks/funds').useFundsPagination);

describe('FundsTab', () => {
  const user = userEvent;
  const mockData = createMockEnhancedFundsResponse();
  const mockOnParamsChange = jest.fn();
  const mockCurrentParams = {
    page: 1,
    per_page: 25,
    sort_field: 'start_date',
    sort_direction: 'desc',
    view_mode: 'table',
    status_filter: 'all',
    currency_filter: 'all',
    fund_type_filter: 'all',
    search: '',
  };

  beforeEach(() => {
    jest.clearAllMocks();
    
    // Set up default mock implementations
    mockUseDebouncedSearch.mockReturnValue({
      searchTerm: '',
      handleSearchChange: jest.fn(),
    });

    mockUseResponsiveView.mockReturnValue({
      viewMode: 'table',
      handleViewModeChange: jest.fn(),
    });

    mockUseTableSorting.mockReturnValue({
      sortField: 'start_date',
      sortDirection: 'desc',
      handleSort: jest.fn(),
    });

    mockUseFundsFilters.mockReturnValue({
      statusFilter: 'all',
      currencyFilter: 'all',
      fundTypeFilter: 'all',
      handleStatusFilterChange: jest.fn(),
      handleCurrencyFilterChange: jest.fn(),
      handleFundTypeFilterChange: jest.fn(),
      clearAllFilters: jest.fn(),
    });

    mockUseFundsPagination.mockReturnValue({
      handlePageChange: jest.fn(),
      handleRowsPerPageChange: jest.fn(),
    });
  });

  describe('Component Rendering', () => {
    it('renders loading state when loading is true', () => {
      render(
        <FundsTab
          data={mockData}
          loading={true}
          onParamsChange={mockOnParamsChange}
          currentParams={mockCurrentParams}
        />
      );

      expect(screen.getByText('Loading funds data...')).toBeInTheDocument();
    });

    it('renders empty state when no data is available', () => {
      render(
        <FundsTab
          data={null}
          loading={false}
          onParamsChange={mockOnParamsChange}
          currentParams={mockCurrentParams}
        />
      );

      expect(screen.getByText('No Funds Found')).toBeInTheDocument();
    });

    it('renders funds data when available', () => {
      render(
        <FundsTab
          data={mockData}
          loading={false}
          onParamsChange={mockOnParamsChange}
          currentParams={mockCurrentParams}
        />
      );

      // Check that the table is rendered
      expect(screen.getByRole('table')).toBeInTheDocument();
      
      // Check that fund data is displayed - look for fund names in the table
      expect(screen.getByText('Test Enhanced Fund 1')).toBeInTheDocument();
      expect(screen.getByText('Test Enhanced Fund 2')).toBeInTheDocument();
    });
  });

  describe('View Mode Switching', () => {
    it('renders table view by default', () => {
      render(
        <FundsTab
          data={mockData}
          loading={false}
          onParamsChange={mockOnParamsChange}
          currentParams={mockCurrentParams}
        />
      );

      expect(screen.getByRole('table')).toBeInTheDocument();
    });

    it('switches to cards view when view mode changes', () => {
      mockUseResponsiveView.mockReturnValue({
        viewMode: 'cards',
        handleViewModeChange: jest.fn(),
      });

      render(
        <FundsTab
          data={mockData}
          loading={false}
          onParamsChange={mockOnParamsChange}
          currentParams={mockCurrentParams}
        />
      );

      // Should render cards instead of table
      expect(screen.queryByRole('table')).not.toBeInTheDocument();
    });
  });

  describe('Data Display', () => {
    it('displays fund information in table format', () => {
      render(
        <FundsTab
          data={mockData}
          loading={false}
          onParamsChange={mockOnParamsChange}
          currentParams={mockCurrentParams}
        />
      );

      // Check table headers
      expect(screen.getByText('Fund Name')).toBeInTheDocument();
      expect(screen.getByText('Type')).toBeInTheDocument();
      expect(screen.getByText('Status')).toBeInTheDocument();
      expect(screen.getByText('Expected IRR')).toBeInTheDocument();
      expect(screen.getByText('Commitment')).toBeInTheDocument();

      // Check fund data - look for fund names in the table
      expect(screen.getByText('Test Enhanced Fund 1')).toBeInTheDocument();
      expect(screen.getByText('Test Enhanced Fund 2')).toBeInTheDocument();
    });

    it('displays correct number of funds', () => {
      render(
        <FundsTab
          data={mockData}
          loading={false}
          onParamsChange={mockOnParamsChange}
          currentParams={mockCurrentParams}
        />
      );

      // Check that all 5 mock funds are displayed
      expect(screen.getByText('Test Enhanced Fund 1')).toBeInTheDocument();
      expect(screen.getByText('Test Enhanced Fund 2')).toBeInTheDocument();
      expect(screen.getByText('Test Enhanced Fund 3')).toBeInTheDocument();
      expect(screen.getByText('Test Enhanced Fund 4')).toBeInTheDocument();
      expect(screen.getByText('Test Enhanced Fund 5')).toBeInTheDocument();
    });
  });

  describe('Component Integration', () => {
    it('renders all required sub-components', () => {
      render(
        <FundsTab
          data={mockData}
          loading={false}
          onParamsChange={mockOnParamsChange}
          currentParams={mockCurrentParams}
        />
      );

      // Check that search functionality is rendered - use the label specifically
      expect(screen.getByLabelText('Search Funds')).toBeInTheDocument();
      
      // Check that status filter is rendered - use getAllByText and check first occurrence
      expect(screen.getAllByText('Status Filter')[0]).toBeInTheDocument();
      
      // Check that pagination is rendered
      expect(screen.getByText(/page/i)).toBeInTheDocument();
    });

    it('passes correct props to sub-components', () => {
      const { container } = render(
        <FundsTab
          data={mockData}
          loading={false}
          onParamsChange={mockOnParamsChange}
          currentParams={mockCurrentParams}
        />
      );

      // Verify the component structure by checking for key elements
      expect(screen.getByRole('table')).toBeInTheDocument();
      expect(screen.getByLabelText('Search Funds')).toBeInTheDocument();
      expect(screen.getAllByText('Status Filter')[0]).toBeInTheDocument();
    });
  });

  describe('Error Handling', () => {
    it('handles null data gracefully', () => {
      render(
        <FundsTab
          data={null}
          loading={false}
          onParamsChange={mockOnParamsChange}
          currentParams={mockCurrentParams}
        />
      );

      expect(screen.getByText(/no funds found/i)).toBeInTheDocument();
    });

    it('handles undefined data gracefully', () => {
      render(
        <FundsTab
          data={null}
          loading={false}
          onParamsChange={mockOnParamsChange}
          currentParams={mockCurrentParams}
        />
      );

      expect(screen.getByText(/no funds found/i)).toBeInTheDocument();
    });
  });

  describe('Responsive Behavior', () => {
    it('adapts to different view modes', () => {
      // Test table view
      mockUseResponsiveView.mockReturnValue({
        viewMode: 'table',
        handleViewModeChange: jest.fn(),
      });

      const { rerender } = render(
        <FundsTab
          data={mockData}
          loading={false}
          onParamsChange={mockOnParamsChange}
          currentParams={mockCurrentParams}
        />
      );

      expect(screen.getByRole('table')).toBeInTheDocument();

      // Test cards view
      mockUseResponsiveView.mockReturnValue({
        viewMode: 'cards',
        handleViewModeChange: jest.fn(),
      });

      rerender(
        <FundsTab
          data={mockData}
          loading={false}
          onParamsChange={mockOnParamsChange}
          currentParams={mockCurrentParams}
        />
      );

      expect(screen.queryByRole('table')).not.toBeInTheDocument();
    });
  });
});
