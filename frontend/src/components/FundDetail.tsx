import React, { useState } from 'react';
import {
  Typography,
  Paper,
  Box,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Button,
  CircularProgress,
  Switch,
  Breadcrumbs,
  Link,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  DialogContentText,
  Tooltip as MuiTooltip
} from '@mui/material';
import { ErrorDisplay } from './ErrorDisplay';
import { TrendingUp, AccountBalance, Edit as EditIcon, Delete as DeleteIcon, Assessment, Info, Receipt, ChevronLeft, ChevronRight } from '@mui/icons-material';
import { useParams, useNavigate } from 'react-router-dom';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Scatter } from 'recharts';
import CreateFundEventModal from './CreateFundEventModal';
import EditFundEventModal from './EditFundEventModal';
import { 
  ExtendedFundEvent,
  ExtendedFund
} from '../types/api';
import { useFundDetail, useDeleteFundEvent } from '../hooks/useFunds';

// ============================================================================
// SECTION COMPONENTS FOR FUND DETAIL REDESIGN
// ============================================================================

interface SectionProps {
  fund: ExtendedFund;
  formatCurrency: (amount: number | null, currency?: string) => string;
  formatDate: (dateString: string | null) => string;
  events?: ExtendedFundEvent[];
}

/**
 * Equity Section - Current investment position and value
 */
