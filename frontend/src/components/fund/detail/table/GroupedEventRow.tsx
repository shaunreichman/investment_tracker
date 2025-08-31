import React from 'react';
import {
  TableRow,
  TableCell,
  Typography,
  Box,
  IconButton
} from '@mui/material';
import { Delete as DeleteIcon } from '@mui/icons-material';
import { ExtendedFundEvent, ExtendedFund, GroupType, FundType } from '../../../../types/api';
import { formatCurrency, formatDate } from '../../../../utils/formatters';
import { EventTypeChip } from '../../../ui/EventTypeChip';
import { GroupedEvent } from './useEventGrouping';

// ============================================================================
// GROUPED EVENT ROW COMPONENT
// ============================================================================

export interface GroupedEventRowProps {
  groupedEvent: GroupedEvent;
  fund: ExtendedFund;
  showTaxEvents: boolean;
  showNavUpdates: boolean;

  onDeleteEvent: (event: ExtendedFundEvent) => void;
}

/**
 * Component to render grouped event rows (interest + withholding tax combinations)
 * Updated to work with new flag-based grouping approach and handle TAX_STATEMENT groups
 */
const GroupedEventRowComponent: React.FC<GroupedEventRowProps> = ({
  groupedEvent,
  fund,
  showTaxEvents,
  showNavUpdates,

  onDeleteEvent
}) => {
  // CALCULATED: Extract events from the grouped event
  const { events, displayDate, displayDescription, groupType } = groupedEvent;
  const isNavBased = fund.tracking_type === FundType.NAV_BASED;

  // CALCULATED: Handle different group types
  if (groupType === GroupType.TAX_STATEMENT) {
    return (
      <TaxStatementGroupRow
        events={events as ExtendedFundEvent[]}
        fund={fund}
        showTaxEvents={showTaxEvents}
        showNavUpdates={showNavUpdates}
        displayDate={displayDate}
        displayDescription={displayDescription}
        onDeleteEvent={onDeleteEvent}
      />
    );
  }

  // CALCULATED: Handle INTEREST_WITHHOLDING groups specifically
  if (groupType === GroupType.INTEREST_WITHHOLDING) {
    return (
      <InterestWithholdingGroupRow
        events={events as ExtendedFundEvent[]}
        fund={fund}
        showTaxEvents={showTaxEvents}
        showNavUpdates={showNavUpdates}
        displayDate={displayDate}
        displayDescription={displayDescription}
        onDeleteEvent={onDeleteEvent}
      />
    );
  }

  // CALCULATED: Handle other grouped events (fallback logic)
  const interestEvent = events.find(e => e.event_type === 'DISTRIBUTION') as ExtendedFundEvent | undefined;
  const withholdingEvent = events.find(e => e.event_type === 'TAX_PAYMENT') as ExtendedFundEvent | undefined;
  const otherEvents = events.filter(e => 
    e.event_type !== 'DISTRIBUTION' && e.event_type !== 'TAX_PAYMENT'
  );

  // CALCULATED: Determine if the interest event should show edit/delete buttons
  const isEditable = interestEvent && ![
    'TAX_PAYMENT', 
    'DAILY_RISK_FREE_INTEREST_CHARGE', 
    'EOFY_DEBT_COST', 
    'MANAGEMENT_FEE', 
    'CARRIED_INTEREST', 
    'OTHER'
  ].includes(interestEvent.event_type);

  return (
    <React.Fragment>
      {/* Combined interest + withholding row */}
      <TableRow hover>
        {/* Date Column */}
        <TableCell>{formatDate(displayDate)}</TableCell>
        
        {/* Type Column */}
        <TableCell>
          <EventTypeChip 
            eventType={interestEvent?.distribution_type || "INTEREST"} 
            size="small" 
          />
        </TableCell>
        
        {/* Description Column */}
        <TableCell>
          <Typography variant="body2">
            {displayDescription}
          </Typography>
        </TableCell>
        
        {/* Equity Column */}
        <TableCell align="right"></TableCell>
        
        {/* NAV Update Column (only for NAV-based funds) */}
        {isNavBased && (
          <TableCell align="right"></TableCell>
        )}
        
        {/* Distributions Column */}
        <TableCell align="right">
          {interestEvent && (
            <Box>
              <Typography variant="body2">
                {formatCurrency(interestEvent.amount || 0, fund.currency)}
              </Typography>
              {withholdingEvent && (
                <Typography variant="caption" color="error.main">
                  {formatCurrency(-(withholdingEvent.amount || 0), fund.currency)}
                </Typography>
              )}
            </Box>
          )}
        </TableCell>
        
        {/* Tax Column */}
        {showTaxEvents && (
          <TableCell align="right"></TableCell>
        )}
        
        {/* Actions Column */}
        <TableCell align="right" sx={{ 
          minWidth: { xs: 80, sm: 120 }, 
          px: { xs: 1, sm: 2 } 
        }}>
          <Box display="flex" gap={{ xs: 0.5, sm: 1.5 }} justifyContent="flex-end" alignItems="center">
            {isEditable && interestEvent && (
              <IconButton
                size="small"
                onClick={() => onDeleteEvent(interestEvent)}
                sx={{
                  color: 'error.main',
                  p: 1,
                  borderRadius: 1,
                  transition: 'all 0.2s ease-in-out',
                  '&:hover': {
                    bgcolor: 'error.light',
                    transform: 'scale(1.05)',
                    boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
                  }
                }}
                title="Delete event"
              >
                <DeleteIcon sx={{ fontSize: 18 }} />
              </IconButton>
            )}
          </Box>
        </TableCell>
      </TableRow>
      
      {/* Render other events on the same date */}
      {otherEvents.map((event) => (
        <OtherEventRow
          key={event.id}
          event={event as ExtendedFundEvent}
          fund={fund}
          showTaxEvents={showTaxEvents}
          showNavUpdates={showNavUpdates}
          onDeleteEvent={onDeleteEvent}
        />
      ))}
    </React.Fragment>
  );
};

