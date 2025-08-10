import React, { useState, useMemo } from 'react';
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
          </Box>
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
