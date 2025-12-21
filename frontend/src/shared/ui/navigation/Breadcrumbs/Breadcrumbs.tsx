// ============================================================================
// BREADCRUMBS - ENTERPRISE-GRADE COMPONENT
// ============================================================================
// Enterprise-grade breadcrumb component with:
// - Semantic HTML structure (<nav>, <ol>, aria-current)
// - React Router Link integration
// - Keyboard activation
// - Overflow handling with tooltips
// - Validation warnings
// - Design token enforcement
// - Analytics support
//
// Usage:
//   <Breadcrumbs
//     items={[
//       { id: 'home', label: 'Home', to: '/' },
//       { id: 'companies', label: 'Companies', to: '/companies' },
//       { id: 'company-123', label: 'Acme Corp', to: '/companies/123' }
//     ]}
//   />
// ============================================================================

import React, { useMemo, useCallback, useEffect } from 'react';
import { Link as RouterLink } from 'react-router-dom';
import {
  Box,
  Typography,
  useTheme,
  Tooltip,
  Breadcrumbs as MuiBreadcrumbs,
} from '@mui/material';
import type { BreadcrumbsProps, BreadcrumbItem, BreadcrumbItemRenderProps } from './Breadcrumbs.types';

// ============================================================================
// VALIDATION HELPERS
// ============================================================================

/**
 * Validates breadcrumb items and emits console warnings for issues
 */
const validateItems = (items: BreadcrumbItem[]): void => {
  if (items.length === 0) {
    console.warn('[Breadcrumbs] Empty items array provided. Breadcrumbs will not render.');
    return;
  }

  // Check for duplicate IDs
  const ids = items.map(item => item.id);
  const duplicateIds = ids.filter((id, index) => ids.indexOf(id) !== index);
  if (duplicateIds.length > 0) {
    console.warn(
      `[Breadcrumbs] Duplicate breadcrumb IDs detected: ${duplicateIds.join(', ')}. This may cause accessibility issues.`
    );
  }

  // Check for duplicate paths (when `to` is provided)
  const paths = items.filter(item => item.to).map(item => item.to!);
  const duplicatePaths = paths.filter((path, index) => paths.indexOf(path) !== index);
  if (duplicatePaths.length > 0) {
    console.warn(
      `[Breadcrumbs] Duplicate breadcrumb paths detected: ${duplicatePaths.join(', ')}. This may cause navigation issues.`
    );
  }

  // Check for missing navigation handlers on intermediate crumbs
  items.forEach((item, index) => {
    const isLast = index === items.length - 1;
    if (!isLast && !item.to && !item.disabled) {
      console.warn(
        `[Breadcrumbs] Intermediate breadcrumb "${item.label}" (id: ${item.id}) has no navigation handler. ` +
        `Provide either a 'to' prop or ensure 'onNavigate' is provided.`
      );
    }
  });
};

/**
 * Calculates which items should be visible based on maxItems
 * Returns array of indices that should be shown
 * Uses middle ellipsis strategy: first item, some middle items, last item
 */
const calculateVisibleIndices = (
  items: BreadcrumbItem[],
  maxItems?: number
): number[] => {
  if (!maxItems || items.length <= maxItems) {
    return items.map((_, index) => index);
  }

  // Middle ellipsis strategy: show first, last, and some middle items
  const first = 0;
  const last = items.length - 1;
  
  // Calculate how many middle items we can show
  const availableSlots = maxItems - 2; // Reserve for first and last
  const middleCount = Math.max(0, availableSlots);
  
  // If we have space for middle items, show them near the end
  const indices: number[] = [first];
  
  if (middleCount > 0 && items.length > 2) {
    // Show last few items before the final item
    const middleStart = Math.max(first + 1, last - middleCount);
    for (let i = middleStart; i < last; i++) {
      indices.push(i);
    }
  }
  
  indices.push(last);
  
  return indices;
};

// ============================================================================
// COMPONENT
// ============================================================================