/**
 * Custom comparator for React.memo to only compare fields that affect rendering
 * This prevents unnecessary re-renders when irrelevant fields change
 * Updated to work with new flag-based grouping interface
 */
const groupedEventRowPropsAreEqual = (prevProps: GroupedEventRowProps, nextProps: GroupedEventRowProps): boolean => {
  // Compare primitive values that affect rendering
  if (
    prevProps.groupedEvent.displayDate !== nextProps.groupedEvent.displayDate ||
    prevProps.groupedEvent.groupId !== nextProps.groupedEvent.groupId ||
    prevProps.groupedEvent.groupType !== nextProps.groupedEvent.groupType ||
    prevProps.fund.id !== nextProps.fund.id ||
    prevProps.fund.tracking_type !== nextProps.fund.tracking_type ||
    prevProps.fund.currency !== nextProps.fund.currency ||
    prevProps.showTaxEvents !== nextProps.showTaxEvents ||
    prevProps.showNavUpdates !== nextProps.showNavUpdates
  ) {
    return false;
  }
  
  // Compare events array length and key fields
  const prevEvents = prevProps.groupedEvent.events;
  const nextEvents = nextProps.groupedEvent.events;
  if (prevEvents.length !== nextEvents.length) {
    return false;
  }
  
  // Check if any events have changed (simplified check)
  for (let i = 0; i < prevEvents.length; i++) {
    const prev = prevEvents[i];
    const next = nextEvents[i];
    if (!prev || !next) continue;
    if (
      prev.id !== next.id ||
      prev.amount !== next.amount ||
      prev.description !== next.description ||
      prev.event_type !== next.event_type ||
      prev.has_withholding_tax !== next.has_withholding_tax ||
      prev.tax_withholding !== next.tax_withholding
    ) {
      return false;
    }
  }
  
  // Functions are reference-based, so we need to check if they're the same
  return prevProps.onDeleteEvent === nextProps.onDeleteEvent;
};

export const GroupedEventRow = React.memo(GroupedEventRowComponent, groupedEventRowPropsAreEqual);

