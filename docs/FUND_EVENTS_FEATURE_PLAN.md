# Fund Cash Flow Events Management Feature Plan

## Overview
Add the ability to view, add, edit, and manage fund cash flow events (capital calls, distributions, unit purchases/sales) through the web UI, integrated into the existing fund detail page.

## Goals
- Provide intuitive interface for managing fund cash flow events
- Support both NAV-based and Cost-based fund types
- Ensure data integrity and proper validation
- Integrate with existing fund calculation system
- Provide real-time feedback on cash flow impact
- Keep existing fund detail page layout

## User Preferences (Confirmed)
- **Event Types:** Capital Call (cost-based), Distribution (all), Unit Purchase/Sale (NAV-based)
- **Button Placement:** Add "Add Cash Flow" button above the events table
- **Templates:** Simple templates (pre-fill event type and basic fields)
- **Validation:**
  - No date ordering, amount, or balance validation for now
  - Only unit validation: prevent selling more units than owned (add this last)

## Implementation Plan

### Phase 1: Foundation
1. **Backend API Enhancement**
   - [ ] Add/update fund cash flow events API endpoints
   - [ ] Implement cash flow validation logic (basic, no unit validation yet)
   - [ ] Add cash flow recalculation triggers
   - [ ] Create cash flow event serialization/deserialization

2. **Frontend Infrastructure**
   - [ ] Create CashFlowEvents component structure
   - [ ] Set up cash flow event type definitions
   - [ ] Create cash flow event form components
   - [ ] Integrate with existing fund detail page
   - [ ] Add "Add Cash Flow" button above events table

### Phase 2: Core Features
3. **Cash Flow Event Display**
   - [ ] Enhance existing fund events display
   - [ ] Implement cash flow event type filtering
   - [ ] Add cash flow event sorting (by date, type, amount)
   - [ ] Display calculated fields (balances, units)

4. **Cash Flow Event Creation**
   - [ ] Create "Add Cash Flow" modal
   - [ ] Implement dynamic form fields based on cash flow type
   - [ ] Add real-time validation for cash flow amounts
   - [ ] Integrate with backend API

### Phase 3: Advanced Features
5. **Cash Flow Event Editing**
   - [ ] Implement event editing functionality
   - [ ] Add edit restrictions and warnings
   - [ ] Add event deletion with confirmation

6. **Enhanced UX**
   - [ ] Add event templates
   - [ ] Implement bulk operations (optional)
   - [ ] Add event search and filtering
   - [ ] Create event impact preview

### Phase 4: Polish & Integration
7. **Performance & Polish**
   - [ ] Optimize for large event lists
   - [ ] Add loading states and error handling
   - [ ] Implement responsive design

8. **Testing & Documentation**
   - [ ] Write comprehensive tests
   - [ ] Update API documentation
   - [ ] Create user documentation
   - [ ] Performance testing

### Validation (Final Step)
- [ ] Add unit validation: prevent selling more units than currently owned (NAV-based funds)

---

## Next Step
**Begin Phase 1: Foundation.**
- Start with backend API enhancements and frontend infrastructure for cash flow events. 