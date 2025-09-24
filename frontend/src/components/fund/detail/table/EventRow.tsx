import React from 'react';
import {
  TableRow,
  TableCell,
  Typography,
  Box,
  IconButton
} from '@mui/material';
import { Delete as DeleteIcon } from '@mui/icons-material';
import { ExtendedFundEvent, ExtendedFund, FundTrackingType } from '../../../../types/api';
import { formatCurrency, formatBrokerageFee, formatDate } from '../../../../utils/formatters';
// event type label is now rendered via EventTypeChip
import { EventTypeChip } from '../../../ui/EventTypeChip';

// ============================================================================
// EVENT ROW COMPONENT
// ============================================================================

export interface EventRowProps {
  event: ExtendedFundEvent;
  fund: ExtendedFund;
  showTaxEvents: boolean;
  showNavUpdates: boolean;

  onDeleteEvent: (event: ExtendedFundEvent) => void;
}

/**
 * Component to render individual event rows in the fund detail table
 * Updated to work with new flag-based grouping approach
 */
const EventRowComponent: React.FC<EventRowProps> = ({
  event,
  fund,
  showTaxEvents,
  showNavUpdates,

  onDeleteEvent
}) => {
  const isNavBased = fund.tracking_type === FundTrackingType.NAV_BASED;
  
  // CALCULATED: Event type classification for display logic
  const isEquity = event.event_type === 'UNIT_PURCHASE' || event.event_type === 'UNIT_SALE' || 
                   event.event_type === 'CAPITAL_CALL' || event.event_type === 'RETURN_OF_CAPITAL';
  const isDistribution = event.event_type === 'DISTRIBUTION';
  const isOther = !isEquity && !isDistribution;

  // CALCULATED: Determine if this event should show edit/delete buttons
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
          <EventTypeChip 
            eventType={event.distribution_type} 
            size="small" 
          />
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
 * Custom comparator for React.memo to only compare fields that affect rendering
 * This prevents unnecessary re-renders when irrelevant fields change
 */
const eventRowPropsAreEqual = (prevProps: EventRowProps, nextProps: EventRowProps): boolean => {
  // Compare primitive values that affect rendering
  if (
    prevProps.event.id !== nextProps.event.id ||
    prevProps.event.event_date !== nextProps.event.event_date ||
    prevProps.event.event_type !== nextProps.event.event_type ||
    prevProps.event.amount !== nextProps.event.amount ||
    prevProps.event.description !== nextProps.event.description ||
    prevProps.event.distribution_type !== nextProps.event.distribution_type ||
    prevProps.event.nav_per_share !== nextProps.event.nav_per_share ||
    prevProps.event.nav_change_absolute !== nextProps.event.nav_change_absolute ||
    prevProps.event.nav_change_percentage !== nextProps.event.nav_change_percentage ||
    prevProps.event.tax_payment_type !== nextProps.event.tax_payment_type ||
    prevProps.event.interest_income_amount !== nextProps.event.interest_income_amount ||
    prevProps.event.interest_income_tax_rate !== nextProps.event.interest_income_tax_rate ||
    prevProps.event.dividend_franked_income_amount !== nextProps.event.dividend_franked_income_amount ||
    prevProps.event.dividend_franked_income_tax_rate !== nextProps.event.dividend_franked_income_tax_rate ||
    prevProps.event.dividend_unfranked_income_amount !== nextProps.event.dividend_unfranked_income_amount ||
    prevProps.event.dividend_unfranked_income_tax_rate !== nextProps.event.dividend_unfranked_income_tax_rate ||
    prevProps.event.capital_gain_income_amount !== nextProps.event.capital_gain_income_amount ||
    prevProps.event.capital_gain_income_tax_rate !== nextProps.event.capital_gain_income_tax_rate ||
    prevProps.event.eofy_debt_interest_deduction_sum_of_daily_interest !== nextProps.event.eofy_debt_interest_deduction_sum_of_daily_interest ||
    prevProps.event.eofy_debt_interest_deduction_rate !== nextProps.event.eofy_debt_interest_deduction_rate ||
    prevProps.event.has_withholding_tax !== nextProps.event.has_withholding_tax ||
    prevProps.event.tax_withholding !== nextProps.event.tax_withholding ||
    prevProps.fund.id !== nextProps.fund.id ||
    prevProps.fund.tracking_type !== nextProps.fund.tracking_type ||
    prevProps.fund.currency !== nextProps.fund.currency ||
    prevProps.showTaxEvents !== nextProps.showTaxEvents ||
    prevProps.showNavUpdates !== nextProps.showNavUpdates
  ) {
    return false;
  }
  
  // Functions are reference-based, so we need to check if they're the same
  return prevProps.onDeleteEvent === nextProps.onDeleteEvent;
};

export const EventRow = React.memo(EventRowComponent, eventRowPropsAreEqual);

/**
 * Component to render equity cell content based on fund type and event type
 * Extracted from FundDetail.tsx for reusability
 */
const EquityCellContent: React.FC<{ event: ExtendedFundEvent; fund: ExtendedFund }> = ({ 
  event, 
  fund 
}) => {
  const isNavBased = fund.tracking_type === FundTrackingType.NAV_BASED;

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
              {event.brokerage_fee && event.brokerage_fee > 0 && (
                <span style={{ color: 'error.main' }}>
                  {' '}- {formatBrokerageFee(event.brokerage_fee, fund.currency)}
                </span>
              )}
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
              {event.brokerage_fee && event.brokerage_fee > 0 && (
                <span style={{ color: 'error.main' }}>
                  {' '}- {formatBrokerageFee(event.brokerage_fee, fund.currency)}
                </span>
              )}
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
 * Component to render NAV update cell content
 * Extracted from FundDetail.tsx for reusability
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
 * Component to render tax cell content with complex tax payment type handling
 * Extracted from FundDetail.tsx for reusability
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