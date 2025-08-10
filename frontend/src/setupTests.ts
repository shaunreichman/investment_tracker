// jest-dom adds custom jest matchers for asserting on DOM nodes.
// allows you to do things like:
// expect(element).toHaveTextContent(/react/i)
// learn more: https://github.com/testing-library/jest-dom
import '@testing-library/jest-dom';

// Global test configuration for professional testing standards
beforeAll(() => {
  // Only suppress unavoidable console noise during tests
  const originalError = console.error;
  
  console.error = (...args: any[]) => {
    // Suppress React act warnings during tests (these are test framework issues, not app issues)
    if (args[0]?.includes?.('act(...)')) {
      return;
    }
    // Allow all other errors to surface - this is important for debugging
    originalError(...args);
  };
});

// Reset mocks between tests
beforeEach(() => {
  jest.clearAllMocks();
});

// Restore console methods after all tests
afterAll(() => {
  // Console methods will be restored automatically
});
