// ============================================================================
// STAT CARD COMPONENT
// ============================================================================

import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  useTheme,
} from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
} from '@mui/icons-material';
import type { StatCardProps } from './StatCard.types';

/**
 * StatCard - Display a single statistic with optional icon and trend
 * 
 * Perfect for dashboard metrics, KPIs, and summary statistics.
 * 
 * @example
 * ```tsx
 * <StatCard
 *   title="Total Committed"
 *   value="$1,234,567"
 *   subtitle="Across 12 funds"
 *   icon={<AccountBalanceIcon />}
 *   color="primary"
 * />
 * 
 * <StatCard
 *   title="Portfolio Value"
 *   value="$2,345,678"
 *   color="success"
 *   trend={{ value: 12.5, direction: 'up', isPositive: true }}
 * />
 * ```
 */
export const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  subtitle,
  icon,
  color = 'default',
  trend,
  onClick,
  className,
}) => {
  const theme = useTheme();

  // Get color based on theme
  const getColor = () => {
    switch (color) {
      case 'primary':
        return theme.palette.primary.main;
      case 'success':
        return theme.palette.success.main;
      case 'error':
        return theme.palette.error.main;
      case 'warning':
        return theme.palette.warning.main;
      case 'info':
        return theme.palette.info.main;
      default:
        return theme.palette.text.primary;
    }
  };

  const cardColor = getColor();
  const isInteractive = !!onClick;

  return (
    <Card
      onClick={onClick}
      sx={{
        cursor: isInteractive ? 'pointer' : 'default',
        transition: 'all 0.2s ease-in-out',
        ...(isInteractive && {
          '&:hover': {
            transform: 'translateY(-2px)',
            boxShadow: 3,
          },
        }),
      }}
      {...(className && { className })}
    >
      <CardContent>
        {/* Title with optional icon */}
        <Box display="flex" alignItems="center" mb={2}>
          {icon && (
            <Box sx={{ mr: 1, color: cardColor }}>
              {icon}
            </Box>
          )}
          <Typography variant="h6" color="textSecondary">
            {title}
          </Typography>
        </Box>

        {/* Main value */}
        <Typography
          variant="h4"
          sx={{
            color: cardColor,
            fontWeight: 600,
            mb: subtitle || trend ? 1 : 0,
          }}
        >
          {value}
        </Typography>

        {/* Trend indicator */}
        {trend && (
          <Box display="flex" alignItems="center" gap={0.5} mb={subtitle ? 1 : 0}>
            {trend.direction === 'up' ? (
              <TrendingUpIcon
                fontSize="small"
                sx={{
                  color: trend.isPositive !== false
                    ? theme.palette.success.main
                    : theme.palette.error.main,
                }}
              />
            ) : (
              <TrendingDownIcon
                fontSize="small"
                sx={{
                  color: trend.isPositive === true
                    ? theme.palette.success.main
                    : theme.palette.error.main,
                }}
              />
            )}
            <Typography
              variant="body2"
              sx={{
                color: trend.isPositive !== false
                  ? theme.palette.success.main
                  : theme.palette.error.main,
                fontWeight: 500,
              }}
            >
              {trend.value}%{trend.label && ` ${trend.label}`}
            </Typography>
          </Box>
        )}

        {/* Subtitle */}
        {subtitle && (
          <Typography variant="body2" color="textSecondary">
            {subtitle}
          </Typography>
        )}
      </CardContent>
    </Card>
  );
};

