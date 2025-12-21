// ============================================================================
// SUMMARY CARD COMPONENT
// ============================================================================

import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Divider,
} from '@mui/material';
import type { SummaryCardProps, SummarySectionRow } from './SummaryCard.types';

/**
 * SummaryCard - Display complex summaries with multiple sections
 * 
 * Perfect for performance summaries, portfolio overviews, or any
 * multi-section data displays.
 * 
 * @example
 * ```tsx
 * <SummaryCard
 *   title="Performance Summary"
 *   icon={<TrendingUpIcon />}
 *   sections={[
 *     {
 *       title: "Returns",
 *       content: [
 *         { label: 'IRR', value: '12.5%', color: 'success.main' },
 *         { label: 'Multiple', value: '2.3x', color: 'success.main' },
 *       ],
 *       showDivider: true
 *     },
 *     {
 *       title: "Capital",
 *       content: [
 *         { label: 'Invested', value: '$1.2M' },
 *         { label: 'Returned', value: '$2.8M' },
 *       ]
 *     }
 *   ]}
 * />
 * ```
 */
export const SummaryCard: React.FC<SummaryCardProps> = ({
  title,
  icon,
  sections,
  footer,
  className,
}) => {
  const renderSectionContent = (content: React.ReactNode | SummarySectionRow[]) => {
    // If content is an array of rows, render them as data rows
    if (Array.isArray(content)) {
      return (
        <Box display="flex" flexDirection="column" gap={1}>
          {content.map((row, rowIndex) => (
            <Box
              key={row.label || rowIndex}
              display="flex"
              justifyContent="space-between"
              alignItems="center"
              sx={{
                py: 0.5,
                px: row.emphasized ? 1 : 0,
                borderRadius: 1,
                backgroundColor: row.emphasized ? 'action.hover' : 'transparent',
              }}
            >
              {/* Label with optional icon */}
              <Box display="flex" alignItems="center" gap={0.5}>
                {row.icon && (
                  <Box sx={{ display: 'flex', alignItems: 'center', fontSize: 18 }}>
                    {row.icon}
                  </Box>
                )}
                <Typography
                  variant="body2"
                  color="textSecondary"
                  sx={{ fontWeight: row.emphasized ? 600 : 400 }}
                >
                  {row.label}
                </Typography>
              </Box>

              {/* Value */}
              <Box display="flex" alignItems="center">
                {typeof row.value === 'string' || typeof row.value === 'number' ? (
                  <Typography
                    variant="body2"
                    sx={{
                      fontWeight: row.emphasized ? 600 : 500,
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
          ))}
        </Box>
      );
    }

    // Otherwise, render the content as-is
    return content;
  };

  return (
    <Card {...(className && { className })}>
      <CardContent>
        {/* Card title with optional icon */}
        <Box display="flex" alignItems="center" mb={3}>
          {icon && (
            <Box sx={{ mr: 2, display: 'flex', alignItems: 'center' }}>
              {icon}
            </Box>
          )}
          <Typography variant="h5">
            {title}
          </Typography>
        </Box>

        {/* Sections */}
        {sections.map((section, sectionIndex) => (
          <Box key={section.title || `section-${sectionIndex}`} mb={sectionIndex < sections.length - 1 ? 3 : 0}>
            {/* Section title */}
            {section.title && (
              <Typography variant="h6" gutterBottom sx={{ fontSize: '1.1rem' }}>
                {section.title}
              </Typography>
            )}

            {/* Section content */}
            {renderSectionContent(section.content)}

            {/* Optional divider */}
            {section.showDivider && sectionIndex < sections.length - 1 && (
              <Divider sx={{ mt: 3 }} />
            )}
          </Box>
        ))}

        {/* Optional footer */}
        {footer && (
          <>
            <Divider sx={{ my: 2 }} />
            <Box>{footer}</Box>
          </>
        )}
      </CardContent>
    </Card>
  );
};

