/**
 * CompanyTable Component
 * 
 * Displays  companies in a table format with sorting capabilities.
 */

import React from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Link,
  Typography,
  Box,
  useTheme,
  IconButton
} from '@mui/material';
import {
  ArrowUpward as ArrowUpwardIcon,
  ArrowDownward as ArrowDownwardIcon
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { Company } from '../../../types/models/company';
import { formatCurrency } from '../../../utils/formatters';

interface CompanyTableProps {
  companies: Company[];
  sortBy: 'name' | 'fund_count' | 'total_equity_balance' | 'active_funds';
  sortOrder: 'asc' | 'desc';
  onSort: (field: 'name' | 'fund_count' | 'total_equity_balance' | 'active_funds') => void;
}

export const CompanyTable: React.FC<CompanyTableProps> = ({
  companies,
  sortBy,
  sortOrder,
  onSort
}) => {
  const theme = useTheme();
  const navigate = useNavigate();

  const SortIcon = ({ field }: { field: string }) => {
    if (sortBy !== field) return null;
    return sortOrder === 'asc' ? (
      <ArrowUpwardIcon sx={{ fontSize: 16, ml: 0.5 }} />
    ) : (
      <ArrowDownwardIcon sx={{ fontSize: 16, ml: 0.5 }} />
    );
  };

  return (
    <TableContainer 
      component={Paper} 
      variant="outlined"
      sx={{
        backgroundColor: theme.palette.background.default,
        border: `1px solid ${theme.palette.divider}`,
        borderRadius: '8px',
        overflow: 'hidden'
      }}
    >
      <Table>
        <TableHead>
          <TableRow>
            <TableCell 
              sx={{ 
                color: theme.palette.text.primary,
                fontWeight: 600,
                fontSize: '14px',
                borderBottom: `1px solid ${theme.palette.divider}`,
                cursor: 'pointer',
                userSelect: 'none',
                '&:hover': {
                  backgroundColor: theme.palette.action.hover
                }
              }}
              onClick={() => onSort('name')}
            >
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                Company Name
                <SortIcon field="name" />
              </Box>
            </TableCell>
            <TableCell 
              sx={{ 
                color: theme.palette.text.primary,
                fontWeight: 600,
                fontSize: '14px',
                borderBottom: `1px solid ${theme.palette.divider}`
              }}
            >
              Description
            </TableCell>
            <TableCell 
              align="right"
              sx={{ 
                color: theme.palette.text.primary,
                fontWeight: 600,
                fontSize: '14px',
                borderBottom: `1px solid ${theme.palette.divider}`,
                cursor: 'pointer',
                userSelect: 'none',
                '&:hover': {
                  backgroundColor: theme.palette.action.hover
                }
              }}
              onClick={() => onSort('fund_count')}
            >
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end' }}>
                Total Funds
                <SortIcon field="fund_count" />
              </Box>
            </TableCell>
            <TableCell 
              align="right"
              sx={{ 
                color: theme.palette.text.primary,
                fontWeight: 600,
                fontSize: '14px',
                borderBottom: `1px solid ${theme.palette.divider}`,
                cursor: 'pointer',
                userSelect: 'none',
                '&:hover': {
                  backgroundColor: theme.palette.action.hover
                }
              }}
              onClick={() => onSort('active_funds')}
            >
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end' }}>
                Active Funds
                <SortIcon field="active_funds" />
              </Box>
            </TableCell>
            <TableCell 
              align="right"
              sx={{ 
                color: theme.palette.text.primary,
                fontWeight: 600,
                fontSize: '14px',
                borderBottom: `1px solid ${theme.palette.divider}`,
                cursor: 'pointer',
                userSelect: 'none',
                '&:hover': {
                  backgroundColor: theme.palette.action.hover
                }
              }}
              onClick={() => onSort('total_equity_balance')}
            >
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end' }}>
                Total Equity
                <SortIcon field="total_equity_balance" />
              </Box>
            </TableCell>
            <TableCell 
              align="right"
              sx={{ 
                color: theme.palette.text.primary,
                fontWeight: 600,
                fontSize: '14px',
                borderBottom: `1px solid ${theme.palette.divider}`
              }}
            >
              Contact
            </TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {companies.map((company, index) => (
            <TableRow 
              key={company.id}
              sx={{
                backgroundColor: index % 2 === 0 ? 'transparent' : 'rgba(255,255,255,0.02)',
                '&:hover': {
                  backgroundColor: theme.palette.background.sidebarHover,
                  cursor: 'pointer'
                }
              }}
              onClick={() => navigate(`/companies/${company.id}`)}
            >
              <TableCell sx={{ 
                borderBottom: `1px solid ${theme.palette.divider}`,
                padding: '16px'
              }}>
                <Box>
                  <Typography
                    variant="subtitle2"
                    sx={{ 
                      color: theme.palette.primary.main,
                      fontWeight: 500,
                      '&:hover': {
                        color: theme.palette.primary.dark
                      }
                    }}
                  >
                    {company.name}
                  </Typography>
                  {company.website && (
                    <Typography 
                      variant="caption" 
                      sx={{ 
                        color: theme.palette.text.muted,
                        display: 'block',
                        mt: 0.5
                      }}
                      onClick={(e) => e.stopPropagation()}
                    >
                      <a 
                        href={company.website} 
                        target="_blank" 
                        rel="noopener noreferrer" 
                        style={{ 
                          textDecoration: 'none',
                          color: theme.palette.text.muted
                        }}
                      >
                        {company.website}
                      </a>
                    </Typography>
                  )}
                </Box>
              </TableCell>
              <TableCell sx={{ 
                borderBottom: `1px solid ${theme.palette.divider}`,
                padding: '16px'
              }}>
                <Typography 
                  variant="body2" 
                  sx={{ 
                    color: theme.palette.text.muted,
                    lineHeight: 1.5
                  }}
                >
                  {company.description || 'No description available'}
                </Typography>
              </TableCell>
              <TableCell align="right" sx={{ 
                borderBottom: `1px solid ${theme.palette.divider}`,
                padding: '16px'
              }}>
                <Chip
                  label={`${company.total_funds || 0} funds`}
                  size="small"
                  sx={{
                    backgroundColor: theme.palette.primary.main,
                    color: theme.palette.text.primary,
                    fontWeight: 500,
                    fontSize: '12px'
                  }}
                />
              </TableCell>
              <TableCell align="right" sx={{ 
                borderBottom: `1px solid ${theme.palette.divider}`,
                padding: '16px'
              }}>
                <Chip
                  label={`${company.total_funds_active || 0} active`}
                  size="small"
                  sx={{
                    backgroundColor: (company.total_funds_active || 0) > 0 ? theme.palette.secondary.main : theme.palette.text.muted,
                    color: theme.palette.text.primary,
                    fontWeight: 500,
                    fontSize: '12px'
                  }}
                />
              </TableCell>
              <TableCell align="right" sx={{ 
                borderBottom: `1px solid ${theme.palette.divider}`,
                padding: '16px'
              }}>
                <Typography 
                  variant="body2" 
                  sx={{ 
                    fontWeight: 600,
                    color: theme.palette.text.primary,
                    fontSize: '14px'
                  }}
                >
                  {formatCurrency(company.current_equity_balance || 0)}
                </Typography>
              </TableCell>
              <TableCell align="right" sx={{ 
                borderBottom: `1px solid ${theme.palette.divider}`,
                padding: '16px'
              }}>
                {company.contacts && company.contacts.length > 0 && company.contacts[0].direct_email && (
                  <Typography 
                    variant="caption" 
                    sx={{ 
                      color: theme.palette.text.muted,
                      fontSize: '12px'
                    }}
                  >
                    {company.contacts[0].direct_email}
                  </Typography>
                )}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
};
