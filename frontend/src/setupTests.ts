// jest-dom adds custom jest matchers for asserting on DOM nodes.
// allows you to do things like:
// expect(element).toHaveTextContent(/react/i)
// learn more: https://github.com/testing-library/jest-dom
import '@testing-library/jest-dom';

// Silence React Router v7 future-flag warnings in tests
const originalWarn = console.warn;
// eslint-disable-next-line @typescript-eslint/no-explicit-any
console.warn = (...args: any[]) => {
  const msg = String(args[0] || '');
  if (msg.includes('React Router Future Flag Warning')) {
    return;
  }
  originalWarn(...args);
};
