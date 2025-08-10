import { axe, toHaveNoViolations } from 'jest-axe';
import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

// Extend Jest matchers for accessibility testing
expect.extend(toHaveNoViolations);

// ============================================================================
// ACCESSIBILITY TESTING HELPERS
// ============================================================================

/**
 * Test component for accessibility compliance using jest-axe
 * @param container - The container element to test
 * @param options - Axe testing options
 * @returns Promise that resolves when accessibility test completes
 */
export const testAccessibility = async (
  container: Element, 
  options?: any
): Promise<void> => {
  const results = await axe(container, options);
  expect(results).toHaveNoViolations();
};

/**
 * Test component for specific accessibility issues
 * @param container - The container element to test
 * @param rules - Specific accessibility rules to test
 * @returns Promise that resolves with accessibility results
 */
export const testSpecificAccessibility = async (
  container: Element,
  rules: string[] = []
): Promise<any> => {
  const results = await axe(container, { 
    rules: rules.reduce((acc, rule) => ({ ...acc, [rule]: { enabled: true } }), {})
  });
  return results;
};

// ============================================================================
// RESPONSIVE TESTING HELPERS
// ============================================================================

/**
 * Mock window resize for responsive testing
 * @param width - Viewport width
 * @param height - Viewport height
 */
export const mockViewport = (width: number, height: number = 768): void => {
  Object.defineProperty(window, 'innerWidth', {
    writable: true,
    configurable: true,
    value: width,
  });
  
  Object.defineProperty(window, 'innerHeight', {
    writable: true,
    configurable: true,
    value: height,
  });
  
  // Trigger resize event
  window.dispatchEvent(new Event('resize'));
};

/**
 * Test component at different viewport sizes
 * @param component - Component to test
 * @param testFn - Test function to run at each breakpoint
 */
export const testResponsiveBehavior = async (
  component: React.ReactElement,
  testFn: (width: number, description: string) => Promise<void>
): Promise<void> => {
  const breakpoints = [
    { width: 375, description: 'mobile' },
    { width: 768, description: 'tablet' },
    { width: 1024, description: 'desktop' },
    { width: 1440, description: 'large desktop' }
  ];
  
  for (const breakpoint of breakpoints) {
    mockViewport(breakpoint.width);
    await testFn(breakpoint.width, breakpoint.description);
  }
};

// ============================================================================
// USER INTERACTION HELPERS
// ============================================================================

/**
 * Create a user event instance with common setup
 * @returns Configured user event instance
 */
export const createUserEvent = () => {
  return userEvent;
};

/**
 * Wait for element to appear with timeout
 * @param queryFn - Query function to find element
 * @param timeout - Timeout in milliseconds
 * @returns Promise that resolves when element appears
 */
export const waitForElement = async (
  queryFn: () => Element | null,
  timeout: number = 5000
): Promise<Element> => {
  return waitFor(() => {
    const element = queryFn();
    if (!element) throw new Error('Element not found');
    return element;
  }, { timeout });
};

/**
 * Wait for element to disappear with timeout
 * @param queryFn - Query function to find element
 * @param timeout - Timeout in milliseconds
 * @returns Promise that resolves when element disappears
 */
export const waitForElementToDisappear = async (
  queryFn: () => Element | null,
  timeout: number = 5000
): Promise<void> => {
  return waitFor(() => expect(queryFn()).not.toBeInTheDocument(), { timeout });
};

// ============================================================================
// COMMON ASSERTION HELPERS
// ============================================================================

/**
 * Assert that loading state is displayed
 */
export const expectLoadingState = (): void => {
  expect(screen.getByRole('progressbar')).toBeInTheDocument();
};

/**
 * Assert that loading state is not displayed
 */
export const expectNoLoadingState = (): void => {
  expect(screen.queryByRole('progressbar')).not.toBeInTheDocument();
};

/**
 * Assert that error state is displayed
 * @param errorMessage - Expected error message (optional)
 */
