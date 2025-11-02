// ============================================================================
// BREADCRUMBS - SHARED COMPONENT
// ============================================================================
// Generic, reusable breadcrumb navigation component with:
// - Hierarchical navigation display
// - Clickable breadcrumb items (except last/current)
// - Optional icon support
// - Theme integration
// - Accessibility (ARIA labels)
// - Custom separator support
//
// Usage:
//   <Breadcrumbs
//     items={[
//       { label: 'Home', path: '/' },
//       { label: 'Companies', path: '/companies' },
//       { label: 'Acme Corp', path: '/companies/123' }
//     ]}
//     onNavigate={(path) => navigate(path)}
//     ariaLabel="Page navigation"
//   />
// ============================================================================

import React from 'react';
import { Breadcrumbs as MuiBreadcrumbs, Link, Typography, Box, useTheme, BreadcrumbsProps as MuiBreadcrumbsProps } from '@mui/material';
import type { BreadcrumbsProps } from './Breadcrumbs.types';

// ============================================================================
// COMPONENT
// ============================================================================

export const Breadcrumbs: React.FC<BreadcrumbsProps> = ({
  items,
  onNavigate,
  separator,
  maxItems,
  ariaLabel = 'breadcrumb',
}) => {
  const theme = useTheme();

  // Build props object conditionally to avoid passing undefined values
  const breadcrumbsProps: Partial<MuiBreadcrumbsProps> = {
    'aria-label': ariaLabel,
    sx: {
      '& .MuiBreadcrumbs-ol': {
        alignItems: 'center',
      },
      '& .MuiBreadcrumbs-li': {
        '&:last-child .MuiTypography-root': {
          color: theme.palette.text.muted, // Muted color for current page
          fontWeight: 400,
        },
      },
    },
  };

  if (separator !== undefined) {
    breadcrumbsProps.separator = separator;
  }

  if (maxItems !== undefined) {
    breadcrumbsProps.maxItems = maxItems;
  }

  return (
    <MuiBreadcrumbs {...breadcrumbsProps}>
      {items.map((item, index) => {
        const isLast = index === items.length - 1;

        return (
          <Link
            key={item.path}
            color={isLast ? 'inherit' : theme.palette.primary.main}
            underline="hover"
            onClick={() => !isLast && onNavigate(item.path)}
            sx={{
              cursor: isLast ? 'default' : 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: 0.5,
              '&:hover': {
                color: isLast ? theme.palette.text.muted : theme.palette.text.hover,
              },
            }}
          >
            {item.icon && (
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                {item.icon}
              </Box>
            )}
            <Typography
              variant="body2"
              sx={{
                color: 'inherit',
                fontWeight: isLast ? 400 : 500,
              }}
            >
              {item.label}
            </Typography>
          </Link>
        );
      })}
    </MuiBreadcrumbs>
  );
};