/**
 * Component to render tax statement group rows
 * Shows financial year, total tax impact, and breakdown of tax components
 */
const TaxStatementGroupRow: React.FC<{
  events: ExtendedFundEvent[];
  fund: ExtendedFund;
  showTaxEvents: boolean;
  showNavUpdates: boolean;
  displayDate: string;
  displayDescription: string;
  onDeleteEvent: (event: ExtendedFundEvent) => void;
}> = ({ events, fund, showTaxEvents, showNavUpdates, displayDate, displayDescription, onDeleteEvent }) => {
  const isNavBased = fund.tracking_type === FundType.NAV_BASED;
  
  // CALCULATED: Categorize events by type for display
  const taxPaymentEvents = events.filter(e => e.event_type === 'TAX_PAYMENT') as ExtendedFundEvent[];
  const debtCostEvents = events.filter(e => e.event_type === 'EOFY_DEBT_COST') as ExtendedFundEvent[];
  
  // CALCULATED: Calculate totals for display
  const totalTaxPayments = taxPaymentEvents.reduce((sum, e) => sum + (e.amount || 0), 0);
  const totalDebtCostBenefits = debtCostEvents.reduce((sum, e) => sum + (e.amount || 0), 0);
  const netTaxImpact = totalTaxPayments + totalDebtCostBenefits;
  
  // CALCULATED: Get financial year from first tax event
  const firstTaxEvent = taxPaymentEvents[0];
  const financialYear = firstTaxEvent?.tax_statement?.financial_year;
  
  // CALCULATED: Determine if any events are editable
  const hasEditableEvents = events.some(e => ![
    'TAX_PAYMENT', 
    'DAILY_RISK_FREE_INTEREST_CHARGE', 
    'EOFY_DEBT_COST', 
    'MANAGEMENT_FEE', 
    'CARRIED_INTEREST', 
    'OTHER'
  ].includes(e.event_type));

  return (
    <React.Fragment>
      {/* Main tax statement summary row */}
      <TableRow hover sx={{ backgroundColor: 'action.hover' }}>
        {/* Date Column */}
        <TableCell>{formatDate(displayDate)}</TableCell>
        
        {/* Type Column */}
        <TableCell>
          <EventTypeChip 
            eventType="TAX_STATEMENT" 
            size="small" 
          />
        </TableCell>
        
        {/* Description Column */}
        <TableCell>
          <Box>
            <Typography variant="body2" fontWeight="medium">
              {displayDescription}
            </Typography>
            {financialYear && (
              <Typography variant="caption" color="text.secondary">
                Financial Year {financialYear}
              </Typography>
            )}
          </Box>
        </TableCell>
        
        {/* Equity Column */}
        <TableCell align="right"></TableCell>
        
        {/* NAV Update Column (only for NAV-based funds) */}
        {isNavBased && (
          <TableCell align="right"></TableCell>
        )}
        
        {/* Distributions Column */}
        <TableCell align="right">
          {/* Show net tax impact */}
          <Box>
            <Typography variant="body2" fontWeight="medium">
              {formatCurrency(netTaxImpact, fund.currency)}
            </Typography>
            {taxPaymentEvents.length > 0 && (
              <Typography variant="caption" color="error.main">
                Tax: {formatCurrency(totalTaxPayments, fund.currency)}
              </Typography>
            )}
            {debtCostEvents.length > 0 && (
              <Typography variant="caption" color="success.main">
                Benefits: {formatCurrency(totalDebtCostBenefits, fund.currency)}
              </Typography>
            )}
          </Box>
        </TableCell>
        
        {/* Tax Column */}
        {showTaxEvents && (
          <TableCell align="right">
            {/* Show breakdown in tax column */}
            <Box>
              <Typography variant="body2" fontWeight="medium">
                {formatCurrency(netTaxImpact, fund.currency)}
              </Typography>
              {taxPaymentEvents.length > 0 && (
                <Typography variant="caption" color="error.main">
                  {taxPaymentEvents.length} payment{taxPaymentEvents.length > 1 ? 's' : ''}
                </Typography>
              )}
            </Box>
          </TableCell>
        )}
        
        {/* Actions Column */}
        <TableCell align="right" sx={{ 
          minWidth: { xs: 80, sm: 120 }, 
          px: { xs: 1, sm: 2 } 
        }}>
          <Box display="flex" gap={{ xs: 0.5, sm: 1.5 }} justifyContent="flex-end" alignItems="center">
            {hasEditableEvents && (
              <IconButton
                size="small"
                onClick={() => {
                  // Find first editable event for delete action
                  const editableEvent = events.find(e => ![
                    'TAX_PAYMENT', 
                    'DAILY_RISK_FREE_INTEREST_CHARGE', 
                    'EOFY_DEBT_COST', 
                    'MANAGEMENT_FEE', 
                    'CARRIED_INTEREST', 
                    'OTHER'
                  ].includes(e.event_type));
                  if (editableEvent) {
                    onDeleteEvent(editableEvent as ExtendedFundEvent);
                  }
                }}
                sx={{
                  color: 'error.main',
                  p: 1,
                  borderRadius: 1,
                  transition: 'all 0.2s ease-in-out',
                  '&:hover': {
                    bgcolor: 'error.light',
                    transform: 'scale(1.05)',
                    boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
                  }
                }}
                title="Delete tax statement group"
              >
                <DeleteIcon sx={{ fontSize: 18 }} />
              </IconButton>
            )}
          </Box>
        </TableCell>
      </TableRow>
      
      {/* Render individual tax events as detail rows */}
      {events.map((event) => (
        <TaxStatementDetailRow
          key={event.id}
          event={event as ExtendedFundEvent}
          fund={fund}
          showTaxEvents={showTaxEvents}
          showNavUpdates={showNavUpdates}
          onDeleteEvent={onDeleteEvent}
        />
      ))}
    </React.Fragment>
  );
};

