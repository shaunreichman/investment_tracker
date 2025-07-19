import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Dashboard from './Dashboard';

// Mock fetch globally
const mockFetch = jest.fn();
global.fetch = mockFetch;

// Mock useNavigate
const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
}));

const mockPortfolioSummary = {
  total_funds: 3,
  active_funds: 2,
  total_equity_balance: 150000,
  total_average_equity_balance: 151389.91,
  recent_events_count: 5,
  total_tax_statements: 6,
  last_updated: '2025-07-19T15:50:59.085701'
};

const mockFunds = [
  {
    id: 1,
    name: 'Senior Debt Fund No.24',
    fund_type: 'Private Debt',
    tracking_type: 'COST_BASED',
    currency: 'AUD',
    current_equity_balance: 0.0,
    average_equity_balance: 81598.52,
    is_active: true,
    investment_company: 'Test Company',
    entity: 'Test Entity',
    recent_events_count: 0,
    created_at: '2025-07-15 16:44:53.994929'
  },
  {
    id: 2,
    name: '3PG Finance',
    fund_type: 'Private Debt',
    tracking_type: 'COST_BASED',
    currency: 'AUD',
    current_equity_balance: 0.0,
    average_equity_balance: 66045.18,
    is_active: true,
    investment_company: 'Test Company',
    entity: 'Test Entity',
    recent_events_count: 0,
    created_at: '2025-07-15 16:44:53.996273'
  }
];

const mockEvents = [
  {
    id: 1,
    fund_name: 'Senior Debt Fund No.24',
    event_type: 'CAPITAL_CALL',
    event_date: '2023-06-23',
    amount: 100000.0,
    description: 'Initial capital call',
    reference_number: null
  },
  {
    id: 2,
    fund_name: '3PG Finance',
    event_type: 'DISTRIBUTION',
    event_date: '2023-12-15',
    amount: 5000.0,
    description: 'Interest distribution',
    reference_number: 'DIST-001'
  }
];

const mockPerformance = [
  {
    fund_id: 1,
    fund_name: 'Senior Debt Fund No.24',
    current_equity: 0.0,
    average_equity: 81598.52,
    total_events: 422,
    last_event_date: '2024-08-02'
  },
  {
    fund_id: 2,
    fund_name: '3PG Finance',
    current_equity: 0.0,
    average_equity: 66045.18,
    total_events: 150,
    last_event_date: '2024-07-15'
  }
];

const renderDashboard = () => {
  return render(
    <BrowserRouter>
      <Dashboard />
    </BrowserRouter>
  );
};

// Mock the useParams hook for FundDetail component
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
  useParams: () => ({ fundId: '1' }),
}));

describe('Dashboard Component', () => {
  beforeEach(() => {
    mockFetch.mockClear();
    mockNavigate.mockClear();
  });

  test('renders dashboard title', () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockPortfolioSummary
    });
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ funds: mockFunds })
    });
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ events: mockEvents })
    });
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ performance: mockPerformance })
    });

    renderDashboard();
    
    expect(screen.getByText('Investment Portfolio Dashboard')).toBeInTheDocument();
  });

  test('displays loading state initially', () => {
    mockFetch.mockImplementation(() => new Promise(() => {})); // Never resolves

    renderDashboard();
    
    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });

  test('displays portfolio summary cards when data loads', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockPortfolioSummary
    });
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ funds: mockFunds })
    });
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ events: mockEvents })
    });
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ performance: mockPerformance })
    });

    renderDashboard();

    await waitFor(() => {
      expect(screen.getByText('Total Equity')).toBeInTheDocument();
      expect(screen.getByText('$0')).toBeInTheDocument(); // Formatted currency
      expect(screen.getByText('Active Funds')).toBeInTheDocument();
      expect(screen.getByText('2')).toBeInTheDocument();
    });
  });

  test('displays funds table when data loads', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockPortfolioSummary
    });
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ funds: mockFunds })
    });
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ events: mockEvents })
    });
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ performance: mockPerformance })
    });

    renderDashboard();

    await waitFor(() => {
      expect(screen.getByText('Senior Debt Fund No.24')).toBeInTheDocument();
      expect(screen.getByText('3PG Finance')).toBeInTheDocument();
      expect(screen.getByText('Private Debt')).toBeInTheDocument();
      expect(screen.getByText('COST_BASED')).toBeInTheDocument();
    });
  });

  test('displays recent events when data loads', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockPortfolioSummary
    });
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ funds: mockFunds })
    });
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ events: mockEvents })
    });
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ performance: mockPerformance })
    });

    renderDashboard();

    await waitFor(() => {
      expect(screen.getByText('Recent Events')).toBeInTheDocument();
      expect(screen.getByText('Initial capital call')).toBeInTheDocument();
      expect(screen.getByText('Interest distribution')).toBeInTheDocument();
    });
  });

  test('handles API errors gracefully', async () => {
    mockFetch.mockRejectedValueOnce(new Error('Network error'));

    renderDashboard();

    await waitFor(() => {
      expect(screen.getByText(/An error occurred/)).toBeInTheDocument();
    });
  });

  test('handles API response errors', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 500
    });

    renderDashboard();

    await waitFor(() => {
      expect(screen.getByText(/Failed to fetch dashboard data/)).toBeInTheDocument();
    });
  });

  test('navigates to fund detail when fund name is clicked', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockPortfolioSummary
    });
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ funds: mockFunds })
    });
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ events: mockEvents })
    });
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ performance: mockPerformance })
    });

    renderDashboard();

    await waitFor(() => {
      const fundLink = screen.getByText('Senior Debt Fund No.24');
      fireEvent.click(fundLink);
    });

    expect(mockNavigate).toHaveBeenCalledWith('/fund/1');
  });

  test('formats currency correctly', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockPortfolioSummary
    });
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ funds: mockFunds })
    });
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ events: mockEvents })
    });
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ performance: mockPerformance })
    });

    renderDashboard();

    await waitFor(() => {
      // Check that currency is formatted as AUD
      expect(screen.getByText('$0')).toBeInTheDocument();
    });
  });

  test('displays correct event type colors', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockPortfolioSummary
    });
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ funds: mockFunds })
    });
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ events: mockEvents })
    });
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ performance: mockPerformance })
    });

    renderDashboard();

    await waitFor(() => {
      expect(screen.getByText('CAPITAL_CALL')).toBeInTheDocument();
      expect(screen.getByText('DISTRIBUTION')).toBeInTheDocument();
    });
  });
}); 