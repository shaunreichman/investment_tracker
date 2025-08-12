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
      contrastText: '#FFFFFF',
    },
    background: {
      default: '#0D1117',   // Deep charcoal
      paper: '#1B1F23',     // Slightly lighter
    },
    text: {
      primary: '#FFFFFF',
      secondary: '#8B949E',
    },
    divider: 'rgba(255,255,255,0.08)',
  },
  
  typography: {
    fontFamily: '"Inter", "Roboto", sans-serif',
    h1: { fontSize: '28px', fontWeight: 600 },
    h2: { fontSize: '22px', fontWeight: 600 },
    h3: { fontSize: '18px', fontWeight: 600 },
    body1: { fontSize: '16px' },
    body2: { fontSize: '14px' },
    button: { textTransform: 'none' },
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
      },
    },
  },
});

export default dockerTheme;
