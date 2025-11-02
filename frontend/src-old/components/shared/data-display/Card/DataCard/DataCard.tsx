// ============================================================================
// DATA CARD COMPONENT
// ============================================================================

import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Divider,
} from '@mui/material';
import type { DataCardProps } from './DataCard.types';

/**
 * DataCard - Display multiple label-value pairs in a card
 * 
 * Perfect for displaying structured data like fund details, statistics,
 * or any key-value information.
 * 
 * @example
 * ```tsx
 * <DataCard
 *   title="Fund Details"
 *   data={[
 *     { label: 'Start Date', value: '2021-01-15', icon: <CalendarIcon /> },
 *     { label: 'Status', value: <StatusChip status="active" /> },
 *     { label: 'IRR', value: '12.5%', color: 'success.main' },
 *   ]}
 * />
 * ```
 */
export const DataCard: React.FC<DataCardProps> = ({
  title,
  data,
  onItemClick,
  className,
}) => {
  return (
    <Card {...(className && { className })}>
      <CardContent>
        {/* Optional title */}
        {title && (
          <>
            <Typography variant="h6" gutterBottom>
              {title}
            </Typography>
            <Divider sx={{ mb: 2 }} />
          </>
        )}

        {/* Data rows */}
        <Box display="flex" flexDirection="column" gap={1.5}>
          {data.map((row, index) => (
            <Box key={index}>
              <Box
                display="flex"
                justifyContent="space-between"
                alignItems="center"
                onClick={onItemClick ? () => onItemClick(index) : undefined}
                sx={{
                  py: 0.5,
                  px: row.highlighted ? 1 : 0,
                  borderRadius: 1,
                  cursor: onItemClick ? 'pointer' : 'default',
                  backgroundColor: row.highlighted ? 'action.hover' : 'transparent',
                  transition: 'all 0.2s ease-in-out',
                  ...(onItemClick && {
                    '&:hover': {
                      backgroundColor: 'action.selected',
                    },
                  }),
                }}
              >
                {/* Label with optional icon */}
                <Box display="flex" alignItems="center" gap={0.5}>
                  {row.icon && (
                    <Box sx={{ display: 'flex', alignItems: 'center', fontSize: 18 }}>
                      {row.icon}
                    </Box>
                  )}
                  <Typography variant="body2" color="textSecondary">
                    {row.label}
                  </Typography>
                </Box>

                {/* Value */}
                <Box display="flex" alignItems="center">
                  {typeof row.value === 'string' || typeof row.value === 'number' ? (
                    <Typography
                      variant="body2"
                      sx={{
                        fontWeight: row.highlighted ? 600 : 500,
                        color: row.color || 'text.primary',
                      }}
                    >
                      {row.value}
                    </Typography>
                  ) : (
                    row.value
                  )}
                </Box>
              </Box>

              {/* Helper text */}
              {row.helperText && (
                <Typography
                  variant="caption"
                  color="textSecondary"
                  sx={{ pl: row.icon ? 3 : 0, display: 'block', mt: 0.5 }}
                >
                  {row.helperText}
                </Typography>
              )}
            </Box>
          ))}
        </Box>
      </CardContent>
    </Card>
  );
};

