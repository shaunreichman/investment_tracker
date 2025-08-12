// Docker Spacing System - Separate module to avoid type intersections
// Following TypeScript memory management principles

export const dockerSpacing = {
  // Base spacing unit (4px grid system)
  base: 4,
  
  // Spacing scale following Docker's generous padding approach
  xs: 4,      // 4px
  sm: 8,      // 8px
  md: 16,     // 16px - inner padding for cards
  lg: 24,     // 24px - outer padding between sections
  xl: 32,     // 32px - major section spacing
  xxl: 48,    // 48px - page-level spacing
  
  // Component-specific spacing
  component: {
    card: {
      padding: 16,        // Inner card padding
      margin: 24,         // Space between cards
    },
    section: {
      padding: 24,        // Section padding
      margin: 32,         // Space between sections
    },
    page: {
      padding: 24,        // Page outer padding
      margin: 48,         // Page-level spacing
    },
  },
  
  // Layout spacing
  layout: {
    sidebar: {
      width: 280,         // Sidebar width
      collapsedWidth: 64, // Collapsed sidebar width
      padding: 16,        // Sidebar internal padding
    },
    header: {
      height: 64,         // Header height
      padding: 16,        // Header padding
    },
    content: {
      padding: 24,        // Main content padding
      maxWidth: 1200,     // Max content width
    },
  },
} as const;

// Type-safe spacing access
export type DockerSpacingKey = keyof typeof dockerSpacing;
export type DockerSpacingValue = typeof dockerSpacing[DockerSpacingKey];
