/**
 * CompanyCards Component
 * 
 * Displays companies in a card/grid format.
 */

import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Chip,
  Link,
  useTheme,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  Business as BusinessIcon,
  Delete as DeleteIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import type { Company } from '@/company/types';
import { formatCurrency } from '@/shared/utils/formatters';

interface CompanyCardsProps {
  companies: Company[];
  onDeleteClick?: (company: Company) => void;
  isDeleting?: boolean;
}

export const CompanyCards: React.FC<CompanyCardsProps> = ({
  companies,
  onDeleteClick,
  isDeleting = false,
}) => {
  const theme = useTheme();
  const navigate = useNavigate();

  return (
    <Box 
      sx={{ 
        display: 'grid',
        gridTemplateColumns: {
          xs: '1fr',
          sm: 'repeat(2, 1fr)',
          md: 'repeat(3, 1fr)',
          lg: 'repeat(4, 1fr)'
        },
        gap: 2,
        p: 2
      }}
    >
      {companies.map((company) => (
        <Card
          key={company.id}
          sx={{
            backgroundColor: theme.palette.background.paper,
            border: `1px solid ${theme.palette.divider}`,
            cursor: 'pointer',
            transition: 'all 0.2s ease-in-out',
            '&:hover': {
              boxShadow: '0px 8px 24px rgba(0,0,0,0.3)',
              transform: 'translateY(-2px)',
              borderColor: theme.palette.primary.main
            }
          }}
          onClick={() => navigate(`/companies/${company.id}`)}
        >
          <CardContent sx={{ p: 3 }}>
            {/* Header */}
            <Box sx={{ display: 'flex', alignItems: 'flex-start', mb: 2 }}>
              <BusinessIcon 
                sx={{ 
                  color: theme.palette.primary.main,
                  fontSize: '32px',
                  mr: 2,
                  flexShrink: 0
                }} 
              />
              <Box sx={{ flex: 1, minWidth: 0 }}>
                <Typography
                  variant="h6"
                  sx={{
                    color: theme.palette.text.primary,
                    fontWeight: 600,
                    mb: 0.5,
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    whiteSpace: 'nowrap'
                  }}
                >
                  {company.name}
                </Typography>
                {company.company_type && (
                  <Chip
                    label={company.company_type}
                    size="small"
                    sx={{
                      height: '20px',
                      fontSize: '11px',
                      backgroundColor: theme.palette.action.selected,
                      color: theme.palette.text.secondary
                    }}
                  />
                )}
              </Box>
              {onDeleteClick && (
                <Tooltip title="Delete company">
                  <IconButton
                    size="small"
                    onClick={(e) => {
                      e.stopPropagation();
                      onDeleteClick(company);
                    }}
                    disabled={isDeleting}
                    color="error"
                    aria-label={`Delete ${company.name}`}
                    sx={{ flexShrink: 0 }}
                  >
                    <DeleteIcon fontSize="small" />
                  </IconButton>
                </Tooltip>
              )}
            </Box>

            {/* Description */}
            <Typography
              variant="body2"
              sx={{
                color: theme.palette.text.secondary,
                mb: 2,
                minHeight: '40px',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                display: '-webkit-box',
                WebkitLineClamp: 2,
                WebkitBoxOrient: 'vertical'
              }}
            >
              {company.description || 'No description available'}
            </Typography>

            {/* Stats */}
            <Box sx={{ mb: 2 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography variant="caption" sx={{ color: theme.palette.text.muted }}>
                  Total Funds
                </Typography>
                <Typography variant="body2" sx={{ fontWeight: 600, color: theme.palette.text.primary }}>
                  {company.total_funds || 0}
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography variant="caption" sx={{ color: theme.palette.text.muted }}>
                  Active Funds
                </Typography>
                <Typography variant="body2" sx={{ fontWeight: 600, color: theme.palette.text.primary }}>
                  {company.total_funds_active || 0}
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                <Typography variant="caption" sx={{ color: theme.palette.text.muted }}>
                  Total Equity
                </Typography>
                <Typography 
                  variant="body2" 
                  sx={{ 
                    fontWeight: 600,
                    color: theme.palette.primary.main
                  }}
                >
                  {formatCurrency(company.current_equity_balance || 0)}
                </Typography>
              </Box>
            </Box>

            {/* Footer */}
            {company.website && (
              <Box 
                sx={{ 
                  pt: 2,
                  borderTop: `1px solid ${theme.palette.divider}`
                }}
                onClick={(e) => e.stopPropagation()}
              >
                <Link
                  href={company.website}
                  target="_blank"
                  rel="noopener noreferrer"
                  sx={{
                    color: theme.palette.primary.main,
                    textDecoration: 'none',
                    fontSize: '12px',
                    display: 'block',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    whiteSpace: 'nowrap',
                    '&:hover': {
                      textDecoration: 'underline'
                    }
                  }}
                >
                  {company.website}
                </Link>
              </Box>
            )}

            {/* Status indicator */}
            {company.status && (
              <Box sx={{ position: 'absolute', top: 12, right: 12 }}>
                <Chip
                  label={company.status}
                  size="small"
                  sx={{
                    height: '20px',
                    fontSize: '10px',
                    backgroundColor: company.status === 'ACTIVE' 
                      ? theme.palette.success.main 
                      : theme.palette.grey[600],
                    color: theme.palette.common.white
                  }}
                />
              </Box>
            )}
          </CardContent>
        </Card>
      ))}
    </Box>
  );
};