export const Breadcrumbs: React.FC<BreadcrumbsProps> = ({
  items,
  LinkComponent = RouterLink,
  onNavigate,
  separator,
  maxItems,
  renderItem,
  ariaLabel = 'Breadcrumb',
  density = 'comfortable',
  showTooltips = true,
  className,
}) => {
  const theme = useTheme();

  // Validate items on mount and when items change
  useEffect(() => {
    validateItems(items);
  }, [items]);

  // Calculate visible indices based on maxItems
  const visibleIndices = useMemo(
    () => calculateVisibleIndices(items, maxItems),
    [items, maxItems]
  );

  // Handle item click/navigation
  const handleItemActivate = useCallback(
    (item: BreadcrumbItem, event: React.MouseEvent | React.KeyboardEvent) => {
      if (item.disabled) {
        event.preventDefault();
        return;
      }

      if (item.to) {
        // Navigation handled by Link component
        return;
      }

      if (onNavigate) {
        event.preventDefault();
        onNavigate(item);
      }
    },
    [onNavigate]
  );

  // Handle keyboard activation
  const handleKeyDown = useCallback(
    (event: React.KeyboardEvent, item: BreadcrumbItem) => {
      if (event.key === 'Enter' || event.key === ' ') {
        event.preventDefault();
        handleItemActivate(item, event);
      }
    },
    [handleItemActivate]
  );

  // Default render function for breadcrumb items
  const defaultRenderItem = useCallback(
    (props: BreadcrumbItemRenderProps): React.ReactNode => {
      const { item, isLast, isTruncated } = props;
      const hasNavigation = !!(item.to || onNavigate);
      const isClickable = !isLast && hasNavigation && !item.disabled;

      // Determine if we should use Link or button
      const useLink = item.to && !item.disabled;
      const useButton = !item.to && onNavigate && !item.disabled && !isLast;

      // Base styles
      const baseStyles = {
        display: 'flex',
        alignItems: 'center',
        gap: theme.spacing(0.5),
        color: isLast
          ? theme.palette.text.muted
          : item.disabled
          ? theme.palette.text.disabled
          : theme.palette.primary.main,
        cursor: isClickable ? 'pointer' : 'default',
        textDecoration: 'none',
        '&:hover': {
          color: isLast
            ? theme.palette.text.muted
            : item.disabled
            ? theme.palette.text.disabled
            : theme.palette.text.hover,
        },
        '&:focus-visible': {
          outline: `2px solid ${theme.palette.primary.main}`,
          outlineOffset: '2px',
          borderRadius: theme.shape.borderRadius,
        },
      };

      // Content wrapper
      const content = (
        <>
          {item.icon && (
            <Box sx={{ display: 'flex', alignItems: 'center', flexShrink: 0 }}>
              {item.icon}
            </Box>
          )}
          <Typography
            variant="body2"
            component="span"
            sx={{
              color: 'inherit',
              fontWeight: isLast ? 400 : 500,
              overflow: isTruncated ? 'hidden' : 'visible',
              textOverflow: isTruncated ? 'ellipsis' : 'clip',
              whiteSpace: isTruncated ? 'nowrap' : 'normal',
              maxWidth: isTruncated ? '150px' : 'none',
            }}
          >
            {item.label}
          </Typography>
        </>
      );

      // Wrap in tooltip if truncated and tooltips enabled
      const wrappedContent = isTruncated && showTooltips ? (
        <Tooltip title={item.label} arrow>
          <Box component="span" sx={baseStyles}>
            {content}
          </Box>
        </Tooltip>
      ) : (
        <Box component="span" sx={baseStyles}>
          {content}
        </Box>
      );

      // Render as Link, button, or span based on navigation capability
      if (useLink) {
        return (
          <LinkComponent
            to={item.to!}
            onClick={(e: React.MouseEvent) => handleItemActivate(item, e)}
            onKeyDown={(e: React.KeyboardEvent) => handleKeyDown(e, item)}
            aria-current={isLast ? 'page' : undefined}
            aria-disabled={item.disabled}
            tabIndex={isClickable ? 0 : -1}
          >
            {wrappedContent}
          </LinkComponent>
        );
      }

      if (useButton) {
        return (
          <Box
            component="button"
            onClick={(e: React.MouseEvent) => handleItemActivate(item, e)}
            onKeyDown={(e: React.KeyboardEvent) => handleKeyDown(e, item)}
            disabled={item.disabled}
            aria-current={isLast ? 'page' : undefined}
            aria-disabled={item.disabled}
            tabIndex={isClickable ? 0 : -1}
            sx={{
              ...baseStyles,
              background: 'none',
              border: 'none',
              padding: 0,
              font: 'inherit',
              '&:disabled': {
                cursor: 'not-allowed',
              },
            }}
          >
            {wrappedContent}
          </Box>
        );
      }

      // Non-clickable span (last item or disabled)
      return (
        <Box
          component="span"
          aria-current={isLast ? 'page' : undefined}
          aria-disabled={item.disabled}
        >
          {wrappedContent}
        </Box>
      );
    },
    [theme, onNavigate, showTooltips, handleItemActivate, handleKeyDown, LinkComponent]
  );

  // Build MUI Breadcrumbs props
  const breadcrumbsProps: {
    'aria-label': string;
    separator?: React.ReactNode;
    maxItems?: number;
    sx: Record<string, unknown>;
  } = {
    'aria-label': ariaLabel,
    sx: {
      '& .MuiBreadcrumbs-ol': {
        alignItems: 'center',
        flexWrap: 'wrap',
        gap: density === 'compact' ? theme.spacing(0.5) : theme.spacing(1),
      },
      '& .MuiBreadcrumbs-li': {
        display: 'flex',
        alignItems: 'center',
      },
    },
  };

  if (separator !== undefined) {
    breadcrumbsProps.separator = separator;
  }

  if (maxItems !== undefined) {
    breadcrumbsProps.maxItems = maxItems;
  }

  // Render breadcrumbs
  return (
    <nav aria-label={ariaLabel} className={className}>
      <MuiBreadcrumbs {...breadcrumbsProps}>
        {items.map((item, index) => {
          const isLast = index === items.length - 1;
          const isVisible = visibleIndices.includes(index);
          const isTruncated = !isVisible && maxItems !== undefined;

          // Determine if we should show ellipsis before this item
          // Show ellipsis if this is the first visible item after hidden items
          const prevIndex = index > 0 ? index - 1 : -1;
          const isFirstVisibleAfterHidden =
            isVisible &&
            prevIndex >= 0 &&
            !visibleIndices.includes(prevIndex) &&
            index > 0;

          const itemProps: BreadcrumbItemRenderProps = {
            item,
            isLast,
            isTruncated: false, // Individual items aren't truncated, only hidden
            index,
          };

          return (
            <React.Fragment key={item.id}>
              {isFirstVisibleAfterHidden && (
                <Typography
                  variant="body2"
                  component="span"
                  sx={{ color: theme.palette.text.muted, mx: 0.5 }}
                  aria-hidden="true"
                >
                  ...
                </Typography>
              )}
              {isVisible ? (
                renderItem ? (
                  renderItem(itemProps)
                ) : (
                  defaultRenderItem(itemProps)
                )
              ) : null}
            </React.Fragment>
          );
        })}
      </MuiBreadcrumbs>
    </nav>
  );
};

