import React from 'react';
import { render, RenderOptions } from '@testing-library/react';

// ============================================================================
// TEST UTILITIES FOR TABLE COMPONENTS
// ============================================================================

/**
 * Custom render function for table components that automatically wraps them in proper table structure
 * This prevents HTML validation warnings about <tr> elements being children of <div>
 * 
 * Usage:
 * import { renderTableComponent } from '../test-utils';
 * 
 * renderTableComponent(<YourTableComponent {...props} />);
 */
export const renderTableComponent = (
  ui: React.ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>
) => {
  const Wrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
    <table>
      <tbody>
        {children}
      </tbody>
    </table>
  );

  return render(ui, { wrapper: Wrapper, ...options });
};

/**
 * Custom render function for table components that need a specific table structure
 * Useful when testing components that expect specific table attributes or classes
 */
export const renderTableComponentWithCustomWrapper = (
  ui: React.ReactElement,
  wrapperProps?: React.HTMLAttributes<HTMLTableElement>,
  options?: Omit<RenderOptions, 'wrapper'>
) => {
  const Wrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
    <table {...wrapperProps}>
      <tbody>
        {children}
      </tbody>
    </table>
  );

  return render(ui, { wrapper: Wrapper, ...options });
};