export const expectErrorState = (errorMessage?: string): void => {
  if (errorMessage) {
    expect(screen.getByText(errorMessage)).toBeInTheDocument();
  } else {
    expect(screen.getByRole('alert')).toBeInTheDocument();
  }
};

/**
 * Assert that no error state is displayed
 */
export const expectNoErrorState = (): void => {
  expect(screen.queryByRole('alert')).not.toBeInTheDocument();
};

/**
 * Assert that empty state is displayed
 * @param emptyMessage - Expected empty state message (optional)
 */
export const expectEmptyState = (emptyMessage?: string): void => {
  if (emptyMessage) {
    expect(screen.getByText(emptyMessage)).toBeInTheDocument();
  } else {
    // Look for common empty state indicators
    const emptyIndicators = [
      /no data/i,
      /empty/i,
      /no results/i,
      /nothing to display/i
    ];
    
    const found = emptyIndicators.some(pattern => 
      screen.queryByText(pattern) !== null
    );
    
    expect(found).toBe(true);
  }
};

// ============================================================================
// FORM TESTING HELPERS
// ============================================================================

/**
 * Fill a form field with value
 * @param label - Field label or placeholder
 * @param value - Value to enter
 */
export const fillFormField = async (label: string, value: string): Promise<void> => {
  const user = createUserEvent();
  const field = screen.getByLabelText(label) || screen.getByPlaceholderText(label);
  await user.type(field, value);
};

/**
 * Select an option from a dropdown
 * @param label - Field label
 * @param option - Option text to select
 */
export const selectDropdownOption = async (label: string, option: string): Promise<void> => {
  const user = createUserEvent();
  const field = screen.getByLabelText(label);
  await user.click(field);
  const optionElement = screen.getByText(option);
  await user.click(optionElement);
};

/**
 * Submit a form
 * @param submitButtonText - Text of submit button
 */
export const submitForm = async (submitButtonText: string = 'Submit'): Promise<void> => {
  const user = createUserEvent();
  const submitButton = screen.getByRole('button', { name: submitButtonText });
  await user.click(submitButton);
};

// ============================================================================
// TABLE TESTING HELPERS
// ============================================================================

/**
 * Assert that table has expected number of rows
 * @param expectedRows - Expected number of data rows
 */
export const expectTableRows = (expectedRows: number): void => {
  const rows = screen.getAllByRole('row');
  // Subtract 1 for header row
  expect(rows.length - 1).toBe(expectedRows);
};

/**
 * Assert that table shows specific data
 * @param expectedData - Array of expected data strings
 */
export const expectTableData = (expectedData: string[]): void => {
  expectedData.forEach(data => {
    expect(screen.getByText(data)).toBeInTheDocument();
  });
};

/**
 * Assert that table has specific columns
 * @param expectedColumns - Array of expected column headers
 */
export const expectTableColumns = (expectedColumns: string[]): void => {
  expectedColumns.forEach(column => {
    expect(screen.getByRole('columnheader', { name: column })).toBeInTheDocument();
  });
};

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

/**
 * Mock console methods to suppress noise during tests
 * @param methods - Console methods to mock
 */
export const mockConsole = (methods: ('warn' | 'error' | 'log' | 'info')[] = ['warn', 'error']): void => {
  methods.forEach(method => {
    jest.spyOn(console, method).mockImplementation(() => {});
  });
};

/**
 * Restore console methods after mocking
 * @param methods - Console methods to restore
 */
export const restoreConsole = (methods: ('warn' | 'error' | 'log' | 'info')[] = ['warn', 'error']): void => {
  methods.forEach(method => {
    jest.restoreAllMocks();
  });
};

/**
 * Create a mock function that returns a promise
 * @param returnValue - Value to return when resolved
 * @param delay - Delay before resolving (optional)
 * @returns Mock function that returns a promise
 */
export const createAsyncMock = <T>(
  returnValue: T, 
  delay: number = 0
): jest.Mock<Promise<T>> => {
  return jest.fn().mockImplementation(() => 
    new Promise<T>(resolve => 
      setTimeout(() => resolve(returnValue), delay)
    )
  );
};
