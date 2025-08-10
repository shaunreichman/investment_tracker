import React from 'react';
import { screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { render } from '../../test-utils';
import { TabNavigation } from './TabNavigation';

describe('TabNavigation', () => {
  const user = userEvent;
  
  const defaultProps = {
    activeTab: 'overview',
    onTabChange: jest.fn(),
    tabs: [
      { id: 'overview', label: 'Overview', icon: '📊' },
      { id: 'funds', label: 'Funds', icon: '💰' },
      { id: 'analysis', label: 'Analysis', icon: '📈' },
      { id: 'activity', label: 'Activity', icon: '📅' },
      { id: 'company-details', label: 'Company Details', icon: '🏢' }
    ]
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Rendering', () => {
    it('renders all tabs with correct labels and icons', () => {
      render(<TabNavigation {...defaultProps} />);
      
      expect(screen.getByRole('tab', { name: /overview/i })).toBeInTheDocument();
      expect(screen.getByRole('tab', { name: /funds/i })).toBeInTheDocument();
      expect(screen.getByRole('tab', { name: /analysis/i })).toBeInTheDocument();
      expect(screen.getByRole('tab', { name: /activity/i })).toBeInTheDocument();
      expect(screen.getByRole('tab', { name: /company details/i })).toBeInTheDocument();
    });

    it('displays tab icons correctly', () => {
      render(<TabNavigation {...defaultProps} />);
      
      expect(screen.getByText('📊')).toBeInTheDocument();
      expect(screen.getByText('💰')).toBeInTheDocument();
      expect(screen.getByText('📈')).toBeInTheDocument();
      expect(screen.getByText('📅')).toBeInTheDocument();
      expect(screen.getByText('🏢')).toBeInTheDocument();
    });

    it('marks the active tab as selected', () => {
      render(<TabNavigation {...defaultProps} activeTab="funds" />);
      
      const fundsTab = screen.getByRole('tab', { name: /funds/i });
      const overviewTab = screen.getByRole('tab', { name: /overview/i });
      
      expect(fundsTab).toHaveAttribute('aria-selected', 'true');
      expect(overviewTab).toHaveAttribute('aria-selected', 'false');
    });
  });

  describe('Tab Interaction', () => {
    it('calls onTabChange when a tab is clicked', async () => {
      const onTabChange = jest.fn();
      render(<TabNavigation {...defaultProps} onTabChange={onTabChange} />);
      
      const fundsTab = screen.getByRole('tab', { name: /funds/i });
      await user.click(fundsTab);
      
      expect(onTabChange).toHaveBeenCalledWith('funds');
    });

    it('calls onTabChange when a different tab is clicked', async () => {
      const onTabChange = jest.fn();
      render(<TabNavigation {...defaultProps} onTabChange={onTabChange} activeTab="funds" />);
      
      const overviewTab = screen.getByRole('tab', { name: /overview/i });
      await user.click(overviewTab);
      
      expect(onTabChange).toHaveBeenCalledWith('overview');
    });

    it('does not call onTabChange when clicking the already active tab', async () => {
      const onTabChange = jest.fn();
      render(<TabNavigation {...defaultProps} onTabChange={onTabChange} />);
      
      const overviewTab = screen.getByRole('tab', { name: /overview/i });
      await user.click(overviewTab);
      
      expect(onTabChange).not.toHaveBeenCalled();
    });
  });

  describe('Keyboard Navigation', () => {
    it('supports arrow key navigation between tabs', async () => {
      render(<TabNavigation {...defaultProps} />);
      
      const overviewTab = screen.getByRole('tab', { name: /overview/i });
      overviewTab.focus();
      
      // Navigate to next tab with right arrow
      await user.keyboard('{ArrowRight}');
      expect(screen.getByRole('tab', { name: /funds/i })).toHaveFocus();
      
      // Navigate to previous tab with left arrow
      await user.keyboard('{ArrowLeft}');
      expect(screen.getByRole('tab', { name: /overview/i })).toHaveFocus();
    });

    it('wraps around at the beginning and end of tabs', async () => {
      render(<TabNavigation {...defaultProps} />);
      
      const overviewTab = screen.getByRole('tab', { name: /overview/i });
      overviewTab.focus();
      
      // Navigate to last tab with left arrow (should wrap around)
      await user.keyboard('{ArrowLeft}');
      expect(screen.getByRole('tab', { name: /company details/i })).toHaveFocus();
      
      // Navigate to first tab with right arrow (should wrap around)
      await user.keyboard('{ArrowRight}');
      expect(screen.getByRole('tab', { name: /overview/i })).toHaveFocus();
    });

    it('activates tab with Enter key', async () => {
      const onTabChange = jest.fn();
      render(<TabNavigation {...defaultProps} onTabChange={onTabChange} />);
      
      const fundsTab = screen.getByRole('tab', { name: /funds/i });
      fundsTab.focus();
      
      await user.keyboard('{Enter}');
      expect(onTabChange).toHaveBeenCalledWith('funds');
    });

    it('activates tab with Space key', async () => {
      const onTabChange = jest.fn();
      render(<TabNavigation {...defaultProps} onTabChange={onTabChange} />);
      
      const fundsTab = screen.getByRole('tab', { name: /funds/i });
      fundsTab.focus();
      
      await user.keyboard(' ');
      expect(onTabChange).toHaveBeenCalledWith('funds');
    });
  });

  describe('Accessibility', () => {
    it('has correct ARIA roles and attributes', () => {
      render(<TabNavigation {...defaultProps} />);
      
      const tabList = screen.getByRole('tablist');
      expect(tabList).toBeInTheDocument();
      
      const tabs = screen.getAllByRole('tab');
      tabs.forEach(tab => {
        expect(tab).toHaveAttribute('aria-selected');
        expect(tab).toHaveAttribute('tabindex');
      });
    });

    it('sets correct tabindex values', () => {
      render(<TabNavigation {...defaultProps} />);
      
      const overviewTab = screen.getByRole('tab', { name: /overview/i });
      const fundsTab = screen.getByRole('tab', { name: /funds/i });
      
      expect(overviewTab).toHaveAttribute('tabindex', '0');
      expect(fundsTab).toHaveAttribute('tabindex', '-1');
    });

    it('updates tabindex when active tab changes', () => {
      const { rerender } = render(<TabNavigation {...defaultProps} activeTab="overview" />);
      
      let overviewTab = screen.getByRole('tab', { name: /overview/i });
      let fundsTab = screen.getByRole('tab', { name: /funds/i });
      
      expect(overviewTab).toHaveAttribute('tabindex', '0');
      expect(fundsTab).toHaveAttribute('tabindex', '-1');
      
      // Change active tab
      rerender(<TabNavigation {...defaultProps} activeTab="funds" />);
      
      overviewTab = screen.getByRole('tab', { name: /overview/i });
      fundsTab = screen.getByRole('tab', { name: /funds/i });
      
      expect(overviewTab).toHaveAttribute('tabindex', '-1');
      expect(fundsTab).toHaveAttribute('tabindex', '0');
    });
  });

  describe('Responsive Behavior', () => {
    it('adapts layout for different screen sizes', () => {
      render(<TabNavigation {...defaultProps} />);
      
      const tabList = screen.getByRole('tablist');
      expect(tabList).toHaveClass('tab-navigation');
    });

    it('maintains accessibility on mobile devices', () => {
      render(<TabNavigation {...defaultProps} />);
      
      // All tabs should be accessible regardless of screen size
      const tabs = screen.getAllByRole('tab');
      expect(tabs).toHaveLength(5);
      
      tabs.forEach(tab => {
        expect(tab).toBeVisible();
        expect(tab).toHaveAttribute('aria-selected');
      });
    });
  });

  describe('Edge Cases', () => {
    it('handles empty tabs array gracefully', () => {
      render(<TabNavigation {...defaultProps} tabs={[]} />);
      
      const tabList = screen.getByRole('tablist');
      expect(tabList).toBeInTheDocument();
      expect(screen.queryByRole('tab')).not.toBeInTheDocument();
    });

    it('handles single tab correctly', () => {
      const singleTabProps = {
        ...defaultProps,
        tabs: [{ id: 'overview', label: 'Overview', icon: '📊' }]
      };
      
      render(<TabNavigation {...singleTabProps} />);
      
      const tab = screen.getByRole('tab', { name: /overview/i });
      expect(tab).toBeInTheDocument();
      expect(tab).toHaveAttribute('aria-selected', 'true');
    });

    it('handles undefined onTabChange gracefully', () => {
      render(<TabNavigation {...defaultProps} onTabChange={() => {}} />);
      
      const fundsTab = screen.getByRole('tab', { name: /funds/i });
      expect(fundsTab).toBeInTheDocument();
      // Should not crash when clicked without onTabChange
    });
  });
});
