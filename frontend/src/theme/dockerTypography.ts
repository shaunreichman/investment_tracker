// Docker Typography System - Separate module to avoid type intersections
// Following TypeScript memory management principles

export const dockerTypography = {
  // Font Family
  fontFamily: {
    primary: '"Inter", "Roboto", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
    mono: '"SF Mono", "Monaco", "Inconsolata", "Roboto Mono", "Source Code Pro", monospace',
  },
  
  // Font Sizes - Following Docker's precise scale
  fontSize: {
    h1: '28px',
    h2: '22px', 
    h3: '18px',
    h4: '16px',
    h5: '14px',
    h6: '12px',
    body1: '16px',
    body2: '14px',
    caption: '12px',
    button: '14px',
    overline: '10px',
  },
  
  // Font Weights
  fontWeight: {
    light: 300,
    regular: 400,
    medium: 500,
    semibold: 600,
    bold: 700,
  },
  
  // Line Heights
  lineHeight: {
    h1: 1.2,
    h2: 1.3,
    h3: 1.4,
    h4: 1.4,
    h5: 1.4,
    h6: 1.4,
    body1: 1.5,
    body2: 1.5,
    caption: 1.4,
    button: 1.4,
  },
  
  // Letter Spacing
  letterSpacing: {
    h1: '-0.02em',
    h2: '-0.01em',
    h3: '0em',
    h4: '0em',
    h5: '0.01em',
    h6: '0.02em',
    body1: '0em',
    body2: '0em',
    caption: '0.02em',
    button: '0.02em',
  },
} as const;

// Type-safe typography access
export type DockerTypographyKey = keyof typeof dockerTypography;
export type DockerTypographyValue = typeof dockerTypography[DockerTypographyKey];
