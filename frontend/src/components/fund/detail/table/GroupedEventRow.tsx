import React from 'react';
import {
  TableRow,
  TableCell,
  Typography,
  Box,
  Chip,
  IconButton
} from '@mui/material';
import { Edit as EditIcon, Delete as DeleteIcon } from '@mui/icons-material';
import { ExtendedFundEvent, ExtendedFund } from '../../../../types/api';
import { formatCurrency, formatDate } from '../../../../utils/formatters';
import { getEventTypeColor } from '../../../../utils/helpers';
import { GroupedEvent } from './useEventGrouping';

// ============================================================================
// GROUPED EVENT ROW COMPONENT
// ============================================================================

export interface GroupedEventRowProps {
  groupedEvent: GroupedEvent;
  fund: ExtendedFund;
  showTaxEvents: boolean;
  showNavUpdates: boolean;
  onEditEvent: (event: ExtendedFundEvent) => void;
  onDeleteEvent: (event: ExtendedFundEvent) => void;
}

/**
 * Component to render grouped event rows (interest + withholding tax combinations)
 * Extracted from FundDetail.tsx lines 684-773 for reusability and testing
 */
export const GroupedEventRow: React.FC<GroupedEventRowProps> = ({
  groupedEvent,
  fund,
  showTaxEvents,
  showNavUpdates,
  onEditEvent,
  onDeleteEvent
}) => {
  const { date, interestEvent, withholdingEvent, otherEvents } = groupedEvent;
  const isNavBased = fund.tracking_type === 'nav_based';

  // Determine if the interest event should show edit/delete buttons
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
        <TableCell>{formatDate(date)}</TableCell>
        
        {/* Type Column */}
        <TableCell>
          <Chip
            label="INTEREST"
            color={getEventTypeColor('DISTRIBUTION') as any}
            size="small"
          />
        </TableCell>
        
        {/* Description Column */}
        <TableCell>
          <Typography variant="body2">
            {interestEvent?.description || '-'}
          </Typography>
          <Typography variant="caption" color="error.main">
            Withholding: {formatCurrency(-(withholdingEvent?.amount || 0), fund.currency)}
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
                {formatCurrency(interestEvent.amount, fund.currency)}
              </Typography>
              <Typography variant="caption" color="error.main">
                {formatCurrency(-(withholdingEvent?.amount || 0), fund.currency)}
              </Typography>
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
              <>
                <IconButton
                  size="small"
                  onClick={() => onEditEvent(interestEvent)}
                  sx={{
                    color: 'primary.main',
                    p: 1,
                    borderRadius: 1,
                    transition: 'all 0.2s ease-in-out',
                    '&:hover': {
                      bgcolor: 'primary.light',
                      transform: 'scale(1.05)',
                      boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
                    }
                  }}
                  title="Edit event"
                >
                  <EditIcon sx={{ fontSize: 18 }} />
                </IconButton>
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
              </>
            )}
          </Box>
        </TableCell>
      </TableRow>
      
      {/* Render other events on the same date */}
      {otherEvents.map((event) => (
        <OtherEventRow
          key={event.id}
          event={event}
          fund={fund}
          showTaxEvents={showTaxEvents}
          showNavUpdates={showNavUpdates}
          onEditEvent={onEditEvent}
          onDeleteEvent={onDeleteEvent}
        />
      ))}
    </React.Fragment>
  );
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
  onEditEvent: (event: ExtendedFundEvent) => void;
  onDeleteEvent: (event: ExtendedFundEvent) => void;
}> = ({ event, fund, showTaxEvents, showNavUpdates, onEditEvent, onDeleteEvent }) => {
  const isNavBased = fund.tracking_type === 'nav_based';
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
        <Chip
          label={event.event_type}
          color={getEventTypeColor(event.event_type) as any}
          size="small"
        />
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
            <>
              <IconButton
                size="small"
                onClick={() => onEditEvent(event)}
                sx={{
                  color: 'primary.main',
                  p: 1,
                  borderRadius: 1,
                  transition: 'all 0.2s ease-in-out',
                  '&:hover': {
                    bgcolor: 'primary.light',
                    transform: 'scale(1.05)',
                    boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
                  }
                }}
                title="Edit event"
              >
                <EditIcon sx={{ fontSize: 18 }} />
              </IconButton>
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
            </>
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
  const isNavBased = fund.tracking_type === 'nav_based';

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