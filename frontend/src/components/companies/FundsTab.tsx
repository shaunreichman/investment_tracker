import React, { useState, useMemo, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  SelectChangeEvent,
  IconButton,
  Tooltip,
  Chip,
  Link,
  TablePagination,
} from '@mui/material';
import {
  Search,
  Sort,
  TrendingUp,
  TrendingDown,
  UnfoldMore,
  ViewList,
  ViewModule,
} from '@mui/icons-material';
import { EnhancedFund, EnhancedFundsResponse } from '../../types/api';
import { formatCurrency, formatPercentage } from '../../utils/formatters';
import { StatusChip } from '../ui/StatusChip';
import { TrackingTypeChip } from '../ui/TrackingTypeChip';
import { useNavigate } from 'react-router-dom';

// ============================================================================
// TYPES
// ============================================================================

interface FundsTabProps {
  data: EnhancedFundsResponse | null;
  loading: boolean;
  onParamsChange: (params: any) => void;
  currentParams: any;
}

// ============================================================================
// COMPONENT
// ============================================================================

export const FundsTab: React.FC<FundsTabProps> = ({
  data,
  loading,
  onParamsChange,
  currentParams,
}) => {
  const navigate = useNavigate();
  const [searchTerm, setSearchTerm] = useState(currentParams.search || '');
  const [statusFilter, setStatusFilter] = useState(currentParams.status_filter || 'all');
  const [currencyFilter, setCurrencyFilter] = useState(currentParams.currency_filter || 'all');
  const [fundTypeFilter, setFundTypeFilter] = useState(currentParams.fund_type_filter || 'all');
  const [viewMode, setViewMode] = useState<'table' | 'cards'>('table');

  // Auto-switch to card view on mobile devices
  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth < 768) {
        setViewMode('cards');
      } else {
        setViewMode('table');
      }
    };

    // Set initial view mode
    handleResize();

    // Add event listener
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // Handle search with debouncing
  const handleSearchChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const value = event.target.value;
    setSearchTerm(value);
    
    // Debounce search API calls
    const timeoutId = setTimeout(() => {
      onParamsChange({ ...currentParams, search: value, page: 1 });
    }, 300);

    return () => clearTimeout(timeoutId);
  };

  const handleStatusFilterChange = (event: SelectChangeEvent<string>) => {
    const value = event.target.value;
    setStatusFilter(value);
    onParamsChange({ ...currentParams, status_filter: value, page: 1 });
  };

  const handleCurrencyFilterChange = (event: SelectChangeEvent<string>) => {
    const value = event.target.value;
    setCurrencyFilter(value);
    onParamsChange({ ...currentParams, currency_filter: value, page: 1 });
  };

  const handleFundTypeFilterChange = (event: SelectChangeEvent<string>) => {
    const value = event.target.value;
    setFundTypeFilter(value);
    onParamsChange({ ...currentParams, fund_type_filter: value, page: 1 });
  };

  const handleSort = (field: string) => {
    const newSortOrder = 
      currentParams.sort_by === field && currentParams.sort_order === 'asc' ? 'desc' : 'asc';
    
    onParamsChange({
      ...currentParams,
      sort_by: field,
      sort_order: newSortOrder,
      page: 1,
    });
  };

  const handlePageChange = (event: unknown, newPage: number) => {
    onParamsChange({ ...currentParams, page: newPage + 1 });
  };

  const handleRowsPerPageChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    onParamsChange({
      ...currentParams,
      per_page: parseInt(event.target.value, 10),
      page: 1,
    });
  };

  const getSortIcon = (field: string) => {
    if (currentParams.sort_by !== field) {
      return <UnfoldMore />;
    }
    return currentParams.sort_order === 'asc' ? <TrendingUp /> : <TrendingDown />;
  };

  const renderSortableHeader = (field: string, label: string, width?: string) => (
    <TableCell 
      style={{ width, cursor: 'pointer', userSelect: 'none' }}
      onClick={() => handleSort(field)}
    >
      <Box display="flex" alignItems="center" gap={1}>
        {label}
        <IconButton size="small" sx={{ p: 0 }}>
          {getSortIcon(field)}
        </IconButton>
      </Box>
    </TableCell>
  );

  if (loading) {
    return (
      <Box p={3}>
        <Typography>Loading funds data...</Typography>
      </Box>
    );
  }

  if (!data || data.funds.length === 0) {
    return (
      <Box p={3}>
        <Card>
          <CardContent>
            <Box textAlign="center" py={4}>
              <Typography variant="h6" color="textSecondary" gutterBottom>
                No Funds Found
              </Typography>
              <Typography variant="body2" color="textSecondary">
                {data?.filters.applied_search || data?.filters.applied_status_filter !== 'all'
                  ? 'Try adjusting your search or filter criteria.'
                  : 'This investment company doesn\'t have any funds yet.'}
              </Typography>
            </Box>
          </CardContent>
        </Card>
      </Box>
    );
  }

  return (
    <Box p={3}>
      {/* Filters and Search */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box display="flex" gap={2} flexWrap="wrap" alignItems="center">
            <TextField
              label="Search Funds"
              variant="outlined"
              size="small"
              value={searchTerm}
              onChange={handleSearchChange}
              InputProps={{
                startAdornment: <Search sx={{ mr: 1, color: 'text.secondary' }} />,
              }}
              sx={{ minWidth: 250 }}
            />
            
            <FormControl size="small" sx={{ minWidth: 150 }}>
              <InputLabel>Status Filter</InputLabel>
              <Select
                value={statusFilter}
                label="Status Filter"
                onChange={handleStatusFilterChange}
              >
                <MenuItem value="all">All Statuses</MenuItem>
                <MenuItem value="active">Active</MenuItem>
                <MenuItem value="completed">Completed</MenuItem>
                <MenuItem value="suspended">Suspended</MenuItem>
              </Select>
            </FormControl>

            <FormControl size="small" sx={{ minWidth: 150 }}>
              <InputLabel>Currency Filter</InputLabel>
              <Select
                value={currencyFilter}
                label="Currency Filter"
                onChange={handleCurrencyFilterChange}
              >
                <MenuItem value="all">All Currencies</MenuItem>
                <MenuItem value="AUD">AUD</MenuItem>
                <MenuItem value="USD">USD</MenuItem>
                <MenuItem value="EUR">EUR</MenuItem>
                <MenuItem value="GBP">GBP</MenuItem>
              </Select>
            </FormControl>

            <FormControl size="small" sx={{ minWidth: 150 }}>
              <InputLabel>Fund Type Filter</InputLabel>
              <Select
                value={fundTypeFilter}
                label="Fund Type Filter"
                onChange={handleFundTypeFilterChange}
              >
                <MenuItem value="all">All Types</MenuItem>
                <MenuItem value="venture_capital">Venture Capital</MenuItem>
                <MenuItem value="private_equity">Private Equity</MenuItem>
                <MenuItem value="real_estate">Real Estate</MenuItem>
                <MenuItem value="infrastructure">Infrastructure</MenuItem>
                <MenuItem value="debt">Debt</MenuItem>
              </Select>
            </FormControl>

              {/* View Toggle */}
              <Box display="flex" alignItems="center" gap={1}>
                <Tooltip title="Table View">
                  <IconButton
                    size="small"
                    onClick={() => setViewMode('table')}
                    color={viewMode === 'table' ? 'primary' : 'default'}
                  >
                    <ViewList />
                  </IconButton>
                </Tooltip>
                <Tooltip title="Card View">
                  <IconButton
                    size="small"
                    onClick={() => setViewMode('cards')}
                    color={viewMode === 'cards' ? 'primary' : 'default'}
                  >
                    <ViewModule />
                  </IconButton>
                </Tooltip>
              </Box>
          </Box>
          
          {/* Active Filters Summary */}
          {(statusFilter !== 'all' || currencyFilter !== 'all' || fundTypeFilter !== 'all' || searchTerm) && (
            <Box mt={2} display="flex" gap={1} flexWrap="wrap" alignItems="center">
              <Typography variant="caption" color="textSecondary">
                Active filters:
              </Typography>
              {statusFilter !== 'all' && (
                <Chip
                  label={`Status: ${statusFilter}`}
                  size="small"
                  onDelete={() => {
                    setStatusFilter('all');
                    onParamsChange({ ...currentParams, status_filter: 'all', page: 1 });
                  }}
                />
              )}
              {currencyFilter !== 'all' && (
                <Chip
                  label={`Currency: ${currencyFilter}`}
                  size="small"
                  onDelete={() => {
                    setCurrencyFilter('all');
                    onParamsChange({ ...currentParams, currency_filter: 'all', page: 1 });
                  }}
                />
              )}
              {fundTypeFilter !== 'all' && (
                <Chip
                  label={`Type: ${fundTypeFilter}`}
                  size="small"
                  onDelete={() => {
                    setFundTypeFilter('all');
                    onParamsChange({ ...currentParams, fund_type_filter: 'all', page: 1 });
                  }}
                />
              )}
              {searchTerm && (
                <Chip
                  label={`Search: "${searchTerm}"`}
                  size="small"
                  onDelete={() => {
                    setSearchTerm('');
                    onParamsChange({ ...currentParams, search: '', page: 1 });
                  }}
                />
              )}
            </Box>
          )}
        </CardContent>
      </Card>

      {/* Funds Table */}
      <Card>
        <CardContent sx={{ p: 0 }}>
          <TableContainer component={Paper} variant="outlined">
            <Table>
              <TableHead>
                <TableRow>
                  {/* Fund Details Section */}
                  {renderSortableHeader('name', 'Fund Name', '200px')}
                  <TableCell>Type</TableCell>
                  <TableCell>Tracking</TableCell>
                  {renderSortableHeader('status', 'Status', '100px')}
                  
                  {/* Estimated Return Section */}
                  {renderSortableHeader('expected_irr', 'Expected IRR', '120px')}
                  {renderSortableHeader('duration_months', 'Duration (Months)', '140px')}
                  
                  {/* Dates Section */}
                  {renderSortableHeader('start_date', 'Start Date', '120px')}
                  {renderSortableHeader('end_date', 'End Date', '120px')}
                  {renderSortableHeader('days_since_last_activity', 'Days Since Activity', '150px')}
                  
                  {/* Equity Section */}
                  {renderSortableHeader('commitment', 'Commitment', '120px')}
                  {renderSortableHeader('invested_capital', 'Invested Capital', '130px')}
                  {renderSortableHeader('current_value', 'Current Value', '130px')}
                  {renderSortableHeader('current_equity_balance', 'Current Balance', '140px')}
                  
                  {/* Distributions Section */}
                  {renderSortableHeader('distribution_count', 'Distributions', '120px')}
                  {renderSortableHeader('total_distribution_amount', 'Total Amount', '130px')}
                  
                  {/* Returns Section */}
                  {renderSortableHeader('completed_irr', 'Completed IRR', '130px')}
                  {renderSortableHeader('performance_vs_expected', 'Performance vs Expected', '160px')}
                  
                  {/* Performance Section */}
                  {renderSortableHeader('unrealized_gains_losses', 'Unrealized G/L', '140px')}
                  {renderSortableHeader('realized_gains_losses', 'Realized G/L', '130px')}
                  {renderSortableHeader('total_profit_loss', 'Total P/L', '120px')}
                </TableRow>
              </TableHead>
              <TableBody>
                {data.funds.map((fund) => (
                  <TableRow key={fund.id} hover>
                    {/* Fund Details */}
                    <TableCell>
                      <Link
                        component="button"
                        variant="subtitle2"
                        onClick={() => navigate(`/funds/${fund.id}`)}
                        sx={{ textDecoration: 'none', cursor: 'pointer' }}
                      >
                        {fund.name}
                      </Link>
                      {fund.description && (
                        <Typography variant="caption" color="textSecondary" display="block">
                          {fund.description}
                        </Typography>
                      )}
                    </TableCell>
                    <TableCell>{fund.fund_type}</TableCell>
                    <TableCell>
                      <TrackingTypeChip trackingType={fund.tracking_type} />
                    </TableCell>
                    <TableCell>
                      <StatusChip status={fund.status} />
                    </TableCell>
                    
                    {/* Estimated Return */}
                    <TableCell align="right">
                      {fund.estimated_return.expected_irr !== null
                        ? formatPercentage(fund.estimated_return.expected_irr)
                        : '-'}
                    </TableCell>
                    <TableCell align="right">
                      {fund.estimated_return.duration_months !== null
                        ? fund.estimated_return.duration_months
                        : '-'}
                    </TableCell>
                    
                    {/* Dates */}
                    <TableCell>
                      {new Date(fund.fund_details.start_date).toLocaleDateString()}
                    </TableCell>
                    <TableCell>
                      {fund.fund_details.end_date
                        ? new Date(fund.fund_details.end_date).toLocaleDateString()
                        : '-'}
                    </TableCell>
                    <TableCell align="right">
                      {fund.fund_details.days_since_last_activity}
                    </TableCell>
                    
                    {/* Equity */}
                    <TableCell align="right">
                      {formatCurrency(fund.equity.commitment)}
                    </TableCell>
                    <TableCell align="right">
                      {formatCurrency(fund.equity.invested_capital)}
                    </TableCell>
                    <TableCell align="right">
                      {formatCurrency(fund.equity.current_value)}
                    </TableCell>
                    <TableCell align="right">
                      {formatCurrency(fund.equity.current_equity_balance)}
                    </TableCell>
                    
                    {/* Distributions */}
                    <TableCell align="right">
                      {fund.distributions.distribution_count}
                    </TableCell>
                    <TableCell align="right">
                      {formatCurrency(fund.distributions.total_distribution_amount)}
                    </TableCell>
                    
                    {/* Returns */}
                    <TableCell align="right">
                      {fund.returns.completed_irr !== null
                        ? formatPercentage(fund.returns.completed_irr)
                        : '-'}
                    </TableCell>
                    <TableCell align="right">
                      {fund.returns.performance_vs_expected !== null
                        ? formatPercentage(fund.returns.performance_vs_expected)
                        : '-'}
                    </TableCell>
                    
                    {/* Performance */}
                    <TableCell align="right">
                      <Typography
                        color={fund.performance.unrealized_gains_losses >= 0 ? 'success.main' : 'error.main'}
                      >
                        {formatCurrency(fund.performance.unrealized_gains_losses)}
                      </Typography>
                    </TableCell>
                    <TableCell align="right">
                      <Typography
                        color={fund.performance.realized_gains_losses >= 0 ? 'success.main' : 'error.main'}
                      >
                        {formatCurrency(fund.performance.realized_gains_losses)}
                      </Typography>
                    </TableCell>
                    <TableCell align="right">
                      <Typography
                        color={fund.performance.total_profit_loss >= 0 ? 'success.main' : 'error.main'}
                        fontWeight="bold"
                      >
                        {formatCurrency(fund.performance.total_profit_loss)}
                      </Typography>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
          
          {/* Mobile Card View */}
          {viewMode === 'cards' && (
            <Box sx={{ p: 2 }}>
              <Box display="grid" gap={2} sx={{ 
                gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr', md: '1fr 1fr 1fr' }
              }}>
                {data.funds.map((fund) => (
                  <Card key={fund.id} variant="outlined" sx={{ height: 'fit-content' }}>
                    <CardContent>
                      {/* Fund Header */}
                      <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
                        <Box>
                          <Link
                            component="button"
                            variant="h6"
                            onClick={() => navigate(`/funds/${fund.id}`)}
                            sx={{ textDecoration: 'none', cursor: 'pointer', textAlign: 'left' }}
                          >
                            {fund.name}
                          </Link>
                          {fund.description && (
                            <Typography variant="body2" color="textSecondary" mt={1}>
                              {fund.description}
                            </Typography>
                          )}
                        </Box>
                        <Box display="flex" gap={1}>
                          <StatusChip status={fund.status} />
                          <TrackingTypeChip trackingType={fund.tracking_type} />
                        </Box>
                      </Box>

                      {/* Fund Details Grid */}
                      <Box display="grid" gap={2} sx={{ gridTemplateColumns: '1fr 1fr' }}>
                        {/* Basic Info */}
                        <Box>
                          <Typography variant="caption" color="textSecondary">Type</Typography>
                          <Typography variant="body2">{fund.fund_type}</Typography>
                        </Box>
                        <Box>
                          <Typography variant="caption" color="textSecondary">Currency</Typography>
                          <Typography variant="body2">{fund.currency}</Typography>
                        </Box>
                        
                        {/* Performance */}
                        <Box>
                          <Typography variant="caption" color="textSecondary">Expected IRR</Typography>
                          <Typography variant="body2">
                            {fund.estimated_return.expected_irr !== null
                              ? formatPercentage(fund.estimated_return.expected_irr)
                              : '-'}
                          </Typography>
                        </Box>
                        <Box>
                          <Typography variant="caption" color="textSecondary">Current Value</Typography>
                          <Typography variant="body2">
                            {formatCurrency(fund.equity.current_value)}
                          </Typography>
                        </Box>

                        {/* Dates */}
                        <Box>
                          <Typography variant="caption" color="textSecondary">Start Date</Typography>
                          <Typography variant="body2">
                            {new Date(fund.fund_details.start_date).toLocaleDateString()}
                          </Typography>
                        </Box>
                        <Box>
                          <Typography variant="caption" color="textSecondary">Days Since Activity</Typography>
                          <Typography variant="body2">
                            {fund.fund_details.days_since_last_activity}
                          </Typography>
                        </Box>
                      </Box>

                      {/* Performance Summary */}
                      <Box mt={2} p={1.5} sx={{ bgcolor: 'grey.50', borderRadius: 1 }}>
                        <Typography variant="caption" color="textSecondary" display="block" mb={1}>
                          Performance Summary
                        </Typography>
                        <Box display="flex" justifyContent="space-between">
                          <Box>
                            <Typography variant="caption" color="textSecondary">Total P/L</Typography>
                            <Typography 
                              variant="body2" 
                              color={fund.performance.total_profit_loss >= 0 ? 'success.main' : 'error.main'}
                              fontWeight="bold"
                            >
                              {formatCurrency(fund.performance.total_profit_loss)}
                            </Typography>
                          </Box>
                          <Box>
                            <Typography variant="caption" color="textSecondary">Completed IRR</Typography>
                            <Typography variant="body2">
                              {fund.returns.completed_irr !== null
                                ? formatPercentage(fund.returns.completed_irr)
                                : '-'}
                            </Typography>
                          </Box>
                        </Box>
                      </Box>
                    </CardContent>
                  </Card>
                ))}
              </Box>
            </Box>
          )}
          
          {/* Pagination */}
          <TablePagination
            component="div"
            count={data.pagination.total_funds}
            page={data.pagination.current_page - 1}
            onPageChange={handlePageChange}
            rowsPerPage={data.pagination.per_page}
            onRowsPerPageChange={handleRowsPerPageChange}
            rowsPerPageOptions={[10, 25, 50, 100]}
            labelDisplayedRows={({ from, to, count }) =>
              `${from}-${to} of ${count !== -1 ? count : `more than ${to}`}`
            }
          />
        </CardContent>
      </Card>
    </Box>
  );
};
