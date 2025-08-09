import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import EventTypeSelector from './EventTypeSelector';

describe('EventTypeSelector', () => {
  const defaultProps = {
    fundTrackingType: 'cost_based' as const,
    eventType: '' as any,
    distributionType: '',
    subDistributionType: '',
    onEventTypeSelect: jest.fn(),
    onDistributionTypeSelect: jest.fn(),
    onSubDistributionTypeSelect: jest.fn(),
    onBack: jest.fn(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Create Mode', () => {
    it('should render event type cards', () => {
      render(<EventTypeSelector {...defaultProps} />);
      
      expect(screen.getByText('Capital Call')).toBeInTheDocument();
      expect(screen.getByText('Capital Return')).toBeInTheDocument();
      expect(screen.getByText('Distribution')).toBeInTheDocument();
    });

    it('should allow selecting event types', () => {
      render(<EventTypeSelector {...defaultProps} />);
      
      fireEvent.click(screen.getByText('Capital Call'));
      
      expect(defaultProps.onEventTypeSelect).toHaveBeenCalledWith('CAPITAL_CALL');
    });

    it('should show distribution type options when distribution is selected', () => {
      render(
        <EventTypeSelector 
          {...defaultProps} 
          eventType="DISTRIBUTION"
        />
      );
      
      expect(screen.getByText('Select Distribution Type')).toBeInTheDocument();
      expect(screen.getByText('Interest')).toBeInTheDocument();
      expect(screen.getByText('Dividend')).toBeInTheDocument();
      expect(screen.getByText('Other')).toBeInTheDocument();
    });

    it('should allow selecting distribution types', () => {
      render(
        <EventTypeSelector 
          {...defaultProps} 
          eventType="DISTRIBUTION"
        />
      );
      
      fireEvent.click(screen.getByText('Interest'));
      
      expect(defaultProps.onDistributionTypeSelect).toHaveBeenCalledWith('INTEREST');
    });

    it('should show sub-distribution options for interest', () => {
      render(
        <EventTypeSelector 
          {...defaultProps} 
          eventType="DISTRIBUTION"
          distributionType="INTEREST"
        />
      );
      
      expect(screen.getByText('Select Interest Sub-Distribution Type')).toBeInTheDocument();
      expect(screen.getByText('Regular')).toBeInTheDocument();
      expect(screen.getByText('Withholding Tax')).toBeInTheDocument();
    });

    it('should show sub-distribution options for dividend', () => {
      render(
        <EventTypeSelector 
          {...defaultProps} 
          eventType="DISTRIBUTION"
          distributionType="DIVIDEND"
        />
      );
      
      expect(screen.getByText('Select Dividend Type')).toBeInTheDocument();
      expect(screen.getByText('Franked')).toBeInTheDocument();
      expect(screen.getByText('Unfranked')).toBeInTheDocument();
    });
  });

  describe('Edit Mode', () => {
    it('should show edit mode info message', () => {
      render(
        <EventTypeSelector 
          {...defaultProps} 
          mode="edit"
          eventType="CAPITAL_CALL"
        />
      );
      
      expect(screen.getByText(/Event type cannot be changed in edit mode/)).toBeInTheDocument();
    });

    it('should disable all event type cards in edit mode', () => {
      render(
        <EventTypeSelector 
          {...defaultProps} 
          mode="edit"
          eventType="CAPITAL_CALL"
        />
      );
      
      fireEvent.click(screen.getByText('Capital Call'));
      
      expect(defaultProps.onEventTypeSelect).not.toHaveBeenCalled();
    });

    it('should show fixed distribution type label in edit mode', () => {
      render(
        <EventTypeSelector 
          {...defaultProps} 
          mode="edit"
          eventType="DISTRIBUTION"
          distributionType="INTEREST"
        />
      );
      
      expect(screen.getByText('Distribution Type (Fixed)')).toBeInTheDocument();
    });

    it('should disable distribution type selection in edit mode', () => {
      render(
        <EventTypeSelector 
          {...defaultProps} 
          mode="edit"
          eventType="DISTRIBUTION"
          distributionType="INTEREST"
        />
      );
      
      fireEvent.click(screen.getByText('Interest'));
      
      expect(defaultProps.onDistributionTypeSelect).not.toHaveBeenCalled();
    });

    it('should show fixed interest type label in edit mode', () => {
      render(
        <EventTypeSelector 
          {...defaultProps} 
          mode="edit"
          eventType="DISTRIBUTION"
          distributionType="INTEREST"
          subDistributionType="WITHHOLDING_TAX"
        />
      );
      
      expect(screen.getByText('Interest Type (Fixed)')).toBeInTheDocument();
    });

    it('should disable sub-distribution type selection in edit mode', () => {
      render(
        <EventTypeSelector 
          {...defaultProps} 
          mode="edit"
          eventType="DISTRIBUTION"
          distributionType="INTEREST"
          subDistributionType="WITHHOLDING_TAX"
        />
      );
      
      fireEvent.click(screen.getByText('Withholding Tax'));
      
      expect(defaultProps.onSubDistributionTypeSelect).not.toHaveBeenCalled();
    });

    it('should show fixed dividend type label in edit mode', () => {
      render(
        <EventTypeSelector 
          {...defaultProps} 
          mode="edit"
          eventType="DISTRIBUTION"
          distributionType="DIVIDEND"
          subDistributionType="DIVIDEND_FRANKED"
        />
      );
      
      expect(screen.getByText('Dividend Type (Fixed)')).toBeInTheDocument();
    });

    it('should disable dividend type selection in edit mode', () => {
      render(
        <EventTypeSelector 
          {...defaultProps} 
          mode="edit"
          eventType="DISTRIBUTION"
          distributionType="DIVIDEND"
          subDistributionType="DIVIDEND_FRANKED"
        />
      );
      
      fireEvent.click(screen.getByText('Franked'));
      
      expect(defaultProps.onSubDistributionTypeSelect).not.toHaveBeenCalled();
    });
  });

  describe('Fund Type Filtering', () => {
    it('should show only cost-based templates for cost-based funds', () => {
      render(
        <EventTypeSelector 
          {...defaultProps} 
          fundTrackingType="cost_based"
        />
      );
      
      expect(screen.getByText('Capital Call')).toBeInTheDocument();
      expect(screen.getByText('Capital Return')).toBeInTheDocument();
      expect(screen.getByText('Distribution')).toBeInTheDocument();
      expect(screen.queryByText('Unit Purchase')).not.toBeInTheDocument();
      expect(screen.queryByText('Unit Sale')).not.toBeInTheDocument();
      expect(screen.queryByText('NAV Update')).not.toBeInTheDocument();
    });

    it('should show only NAV-based templates for NAV-based funds', () => {
      render(
        <EventTypeSelector 
          {...defaultProps} 
          fundTrackingType="nav_based"
        />
      );
      
      expect(screen.getByText('Unit Purchase')).toBeInTheDocument();
      expect(screen.getByText('Unit Sale')).toBeInTheDocument();
      expect(screen.getByText('NAV Update')).toBeInTheDocument();
      expect(screen.getByText('Distribution')).toBeInTheDocument();
      expect(screen.queryByText('Capital Call')).not.toBeInTheDocument();
      expect(screen.queryByText('Capital Return')).not.toBeInTheDocument();
    });
  });
}); 