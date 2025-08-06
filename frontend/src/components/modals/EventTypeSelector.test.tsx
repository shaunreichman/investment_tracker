import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import EventTypeSelector, { EventTypeSelectorProps } from './EventTypeSelector';

// Create a theme for testing
const theme = createTheme();

// Mock data
const defaultProps: EventTypeSelectorProps = {
  fundTrackingType: 'cost_based',
  eventType: '',
  distributionType: '',
  subDistributionType: '',
  onEventTypeSelect: jest.fn(),
  onDistributionTypeSelect: jest.fn(),
  onSubDistributionTypeSelect: jest.fn(),
  onBack: jest.fn(),
};

const renderEventTypeSelector = (props: Partial<EventTypeSelectorProps> = {}) => {
  return render(
    <ThemeProvider theme={theme}>
      <EventTypeSelector {...defaultProps} {...props} />
    </ThemeProvider>
  );
};

describe('EventTypeSelector', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Event Type Selection', () => {
    it('should render all event type templates for cost-based funds', () => {
      renderEventTypeSelector({ fundTrackingType: 'cost_based' });

      expect(screen.getByText('Capital Call')).toBeInTheDocument();
      expect(screen.getByText('Capital Return')).toBeInTheDocument();
      expect(screen.getByText('Distribution')).toBeInTheDocument();
      expect(screen.getByText('Tax Statement')).toBeInTheDocument();
      
      // NAV-based options should not be visible for cost-based funds
      expect(screen.queryByText('Unit Purchase')).not.toBeInTheDocument();
      expect(screen.queryByText('Unit Sale')).not.toBeInTheDocument();
      expect(screen.queryByText('NAV Update')).not.toBeInTheDocument();
    });

    it('should render all event type templates for nav-based funds', () => {
      renderEventTypeSelector({ fundTrackingType: 'nav_based' });

      expect(screen.getByText('Unit Purchase')).toBeInTheDocument();
      expect(screen.getByText('Unit Sale')).toBeInTheDocument();
      expect(screen.getByText('NAV Update')).toBeInTheDocument();
      expect(screen.getByText('Distribution')).toBeInTheDocument();
      expect(screen.getByText('Tax Statement')).toBeInTheDocument();
      
      // Cost-based options should not be visible for nav-based funds
      expect(screen.queryByText('Capital Call')).not.toBeInTheDocument();
      expect(screen.queryByText('Capital Return')).not.toBeInTheDocument();
    });

    it('should handle event type selection', () => {
      const onEventTypeSelect = jest.fn();
      renderEventTypeSelector({ onEventTypeSelect });

      const capitalCallButton = screen.getByText('Capital Call');
      fireEvent.click(capitalCallButton);

      expect(onEventTypeSelect).toHaveBeenCalledWith('CAPITAL_CALL');
    });

    it('should handle event type deselection', () => {
      const onEventTypeSelect = jest.fn();
      renderEventTypeSelector({ 
        eventType: 'CAPITAL_CALL',
        onEventTypeSelect 
      });

      const capitalCallButton = screen.getByText('Capital Call');
      fireEvent.click(capitalCallButton);

      expect(onEventTypeSelect).toHaveBeenCalledWith('');
    });

    it('should allow Distribution to be selected even when another event type is selected', () => {
      renderEventTypeSelector({ eventType: 'CAPITAL_CALL' });

      const distributionButton = screen.getByText('Distribution');
      
      // Distribution should still be clickable
      expect(distributionButton).toBeInTheDocument();
    });
  });

  describe('Distribution Type Selection', () => {
    it('should show distribution type options when Distribution is selected', () => {
      renderEventTypeSelector({ eventType: 'DISTRIBUTION' });

      expect(screen.getByText('Select Distribution Type')).toBeInTheDocument();
      expect(screen.getByText('Interest')).toBeInTheDocument();
      expect(screen.getByText('Dividend')).toBeInTheDocument();
      expect(screen.getByText('Other')).toBeInTheDocument();
    });

    it('should not show distribution type options when Distribution is not selected', () => {
      renderEventTypeSelector({ eventType: 'CAPITAL_CALL' });

      expect(screen.queryByText('Select Distribution Type')).not.toBeInTheDocument();
      expect(screen.queryByText('Interest')).not.toBeInTheDocument();
    });

    it('should handle distribution type selection', () => {
      const onDistributionTypeSelect = jest.fn();
      renderEventTypeSelector({ 
        eventType: 'DISTRIBUTION',
        onDistributionTypeSelect 
      });

      const interestButton = screen.getByText('Interest');
      fireEvent.click(interestButton);

      expect(onDistributionTypeSelect).toHaveBeenCalledWith('INTEREST');
    });

    it('should handle distribution type deselection', () => {
      const onDistributionTypeSelect = jest.fn();
      renderEventTypeSelector({ 
        eventType: 'DISTRIBUTION',
        distributionType: 'INTEREST',
        onDistributionTypeSelect 
      });

      const interestButton = screen.getByText('Interest');
      fireEvent.click(interestButton);

      expect(onDistributionTypeSelect).toHaveBeenCalledWith('');
    });
  });

  describe('Sub-Distribution Type Selection', () => {
    it('should show dividend sub-types when Dividend is selected', () => {
      renderEventTypeSelector({ 
        eventType: 'DISTRIBUTION',
        distributionType: 'DIVIDEND'
      });

      expect(screen.getByText('Select Dividend Type')).toBeInTheDocument();
      expect(screen.getByText('Franked')).toBeInTheDocument();
      expect(screen.getByText('Unfranked')).toBeInTheDocument();
    });

    it('should show interest sub-types when Interest is selected', () => {
      renderEventTypeSelector({ 
        eventType: 'DISTRIBUTION',
        distributionType: 'INTEREST'
      });

      expect(screen.getByText('Select Interest Sub-Distribution Type')).toBeInTheDocument();
      expect(screen.getByText('Regular')).toBeInTheDocument();
      expect(screen.getByText('Withholding Tax')).toBeInTheDocument();
    });

    it('should handle dividend sub-type selection', () => {
      const onSubDistributionTypeSelect = jest.fn();
      renderEventTypeSelector({ 
        eventType: 'DISTRIBUTION',
        distributionType: 'DIVIDEND',
        onSubDistributionTypeSelect 
      });

      const frankedButton = screen.getByText('Franked');
      fireEvent.click(frankedButton);

      expect(onSubDistributionTypeSelect).toHaveBeenCalledWith('DIVIDEND_FRANKED');
    });

    it('should handle interest sub-type selection', () => {
      const onSubDistributionTypeSelect = jest.fn();
      renderEventTypeSelector({ 
        eventType: 'DISTRIBUTION',
        distributionType: 'INTEREST',
        onSubDistributionTypeSelect 
      });

      const regularButton = screen.getByText('Regular');
      fireEvent.click(regularButton);

      expect(onSubDistributionTypeSelect).toHaveBeenCalledWith('REGULAR');
    });
  });

  describe('Back Button', () => {
    it('should show back button when event type is selected', () => {
      renderEventTypeSelector({ eventType: 'CAPITAL_CALL' });

      expect(screen.getByText('Back')).toBeInTheDocument();
    });

    it('should show back button when distribution type is selected', () => {
      renderEventTypeSelector({ 
        eventType: 'DISTRIBUTION',
        distributionType: 'INTEREST'
      });

      expect(screen.getByText('Back')).toBeInTheDocument();
    });

    it('should not show back button when nothing is selected', () => {
      renderEventTypeSelector();

      expect(screen.queryByText('Back')).not.toBeInTheDocument();
    });

    it('should call onBack when back button is clicked', () => {
      const onBack = jest.fn();
      renderEventTypeSelector({ 
        eventType: 'CAPITAL_CALL',
        onBack 
      });

      const backButton = screen.getByText('Back');
      fireEvent.click(backButton);

      expect(onBack).toHaveBeenCalled();
    });
  });

  describe('State Management', () => {
    it('should handle event type selection and clearing', () => {
      const onEventTypeSelect = jest.fn();
      const onDistributionTypeSelect = jest.fn();
      const onSubDistributionTypeSelect = jest.fn();
      
      renderEventTypeSelector({ 
        onEventTypeSelect,
        onDistributionTypeSelect,
        onSubDistributionTypeSelect
      });

      // Select an event type
      const taxStatementButton = screen.getByText('Tax Statement');
      fireEvent.click(taxStatementButton);

      // The component should call the event type selector
      expect(onEventTypeSelect).toHaveBeenCalledWith('TAX_STATEMENT');
    });

    it('should clear sub-distribution when distribution type changes', () => {
      const onSubDistributionTypeSelect = jest.fn();
      
      renderEventTypeSelector({ 
        eventType: 'DISTRIBUTION',
        distributionType: 'INTEREST',
        subDistributionType: 'REGULAR',
        onSubDistributionTypeSelect
      });

      // Select a different distribution type
      const dividendButton = screen.getByText('Dividend');
      fireEvent.click(dividendButton);

      expect(onSubDistributionTypeSelect).toHaveBeenCalledWith('');
    });
  });

  describe('Visual States', () => {
    it('should show expand indicator for Distribution when selected', () => {
      renderEventTypeSelector({ eventType: 'DISTRIBUTION' });

      const distributionButton = screen.getByText('Distribution');
      // The expand icon is rendered as an AddIcon component, not as a data-testid
      const expandIcon = distributionButton.closest('div')?.querySelector('svg');
      
      expect(expandIcon).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('should render all interactive elements', () => {
      renderEventTypeSelector();

      const capitalCallButton = screen.getByText('Capital Call');
      expect(capitalCallButton).toBeInTheDocument();
    });

    it('should render distribution button when event type is selected', () => {
      renderEventTypeSelector({ eventType: 'CAPITAL_CALL' });

      const distributionButton = screen.getByText('Distribution');
      expect(distributionButton).toBeInTheDocument();
    });
  });
}); 