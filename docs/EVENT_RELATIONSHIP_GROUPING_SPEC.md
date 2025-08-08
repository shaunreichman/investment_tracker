# Event Relationship Grouping Specification

## Overview
Currently, interest distribution events with tax withheld create two separate fund events (distribution + tax payment) on the same date. The frontend manually groups these by date and event type. This specification defines a simple flag-based approach to make frontend grouping much easier and more reliable.

## Design Philosophy
- **Simple flag approach**: Add `has_withholding_tax` boolean to interest distribution events
- **Clear intent**: Flag explicitly indicates when a distribution has withholding tax
- **Easier frontend logic**: Direct flag check instead of complex date/event type matching
- **Better performance**: No need to search for related events
- **Cleaner API**: Simple boolean field in API response

## Implementation Strategy

### Phase 1: Backend Flag Enhancement ✅ **COMPLETED**
**Goal**: Add has_withholding_tax flag to FundEvent model
**Tasks**:
- [x] Add `has_withholding_tax` boolean field to FundEvent model
- [x] Update `add_interest_distribution_with_withholding_tax` to set flag to true
- [x] Remove unused `create_distribution_with_tax_static` method (dead code)
- [x] Add migration for new field (field already existed in database)
- [x] Update API to include has_withholding_tax in responses
**Design Principles**:
- Simple boolean flag, no complex relationships
- Flag only set on interest distribution events
- Maintain backward compatibility with existing events

### Phase 2: Frontend Logic Simplification
**Goal**: Simplify frontend grouping logic using the flag
**Tasks**:
- [ ] Update `ExtendedFundEvent` interface to include has_withholding_tax
- [ ] Simplify `useEventGrouping` hook to use flag for grouping
- [ ] Replace complex date/event type matching with direct flag check
- [ ] Update `GroupedEventRow` to use simplified logic
- [ ] Add fallback logic for events without flag data
**Design Principles**:
- Use flag as primary grouping indicator
- Keep existing UI/UX patterns
- Graceful fallback for events without flag data

### Phase 3: Data Migration and Testing
**Goal**: Ensure existing data works with new flag system
**Tasks**:
- [ ] Run `test_main.py` to reset database to clean test state
- [ ] Add tests for flag setting and API responses
- [ ] Test grouping logic with various flag scenarios
- [ ] Update existing tests to work with new flag structure
**Design Principles**:
- Use test database reset instead of complex migration scripts
- Set flag based on presence of related withholding tax events
- Graceful fallback for events without flag data

## Success Metrics
- **Simplified Frontend Logic**: 70% reduction in grouping complexity
- **Better Performance**: Direct flag check instead of event searching
- **Clearer Intent**: Explicit indication of withholding tax relationships
- **Maintainability**: Simple boolean logic instead of complex matching
- **Reliability**: Flag-based grouping is more reliable than date matching

## Technical Considerations

### API Response Structure
```json
{
  "events": [
    {
      "id": 123,
      "event_type": "DISTRIBUTION",
      "amount": 1000.0,
      "distribution_type": "INTEREST",
      "has_withholding_tax": true
    },
    {
      "id": 124,
      "event_type": "TAX_PAYMENT",
      "amount": 100.0,
      "tax_payment_type": "NON_RESIDENT_INTEREST_WITHHOLDING"
    }
  ]
}
```

### Frontend Logic Simplification
```typescript
// Current complex logic
const interestEvent = dateEvents.find(e => 
  e.event_type === 'DISTRIBUTION' && e.distribution_type === 'INTEREST'
);
const withholdingEvent = dateEvents.find(e => 
  e.event_type === 'TAX_PAYMENT' && e.tax_payment_type === 'NON_RESIDENT_INTEREST_WITHHOLDING'
);

// Simplified logic with flag
const interestEvent = dateEvents.find(e => 
  e.event_type === 'DISTRIBUTION' && e.distribution_type === 'INTEREST'
);
const withholdingEvent = interestEvent?.has_withholding_tax ? 
  dateEvents.find(e => e.event_type === 'TAX_PAYMENT' && e.tax_payment_type === 'NON_RESIDENT_INTEREST_WITHHOLDING') : 
  null;
```

### Migration Strategy
- **Phase 1**: Add field without breaking existing functionality
- **Phase 2**: Set flag for existing events based on presence of withholding tax events
- **Phase 3**: Update frontend to use simplified flag-based logic
- **Phase 4**: Remove legacy date-based grouping logic

## Risk Mitigation
- **Backward Compatibility**: Existing API responses continue to work
- **Gradual Migration**: Frontend can use both flag and date-based grouping
- **Data Validation**: Validate flag setting during migration
- **Rollback Plan**: Can revert to date-based grouping if needed

## Future Considerations
- **Extensibility**: If other event types need grouping, similar flags can be added
- **Real-time Updates**: WebSocket support for flag changes
- **Advanced Display**: More sophisticated formatting based on flag
- **Audit Trail**: Track flag changes for compliance 