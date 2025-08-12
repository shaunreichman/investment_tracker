// Docker Color Palette - Separate module to avoid type intersections
// Following TypeScript memory management principles

export const dockerColors = {
  // Primary Background Colors
  background: {
    main: '#0D1117',        // Deep charcoal/blue-black
    surface: '#1B1F23',     // Slightly lighter dark
    panel: '#21262D',       // Panel/card background
    sidebar: '#161B22',     // Sidebar background
  },
  
  // Header & Navigation
  header: {
    primary: '#0066CC',     // Rich gradient blue start
    secondary: '#004499',   // Deeper navy
    accent: '#007FFF',      // Bright blue accent
  },
  
  // Accent Colors
  accent: {
    primary: '#007FFF',     // Primary blue
    secondary: '#1E90FF',   // Lighter blue
    success: '#28A745',     // Success green
    warning: '#FFC107',     // Warning yellow
    error: '#DC3545',       // Error red
  },
  
  // Text Colors
  text: {
    primary: '#FFFFFF',     // High-contrast white
    secondary: '#8B949E',   // Soft gray
    muted: '#6E7681',       // Muted text
  },
  
  // Border & Divider Colors
  border: {
    primary: 'rgba(255,255,255,0.08)',
    secondary: 'rgba(255,255,255,0.12)',
    accent: 'rgba(0,127,255,0.3)',
  },
  
  // Interactive States
  interactive: {
    hover: 'rgba(255,255,255,0.04)',
    active: 'rgba(0,127,255,0.1)',
    focus: 'rgba(0,127,255,0.2)',
  },
} as const;

// Type-safe color access
export type DockerColorKey = keyof typeof dockerColors;
export type DockerColorValue = typeof dockerColors[DockerColorKey];
