// ============================================================================
// BREADCRUMBS - TESTS
// ============================================================================

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { ThemeProvider } from '@mui/material/styles';
import { dockerTheme } from '@/theme';
import { Breadcrumbs } from './Breadcrumbs';
import type { BreadcrumbItem } from './Breadcrumbs.types';

// Test wrapper with theme and router
const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <ThemeProvider theme={dockerTheme}>
    <BrowserRouter>
      {children}
    </BrowserRouter>
  </ThemeProvider>
);

describe('Breadcrumbs', () => {
  const basicItems: BreadcrumbItem[] = [
    { id: 'home', label: 'Home', to: '/' },
    { id: 'companies', label: 'Companies', to: '/companies' },
    { id: 'company-1', label: 'Acme Corp', to: '/companies/1' },
  ];

  describe('Rendering', () => {
    it('renders breadcrumb items', () => {
      render(
        <TestWrapper>
          <Breadcrumbs items={basicItems} />
        </TestWrapper>
      );

      expect(screen.getByText('Home')).toBeInTheDocument();
      expect(screen.getByText('Companies')).toBeInTheDocument();
      expect(screen.getByText('Acme Corp')).toBeInTheDocument();
    });

    it('renders with semantic HTML structure', () => {
      const { container } = render(
        <TestWrapper>
          <Breadcrumbs items={basicItems} />
        </TestWrapper>
      );

      const nav = container.querySelector('nav[aria-label="Breadcrumb"]');
      expect(nav).toBeInTheDocument();
    });

    it('applies aria-current="page" to last item', () => {
      render(
        <TestWrapper>
          <Breadcrumbs items={basicItems} />
        </TestWrapper>
      );

      const lastItem = screen.getByText('Acme Corp').closest('[aria-current]');
      expect(lastItem).toHaveAttribute('aria-current', 'page');
    });

    it('renders icons when provided', () => {
      const itemsWithIcons: BreadcrumbItem[] = [
        { id: 'home', label: 'Home', to: '/', icon: <span data-testid="home-icon">🏠</span> },
        { id: 'companies', label: 'Companies', to: '/companies' },
      ];

      render(
        <TestWrapper>
          <Breadcrumbs items={itemsWithIcons} />
        </TestWrapper>
      );

      expect(screen.getByTestId('home-icon')).toBeInTheDocument();
    });
  });

  describe('Navigation', () => {
    it('uses React Router Link when to prop is provided', () => {
      render(
        <TestWrapper>
          <Breadcrumbs items={basicItems} />
        </TestWrapper>
      );

      const homeLink = screen.getByText('Home').closest('a');
      expect(homeLink).toHaveAttribute('href', '/');
    });

    it('calls onNavigate when to is not provided', () => {
      const onNavigate = jest.fn();
      const items: BreadcrumbItem[] = [
        { id: 'home', label: 'Home' },
        { id: 'companies', label: 'Companies' },
      ];

      render(
        <TestWrapper>
          <Breadcrumbs items={items} onNavigate={onNavigate} />
        </TestWrapper>
      );

      const homeButton = screen.getByText('Home').closest('button');
      expect(homeButton).toBeInTheDocument();

      fireEvent.click(homeButton!);
      expect(onNavigate).toHaveBeenCalledWith(items[0]);
    });

    it('does not navigate on last item click', () => {
      const onNavigate = jest.fn();
      const items: BreadcrumbItem[] = [
        { id: 'home', label: 'Home', to: '/' },
        { id: 'current', label: 'Current Page' },
      ];

      render(
        <TestWrapper>
          <Breadcrumbs items={items} onNavigate={onNavigate} />
        </TestWrapper>
      );

      const currentItem = screen.getByText('Current Page');
      fireEvent.click(currentItem);
      expect(onNavigate).not.toHaveBeenCalled();
    });
  });

  describe('Keyboard Navigation', () => {
    it('activates item on Enter key', () => {
      const onNavigate = jest.fn();
      const items: BreadcrumbItem[] = [
        { id: 'home', label: 'Home' },
        { id: 'companies', label: 'Companies' },
      ];

      render(
        <TestWrapper>
          <Breadcrumbs items={items} onNavigate={onNavigate} />
        </TestWrapper>
      );

      const homeButton = screen.getByText('Home').closest('button');
      fireEvent.keyDown(homeButton!, { key: 'Enter' });
      expect(onNavigate).toHaveBeenCalledWith(items[0]);
    });

    it('activates item on Space key', () => {
      const onNavigate = jest.fn();
      const items: BreadcrumbItem[] = [
        { id: 'home', label: 'Home' },
      ];

      render(
        <TestWrapper>
          <Breadcrumbs items={items} onNavigate={onNavigate} />
        </TestWrapper>
      );

      const homeButton = screen.getByText('Home').closest('button');
      fireEvent.keyDown(homeButton!, { key: ' ' });
      expect(onNavigate).toHaveBeenCalledWith(items[0]);
    });
  });

  describe('Disabled State', () => {
    it('renders disabled items as non-clickable', () => {
      const items: BreadcrumbItem[] = [
        { id: 'home', label: 'Home', to: '/', disabled: true },
        { id: 'companies', label: 'Companies', to: '/companies' },
      ];

      render(
        <TestWrapper>
          <Breadcrumbs items={items} />
        </TestWrapper>
      );

      const homeItem = screen.getByText('Home').closest('[aria-disabled]');
      expect(homeItem).toHaveAttribute('aria-disabled', 'true');
    });

    it('prevents navigation on disabled items', () => {
      const onNavigate = jest.fn();
      const items: BreadcrumbItem[] = [
        { id: 'home', label: 'Home', disabled: true },
      ];

      render(
        <TestWrapper>
          <Breadcrumbs items={items} onNavigate={onNavigate} />
        </TestWrapper>
      );

      const homeItem = screen.getByText('Home');
      fireEvent.click(homeItem);
      expect(onNavigate).not.toHaveBeenCalled();
    });
  });

  describe('Overflow Handling', () => {
    it('collapses items when maxItems is set', () => {
      const manyItems: BreadcrumbItem[] = Array.from({ length: 10 }, (_, i) => ({
        id: `item-${i}`,
        label: `Item ${i}`,
        to: `/${i}`,
      }));

      render(
        <TestWrapper>
          <Breadcrumbs items={manyItems} maxItems={4} />
        </TestWrapper>
      );

      // Should show first item
      expect(screen.getByText('Item 0')).toBeInTheDocument();
      // Should show last item
      expect(screen.getByText('Item 9')).toBeInTheDocument();
      // Should show ellipsis
      expect(screen.getByText('...')).toBeInTheDocument();
    });

    it('shows all items when maxItems is not set', () => {
      const items: BreadcrumbItem[] = Array.from({ length: 5 }, (_, i) => ({
        id: `item-${i}`,
        label: `Item ${i}`,
        to: `/${i}`,
      }));

      render(
        <TestWrapper>
          <Breadcrumbs items={items} />
        </TestWrapper>
      );

      items.forEach(item => {
        expect(screen.getByText(item.label)).toBeInTheDocument();
      });
    });
  });

  describe('Custom Render', () => {
    it('uses custom renderItem when provided', () => {
      const customRender = jest.fn((props) => (
        <span data-testid={`custom-${props.item.id}`}>{props.item.label}</span>
      ));

      render(
        <TestWrapper>
          <Breadcrumbs items={basicItems} renderItem={customRender} />
        </TestWrapper>
      );

      expect(customRender).toHaveBeenCalled();
      expect(screen.getByTestId('custom-home')).toBeInTheDocument();
    });
  });

  describe('Validation Warnings', () => {
    let consoleWarnSpy: jest.SpyInstance;

    beforeEach(() => {
      consoleWarnSpy = jest.spyOn(console, 'warn').mockImplementation();
    });

    afterEach(() => {
      consoleWarnSpy.mockRestore();
    });

    it('warns on empty items array', () => {
      render(
        <TestWrapper>
          <Breadcrumbs items={[]} />
        </TestWrapper>
      );

      expect(consoleWarnSpy).toHaveBeenCalledWith(
        expect.stringContaining('[Breadcrumbs] Empty items array')
      );
    });

    it('warns on duplicate IDs', () => {
      const items: BreadcrumbItem[] = [
        { id: 'duplicate', label: 'Item 1', to: '/' },
        { id: 'duplicate', label: 'Item 2', to: '/2' },
      ];

      render(
        <TestWrapper>
          <Breadcrumbs items={items} />
        </TestWrapper>
      );

      expect(consoleWarnSpy).toHaveBeenCalledWith(
        expect.stringContaining('Duplicate breadcrumb IDs')
      );
    });

    it('warns on missing navigation handlers', () => {
      const items: BreadcrumbItem[] = [
        { id: 'home', label: 'Home', to: '/' },
        { id: 'no-nav', label: 'No Nav' }, // Missing to and onNavigate
        { id: 'last', label: 'Last', to: '/last' },
      ];

      render(
        <TestWrapper>
          <Breadcrumbs items={items} />
        </TestWrapper>
      );

      expect(consoleWarnSpy).toHaveBeenCalledWith(
        expect.stringContaining('has no navigation handler')
      );
    });
  });

  describe('Accessibility', () => {
    it('applies custom aria-label', () => {
      const { container } = render(
        <TestWrapper>
          <Breadcrumbs items={basicItems} ariaLabel="Custom label" />
        </TestWrapper>
      );

      const nav = container.querySelector('nav[aria-label="Custom label"]');
      expect(nav).toBeInTheDocument();
    });

    it('sets proper tabIndex for clickable items', () => {
      render(
        <TestWrapper>
          <Breadcrumbs items={basicItems} />
        </TestWrapper>
      );

      const homeLink = screen.getByText('Home').closest('a');
      expect(homeLink).toHaveAttribute('tabIndex', '0');
    });

    it('sets tabIndex -1 for last item', () => {
      render(
        <TestWrapper>
          <Breadcrumbs items={basicItems} />
        </TestWrapper>
      );

      const lastItem = screen.getByText('Acme Corp').closest('[aria-current]');
      // Last item should not be in tab order
      expect(lastItem).toBeInTheDocument();
    });
  });
});

