/**
 * Fund visualization configuration.
 *
 * These SYSTEM defaults keep sparkline and table experiences consistent for
 * fund summaries. Components can override when needed, but this provides an
 * enterprise baseline.
 */
export const CHART_CONFIG = {
  COLORS: {
    NAV_LINE: '#1976d2',
    PURCHASE_POINT: '#4caf50',
    SALE_POINT: '#f44336',
    GRID: '#e0e0e0',
    BACKGROUND: '#ffffff',
  },
  DIMENSIONS: {
    HEIGHT: 200,
    MARGIN: { top: 20, right: 20, bottom: 30, left: 40 },
  },
  ANIMATION: {
    DURATION: 300,
    EASING: 'ease-in-out',
  },
} as const;

export const TABLE_CONFIG = {
  SORT_DIRECTIONS: {
    ASC: 'asc',
    DESC: 'desc',
  },
} as const;

