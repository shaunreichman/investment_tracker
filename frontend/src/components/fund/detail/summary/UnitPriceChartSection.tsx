import React from 'react';
import {
  Typography,
  Paper,
  Box
} from '@mui/material';
import { TrendingUp } from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Scatter } from 'recharts';
import { ExtendedFund, ExtendedFundEvent } from '../../../../types/api';

interface SectionProps {
  fund: ExtendedFund;
  formatCurrency: (amount: number | null, currency?: string) => string;
  formatDate: (dateString: string | null) => string;
  events?: ExtendedFundEvent[];
}

/**
 * Unit Price Chart Section - NAV performance chart for NAV-based funds
 */
const UnitPriceChartSectionComponent: React.FC<SectionProps> = ({ fund, formatCurrency, formatDate, events }) => {
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

export default React.memo(UnitPriceChartSectionComponent);