/**
 * Component to render interest withholding group rows
 * Shows interest amount normally with withholding amount below in red with smaller font
 * Enhanced styling and accessibility for enterprise-grade display
 */
const InterestWithholdingGroupRow: React.FC<{
  events: ExtendedFundEvent[];
  fund: ExtendedFund;
  showTaxEvents: boolean;
  showNavUpdates: boolean;
  displayDate: string;
  displayDescription: string;
  onDeleteEvent: (event: ExtendedFundEvent) => void;
}> = ({ events, fund, showTaxEvents, showNavUpdates, displayDate, displayDescription, onDeleteEvent }) => {
  const isNavBased = fund.tracking_type === FundType.NAV_BASED;
  
  // CALCULATED: Extract interest and withholding events
  const interestEvent = events.find(e => e.event_type === 'DISTRIBUTION') as ExtendedFundEvent | undefined;
  const withholdingEvent = events.find(e => e.event_type === 'TAX_PAYMENT') as ExtendedFundEvent | undefined;
  const otherEvents = events.filter(e => 
    e.event_type !== 'DISTRIBUTION' && e.event_type !== 'TAX_PAYMENT'
  );
  // CALCULATED: Determine if the interest event should show edit/delete buttons
  const isEditable = interestEvent && ![
    'TAX_PAYMENT', 
    'DAILY_RISK_FREE_INTEREST_CHARGE', 
    'EOFY_DEBT_COST', 
    'MANAGEMENT_FEE', 
    'CARRIED_INTEREST', 
    'OTHER'
  ].includes(interestEvent.event_type);

  return (
    <React.Fragment>
      {/* Main interest + withholding row with enhanced styling */}
      <TableRow hover sx={{ 
        backgroundColor: 'background.paper',
        '&:hover': {
          backgroundColor: 'action.hover',
          '& .withholding-amount': {
            color: 'error.dark',
            fontWeight: 500
          }
        }
      }}>
        {/* Date Column */}
        <TableCell>{formatDate(displayDate)}</TableCell>
        
        {/* Type Column */}
        <TableCell>
          <EventTypeChip 
            eventType={interestEvent?.distribution_type || "INTEREST"} 
            size="small" 
          />
        </TableCell>
        
        {/* Description Column */}
        <TableCell>
          <Typography variant="body2" fontWeight="medium">
            {displayDescription}
          </Typography>
          {/* Add additional context for withholding tax */}
          {withholdingEvent && (
            <Typography variant="caption" color="text.secondary">
              Withholding Tax Applied
            </Typography>
          )}
        </TableCell>
        
        {/* Equity Column */}
        <TableCell align="right"></TableCell>
        
        {/* NAV Update Column (only for NAV-based funds) */}
        {isNavBased && (
          <TableCell align="right"></TableCell>
        )}
        
        {/* Distributions Column - Enhanced display for interest + withholding */}
        <TableCell align="right">
          {interestEvent && (
            <Box>
              {/* Interest amount - standard size to match other rows */}
              <Typography 
                variant="body2" 
                aria-label={`Interest amount: ${formatCurrency(interestEvent.amount || 0, fund.currency)}`}
              >
                {formatCurrency(interestEvent.amount || 0, fund.currency)}
              </Typography>
              
              {/* Withholding amount - smaller red text below */}
              {withholdingEvent && (
                <Typography 
                  variant="caption" 
                  color="error.main"
                  className="withholding-amount"
                  sx={{
                    fontSize: '0.75rem',
                    fontWeight: 400,
                    lineHeight: 1.2,
                    mt: 0.5,
                    display: 'block'
                  }}
                  aria-label={`Withholding tax: ${formatCurrency(-(withholdingEvent.amount || 0), fund.currency)}`}
                >
                  {formatCurrency(-(withholdingEvent.amount || 0), fund.currency)}
                </Typography>
              )}
            </Box>
          )}
        </TableCell>
        
        {/* Tax Column */}
        {showTaxEvents && (
          <TableCell align="right">
            {/* Tax column left empty for interest withholding groups to avoid duplication */}
          </TableCell>
        )}
        
        {/* Actions Column */}
        <TableCell align="right" sx={{ 
          minWidth: { xs: 80, sm: 120 }, 
          px: { xs: 1, sm: 2 } 
        }}>
          <Box display="flex" gap={{ xs: 0.5, sm: 1.5 }} justifyContent="flex-end" alignItems="center">
            {isEditable && interestEvent && (
              <IconButton
                size="small"
                onClick={() => onDeleteEvent(interestEvent)}
                sx={{
                  color: 'error.main',
                  p: 1,
                  borderRadius: 1,
                  transition: 'all 0.2s ease-in-out',
                  '&:hover': {
                    bgcolor: 'error.light',
                    transform: 'scale(1.05)',
                    boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
                  }
                }}
                title="Delete interest event"
                aria-label="Delete interest event"
              >
                <DeleteIcon sx={{ fontSize: 18 }} />
              </IconButton>
            )}
          </Box>
        </TableCell>
      </TableRow>
      
      {/* Render other events on the same date */}
      {otherEvents.map((event) => (
        <OtherEventRow
          key={event.id}
          event={event as ExtendedFundEvent}
          fund={fund}
          showTaxEvents={showTaxEvents}
          showNavUpdates={showNavUpdates}
          onDeleteEvent={onDeleteEvent}
        />
      ))}
    </React.Fragment>
  );
};

