// Docker Color Palette - Updated with new specifications
// Following TypeScript memory management principles

export const dockerColors = {
  // Primary Background Colors
  background: {
    primary: '#10151a',        // Main dashboard background
    secondary: '#070b0d',      // Navigation sidebar background
    panel: '#1F2937',          // Panel/card background
    topbar: 'linear-gradient(90deg, #051B51 0%, #00298B 100%)', // TopBar gradient background
    table: '#10151a',          // Table background color (same as dashboard)
  },
  
  // Accent Colors
  accent: {
    primary: '#2496ED',        // Docker blue
    secondary: '#1B7FC4',      // Slightly darker variant for hover/active states
    success: '#06a58c',        // Dashboard green success/active colour
    lightBlue: '#4ca2fa',      // Dashboard light blue text colour
  },
  
  // Text Colors
  text: {
    primary: '#FFFFFF',        // White
    secondary: '#C9D1D9',      // Light grey
    muted: '#8B949E',          // Muted text for section labels
  },
  
  // Status Colors
  status: {
    success: '#06a58c',        // Dashboard green success/active colour
    warning: '#F2C94C',        // Warning yellow
    error: '#F85149',          // Error red
  },
  
  // Border & Divider Colors
  border: {
    primary: '#303234',        // Navigation selection color
    secondary: 'rgba(36, 150, 237, 0.1)', // Hover state background
  },
  
  // Interactive States
  interactive: {
    hover: '#19222a',          // Dashboard hover row
    active: 'rgba(27, 127, 196, 0.2)', // Active state background
    focus: 'rgba(36, 150, 237, 0.2)',  // Focus state
    selection: '#303234',      // Navigation selection
  },
} as const;

// Type-safe color access
export type DockerColorKey = keyof typeof dockerColors;
export type DockerColorValue = typeof dockerColors[DockerColorKey];
