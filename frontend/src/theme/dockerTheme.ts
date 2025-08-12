// Docker Theme - Updated with new color specifications
// Following TypeScript memory management principles strictly
// MAXIMUM 5-6 component overrides, simple types, no complex structures

import { createTheme } from '@mui/material/styles';

// Docker Spacing System - Following spec requirements
export const dockerSpacing = {
  xs: 4,      // 4px
  sm: 8,      // 8px
  md: 16,     // 16px - inner padding for cards (spec requirement)
  lg: 24,     // 24px - outer padding between sections (spec requirement)
  xl: 32,     // 32px - major section spacing
  xxl: 48,    // 48px - page-level spacing
} as const;

// Create minimal theme with only essential overrides
export const dockerTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#2496ED',      // Docker blue
      light: '#1B7FC4',     // Slightly darker variant
      dark: '#1B7FC4',      // Darker variant for hover/active
      contrastText: '#FFFFFF',
    },
    secondary: {
      main: '#06a58c',      // Dashboard green success/active colour
      light: '#06a58c',     // Dashboard green success/active colour
      dark: '#06a58c',      // Dashboard green success/active colour
      contrastText: '#FFFFFF',
    },
    error: {
      main: '#F85149',      // Error red
      light: '#F85149',     // Error red
      dark: '#F85149',      // Error red
      contrastText: '#FFFFFF',
    },
    warning: {
      main: '#F2C94C',      // Warning yellow
      light: '#F2C94C',     // Warning yellow
      dark: '#F2C94C',      // Warning yellow
      contrastText: '#000000',
    },
    info: {
      main: '#4ca2fa',      // Dashboard light blue text colour
      light: '#2496ED',     // Docker blue
      dark: '#1B7FC4',      // Darker blue
      contrastText: '#FFFFFF',
    },
    success: {
      main: '#06a58c',      // Dashboard green success/active colour
      light: '#06a58c',     // Dashboard green success/active colour
      dark: '#06a58c',      // Dashboard green success/active colour
      contrastText: '#FFFFFF',
    },
    background: {
      default: '#10151a',   // Main dashboard background
      paper: '#1F2937',     // Panel background
    },
    text: {
      primary: '#FFFFFF',   // White
      secondary: '#C9D1D9', // Light grey
    },
    divider: '#303234',     // Navigation selection color
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
          backgroundColor: '#1F2937',
          borderRadius: 8,
          boxShadow: '0px 1px 4px rgba(0,0,0,0.2)',
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
            backgroundColor: '#1B7FC4', // Darker blue on hover
          },
        },
        outlined: {
          '&:hover': {
            backgroundColor: '#19222a', // Dashboard hover row
          },
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          borderRadius: 6,
          fontWeight: 500,
          fontSize: '12px',
          height: '24px',
        },
        label: {
          padding: '0 8px',
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: 8,
            backgroundColor: '#1F2937', // Panel background
            '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
              borderColor: '#2496ED', // Docker blue focus
              borderWidth: 2,
            },
            '&:hover .MuiOutlinedInput-notchedOutline': {
              borderColor: '#303234', // Navigation selection color on hover
            },
          },
        },
      },
    },
    MuiTableContainer: {
      styleOverrides: {
        root: {
          backgroundColor: '#1F2937',
          borderRadius: 8,
          boxShadow: '0px 1px 4px rgba(0,0,0,0.2)',
          overflow: 'hidden',
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundColor: '#1F2937',
          borderRadius: 8,
          boxShadow: '0px 1px 4px rgba(0,0,0,0.2)',
        },
        outlined: {
          backgroundColor: '#10151a', // Same as dashboard background
        },
      },
    },
    MuiTableHead: {
      styleOverrides: {
        root: {
          backgroundColor: '#070b0d', // Navigation sidebar background for headers
          '& .MuiTableCell-head': {
            fontWeight: 600,
            fontSize: '14px',
            color: '#FFFFFF',
            borderBottom: '1px solid #303234',
          },
        },
      },
    },
    MuiTableBody: {
      styleOverrides: {
        root: {
          '& .MuiTableRow-root:nth-of-type(even)': {
            backgroundColor: 'rgba(255,255,255,0.02)', // Alternating row background
          },
          '& .MuiTableRow-root:hover': {
            backgroundColor: '#19222a', // Dashboard hover row
          },
        },
      },
    },
    MuiTableCell: {
      styleOverrides: {
        root: {
          borderBottom: '1px solid #303234',
          padding: '12px 16px',
          color: '#FFFFFF',
          fontSize: '14px',
        },
      },
    },
    MuiDivider: {
      styleOverrides: {
        root: {
          backgroundColor: '#303234',
          margin: '16px 0',
        },
      },
    },
    MuiIconButton: {
      styleOverrides: {
        root: {
          borderRadius: 6,
          '&:hover': {
            backgroundColor: '#19222a', // Dashboard hover row
          },
        },
      },
    },
  },
});

export default dockerTheme;