/**
 * Component to render individual tax events within a tax statement group
 * Shows detailed breakdown of each tax component
 */
const TaxStatementDetailRow: React.FC<{
  event: ExtendedFundEvent;
  fund: ExtendedFund;
  showTaxEvents: boolean;
  showNavUpdates: boolean;
  onDeleteEvent: (event: ExtendedFundEvent) => void;
}> = ({ event, fund, showTaxEvents, showNavUpdates, onDeleteEvent }) => {
  const isNavBased = fund.tracking_type === FundType.NAV_BASED;
  
  // CALCULATED: Determine if this event is editable
  const isEditable = ![
    'TAX_PAYMENT', 
    'DAILY_RISK_FREE_INTEREST_CHARGE', 
    'EOFY_DEBT_COST', 
    'MANAGEMENT_FEE', 
    'CARRIED_INTEREST', 
    'OTHER'
  ].includes(event.event_type);

  return (
    <TableRow hover sx={{ backgroundColor: 'background.default' }}>
      {/* Date Column - Empty for detail rows */}
      <TableCell></TableCell>
      
      {/* Type Column */}
      <TableCell>
        <EventTypeChip 
          eventType={event.event_type} 
          size="small" 
        />
      </TableCell>
      
      {/* Description Column */}
      <TableCell>
        <Box sx={{ pl: 2 }}>
          <Typography variant="body2">
            {event.description || getTaxEventDescription(event)}
          </Typography>
          {event.tax_payment_type && (
            <Typography variant="caption" color="text.secondary">
              {event.tax_payment_type.replace(/_/g, ' ')}
            </Typography>
          )}
        </Box>
      </TableCell>
      
      {/* Equity Column */}
      <TableCell align="right"></TableCell>
      
      {/* NAV Update Column (only for NAV-based funds) */}
      {isNavBased && (
        <TableCell align="right"></TableCell>
      )}
      
      {/* Distributions Column */}
      <TableCell align="right">
        {formatCurrency(event.amount || 0, fund.currency)}
      </TableCell>
      
      {/* Tax Column */}
      {showTaxEvents && (
        <TableCell align="right">
          {event.event_type === 'TAX_PAYMENT' && (
            <TaxCellContent event={event} fund={fund} />
          )}
          {event.event_type === 'EOFY_DEBT_COST' && (
            <TaxCellContent event={event} fund={fund} />
          )}
        </TableCell>
      )}
      
      {/* Actions Column */}
      <TableCell align="right" sx={{ 
        minWidth: { xs: 80, sm: 120 }, 
        px: { xs: 1, sm: 2 } 
      }}>
        <Box display="flex" gap={{ xs: 0.5, sm: 1.5 }} justifyContent="flex-end" alignItems="center">
          {isEditable && (
            <IconButton
              size="small"
              onClick={() => onDeleteEvent(event)}
              sx={{
                color: 'error.main',
                p: 1,
                borderRadius: 1,
                transition: 'all 0.2s ease-in-out',
                '&:hover': {
                  bgcolor: 'error.light',
                  transform: 'scale(1.05)',
                  boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
                }
              }}
              title="Delete event"
            >
              <DeleteIcon sx={{ fontSize: 18 }} />
            </IconButton>
          )}
        </Box>
      </TableCell>
    </TableRow>
  );
};

