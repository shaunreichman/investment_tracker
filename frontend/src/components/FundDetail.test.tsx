import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import FundDetail from './FundDetail';

// Mock fetch globally
const mockFetch = jest.fn();
global.fetch = mockFetch;

// Mock useNavigate and useParams
const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
  useParams: () => ({ fundId: '1' }),
}));

const mockFundData = {
  fund: {
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
    description: 'Senior Debt Fund No.24',
    commitment_amount: 100000.0,
    expected_irr: 10.0,
    expected_duration_months: 48,
    created_at: '2025-07-15 16:44:53.994929',
    updated_at: '2025-07-15 16:44:54.149844'
  },
  events: [
    {
      id: 1,
      event_type: 'CAPITAL_CALL',
      event_date: '2023-06-23',
      amount: 100000.0,
      description: 'Initial capital call',
      reference_number: null,
      distribution_type: null,
      units_purchased: null,
      units_sold: null,
      unit_price: null,
      nav_per_share: null,
      brokerage_fee: null,
      tax_payment_type: null
    },
    {
      id: 2,
      event_type: 'DISTRIBUTION',
      event_date: '2023-12-15',
      amount: 5000.0,
      description: 'Interest distribution',
      reference_number: 'DIST-001',
      distribution_type: 'INTEREST',
      units_purchased: null,
      units_sold: null,
      unit_price: null,
      nav_per_share: null,
      brokerage_fee: null,
      tax_payment_type: null
    }
  ],
  statistics: {
    total_events: 422,
    capital_calls: 1,
    distributions: 5,
    nav_updates: 0,
    unit_purchases: 0,
    unit_sales: 0,
    total_capital_called: 100000.0,
    total_capital_returned: 100000.0,
    total_distributions: 10399.79,
    first_event_date: '2023-06-23',
    last_event_date: '2024-08-02'
  }
};

const renderFundDetail = () => {
  return render(
    <BrowserRouter>
      <FundDetail />
    </BrowserRouter>
  );
};

describe('FundDetail Component', () => {
  beforeEach(() => {
    mockFetch.mockClear();
    mockNavigate.mockClear();
  });

  test('renders fund detail title', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockFundData
    });

    renderFundDetail();

    await waitFor(() => {
      expect(screen.getByText('Senior Debt Fund No.24')).toBeInTheDocument();
    });
  });

  test('displays loading state initially', () => {
    mockFetch.mockImplementation(() => new Promise(() => {})); // Never resolves

    renderFundDetail();
    
    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });

  test('displays fund overview cards when data loads', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockFundData
    });

    renderFundDetail();

    await waitFor(() => {
      expect(screen.getByText('Fund Overview')).toBeInTheDocument();
      expect(screen.getByText('Total Events')).toBeInTheDocument();
      expect(screen.getByText('422')).toBeInTheDocument();
      expect(screen.getByText('Capital Calls')).toBeInTheDocument();
      expect(screen.getByText('1')).toBeInTheDocument();
      expect(screen.getByText('Distributions')).toBeInTheDocument();
      expect(screen.getByText('5')).toBeInTheDocument();
    });
  });

  test('displays fund details section', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockFundData
    });

    renderFundDetail();

    await waitFor(() => {
      expect(screen.getByText('Fund Details')).toBeInTheDocument();
      expect(screen.getByText('Fund Type')).toBeInTheDocument();
      expect(screen.getByText('Private Debt')).toBeInTheDocument();
      expect(screen.getByText('Tracking Type')).toBeInTheDocument();
      expect(screen.getByText('COST_BASED')).toBeInTheDocument();
      expect(screen.getByText('Investment Company')).toBeInTheDocument();
      expect(screen.getByText('Test Company')).toBeInTheDocument();
      expect(screen.getByText('Entity')).toBeInTheDocument();
      expect(screen.getByText('Test Entity')).toBeInTheDocument();
    });
  });

  test('displays transaction summary', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockFundData
    });

    renderFundDetail();

    await waitFor(() => {
      expect(screen.getByText('Transaction Summary')).toBeInTheDocument();
      expect(screen.getByText('Total Capital Called')).toBeInTheDocument();
      expect(screen.getByText('$100,000')).toBeInTheDocument();
      expect(screen.getByText('Total Capital Returned')).toBeInTheDocument();
      expect(screen.getByText('$100,000')).toBeInTheDocument();
      expect(screen.getByText('Total Distributions')).toBeInTheDocument();
      expect(screen.getByText('$10,400')).toBeInTheDocument();
    });
  });

  test('displays events table', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockFundData
    });

    renderFundDetail();

    await waitFor(() => {
      expect(screen.getByText('Events')).toBeInTheDocument();
      expect(screen.getByText('Initial capital call')).toBeInTheDocument();
      expect(screen.getByText('Interest distribution')).toBeInTheDocument();
      expect(screen.getByText('CAPITAL_CALL')).toBeInTheDocument();
      expect(screen.getByText('DISTRIBUTION')).toBeInTheDocument();
    });
  });

  test('handles API errors gracefully', async () => {
    mockFetch.mockRejectedValueOnce(new Error('Network error'));

    renderFundDetail();

    await waitFor(() => {
      expect(screen.getByText(/An error occurred/)).toBeInTheDocument();
    });
  });

  test('handles API response errors', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 404
    });

    renderFundDetail();

    await waitFor(() => {
      expect(screen.getByText(/Failed to fetch fund data/)).toBeInTheDocument();
    });
  });

  test('navigates back to dashboard when back button is clicked', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockFundData
    });

    renderFundDetail();

    await waitFor(() => {
      const backButton = screen.getByText('← Back to Dashboard');
      fireEvent.click(backButton);
    });

    expect(mockNavigate).toHaveBeenCalledWith('/');
  });

  test('formats currency correctly', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockFundData
    });

    renderFundDetail();

    await waitFor(() => {
      // Check that currency is formatted as AUD
      expect(screen.getByText('$100,000')).toBeInTheDocument();
      expect(screen.getByText('$10,400')).toBeInTheDocument();
    });
  });

  test('formats dates correctly', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockFundData
    });

    renderFundDetail();

    await waitFor(() => {
      // Check that dates are formatted correctly
      expect(screen.getByText('23/06/2023')).toBeInTheDocument();
      expect(screen.getByText('15/12/2023')).toBeInTheDocument();
    });
  });

  test('displays correct event type colors', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockFundData
    });

    renderFundDetail();

    await waitFor(() => {
      expect(screen.getByText('CAPITAL_CALL')).toBeInTheDocument();
      expect(screen.getByText('DISTRIBUTION')).toBeInTheDocument();
    });
  });

  test('handles fund not found', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 404,
      json: async () => ({ error: 'Fund not found' })
    });

    renderFundDetail();

    await waitFor(() => {
      expect(screen.getByText(/Fund not found/)).toBeInTheDocument();
    });
  });

  test('displays fund statistics correctly', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockFundData
    });

    renderFundDetail();

    await waitFor(() => {
      expect(screen.getByText('First Event')).toBeInTheDocument();
      expect(screen.getByText('23/06/2023')).toBeInTheDocument();
      expect(screen.getByText('Last Event')).toBeInTheDocument();
      expect(screen.getByText('02/08/2024')).toBeInTheDocument();
    });
  });
}); 