const EquitySection: React.FC<SectionProps> = ({ fund, formatCurrency, formatDate }) => {
  // Phase 3.2: Enhanced data organization for equity metrics
  const equityMetrics = [
    {
      label: 'Current Balance',
      value: fund.current_equity_balance ?? null,
      color: 'primary.main',
      icon: '💰',
      priority: 1
    },
    {
      label: 'Average Balance',
      value: fund.average_equity_balance ?? null,
      color: 'primary.main',
      icon: '📊',
      priority: 2
    },
    {
      label: 'Commitment',
      value: fund.commitment_amount ?? null,
      color: 'info.main',
      icon: '📋',
      priority: 3
    },
    ...(fund.tracking_type === 'nav_based' ? [{
      label: 'NAV Fund Value',
      value: fund.current_nav_fund_value ?? null,
      color: 'success.main',
      icon: '📈',
      priority: 4
    }] : [])
  ].filter(metric => metric.value !== null);

  return (
    <Paper sx={{ 
      p: 0.75, 
      mb: 1, 
      borderRadius: 2,
      // Phase 4: Enhanced visual effects
      boxShadow: '0 2px 8px rgba(0,0,0,0.08), 0 1px 3px rgba(0,0,0,0.12)',
      transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
      '&:hover': {
        boxShadow: '0 4px 16px rgba(0,0,0,0.12), 0 2px 6px rgba(0,0,0,0.16)',
        transform: 'translateY(-1px)'
      }
    }}>
      <Box display="flex" alignItems="center" mb={0.5}>
        <AccountBalance color="primary" sx={{ mr: 0.5, fontSize: 16 }} />
        <Typography variant="h6" sx={{ fontSize: 16 }}>Equity Position</Typography>
      </Box>
      
      {/* Phase 3B: Enhanced card layout with consistent styling */}
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
        {equityMetrics.map((metric, index) => (
          <Box 
            key={index}
            sx={{ 
              display: 'flex', 
              justifyContent: 'space-between', 
              alignItems: 'center',
              p: 0.5,
              borderRadius: 1,
              backgroundColor: index === 0 ? 'primary.50' : 'transparent',
              border: '1px solid',
              borderColor: 'grey.200',
              // Phase 4: Enhanced hover effects for individual items
              transition: 'all 0.2s ease-in-out',
              '&:hover': {
                backgroundColor: index === 0 ? 'primary.100' : 'grey.50',
                borderColor: 'grey.300',
                transform: 'translateX(2px)'
              }
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
              <span style={{ fontSize: '12px' }}>{metric.icon}</span>
              <Typography variant="body2" color="text.secondary" sx={{ fontSize: 11 }}>
                {metric.label}
          </Typography>
        </Box>
            <Typography 
              variant="body2" 
              sx={{ 
                color: metric.color,
                fontSize: 12,
                fontWeight: index === 0 ? 700 : 600
              }}
            >
              {formatCurrency(metric.value, fund.currency)}
          </Typography>
        </Box>
        ))}
      </Box>
    </Paper>
  );
};

/**
 * Expected Performance Section - Planned/expected fund metrics
 */
const ExpectedPerformanceSection: React.FC<SectionProps> = ({ fund, formatCurrency, formatDate }) => {
  // Phase 3.3: Enhanced data organization for performance metrics
  const performanceMetrics = [
    {
      label: 'Expected IRR',
      value: fund.expected_irr,
      unit: '%',
      color: 'success.main',
      icon: '📈',
      priority: 1
    },
    {
      label: 'Expected Duration',
      value: fund.expected_duration_months,
      unit: ' months',
      color: 'success.main',
      icon: '⏱️',
      priority: 2
    }
  ].filter(metric => metric.value !== null && metric.value !== undefined);

  // Only show if metrics exist
  if (performanceMetrics.length === 0) {
    return null;
  }

  return (
    <Paper sx={{ 
      p: 0.75, 
      mb: 1, 
      borderRadius: 2,
      // Phase 4: Enhanced visual effects
      boxShadow: '0 2px 8px rgba(0,0,0,0.08), 0 1px 3px rgba(0,0,0,0.12)',
      transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
      '&:hover': {
        boxShadow: '0 4px 16px rgba(0,0,0,0.12), 0 2px 6px rgba(0,0,0,0.16)',
        transform: 'translateY(-1px)'
      }
    }}>
      <Box display="flex" alignItems="center" mb={0.5}>
        <TrendingUp color="success" sx={{ mr: 0.5, fontSize: 16 }} />
        <Typography variant="h6" sx={{ fontSize: 16 }}>Expected Performance</Typography>
      </Box>
      
      {/* Phase 3.3: Enhanced card layout with better density */}
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
        {performanceMetrics.map((metric, index) => (
          <Box 
            key={index}
            sx={{ 
              display: 'flex', 
              justifyContent: 'space-between', 
              alignItems: 'center',
              p: 0.5,
              borderRadius: 1,
              backgroundColor: 'success.50',
              border: '1px solid',
              borderColor: 'grey.200',
              // Phase 4: Enhanced hover effects for individual items
              transition: 'all 0.2s ease-in-out',
              '&:hover': {
                backgroundColor: 'success.100',
                borderColor: 'grey.300',
                transform: 'translateX(2px)'
              }
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
              <span style={{ fontSize: '12px' }}>{metric.icon}</span>
              <Typography variant="body2" color="text.secondary" sx={{ fontSize: 11 }}>
                {metric.label}
            </Typography>
          </Box>
            <Typography 
              variant="body2" 
              sx={{ 
                color: metric.color,
                fontSize: 12,
                fontWeight: 600
              }}
            >
              {metric.value}{metric.unit}
            </Typography>
          </Box>
        ))}
      </Box>
    </Paper>
  );
};

/**
 * Completed Performance Section - Historical performance for finished funds
 */
const CompletedPerformanceSection: React.FC<SectionProps> = ({ fund, formatCurrency, formatDate }) => {
  // Only show if fund is completed (not active)
  if (fund.status === 'active') {
    return null;
  }

  // Phase 3B: Enhanced data organization for completed performance
  const performanceMetrics = [
    {
      label: 'IRR',
      value: fund.completed_irr,
      unit: '%',
      color: 'info.main',
      icon: '📊',
      priority: 1
    },
    {
      label: 'Net-tax IRR',
      value: fund.completed_after_tax_irr,
      unit: '%',
      color: 'info.main',
      icon: '💰',
      priority: 2
    },
    {
      label: 'Gross IRR',
      value: fund.completed_real_irr,
      unit: '%',
      color: 'info.main',
      icon: '📈',
      priority: 3
    }
  ].filter(metric => metric.value !== null && metric.value !== undefined);

  if (performanceMetrics.length === 0) {
    return null;
  }

  return (
    <Paper sx={{ 
      p: 0.75, 
      mb: 1, 
      borderRadius: 2,
      // Phase 4: Enhanced visual effects
      boxShadow: '0 2px 8px rgba(0,0,0,0.08), 0 1px 3px rgba(0,0,0,0.12)',
      transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
      '&:hover': {
        boxShadow: '0 4px 16px rgba(0,0,0,0.12), 0 2px 6px rgba(0,0,0,0.16)',
        transform: 'translateY(-1px)'
      }
    }}>
      <Box display="flex" alignItems="center" mb={0.5}>
        <Assessment color="info" sx={{ mr: 0.5, fontSize: 16 }} />
        <Typography variant="h6" sx={{ fontSize: 16 }}>Completed Performance</Typography>
      </Box>
      
      {/* Phase 3B: Enhanced card layout with consistent styling */}
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
        {performanceMetrics.map((metric, index) => (
          <Box 
            key={index}
            sx={{ 
              display: 'flex', 
              justifyContent: 'space-between', 
              alignItems: 'center',
              p: 0.5,
              borderRadius: 1,
              backgroundColor: 'info.50',
              border: '1px solid',
              borderColor: 'grey.200',
              // Phase 4: Enhanced hover effects for individual items
              transition: 'all 0.2s ease-in-out',
              '&:hover': {
                backgroundColor: 'info.100',
                borderColor: 'grey.300',
                transform: 'translateX(2px)'
              }
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
              <span style={{ fontSize: '12px' }}>{metric.icon}</span>
              <Typography variant="body2" color="text.secondary" sx={{ fontSize: 11 }}>
                {metric.label}
            </Typography>
          </Box>
            <Typography 
              variant="body2" 
              sx={{ 
                color: metric.color,
                fontSize: 12,
                fontWeight: 600
              }}
            >
              {metric.value ? (metric.value * 100).toFixed(2) : '0.00'}{metric.unit}
            </Typography>
          </Box>
        ))}
      </Box>
    </Paper>
  );
};

/**
 * Fund Details Section - Basic fund information
 */
const FundDetailsSection: React.FC<SectionProps> = ({ fund, formatCurrency, formatDate }) => {
  // Helper function to get status display info
  const getStatusInfo = (status: string) => {
    switch (status) {
      case 'active':
        return { 
          value: 'Active', 
          color: '#4caf50', // Lighter green
          icon: '📊',
          tooltip: 'Fund is still invested and has capital at risk'
        };
      case 'realized':
        return { 
          value: 'Realized', 
          color: '#424242', // Dark gray
          icon: '📊',
          tooltip: 'All capital has been returned. Fund will be completed once the final tax statement is added.'
        };
      case 'completed':
        return { 
          value: 'Completed', 
          color: '#000000', // Black
          icon: '📊',
          tooltip: 'Fund is fully realized and all tax obligations are complete'
        };
      default:
        return { 
          value: 'Unknown', 
          color: 'text.secondary', 
          icon: '📊',
          tooltip: 'Unknown fund status'
        };
    }
  };

  const statusInfo = getStatusInfo(fund.status);
  
  const fundDetails = [
    { label: 'Status', value: statusInfo.value, color: statusInfo.color, icon: statusInfo.icon, priority: 1, isStatus: true },
    { label: 'Currency', value: fund.currency, color: 'text.primary', icon: '💱', priority: 2 },
    ...(fund.actual_duration_months ? [{ label: 'Actual Duration', value: `${fund.actual_duration_months} months`, color: 'text.primary', icon: '⏱️', priority: 3 }] : [])
  ];

  return (
    <Paper sx={{ 
      p: 0.75, 
      mb: 1, 
      borderRadius: 2,
      // Phase 4: Enhanced visual effects
      boxShadow: '0 2px 8px rgba(0,0,0,0.08), 0 1px 3px rgba(0,0,0,0.12)',
      transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
      '&:hover': {
        boxShadow: '0 4px 16px rgba(0,0,0,0.12), 0 2px 6px rgba(0,0,0,0.16)',
        transform: 'translateY(-1px)'
      }
    }}>
      <Box display="flex" alignItems="center" mb={0.5}>
        <Info color="primary" sx={{ mr: 0.5, fontSize: 16 }} />
        <Typography variant="h6" sx={{ fontSize: 16 }}>Fund Details</Typography>
      </Box>
      
      {/* Phase 3B: Enhanced card layout with consistent styling */}
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
        {fundDetails.map((detail, index) => (
          <Box 
            key={index}
              sx={{
              display: 'flex', 
              justifyContent: 'space-between', 
              alignItems: 'center',
              p: 0.5,
              borderRadius: 1,
              backgroundColor: detail.priority === 1 ? 'success.50' : 'transparent',
              border: '1px solid',
              borderColor: 'grey.200',
              // Phase 4: Enhanced hover effects for individual items
              transition: 'all 0.2s ease-in-out',
              '&:hover': {
                backgroundColor: detail.priority === 1 ? 'success.100' : 'grey.50',
                borderColor: 'grey.300',
                transform: 'translateX(2px)'
              }
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
              <span style={{ fontSize: '12px' }}>{detail.icon}</span>
              <Typography variant="body2" color="text.secondary" sx={{ fontSize: 11 }}>
                {detail.label}
              </Typography>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
              {detail.isStatus && (
                <MuiTooltip title={statusInfo.tooltip} arrow>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, cursor: 'help' }}>
                    <Box sx={{ 
                    width: 8,
                    height: 8,
                    borderRadius: '50%',
                    bgcolor: statusInfo.color,
                      // Phase 4: Enhanced status indicator
                      transition: 'all 0.2s ease-in-out',
                      boxShadow: statusInfo.color === 'success.main' ? '0 0 4px rgba(76, 175, 80, 0.4)' : 'none'
                    }} />
                    <Typography variant="body2" sx={{ color: detail.color, fontSize: 12, fontWeight: detail.priority === 1 ? 600 : 500 }}>
                      {detail.value}
                    </Typography>
                  </Box>
                </MuiTooltip>
              )}
              {!detail.isStatus && (
                <Typography variant="body2" sx={{ color: detail.color, fontSize: 12, fontWeight: detail.priority === 1 ? 600 : 500 }}>
                  {detail.value}
                </Typography>
              )}
            </Box>
        </Box>
        ))}
      </Box>
    </Paper>
  );
};

/**
 * Transaction Summary Section - Summary of all transaction types
 */
const TransactionSummarySection: React.FC<SectionProps> = ({ fund, formatCurrency, formatDate }) => {
  const transactionData = [
    // Capital transactions (cost-based funds)
    ...(fund.tracking_type === 'cost_based' ? [
      { type: 'Capital Calls', amount: fund.total_capital_calls ?? null, color: 'error.main', icon: '📤' },
      { type: 'Returns of Capital', amount: fund.total_capital_returns ?? null, color: 'success.main', icon: '📥' }
    ] : []),
    // Unit transactions (NAV-based funds)
    ...(fund.tracking_type === 'nav_based' ? [
      { type: 'Unit Purchases', amount: fund.total_unit_purchases ?? null, color: 'primary.main', icon: '📈' },
      { type: 'Unit Sales', amount: fund.total_unit_sales ?? null, color: 'secondary.main', icon: '📉' }
    ] : []),
    // Income transactions (all funds)
    { type: 'Distributions', amount: fund.total_distributions ?? null, color: 'info.main', icon: '💰' },
    { type: 'Tax Payments', amount: fund.total_tax_payments ?? null, color: 'warning.main', icon: '🏛️' },
    { type: 'Total Cost of Capital Interest', amount: fund.total_daily_interest_charges ?? null, color: 'info.main', icon: '📊' }
  ].filter(item => item.amount !== null);

  return (
    <Paper sx={{ 
      p: 0.75, 
      mb: 1, 
      borderRadius: 2,
      // Phase 4: Enhanced visual effects
      boxShadow: '0 2px 8px rgba(0,0,0,0.08), 0 1px 3px rgba(0,0,0,0.12)',
      transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
      '&:hover': {
        boxShadow: '0 4px 16px rgba(0,0,0,0.12), 0 2px 6px rgba(0,0,0,0.16)',
        transform: 'translateY(-1px)'
      }
    }}>
      <Box display="flex" alignItems="center" mb={0.5}>
        <Receipt color="secondary" sx={{ mr: 0.5, fontSize: 16 }} />
        <Typography variant="h6" sx={{ fontSize: 16 }}>Transaction Summary</Typography>
      </Box>
      
      {/* Phase 3B: Enhanced card layout with consistent styling */}
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
        {transactionData.map((item, index) => (
          <Box 
            key={index}
            sx={{ 
              display: 'flex', 
              justifyContent: 'space-between', 
              alignItems: 'center',
              p: 0.5,
              borderRadius: 1,
              backgroundColor: 'transparent',
              border: '1px solid',
              borderColor: 'grey.200',
              // Phase 4: Enhanced hover effects for individual items
              transition: 'all 0.2s ease-in-out',
              '&:hover': {
                backgroundColor: 'grey.50',
                borderColor: 'grey.300',
                transform: 'translateX(2px)'
              }
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
              <span style={{ fontSize: '12px' }}>{item.icon}</span>
              <Typography variant="body2" color="text.secondary" sx={{ fontSize: 11 }}>
                {item.type}
            </Typography>
          </Box>
            <Typography variant="body2" sx={{ color: item.color, fontSize: 12, fontWeight: 600 }}>
              {formatCurrency(item.amount, fund.currency)}
            </Typography>
          </Box>
        ))}
          </Box>
    </Paper>
  );
};

/**
 * Unit Price Chart Section - NAV performance chart for NAV-based funds
 */
const UnitPriceChartSection: React.FC<SectionProps> = ({ fund, formatCurrency, formatDate, events }) => {
  // Only show for NAV-based funds
  if (fund.tracking_type !== 'nav_based') {
    return null;
  }

  return (
    <Paper sx={{ 
      p: 0.75, 
      mb: 1, 
      borderRadius: 2,
      // Phase 4: Enhanced visual effects
      boxShadow: '0 2px 8px rgba(0,0,0,0.08), 0 1px 3px rgba(0,0,0,0.12)',
      transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
      '&:hover': {
        boxShadow: '0 4px 16px rgba(0,0,0,0.12), 0 2px 6px rgba(0,0,0,0.16)',
        transform: 'translateY(-1px)'
      }
    }}>
      <Box display="flex" alignItems="center" mb={0.5}>
        <TrendingUp color="primary" sx={{ mr: 0.5, fontSize: 16 }} />
        <Typography variant="h6" sx={{ fontSize: 16 }}>Unit Price Performance</Typography>
          </Box>
      
      <Box sx={{ height: 200, position: 'relative' }}>
        {(() => {
          try {
            // Use events passed as prop, fallback to empty array
            const chartEvents = events || [];
            
            // Prepare NAV data - separate for continuous line
            const navData = chartEvents
              .filter((event: any) => event.event_type === 'NAV_UPDATE' && event.nav_per_share)
              .map((event: any) => ({
                date: new Date(event.event_date).getTime(),
                displayDate: new Date(event.event_date).toLocaleDateString('en-AU', {
                  day: '2-digit',
                  month: 'short',
                  year: 'numeric'
                }),
                nav: event.nav_per_share,
                timestamp: new Date(event.event_date).getTime()
              }))
              .sort((a: any, b: any) => a.timestamp - b.timestamp);

            // Prepare purchase/sale data - separate for markers
            const purchaseData = chartEvents
              .filter((event: any) => (event.event_type === 'UNIT_PURCHASE' || event.description?.includes('purchase')) && event.amount && event.units_purchased)
              .map((event: any) => ({
                date: new Date(event.event_date).getTime(),
                displayDate: new Date(event.event_date).toLocaleDateString('en-AU', {
                  day: '2-digit',
                  month: 'short',
                  year: 'numeric'
                }),
                purchase: (event.amount || 0) / (event.units_purchased || 1),
                timestamp: new Date(event.event_date).getTime(),
                type: 'Purchase',
                units: event.units_purchased || 0,
                amount: event.amount || 0,
                description: event.description
              }));

            const saleData = chartEvents
              .filter((event: any) => (event.event_type === 'UNIT_SALE' || event.description?.includes('sale')) && event.amount && event.units_sold)
              .map((event: any) => ({
                date: new Date(event.event_date).getTime(),
                displayDate: new Date(event.event_date).toLocaleDateString('en-AU', {
                  day: '2-digit',
                  month: 'short',
                  year: 'numeric'
                }),
                sale: (event.amount || 0) / (event.units_sold || 1),
                timestamp: new Date(event.event_date).getTime(),
                type: 'Sale',
                units: event.units_sold || 0,
                amount: event.amount || 0,
                description: event.description
              }));

            // Calculate shared domain from ALL data
            const allValues = [
              ...navData.map((d: any) => d.nav),
              ...purchaseData.map((d: any) => d.purchase),
              ...saleData.map((d: any) => d.sale)
            ].filter((v): v is number => v !== null && v !== undefined);

            const allDates = [
              ...navData.map((d: any) => d.timestamp),
              ...purchaseData.map((d: any) => d.timestamp),
              ...saleData.map((d: any) => d.timestamp)
            ];

            if (allValues.length === 0) {
              return (
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%' }}>
                  <Typography variant="body2" color="text.secondary">
                    No chart data available
            </Typography>
          </Box>
              );
            }

            const minValue = Math.min(...allValues);
            const maxValue = Math.max(...allValues);
            const padding = (maxValue - minValue) * 0.1;

            const minDate = Math.min(...allDates);
            const maxDate = Math.max(...allDates);
            const datePadding = (maxDate - minDate) * 0.05;

            const yDomain = [minValue - padding, maxValue + padding];
            const xDomain = [minDate - datePadding, maxDate + datePadding];

            return (
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={navData}>
                  <CartesianGrid 
                    strokeDasharray="3 3" 
                    vertical={true}
                    horizontal={true}
                    stroke="#f0f0f0"
                  />
                  <XAxis 
                    dataKey="date" 
                    tick={{ fontSize: 10 }}
                    angle={-45}
                    textAnchor="end"
                    height={60}
                    domain={xDomain}
                    type="number"
                    scale="time"
                    tickFormatter={(value) => new Date(value).toLocaleDateString('en-AU', {
                      day: '2-digit',
                      month: 'short',
                      year: 'numeric'
                    })}
                    ticks={(() => {
                      // Generate ticks at end of each month within the date range
                      const ticks = [];
                      const startDate = new Date(minDate);
                      const endDate = new Date(maxDate);
                      
                      // Start from the first day of the month containing the start date
                      let currentDate = new Date(startDate.getFullYear(), startDate.getMonth(), 1);
                      
                      // Add safety check to prevent infinite loops
                      let iterationCount = 0;
                      const maxIterations = 50; // Safety limit
                      
                      while (currentDate <= endDate && iterationCount < maxIterations) {
                        // Set to last day of current month
                        const lastDayOfMonth = new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 0);
                        ticks.push(lastDayOfMonth.getTime());
                        
                        // Move to first day of next month
                        currentDate.setMonth(currentDate.getMonth() + 1);
                        currentDate.setDate(1);
                        iterationCount++;
                      }
                      
                      return ticks;
                    })()}
                  />
                  <YAxis 
                    tick={{ fontSize: 10 }}
                    tickFormatter={(value) => `$${value.toFixed(2)}`}
                    domain={yDomain}
                  />
                  <Tooltip 
                    formatter={(value, name) => {
                      if (name === 'nav') return [`$${value}`, 'NAV'];
                      if (name === 'purchase') return [`$${value}`, 'Purchase'];
                      if (name === 'sale') return [`$${value}`, 'Sale'];
                      return [value, name];
                    }}
                    labelFormatter={(label) => `Date: ${new Date(label).toLocaleDateString('en-AU', {
                      day: '2-digit',
                      month: 'short',
                      year: 'numeric'
                    })}`}
                  />
                  <Line 
                    type="linear" 
                    dataKey="nav" 
                    stroke="#1976d2" 
                    strokeWidth={2}
                    dot={{ fill: '#1976d2', strokeWidth: 2, r: 3, stroke: '#1976d2' }}
                    activeDot={{ r: 5, fill: '#1976d2', stroke: '#1976d2', strokeWidth: 2 }}
                    connectNulls={false}
                    isAnimationActive={false}
                  />
                  <Scatter 
                    dataKey="purchase" 
                    fill="#4caf50" 
                    stroke="#4caf50"
                    shape="star"
                    data={purchaseData}
                  />
                  <Scatter 
                    dataKey="sale" 
                    fill="#f44336" 
                    stroke="#f44336"
                    shape="star"
                    data={saleData}
                  />
                </LineChart>
              </ResponsiveContainer>
            );
          } catch (error) {
            console.error('Chart error:', error);
            return (
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%' }}>
                <Typography variant="body2" color="error">
                  Error loading chart
            </Typography>
          </Box>
            );
          }
        })()}
      </Box>
    </Paper>
  );
};

// ============================================================================
// MAIN FUND DETAIL COMPONENT
// ============================================================================

const FundDetail: React.FC = () => {
  const { fundId } = useParams<{ fundId: string }>();
  const navigate = useNavigate();
  const [showTaxEvents, setShowTaxEvents] = useState(true);
  const [showNavUpdates, setShowNavUpdates] = useState(true);
  const [eventModalOpen, setEventModalOpen] = useState(false);
  const [editModalOpen, setEditModalOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [selectedEvent, setSelectedEvent] = useState<ExtendedFundEvent | null>(null);
  const [deletingEvent, setDeletingEvent] = useState(false);

  // Phase 2C: Sidebar toggle state with localStorage persistence
  const [sidebarVisible, setSidebarVisible] = useState(() => {
    const saved = localStorage.getItem('fundDetailSidebarVisible');
    return saved !== null ? JSON.parse(saved) : true;
  });

  const toggleSidebar = () => {
    const newState = !sidebarVisible;
    setSidebarVisible(newState);
    localStorage.setItem('fundDetailSidebarVisible', JSON.stringify(newState));
  };

  // Centralized API hooks
  const { data: fundData, loading, error, refetch } = useFundDetail(Number(fundId));
  const deleteFundEvent = useDeleteFundEvent(Number(fundId), selectedEvent?.id || 0);



  const formatCurrency = (amount: number | null, currency: string = 'AUD') => {
    if (amount === null) return '-';
    
    // Excel accounting format: parentheses for negatives, no minus sign
    const absAmount = Math.abs(amount);
    const formatted = new Intl.NumberFormat('en-AU', {
      style: 'currency',
      currency: currency,
    }).format(absAmount);
    
    return amount < 0 ? `(${formatted})` : formatted;
  };

  const formatBrokerageFee = (amount: number | null, currency: string = 'AUD') => {
    if (amount === null) return '-';
    const rounded = Math.round(amount);
    const formatted = new Intl.NumberFormat('en-AU', {
      style: 'currency',
      currency: currency,
    }).format(rounded);
    
    // Remove .00 for whole numbers
    return formatted.replace(/\.00$/, '');
  };

  const formatDate = (dateString: string | null) => {
    if (!dateString) return '-';
    const date = new Date(dateString);
    const day = date.getDate();
    const month = date.toLocaleDateString('en-AU', { month: 'short' });
    const year = date.getFullYear().toString().slice(-2);
    return `${day}-${month}-${year}`;
  };

  const getEventTypeColor = (eventType: string) => {
    switch (eventType) {
      case 'CAPITAL_CALL':
        return 'primary';
      case 'DISTRIBUTION':
        return 'success';
      case 'RETURN_OF_CAPITAL':
        return 'warning';
      case 'NAV_UPDATE':
        return 'info';
      case 'UNIT_PURCHASE':
        return 'primary';
      case 'UNIT_SALE':
        return 'warning';
      case 'TAX_PAYMENT':
        return 'error';
      default:
        return 'default';
    }
  };

  const getEventTypeLabel = (event: ExtendedFundEvent) => {
    // Show only subtype if available, otherwise show the main type
    if (event.distribution_type) {
      // Format distribution type to be consistent (uppercase)
      return event.distribution_type.toUpperCase();
    }
    if (event.tax_payment_type) {
      return event.tax_payment_type;
    }
    
    // For events without subtypes, show the main type
    return event.event_type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  // Add this function to refresh events after event creation
  const handleEventCreated = () => {
    // Re-fetch fund details using centralized hook
    refetch();
  };

  const handleEventUpdated = () => {
    // Re-fetch fund details using centralized hook
    refetch();
  };

  const handleEditEvent = (event: ExtendedFundEvent) => {
    // Check if there's a withholding tax event on the same date
    const sameDateEvents = fundData?.events.filter((e: ExtendedFundEvent) => e.event_date === event.event_date) || [];
    const withholdingEvent = sameDateEvents.find((e: ExtendedFundEvent) => 
      e.event_type === 'TAX_PAYMENT' && e.tax_payment_type === 'NON_RESIDENT_INTEREST_WITHHOLDING'
    );
    
    // Add withholding context to the event
    const eventWithContext = {
      ...event,
      has_withholding_tax: !!withholdingEvent,
      withholding_amount: withholdingEvent?.amount || null,
      withholding_rate: withholdingEvent ? 10 : null, // Default rate
      net_interest: withholdingEvent ? (event.amount || 0) - (withholdingEvent.amount || 0) : null
    };
    
    setSelectedEvent(eventWithContext);
    setEditModalOpen(true);
  };

  const handleDeleteEvent = (event: ExtendedFundEvent) => {
    setSelectedEvent(event);
    setDeleteDialogOpen(true);
  };

  const confirmDeleteEvent = async () => {
    if (!selectedEvent || !fundId) return;

    setDeletingEvent(true);
    try {
      await deleteFundEvent.mutate();
      
      // Refresh the fund data using centralized hook
      refetch();
      setDeleteDialogOpen(false);
      setSelectedEvent(null);
    } catch (err) {
      // Error handling will be done by the centralized hook
      console.error('Failed to delete event:', err);
    } finally {
      setDeletingEvent(false);
    }
  };

  if (loading) {
    return (
      <Box p={3}>
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px" flexDirection="column" gap={2}>
          {/* Phase 4: Enhanced loading state */}
          <CircularProgress 
            size={40} 
            sx={{ 
              color: 'primary.main',
              '& .MuiCircularProgress-circle': {
                strokeLinecap: 'round',
              }
            }} 
          />
          <Typography variant="body2" color="text.secondary" sx={{ opacity: 0.8 }}>
            Loading fund details...
          </Typography>
        </Box>
      </Box>
    );
  }

  if (error) {
    return (
      <Box p={3}>
        <ErrorDisplay
          error={error}
          canRetry={error.retryable}
          onRetry={() => refetch()}
          onDismiss={() => navigate('/')}
          variant="inline"
        />
        <Button
          variant="outlined"
          onClick={() => navigate('/')}
          sx={{ mt: 2 }}
        >
          Back to Dashboard
        </Button>
      </Box>
    );
  }

  if (!fundData) {
    return (
      <Box p={3}>
        <Box sx={{ p: 2, bgcolor: 'warning.light', borderRadius: 1, display: 'flex', alignItems: 'center' }}>
          <Typography variant="body1" fontWeight="medium" color="warning.main">
            No fund data available
          </Typography>
        </Box>
      </Box>
    );
  }

  const { fund, events } = fundData;

  return (
    <Box p={3}>
      {/* Breadcrumb Navigation */}
      <Breadcrumbs aria-label="breadcrumb" sx={{ mb: 2 }}>
        <Link
          component="button"
          variant="body2"
          onClick={() => navigate('/')}
          sx={{ textDecoration: 'none', cursor: 'pointer' }}
        >
          Investment Companies
        </Link>
        <Link
          component="button"
          variant="body2"
          onClick={() => navigate(`/companies/${fund.investment_company_id}`)}
          sx={{ textDecoration: 'none', cursor: 'pointer' }}
        >
          {fund.investment_company}
        </Link>
        <Typography color="text.primary">{fund.name}</Typography>
      </Breadcrumbs>

      {/* Header */}
      <Box sx={{ mb: 3, position: 'relative' }}>
        <Typography 
          variant="h4" 
          component="h1" 
          gutterBottom
          sx={{ 
            fontWeight: 600,
            color: 'text.primary',
            letterSpacing: '-0.02em'
          }}
        >
          {fund.name}
        </Typography>
        <Typography 
          variant="subtitle1" 
          color="text.secondary" 
          gutterBottom
          sx={{ 
            fontWeight: 400,
            opacity: 0.8
          }}
        >
          {fund.fund_type} • {fund.entity} • {fund.investment_company}
        </Typography>
        
        {/* Phase 2C: Sidebar Toggle Button */}
        <IconButton
          onClick={toggleSidebar}
          sx={{ 
            position: 'absolute', 
            right: 0, 
            top: 0,
            zIndex: 1,
            bgcolor: 'background.paper',
            // Phase 4: Enhanced visual polish
            boxShadow: '0 4px 16px rgba(0,0,0,0.08), 0 2px 6px rgba(0,0,0,0.12)',
            borderRadius: 2,
            transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
            '&:hover': {
              bgcolor: 'action.hover',
              transform: 'translateY(-2px)',
              boxShadow: '0 6px 20px rgba(0,0,0,0.12), 0 3px 8px rgba(0,0,0,0.16)'
            }
          }}
        >
          {sidebarVisible ? <ChevronLeft /> : <ChevronRight />}
        </IconButton>
      </Box>

      {/* Phase 2C: Side-by-Side Layout */}
      <Box sx={{ 
        display: 'flex', 
        flexDirection: { xs: 'column', sm: 'row' },
        gap: { xs: 2, sm: 3 },
        minHeight: { xs: 'auto', sm: 'calc(100vh - 200px)' },
        height: { xs: 'auto', sm: 'calc(100vh - 200px)' },
        alignItems: 'stretch',
        transition: 'all 0.3s ease-in-out',
        // Visual separation: Add subtle border between sidebar and main area
        '& > *:first-of-type': {
          borderRight: { sm: '1px solid' },
          borderColor: { sm: 'divider' },
          pr: { sm: 2 }
        }
      }}>
        {/* Left Sidebar - Summary Sections */}
        <Box sx={{ 
          width: sidebarVisible ? { xs: '100%', sm: '322px', md: '368px', lg: '414px' } : 0,
          flexShrink: 0,
          position: { xs: 'static', sm: 'relative' },
          height: { xs: 'auto', sm: '100%' },
          overflowY: { xs: 'visible', sm: 'auto' },
          transition: 'all 0.3s ease-in-out',
          overflow: 'hidden',
          // Responsive optimization: Better mobile experience
          order: { xs: 1, sm: 0 },
          mb: { xs: 2, sm: 0 },
          // Phase 4: Enhanced visual polish
          bgcolor: 'background.paper',
          borderRadius: { sm: 2 },
          boxShadow: { sm: '0 4px 16px rgba(0,0,0,0.08), 0 2px 6px rgba(0,0,0,0.12)' },
          display: 'flex',
          flexDirection: 'column',
          // Hide completely when not visible
          opacity: sidebarVisible ? 1 : 0,
          visibility: sidebarVisible ? 'visible' : 'hidden',
          transform: sidebarVisible ? 'translateX(0)' : 'translateX(-100%)'
        }}>
          {/* Summary Section Header */}
          <Box sx={{ 
            p: 3, 
            borderBottom: 1, 
            borderColor: 'divider',
            bgcolor: 'grey.50'
          }}>
            <Typography 
              variant="h6"
              sx={{ 
                fontWeight: 600,
                color: 'text.primary',
                letterSpacing: '-0.01em'
              }}
            >
              Summary
            </Typography>
          </Box>
          
      <EquitySection fund={fund} formatCurrency={formatCurrency} formatDate={formatDate} />
      <ExpectedPerformanceSection fund={fund} formatCurrency={formatCurrency} formatDate={formatDate} />
      <CompletedPerformanceSection fund={fund} formatCurrency={formatCurrency} formatDate={formatDate} />
      <FundDetailsSection fund={fund} formatCurrency={formatCurrency} formatDate={formatDate} />
      <TransactionSummarySection fund={fund} formatCurrency={formatCurrency} formatDate={formatDate} />
          <UnitPriceChartSection fund={fund} formatCurrency={formatCurrency} formatDate={formatDate} events={events} />
        </Box>

        {/* Right Main Area - Events Table */}
        <Box sx={{ 
          flex: 1,
          minWidth: 0,
          height: { xs: 'auto', sm: '100%' },
          overflow: 'hidden',
          // Responsive optimization: Better mobile experience
          order: { xs: 2, sm: 1 },
          width: { xs: '100%', sm: 'auto' },
          // Phase 4: Enhanced visual polish
          bgcolor: 'background.paper',
          borderRadius: { sm: 2 },
          boxShadow: { sm: '0 4px 16px rgba(0,0,0,0.08), 0 2px 6px rgba(0,0,0,0.12)' },
          pl: { sm: 2 },
          display: 'flex',
          flexDirection: 'column'
        }}>
      {/* Events Table Header with Add Cash Flow Button */}
      <Paper sx={{ 
        width: '100%', 
        overflow: 'hidden', 
        mb: 3,
        flex: 1,
        display: 'flex',
        flexDirection: 'column',
        // Phase 4: Enhanced visual polish
        boxShadow: '0 4px 16px rgba(0,0,0,0.08), 0 2px 6px rgba(0,0,0,0.12)',
        borderRadius: 2,
        transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
        '&:hover': {
          boxShadow: '0 6px 20px rgba(0,0,0,0.12), 0 3px 8px rgba(0,0,0,0.16)'
        }
      }}>
        <Box sx={{ 
          p: 3, 
          borderBottom: 1, 
          borderColor: 'divider',
          bgcolor: 'grey.50'
        }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography 
              variant="h6"
              sx={{ 
                fontWeight: 600,
                color: 'text.primary',
                letterSpacing: '-0.01em'
              }}
            >
              Fund Events ({(() => {
                const filteredEvents = (events || []).filter(event => {
                  if (!showTaxEvents && (event.event_type === 'TAX_PAYMENT' || event.event_type === 'EOFY_DEBT_COST')) {
                    return false;
                  }
                  if (!showNavUpdates && event.event_type === 'NAV_UPDATE') {
                    return false;
                  }
                  return true;
                });
                return filteredEvents.length;
              })()})
            </Typography>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <Button
                variant="outlined"
                color="primary"
                onClick={() => setEventModalOpen(true)}
                sx={{ 
                  minWidth: { xs: 100, sm: 120 },
                  fontSize: { xs: 11, sm: 12 },
                  textTransform: 'none',
                  borderRadius: 1.5,
                  px: { xs: 1.5, sm: 2 },
                  py: { xs: 0.5, sm: 0.75 },
                  transition: 'all 0.2s ease-in-out',
                  '&:hover': {
                    transform: 'translateY(-1px)',
                    boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
                  }
                }}
              >
                Add Event
              </Button>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Typography variant="body2" color="text.secondary">
                  Show Tax Events
                </Typography>
                <Switch
                  checked={showTaxEvents}
                  onChange={(e) => setShowTaxEvents(e.target.checked)}
                  size="small"
                  sx={{
                    '& .MuiSwitch-switchBase': {
                      color: 'grey.400',
                      transition: 'all 0.2s ease-in-out',
                    },
                    '& .MuiSwitch-switchBase.Mui-checked': {
                      color: 'primary.main',
                    },
                    '& .MuiSwitch-switchBase.Mui-checked + .MuiSwitch-track': {
                      backgroundColor: 'primary.main',
                    },
                    '&:hover .MuiSwitch-switchBase': {
                      transform: 'scale(1.05)',
                    }
                  }}
                />
              </Box>
              {fund.tracking_type === 'nav_based' && (
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Typography variant="body2" color="text.secondary">
                    Show NAV Updates
                  </Typography>
                  <Switch
                    checked={showNavUpdates}
                    onChange={(e) => setShowNavUpdates(e.target.checked)}
                    size="small"
                    sx={{
                      '& .MuiSwitch-switchBase': {
                        color: 'grey.400',
                        transition: 'all 0.2s ease-in-out',
                      },
                      '& .MuiSwitch-switchBase.Mui-checked': {
                        color: 'primary.main',
                      },
                      '& .MuiSwitch-switchBase.Mui-checked + .MuiSwitch-track': {
                        backgroundColor: 'primary.main',
                      },
                      '&:hover .MuiSwitch-switchBase': {
                        transform: 'scale(1.05)',
                      }
                    }}
                  />
                </Box>
              )}
            </Box>
          </Box>
        </Box>
        {/* Events Table */}
        <TableContainer sx={{ 
          flex: 1,
          maxHeight: { xs: 300, sm: 'none' },
          scrollBehavior: 'smooth',
          // Phase 4: Enhanced scrollbar styling
          '&::-webkit-scrollbar': {
            width: '8px',
            height: '8px'
          },
          '&::-webkit-scrollbar-track': {
            backgroundColor: 'grey.100',
            borderRadius: '4px'
          },
          '&::-webkit-scrollbar-thumb': {
            backgroundColor: 'grey.400',
            borderRadius: '4px',
            transition: 'background-color 0.2s ease-in-out',
            '&:hover': {
              backgroundColor: 'grey.500'
            }
          },
          // Responsive optimization: Better mobile table experience
          fontSize: { xs: '12px', sm: '13px' }
        }}>
          <Table stickyHeader size="small">
            <TableHead>
              <TableRow>
                <TableCell 
                  sx={{ 
                    py: { xs: 1, sm: 1.5 }, 
                    px: { xs: 1, sm: 2 }, 
                    fontWeight: 600, 
                    fontSize: { xs: 12, sm: 13 },
                    backgroundColor: 'grey.50',
                    borderBottom: 2,
                    borderColor: 'grey.300',
                    color: 'text.primary'
                  }}
                >
                  Date
                </TableCell>
                <TableCell 
                  sx={{ 
                    py: { xs: 1, sm: 1.5 }, 
                    px: { xs: 1, sm: 2 }, 
                    fontWeight: 600, 
                    fontSize: { xs: 12, sm: 13 },
                    backgroundColor: 'grey.50',
                    borderBottom: 2,
                    borderColor: 'grey.300',
                    color: 'text.primary'
                  }}
                >
                  Type
                </TableCell>
                <TableCell 
                  sx={{ 
                    py: { xs: 1, sm: 1.5 }, 
                    px: { xs: 1, sm: 2 }, 
                    fontWeight: 600, 
                    fontSize: { xs: 12, sm: 13 },
                    backgroundColor: 'grey.50',
                    borderBottom: 2,
                    borderColor: 'grey.300',
                    color: 'text.primary'
                  }}
                >
                  Description
                </TableCell>
                <TableCell 
                  align="center" 
                  sx={{ 
                    py: { xs: 1, sm: 1.5 }, 
                    px: { xs: 1, sm: 2 }, 
                    fontWeight: 600, 
                    fontSize: { xs: 12, sm: 13 },
                    backgroundColor: 'grey.50',
                    borderBottom: 2,
                    borderColor: 'grey.300',
                    color: 'text.primary'
                  }}
                >
                  Equity
                </TableCell>
                {fund.tracking_type === 'nav_based' && (
                  <TableCell 
                    align="center" 
                    sx={{ 
                      py: { xs: 1, sm: 1.5 }, 
                      px: { xs: 1, sm: 2 }, 
                      fontWeight: 600, 
                      fontSize: { xs: 12, sm: 13 },
                      backgroundColor: 'grey.50',
                      borderBottom: 2,
                      borderColor: 'grey.300',
                      color: 'text.primary'
                    }}
                  >
                    Nav Update
                  </TableCell>
                )}
                <TableCell 
                  align="center" 
                  sx={{ 
                    py: { xs: 1, sm: 1.5 }, 
                    px: { xs: 1, sm: 2 }, 
                    fontWeight: 600, 
                    fontSize: { xs: 12, sm: 13 },
                    backgroundColor: 'grey.50',
                    borderBottom: 2,
                    borderColor: 'grey.300',
                    color: 'text.primary'
                  }}
                >
                  Distributions
                </TableCell>
                {showTaxEvents && (
                  <TableCell 
                    align="right"
                    sx={{ 
                      py: 1.5, 
                      px: 2, 
                      fontWeight: 600, 
                      fontSize: 13,
                      backgroundColor: 'grey.50',
                      borderBottom: 2,
                      borderColor: 'grey.300',
                      color: 'text.primary'
                    }}
                  >
                    Tax
                  </TableCell>
                )}
                <TableCell 
                  align="right"
                  sx={{ 
                    py: { xs: 1, sm: 1.5 }, 
                    px: { xs: 1, sm: 2 }, 
                    fontWeight: 600, 
                    fontSize: { xs: 12, sm: 13 },
                    backgroundColor: 'grey.50',
                    borderBottom: 2,
                    borderColor: 'grey.300',
                    color: 'text.primary'
                  }}
                >
                  Actions
                </TableCell>
              </TableRow>
            </TableHead>
            <TableBody sx={{ 
              '& .MuiTableCell-root': { 
                py: { xs: 0.5, sm: 1 }, 
                px: { xs: 1, sm: 2 }, 
                fontSize: { xs: 12, sm: 13 } 
              },
              // Phase 4: Enhanced table row styling
              '& .MuiTableRow-root': {
                transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                borderRadius: 1,
                '&:hover': {
                  backgroundColor: 'action.hover',
                  transform: 'translateY(-2px)',
                  boxShadow: '0 4px 12px rgba(0,0,0,0.15), 0 2px 4px rgba(0,0,0,0.1)',
                  '& .MuiTableCell-root': {
                    borderBottom: '1px solid',
                    borderColor: 'divider'
                  }
                }
              }
            }}
            // Performance optimization: Only render visible rows
            >
              {(() => {
                // Performance optimization: Show loading state for large datasets
                if (events.length > 100) {
                  console.log(`Processing ${events.length} events - this may take a moment...`);
                }
                
                // Debug: Log all events
                console.log('All events:', events);
                console.log('Events with RETURN_OF_CAPITAL:', events.filter(e => e.event_type === 'RETURN_OF_CAPITAL'));
                console.log('Event types:', events.map(e => ({ id: e.id, type: e.event_type, description: e.description, amount: e.amount })));
                
                // Group events by date and type to combine interest distributions with withholding tax
                const groupedEvents: { [key: string]: ExtendedFundEvent[] } = {};
                
                events.forEach(event => {
                  const dateKey = event.event_date;
                  if (!groupedEvents[dateKey]) {
                    groupedEvents[dateKey] = [];
                  }
                  groupedEvents[dateKey].push(event);
                });

                return Object.entries(groupedEvents).map(([date, dateEvents]) => {
                  // Debug: Log all dates and their events
                  console.log(`Processing date: ${date}, events:`, dateEvents);
                  
                  // Find interest distribution and related withholding tax for this date
                  const interestEvent = dateEvents.find(e => 
                    e.event_type === 'DISTRIBUTION' && e.distribution_type === 'INTEREST'
                  );
                  const withholdingEvent = dateEvents.find(e => 
                    e.event_type === 'TAX_PAYMENT' && e.tax_payment_type === 'NON_RESIDENT_INTEREST_WITHHOLDING'
                  );

                  // If we have both interest and withholding on the same date, combine them
                  if (interestEvent && withholdingEvent) {
                                              const isNavBased = fund.tracking_type === 'nav_based';
                          const isDistributionEvent = interestEvent.event_type === 'DISTRIBUTION';

                    return (
                      <React.Fragment key={`${date}-combined`}>
                        {/* Combined interest + withholding row */}
                        <TableRow hover>
                          <TableCell>{formatDate(date)}</TableCell>
                          <TableCell>
                            <Chip
                              label="INTEREST"
                              color={getEventTypeColor('DISTRIBUTION') as any}
                              size="small"
                            />
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2">
                              {interestEvent.description || '-'}
                            </Typography>
                                                          <Typography variant="caption" color="error.main">
                                Withholding: {formatCurrency(-(withholdingEvent?.amount || 0), fund.currency)}
                              </Typography>
                          </TableCell>
                        {/* EQUITY Section */}
                        <TableCell align="right"></TableCell>
                        {/* NAV UPDATE Section (only for NAV-based funds) */}
                        {fund.tracking_type === 'nav_based' && (
                          <TableCell align="right"></TableCell>
                        )}
                        {/* DISTRIBUTIONS Section */}
                        <TableCell align="right">
                          {isDistributionEvent ? (
                            <Box>
                              <Typography variant="body2">
                                {formatCurrency(interestEvent.amount, fund.currency)}
                              </Typography>
                              <Typography variant="caption" color="error.main">
                                {formatCurrency(-(withholdingEvent.amount || 0), fund.currency)}
                              </Typography>
                            </Box>
                          ) : ''}
                        </TableCell>
                        {/* Tax Section */}
                        {showTaxEvents && (
                          <TableCell align="right"></TableCell>
                        )}
                        {/* Actions Column */}
                        <TableCell align="right" sx={{ 
                          minWidth: { xs: 80, sm: 120 }, 
                          px: { xs: 1, sm: 2 } 
                        }}>
                          <Box display="flex" gap={{ xs: 0.5, sm: 1.5 }} justifyContent="flex-end" alignItems="center">
                            {/* Only show edit/delete for user-editable events */}
                            {!['TAX_PAYMENT', 'DAILY_RISK_FREE_INTEREST_CHARGE', 'EOFY_DEBT_COST', 'MANAGEMENT_FEE', 'CARRIED_INTEREST', 'OTHER'].includes(interestEvent.event_type) && (
                              <>
                                <IconButton
                                  size="small"
                                  onClick={() => handleEditEvent(interestEvent)}
                                  sx={{
                                    color: 'primary.main',
                                    p: 1,
                                    borderRadius: 1,
                                    transition: 'all 0.2s ease-in-out',
                                    '&:hover': {
                                      bgcolor: 'primary.light',
                                      transform: 'scale(1.05)',
                                      boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
                                    }
                                  }}
                                  title="Edit event"
                                >
                                  <EditIcon sx={{ fontSize: 18 }} />
                                </IconButton>
                                <IconButton
                                  size="small"
                                  onClick={() => handleDeleteEvent(interestEvent)}
                                  sx={{
                                    color: 'error.main',
                                    p: 1,
                                    borderRadius: 1,
                                    transition: 'all 0.2s ease-in-out',
                                    '&:hover': {
                                      bgcolor: 'error.light',
                                      transform: 'scale(1.05)',
                                      boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
                                    }
                                  }}
                                  title="Delete event"
                                >
                                  <DeleteIcon sx={{ fontSize: 18 }} />
                                </IconButton>
                              </>
                            )}
                          </Box>
                        </TableCell>
                        </TableRow>
                        
                        {/* Process other events on the same date (like RETURN_OF_CAPITAL) */}
                        {dateEvents.filter(event => 
                          event.id !== interestEvent.id && 
                          event.id !== withholdingEvent.id
                        ).map((event) => {
                          // Debug RETURN_OF_CAPITAL events specifically
                          if (event.event_type === 'RETURN_OF_CAPITAL') {
                            console.log('Processing RETURN_OF_CAPITAL event (after combined):', event);
                          }
                          
                          const isNavBased = fund.tracking_type === 'nav_based';
                          const isEquityEvent = isNavBased 
                            ? (event.event_type === 'UNIT_PURCHASE' || event.event_type === 'UNIT_SALE')
                            : (event.event_type === 'CAPITAL_CALL' || event.event_type === 'RETURN_OF_CAPITAL');
                          const isDistributionEvent = event.event_type === 'DISTRIBUTION';
                          const isOtherEvent = !isEquityEvent && !isDistributionEvent;

                          // Skip withholding tax events that are already combined
                          if (event.event_type === 'TAX_PAYMENT' && event.tax_payment_type === 'NON_RESIDENT_INTEREST_WITHHOLDING') {
                            return null;
                          }

                          // Skip tax and debt events if toggle is off
                          if (!showTaxEvents && (event.event_type === 'TAX_PAYMENT' || event.event_type === 'EOFY_DEBT_COST')) {
                            return null;
                          }

                          // Skip NAV updates if toggle is off
                          if (!showNavUpdates && event.event_type === 'NAV_UPDATE') {
                            return null;
                          }

                          return (
                            <TableRow key={event.id} hover>
                              <TableCell>{formatDate(event.event_date)}</TableCell>
                              <TableCell>
                                <Chip
                                  label={getEventTypeLabel(event)}
                                  color={getEventTypeColor(event.event_type) as any}
                                  size="small"
                                />
                              </TableCell>
                              <TableCell>
                                <Typography variant="body2">
                                  {event.description || '-'}
                                </Typography>
                                {event.distribution_type && (
                                  <Typography variant="caption" color="text.secondary">
                                    {event.distribution_type}
                                  </Typography>
                                )}
                              </TableCell>
                              {/* EQUITY Section */}
                              <TableCell align="right">
                                {isEquityEvent && (
                                  (() => {
                                    // Handle NAV-based funds
                                    if (isNavBased) {
                                      if (event.event_type === 'UNIT_PURCHASE') {
                                        return (
                                          <Box>
                                            <Typography variant="body2" color="error.main">
                                              ({formatCurrency(event.amount, fund.currency)})
                                            </Typography>
                                            {event.units_purchased && event.unit_price && (
                                              <Typography variant="caption" color="text.secondary">
                                                {event.units_purchased} × {formatCurrency(event.unit_price, fund.currency)}
                                                {event.brokerage_fee && event.brokerage_fee > 0 && (
                                                  <span style={{ color: 'error.main' }}>
                                                    {' '}- {formatBrokerageFee(event.brokerage_fee, fund.currency)}
                                                  </span>
                                                )}
                                              </Typography>
                                            )}
                                          </Box>
                                        );
                                      } else if (event.event_type === 'UNIT_SALE') {
                                        return (
                                          <Box>
                                            <Typography variant="body2">
                                              {formatCurrency(event.amount, fund.currency)}
                                            </Typography>
                                            {event.units_sold && event.unit_price && (
                                              <Typography variant="caption" color="text.secondary">
                                                {event.units_sold} × {formatCurrency(event.unit_price, fund.currency)}
                                                {event.brokerage_fee && event.brokerage_fee > 0 && (
                                                  <span style={{ color: 'error.main' }}>
                                                    {' '}- {formatBrokerageFee(event.brokerage_fee, fund.currency)}
                                                  </span>
                                                )}
                                              </Typography>
                                            )}
                                          </Box>
                                        );
                                      }
                                    } else {
                                      // Handle cost-based funds
                                      if (event.event_type === 'CAPITAL_CALL') {
                                        return (
                                          <Typography variant="body2" color="error.main">
                                            ({formatCurrency(event.amount, fund.currency)})
                                          </Typography>
                                        );
                                      } else if (event.event_type === 'RETURN_OF_CAPITAL') {
                                        return (
                                          <Typography variant="body2">
                                            {formatCurrency(event.amount, fund.currency)}
                                          </Typography>
                                        );
                                      }
                                    }
                                    return '';
                                  })()
                                )}
                              </TableCell>
                              {/* NAV UPDATE Section (only for NAV-based funds) */}
                              {fund.tracking_type === 'nav_based' && (
                                <TableCell align="right">
                                  {event.event_type === 'NAV_UPDATE' && event.nav_per_share ? (
                                    <Box>
                                      <Typography variant="body2">
                                        {formatCurrency(event.nav_per_share, fund.currency)}
                                      </Typography>
                                      {event.nav_change_absolute != null && event.nav_change_percentage != null && (
                                        <Typography 
                                          variant="caption" 
                                          color={event.nav_change_absolute >= 0 ? 'success.main' : 'error.main'}
                                        >
                                          {event.nav_change_absolute >= 0 ? '+' : ''}{formatCurrency(event.nav_change_absolute, fund.currency)}, {event.nav_change_percentage >= 0 ? '+' : ''}{event.nav_change_percentage.toFixed(1)}%
                                        </Typography>
                                      )}
                                    </Box>
                                  ) : ''}
                                </TableCell>
                              )}
                              {/* DISTRIBUTIONS Section */}
                              <TableCell align="right">
                                {isDistributionEvent ? formatCurrency(event.amount, fund.currency) : ''}
                              </TableCell>
                              {/* Tax Section */}
                              {showTaxEvents && (
                                <TableCell align="right">
                                  {isOtherEvent && event.amount ? (
                            event.event_type === 'TAX_PAYMENT' ? (
                              <Box>
                                <Typography variant="body2" color="error.main">
                                  {formatCurrency(-event.amount, fund.currency)}
                                </Typography>
                                {(() => {
                                  // Get income and tax rate based on tax payment type
                                  let incomeAmount: number | null = null;
                                  let taxRate: number | null = null;
                                  

                                  
                                  switch (event.tax_payment_type) {
                                    case 'EOFY_INTEREST_TAX':
                                      incomeAmount = event.interest_income_amount ?? null;
                                      taxRate = event.interest_income_tax_rate ?? null;
                                      break;
                                    case 'DIVIDENDS_FRANKED_TAX':
                                      incomeAmount = event.dividend_franked_income_amount ?? null;
                                      taxRate = event.dividend_franked_income_tax_rate ?? null;
                                      break;
                                    case 'DIVIDENDS_UNFRANKED_TAX':
                                      incomeAmount = event.dividend_unfranked_income_amount ?? null;
                                      taxRate = event.dividend_unfranked_income_tax_rate ?? null;
                                      break;
                                    case 'CAPITAL_GAINS_TAX':
                                      incomeAmount = event.capital_gain_income_amount ?? null;
                                      taxRate = event.capital_gain_income_tax_rate ?? null;
                                      break;
                                  }
                                  
                                  if (incomeAmount && taxRate) {
                                    return (
                                      <Typography variant="caption" color="text.secondary">
                                        {formatCurrency(incomeAmount, fund.currency)} @ {taxRate}%
                                      </Typography>
                                    );
                                  } else if (event.description) {
                                    // Fallback to description if income/tax rate not available
                                    return (
                                      <Typography variant="caption" color="text.secondary">
                                        {event.description}
                                      </Typography>
                                    );
                                  }
                                  return null;
                                })()}
                              </Box>
                            ) : event.event_type === 'EOFY_DEBT_COST' ? (
                              <Box>
                                <Typography variant="body2">
                                  {formatCurrency(event.amount, fund.currency)}
                                </Typography>
                                {(() => {
                                  // Get total interest and deduction rate for EOFY debt cost events
                                  const totalInterest = event.eofy_debt_interest_deduction_sum_of_daily_interest ?? null;
                                  const deductionRate = event.eofy_debt_interest_deduction_rate ?? null;
                                  
                                  if (totalInterest && deductionRate) {
                                    return (
                                      <Typography variant="caption" color="text.secondary">
                                        {formatCurrency(totalInterest, fund.currency)} @ {deductionRate}%
                                      </Typography>
                                    );
                                  } else if (event.description) {
                                    // Fallback to description if data not available
                                    return (
                                      <Typography variant="caption" color="text.secondary">
                                        {event.description}
                                      </Typography>
                                    );
                                  }
                                  return null;
                                })()}
                              </Box>
                            ) : formatCurrency(event.amount, fund.currency)
                          ) : ''}
                          </TableCell>
                        )}
                        {/* Actions Column */}
                        <TableCell align="right" sx={{ minWidth: 120, px: 2 }}>
                          <Box display="flex" gap={1.5} justifyContent="flex-end" alignItems="center">
                            {/* Only show edit/delete for user-editable events */}
                            {!['TAX_PAYMENT', 'DAILY_RISK_FREE_INTEREST_CHARGE', 'EOFY_DEBT_COST', 'MANAGEMENT_FEE', 'CARRIED_INTEREST', 'OTHER'].includes(event.event_type) && (
                              <>
                                <IconButton
                                  size="small"
                                  onClick={() => handleEditEvent(event)}
                                  sx={{
                                    color: 'primary.main',
                                    p: 1,
                                    borderRadius: 1,
                                    transition: 'all 0.2s ease-in-out',
                                    '&:hover': {
                                      bgcolor: 'primary.light',
                                      transform: 'scale(1.05)',
                                      boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
                                    }
                                  }}
                                  title="Edit event"
                                >
                                  <EditIcon sx={{ fontSize: 18 }} />
                                </IconButton>
                                <IconButton
                                  size="small"
                                  onClick={() => handleDeleteEvent(event)}
                                  sx={{
                                    color: 'error.main',
                                    p: 1,
                                    borderRadius: 1,
                                    transition: 'all 0.2s ease-in-out',
                                    '&:hover': {
                                      bgcolor: 'error.light',
                                      transform: 'scale(1.05)',
                                      boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
                                    }
                                  }}
                                  title="Delete event"
                                >
                                  <DeleteIcon sx={{ fontSize: 18 }} />
                                </IconButton>
                              </>
                            )}
                          </Box>
                        </TableCell>
                      </TableRow>
                    );
                  }).filter(Boolean)}
                      </React.Fragment>
                    );
                  }

                  // For all other events, display normally
                  return dateEvents.map((event) => {
                    // Debug RETURN_OF_CAPITAL events specifically
                    if (event.event_type === 'RETURN_OF_CAPITAL') {
                      console.log('Processing RETURN_OF_CAPITAL event:', event);
                      console.log('Date events for this date:', dateEvents);
                    }
                    
                    const isNavBased = fund.tracking_type === 'nav_based';
                    const isEquityEvent = isNavBased 
                      ? (event.event_type === 'UNIT_PURCHASE' || event.event_type === 'UNIT_SALE')
                      : (event.event_type === 'CAPITAL_CALL' || event.event_type === 'RETURN_OF_CAPITAL');
                    const isDistributionEvent = event.event_type === 'DISTRIBUTION';
                    const isOtherEvent = !isEquityEvent && !isDistributionEvent;



                    // Skip standalone withholding tax events (they should only appear when combined with interest distributions)
                    if (event.event_type === 'TAX_PAYMENT' && event.tax_payment_type === 'NON_RESIDENT_INTEREST_WITHHOLDING') {
                      return null;
                    }

                    // Skip tax and debt events if toggle is off
                    if (!showTaxEvents && (event.event_type === 'TAX_PAYMENT' || event.event_type === 'EOFY_DEBT_COST')) {
                      return null;
                    }

                    // Skip NAV updates if toggle is off
                    if (!showNavUpdates && event.event_type === 'NAV_UPDATE') {
                      return null;
                    }

                    return (
                      <TableRow key={event.id} hover>
                        <TableCell>{formatDate(event.event_date)}</TableCell>
                        <TableCell>
                          <Chip
                            label={getEventTypeLabel(event)}
                            color={getEventTypeColor(event.event_type) as any}
                            size="small"
                          />
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2">
                            {event.description || '-'}
                          </Typography>
                          {event.distribution_type && (
                            <Typography variant="caption" color="text.secondary">
                              {event.distribution_type}
                            </Typography>
                          )}
                        </TableCell>
                        {/* EQUITY Section */}
                        <TableCell align="right">
                          {isEquityEvent && (
                            (() => {
                              // Handle NAV-based funds
                              if (isNavBased) {
                                if (event.event_type === 'UNIT_PURCHASE') {
                                  return (
                                    <Box>
                                      <Typography variant="body2" color="error.main">
                                        ({formatCurrency(event.amount, fund.currency)})
                                      </Typography>
                                      {event.units_purchased && event.unit_price && (
                                        <Typography variant="caption" color="text.secondary">
                                          {event.units_purchased} × {formatCurrency(event.unit_price, fund.currency)}
                                          {event.brokerage_fee && event.brokerage_fee > 0 && (
                                            <span style={{ color: 'error.main' }}>
                                              {' '}- {formatBrokerageFee(event.brokerage_fee, fund.currency)}
                                            </span>
                                          )}
                                        </Typography>
                                      )}
                                    </Box>
                                  );
                                } else if (event.event_type === 'UNIT_SALE') {
                                  return (
                                    <Box>
                                      <Typography variant="body2">
                                        {formatCurrency(event.amount, fund.currency)}
                                      </Typography>
                                      {event.units_sold && event.unit_price && (
                                        <Typography variant="caption" color="text.secondary">
                                          {event.units_sold} × {formatCurrency(event.unit_price, fund.currency)}
                                          {event.brokerage_fee && event.brokerage_fee > 0 && (
                                            <span style={{ color: 'error.main' }}>
                                              {' '}- {formatBrokerageFee(event.brokerage_fee, fund.currency)}
                                            </span>
                                          )}
                                        </Typography>
                                      )}
                                    </Box>
                                  );
                                }
                              } else {
                                // Handle cost-based funds
                                if (event.event_type === 'CAPITAL_CALL') {
                                  return (
                                    <Typography variant="body2" color="error.main">
                                      ({formatCurrency(event.amount, fund.currency)})
                                    </Typography>
                                  );
                                } else if (event.event_type === 'RETURN_OF_CAPITAL') {
                                  return (
                                    <Typography variant="body2">
                                      {formatCurrency(event.amount, fund.currency)}
                                    </Typography>
                                  );
                                }
                              }
                              return '';
                            })()
                          )}
                        </TableCell>
                                                {/* NAV UPDATE Section (only for NAV-based funds) */}
                        {fund.tracking_type === 'nav_based' && (
                          <TableCell align="right">
                            {event.event_type === 'NAV_UPDATE' && event.nav_per_share ? (
                              <Box>
                                <Typography variant="body2">
                                  {formatCurrency(event.nav_per_share, fund.currency)}
                                </Typography>
                                {event.nav_change_absolute != null && event.nav_change_percentage != null && (
                                  <Typography 
                                    variant="caption" 
                                    color={event.nav_change_absolute >= 0 ? 'success.main' : 'error.main'}
                                  >
                                    {event.nav_change_absolute >= 0 ? '+' : ''}{formatCurrency(event.nav_change_absolute, fund.currency)}, {event.nav_change_percentage >= 0 ? '+' : ''}{event.nav_change_percentage.toFixed(1)}%
                                  </Typography>
                                )}
                              </Box>
                            ) : ''}
                          </TableCell>
                        )}
                        {/* DISTRIBUTIONS Section */}
                        <TableCell align="right">
                          {isDistributionEvent ? formatCurrency(event.amount, fund.currency) : ''}
                        </TableCell>
                        {/* Tax Section */}
                        {showTaxEvents && (
                          <TableCell align="right">
                            {isOtherEvent && event.amount ? (
                            event.event_type === 'TAX_PAYMENT' ? (
                              <Box>
                                <Typography variant="body2" color="error.main">
                                  {formatCurrency(-event.amount, fund.currency)}
                                </Typography>
                                {(() => {
                                  // Get income and tax rate based on tax payment type
                                  let incomeAmount: number | null = null;
                                  let taxRate: number | null = null;
                                  

                                  
                                  switch (event.tax_payment_type) {
                                    case 'EOFY_INTEREST_TAX':
                                      incomeAmount = event.interest_income_amount ?? null;
                                      taxRate = event.interest_income_tax_rate ?? null;
                                      break;
                                    case 'DIVIDENDS_FRANKED_TAX':
                                      incomeAmount = event.dividend_franked_income_amount ?? null;
                                      taxRate = event.dividend_franked_income_tax_rate ?? null;
                                      break;
                                    case 'DIVIDENDS_UNFRANKED_TAX':
                                      incomeAmount = event.dividend_unfranked_income_amount ?? null;
                                      taxRate = event.dividend_unfranked_income_tax_rate ?? null;
                                      break;
                                    case 'CAPITAL_GAINS_TAX':
                                      incomeAmount = event.capital_gain_income_amount ?? null;
                                      taxRate = event.capital_gain_income_tax_rate ?? null;
                                      break;
                                  }
                                  
                                  if (incomeAmount && taxRate) {
                                    return (
                                      <Typography variant="caption" color="text.secondary">
                                        {formatCurrency(incomeAmount, fund.currency)} @ {taxRate}%
                                      </Typography>
                                    );
                                  } else if (event.description) {
                                    // Fallback to description if income/tax rate not available
                                    return (
                                      <Typography variant="caption" color="text.secondary">
                                        {event.description}
                                      </Typography>
                                    );
                                  }
                                  return null;
                                })()}
                              </Box>
                            ) : event.event_type === 'EOFY_DEBT_COST' ? (
                              <Box>
                                <Typography variant="body2">
                                  {formatCurrency(event.amount, fund.currency)}
                                </Typography>
                                {(() => {
                                  // Get total interest and deduction rate for EOFY debt cost events
                                  const totalInterest = event.eofy_debt_interest_deduction_sum_of_daily_interest ?? null;
                                  const deductionRate = event.eofy_debt_interest_deduction_rate ?? null;
                                  
                                  if (totalInterest && deductionRate) {
                                    return (
                                      <Typography variant="caption" color="text.secondary">
                                        {formatCurrency(totalInterest, fund.currency)} @ {deductionRate}%
                                      </Typography>
                                    );
                                  } else if (event.description) {
                                    // Fallback to description if data not available
                                    return (
                                      <Typography variant="caption" color="text.secondary">
                                        {event.description}
                                      </Typography>
                                    );
                                  }
                                  return null;
                                })()}
                              </Box>
                            ) : formatCurrency(event.amount, fund.currency)
                          ) : ''}
                          </TableCell>
                        )}
                        {/* Actions Column */}
                        <TableCell align="right" sx={{ minWidth: 120, px: 2 }}>
                          <Box display="flex" gap={1.5} justifyContent="flex-end" alignItems="center">
                            {/* Only show edit/delete for user-editable events */}
                            {!['TAX_PAYMENT', 'DAILY_RISK_FREE_INTEREST_CHARGE', 'EOFY_DEBT_COST', 'MANAGEMENT_FEE', 'CARRIED_INTEREST', 'OTHER'].includes(event.event_type) && (
                              <>
                                <IconButton
                                  size="small"
                                  onClick={() => handleEditEvent(event)}
                                  sx={{
                                    color: 'primary.main',
                                    p: 1,
                                    borderRadius: 1,
                                    transition: 'all 0.2s ease-in-out',
                                    '&:hover': {
                                      bgcolor: 'primary.light',
                                      transform: 'scale(1.05)',
                                      boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
                                    }
                                  }}
                                  title="Edit event"
                                >
                                  <EditIcon sx={{ fontSize: 18 }} />
                                </IconButton>
                                <IconButton
                                  size="small"
                                  onClick={() => handleDeleteEvent(event)}
                                  sx={{
                                    color: 'error.main',
                                    p: 1,
                                    borderRadius: 1,
                                    transition: 'all 0.2s ease-in-out',
                                    '&:hover': {
                                      bgcolor: 'error.light',
                                      transform: 'scale(1.05)',
                                      boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
                                    }
                                  }}
                                  title="Delete event"
                                >
                                  <DeleteIcon sx={{ fontSize: 18 }} />
                                </IconButton>
                              </>
                            )}
                          </Box>
                        </TableCell>
                      </TableRow>
                    );
                  }).filter(Boolean);
                }).flat();
              })()}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>


          </Box>
      </Box>
      {/* Modal rendered at root */}
      <CreateFundEventModal
        open={eventModalOpen}
        onClose={() => setEventModalOpen(false)}
        onEventCreated={handleEventCreated}
        fundId={fund.id}
        fundTrackingType={fund.tracking_type === 'nav_based' ? 'nav_based' : 'cost_based'}
      />
      
      {/* Edit Event Modal */}
      <EditFundEventModal
        open={editModalOpen}
        onClose={() => setEditModalOpen(false)}
        onEventUpdated={handleEventUpdated}
        fundId={fund.id}
        event={selectedEvent}
      />
      
      {/* Delete Confirmation Dialog */}
      <Dialog
        open={deleteDialogOpen}
        onClose={() => setDeleteDialogOpen(false)}
      >
        <DialogTitle>Confirm Delete</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Are you sure you want to delete this event? This action cannot be undone.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)} disabled={deletingEvent}>
            Cancel
          </Button>
          <Button 
            onClick={confirmDeleteEvent} 
            color="error" 
            variant="contained"
            disabled={deletingEvent}
          >
            {deletingEvent ? <CircularProgress size={20} /> : 'Delete'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default FundDetail; 