/**
 * Helper function to generate descriptions for tax events
 */
const getTaxEventDescription = (event: ExtendedFundEvent): string => {
  switch (event.event_type) {
    case 'TAX_PAYMENT':
      return 'Tax Payment';
    case 'EOFY_DEBT_COST':
      return 'EOFY Debt Interest Deduction';
    default:
      return event.event_type.replace(/_/g, ' ');
  }
};

/**
 * Component to render other events that are part of a grouped event
 * This handles events like RETURN_OF_CAPITAL that appear on the same date as interest + withholding
 */
const OtherEventRow: React.FC<{
  event: ExtendedFundEvent;
  fund: ExtendedFund;
  showTaxEvents: boolean;
  showNavUpdates: boolean;
  onDeleteEvent: (event: ExtendedFundEvent) => void;
}> = ({ event, fund, showTaxEvents, showNavUpdates, onDeleteEvent }) => {
  const isNavBased = fund.tracking_type === FundType.NAV_BASED;
  const isEquity = event.event_type === 'UNIT_PURCHASE' || event.event_type === 'UNIT_SALE' || 
                   event.event_type === 'CAPITAL_CALL' || event.event_type === 'RETURN_OF_CAPITAL';
  const isDistribution = event.event_type === 'DISTRIBUTION';
  const isOther = !isEquity && !isDistribution;

  // Determine if this event should show edit/delete buttons
  const isEditable = ![
    'TAX_PAYMENT', 
    'DAILY_RISK_FREE_INTEREST_CHARGE', 
    'EOFY_DEBT_COST', 
    'MANAGEMENT_FEE', 
    'CARRIED_INTEREST', 
    'OTHER'
  ].includes(event.event_type);

  return (
    <TableRow key={event.id} hover>
      {/* Date Column */}
      <TableCell>{formatDate(event.event_date)}</TableCell>
      
      {/* Type Column */}
      <TableCell>
        {isDistribution && event.distribution_type ? (
          <EventTypeChip eventType={event.distribution_type} size="small" />
        ) : (
          <EventTypeChip eventType={event.event_type} size="small" />
        )}
      </TableCell>
      
      {/* Description Column */}
      <TableCell>
        <Typography variant="body2">
          {event.description || '-'}
        </Typography>
        {event.distribution_type && (
          <Typography variant="caption" color="text.secondary">
            {event.distribution_type}
          </Typography>
        )}
      </TableCell>
      
      {/* Equity Column */}
      <TableCell align="right">
        {isEquity && (
          <EquityCellContent event={event} fund={fund} />
        )}
      </TableCell>
      
      {/* NAV Update Column (only for NAV-based funds) */}
      {isNavBased && (
        <TableCell align="right">
          {event.event_type === 'NAV_UPDATE' && event.nav_per_share ? (
            <NavUpdateCellContent event={event} fund={fund} />
          ) : ''}
        </TableCell>
      )}
      
      {/* Distributions Column */}
      <TableCell align="right">
        {isDistribution ? formatCurrency(event.amount, fund.currency) : ''}
      </TableCell>
      
      {/* Tax Column */}
      {showTaxEvents && (
        <TableCell align="right">
          {isOther && event.amount ? (
            <TaxCellContent event={event} fund={fund} />
          ) : ''}
        </TableCell>
      )}
      
      {/* Actions Column */}
      <TableCell align="right" sx={{ minWidth: 120, px: 2 }}>
        <Box display="flex" gap={1.5} justifyContent="flex-end" alignItems="center">
                      {isEditable && (
              <IconButton
                size="small"
                onClick={() => onDeleteEvent(event)}
                sx={{
                  color: 'error.main',
                  p: 1,
                  borderRadius: 1,
                  transition: 'all 0.2s ease-in-out',
                  '&:hover': {
                    bgcolor: 'error.light',
                    transform: 'scale(1.05)',
                    boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
                  }
                }}
                title="Delete event"
              >
                <DeleteIcon sx={{ fontSize: 18 }} />
              </IconButton>
            )}
        </Box>
      </TableCell>
    </TableRow>
  );
};

