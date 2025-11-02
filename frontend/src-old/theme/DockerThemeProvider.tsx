// Docker Theme Provider - Wraps MUI ThemeProvider with our Docker theme
// Following TypeScript memory management principles

import React from 'react';
import { ThemeProvider } from '@mui/material/styles';
import { CssBaseline } from '@mui/material';
import { dockerTheme } from './dockerTheme';

interface DockerThemeProviderProps {
  children: React.ReactNode;
}

export const DockerThemeProvider: React.FC<DockerThemeProviderProps> = ({ children }) => {
  return (
    <ThemeProvider theme={dockerTheme}>
      <CssBaseline />
      {children}
    </ThemeProvider>
  );
};

export default DockerThemeProvider;
