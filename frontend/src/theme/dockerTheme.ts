// Docker Theme - MINIMAL VERSION for memory efficiency
// Following TypeScript memory management principles strictly
// MAXIMUM 5-6 component overrides, simple types, no complex structures

import { createTheme } from '@mui/material/styles';

// Create minimal theme with only essential overrides
export const dockerTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#007FFF',      // Docker blue
      light: '#1E90FF',     // Lighter blue
      dark: '#004499',      // Deeper navy
      contrastText: '#FFFFFF',
    },
    secondary: {
      main: '#28A745',      // Success green
      light: '#4CAF50',     // Lighter green
      dark: '#1B5E20',      // Darker green
      contrastText: '#FFFFFF',
    },
    error: {
      main: '#DC3545',      // Error red
      light: '#EF5350',     // Lighter red
      dark: '#C62828',      // Darker red
      contrastText: '#FFFFFF',
    },
    warning: {
      main: '#FFC107',      // Warning yellow
      light: '#FFD54F',     // Lighter yellow
      dark: '#F57F17',      // Darker yellow
      contrastText: '#000000',
    },
    info: {
      main: '#007FFF',      // Info blue
      light: '#1E90FF',     // Lighter blue
      dark: '#004499',      // Darker blue
      contrastText: '#FFFFFF',
    },
    success: {
      main: '#28A745',      // Success green
      light: '#4CAF50',     // Lighter green
      dark: '#1B5E20',      // Darker green
      contrastText: '#FFFFFF',
    },
    background: {
      default: '#0D1117',   // Deep charcoal
      paper: '#1B1F23',     // Slightly lighter
    },
    text: {
      primary: '#FFFFFF',   // High-contrast white
      secondary: '#8B949E', // Soft gray
    },
    divider: 'rgba(255,255,255,0.08)',
  },
  
  typography: {
    fontFamily: '"Inter", "Roboto", sans-serif',
    h1: { 
      fontSize: '28px', 
      fontWeight: 600,
      lineHeight: 1.2,
      letterSpacing: '-0.02em',
    },
    h2: { 
      fontSize: '22px', 
      fontWeight: 600,
      lineHeight: 1.3,
      letterSpacing: '-0.01em',
    },
    h3: { 
      fontSize: '18px', 
      fontWeight: 600,
      lineHeight: 1.4,
    },
    body1: { 
      fontSize: '16px',
      lineHeight: 1.5,
    },
    body2: { 
      fontSize: '14px',
      lineHeight: 1.5,
    },
    button: { 
      textTransform: 'none',
      lineHeight: 1.4,
      letterSpacing: '0.02em',
    },
  },
  
  shape: {
    borderRadius: 8,
  },
  
  // MAXIMUM 5-6 component overrides for memory efficiency
  components: {
    MuiCard: {
      styleOverrides: {
        root: {
          backgroundColor: '#1B1F23',
          borderRadius: 8,
          boxShadow: '0px 4px 12px rgba(0,0,0,0.2)',
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          textTransform: 'none',
          fontWeight: 500,
        },
        contained: {
          '&:hover': {
            backgroundColor: '#1E90FF', // Lighter blue on hover
          },
        },
        outlined: {
          '&:hover': {
            backgroundColor: 'rgba(255,255,255,0.04)', // Subtle hover effect
          },
        },
      },
    },
  },
});

export default dockerTheme;