/**
 * Component to render equity cell content for other events in grouped rows
 * Reused from EventRow component
 */
const EquityCellContent: React.FC<{ event: ExtendedFundEvent; fund: ExtendedFund }> = ({ 
  event, 
  fund 
}) => {
  const isNavBased = fund.tracking_type === FundType.NAV_BASED;

  if (isNavBased) {
    if (event.event_type === 'UNIT_PURCHASE') {
      return (
        <Box>
          <Typography variant="body2" color="error.main">
            ({formatCurrency(event.amount, fund.currency)})
          </Typography>
          {event.units_purchased && event.unit_price && (
            <Typography variant="caption" color="text.secondary">
              {event.units_purchased} × {formatCurrency(event.unit_price, fund.currency)}
            </Typography>
          )}
        </Box>
      );
    } else if (event.event_type === 'UNIT_SALE') {
      return (
        <Box>
          <Typography variant="body2">
            {formatCurrency(event.amount, fund.currency)}
          </Typography>
          {event.units_sold && event.unit_price && (
            <Typography variant="caption" color="text.secondary">
              {event.units_sold} × {formatCurrency(event.unit_price, fund.currency)}
            </Typography>
          )}
        </Box>
      );
    }
  } else {
    // Cost-based fund
    if (event.event_type === 'CAPITAL_CALL') {
      return (
        <Typography variant="body2" color="error.main">
          ({formatCurrency(event.amount, fund.currency)})
        </Typography>
      );
    } else if (event.event_type === 'RETURN_OF_CAPITAL') {
      return (
        <Typography variant="body2">
          {formatCurrency(event.amount, fund.currency)}
        </Typography>
      );
    }
  }

  return null;
};

/**
 * Component to render NAV update cell content for other events in grouped rows
 * Reused from EventRow component
 */
const NavUpdateCellContent: React.FC<{ event: ExtendedFundEvent; fund: ExtendedFund }> = ({ 
  event, 
  fund 
}) => {
  return (
    <Box>
      <Typography variant="body2">
        {formatCurrency(event.nav_per_share!, fund.currency)}
      </Typography>
      {event.nav_change_absolute != null && event.nav_change_percentage != null && (
        <Typography 
          variant="caption" 
          color={event.nav_change_absolute >= 0 ? 'success.main' : 'error.main'}
        >
          {event.nav_change_absolute >= 0 ? '+' : ''}{formatCurrency(event.nav_change_absolute, fund.currency)}, {event.nav_change_percentage >= 0 ? '+' : ''}{event.nav_change_percentage.toFixed(1)}%
        </Typography>
      )}
    </Box>
  );
};

/**
 * Component to render tax cell content for other events in grouped rows
 * Reused from EventRow component
 */
const TaxCellContent: React.FC<{ event: ExtendedFundEvent; fund: ExtendedFund }> = ({ 
  event, 
  fund 
}) => {
  if (event.event_type === 'TAX_PAYMENT') {
    return (
      <Box>
        <Typography variant="body2" color="error.main">
          {formatCurrency(-(event.amount || 0), fund.currency)}
        </Typography>
        {(() => {
          // Get income and tax rate based on tax payment type
          let incomeAmount: number | null = null;
          let taxRate: number | null = null;
          
          switch (event.tax_payment_type) {
            case 'EOFY_INTEREST_TAX':
              incomeAmount = event.interest_income_amount ?? null;
              taxRate = event.interest_income_tax_rate ?? null;
              break;
            case 'DIVIDENDS_FRANKED_TAX':
              incomeAmount = event.dividend_franked_income_amount ?? null;
              taxRate = event.dividend_franked_income_tax_rate ?? null;
              break;
            case 'DIVIDENDS_UNFRANKED_TAX':
              incomeAmount = event.dividend_unfranked_income_amount ?? null;
              taxRate = event.dividend_unfranked_income_tax_rate ?? null;
              break;
            case 'CAPITAL_GAINS_TAX':
              incomeAmount = event.capital_gain_income_amount ?? null;
              taxRate = event.capital_gain_income_tax_rate ?? null;
              break;
          }
          
          if (incomeAmount && taxRate) {
            return (
              <Typography variant="caption" color="text.secondary">
                {formatCurrency(incomeAmount, fund.currency)} @ {taxRate}%
              </Typography>
            );
          } else if (event.description) {
            // Fallback to description if income/tax rate not available
            return (
              <Typography variant="caption" color="text.secondary">
                {event.description}
              </Typography>
            );
          }
          return null;
        })()}
      </Box>
    );
  } else if (event.event_type === 'EOFY_DEBT_COST') {
    return (
      <Box>
        <Typography variant="body2">
          {formatCurrency(event.amount, fund.currency)}
        </Typography>
        {(() => {
          // Get total interest and deduction rate for EOFY debt cost events
          const totalInterest = event.eofy_debt_interest_deduction_sum_of_daily_interest ?? null;
          const deductionRate = event.eofy_debt_interest_deduction_rate ?? null;
          
          if (totalInterest && deductionRate) {
            return (
              <Typography variant="caption" color="text.secondary">
                {formatCurrency(totalInterest, fund.currency)} @ {deductionRate}%
              </Typography>
            );
          } else if (event.description) {
            // Fallback to description if data not available
            return (
              <Typography variant="caption" color="text.secondary">
                {event.description}
              </Typography>
            );
          }
          return null;
        })()}
      </Box>
    );
  } else {
    return <Typography variant="body2">{formatCurrency(event.amount || 0, fund.currency)}</Typography>;
  }
}; 