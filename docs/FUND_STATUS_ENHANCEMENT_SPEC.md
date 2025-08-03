# Fund Status Enhancement Specification

## Overview
Enhance the fund status system from binary (Active/Exited) to three-state (Active/Realized/Completed) with event-driven status updates to accurately reflect fund lifecycle stages.

## Design Philosophy
- **Event-Driven**: Status updates triggered by specific events (equity changes, tax statements)
- **Business-Focused**: Status reflects actual fund lifecycle, not just technical state
- **Single Source of Truth**: The `status` field is the only authority for fund lifecycle state
- **Clear Definitions**: Each status has unambiguous business meaning
- **No Redundancy**: Remove legacy fields to avoid conflicting state

## Implementation Strategy

### Phase 1: Core Status System Enhancement
**Goal**: Implement three-state status system with clear business definitions

**Tasks**:
- [x] **Add FundStatus Enum**
  - [x] Create `FundStatus` enum with `ACTIVE`, `REALIZED`, `COMPLETED`
  - [x] Update database schema to use new enum
  - [x] Create migration for existing funds
- [x] **Update Status Logic**
  - [x] Replace `is_active` boolean with `status` enum field
  - [x] Implement new status determination logic
  - [x] Update `should_be_active` property to use new status
- [ ] **Remove Legacy Fields**
  - [ ] Remove `final_tax_statement_received` field from model and database
  - [ ] Update all code to reference only the `status` field
  - [ ] Create migration to drop the legacy field
- [ ] **Single Source of Truth**
  - [ ] Ensure all business logic uses only the `status` field
  - [ ] Remove any references to `final_tax_statement_received`
  - [ ] Update API responses to include new status field

**Design Principles**:
- Status transitions are automatic based on business rules
- Manual status overrides allowed for edge cases
- Clear audit trail of status changes
- **Single source of truth**: Only the `status` field determines fund lifecycle
- **No redundancy**: Remove legacy fields to prevent conflicting state

### Phase 2: Event-Driven Status Updates
**Goal**: Implement automatic status updates triggered by specific events

**Tasks**:
- [ ] **Equity Event Triggers**
  - [ ] Add status check after capital call events
  - [ ] Add status check after return of capital events
  - [ ] Add status check after unit purchase/sale events
  - [ ] Implement transition to `REALIZED` when equity balance reaches zero
- [ ] **Tax Statement Event Triggers**
  - [ ] Add status check after tax statement creation
  - [ ] Implement logic to determine "final" tax statement
  - [ ] Add transition to `COMPLETED` when final tax statement received
- [ ] **Status Update Methods**
  - [ ] Create `update_status_after_equity_event()` method
  - [ ] Create `update_status_after_tax_statement()` method
  - [ ] Add status change logging and audit trail

**Design Principles**:
- Status updates happen immediately after relevant events
- No periodic background checks required
- Clear business rules for each transition

### Phase 3: Status-Based Tax Statement Logic
**Goal**: Implement logic to determine when a fund should transition to `COMPLETED`

**Tasks**:
- [ ] **Completed Status Logic**
  - [ ] Define criteria for `COMPLETED` status (e.g., fund end date + X months)
  - [ ] Implement logic to detect when final tax statement event has occurred
  - [ ] Add configuration for completed status timing
- [ ] **Tax Statement Event Tracking**
  - [ ] Track tax statement events after fund realization
  - [ ] Implement logic for multiple tax statements after realization
  - [ ] Handle edge cases (missing tax statements, late filings)

**Design Principles**:
- Conservative approach: prefer staying `REALIZED` over premature `COMPLETED`
- Use tax statement events to determine completion, not legacy fields
- Clear documentation of completed status criteria

### Phase 4: UI and API Updates
**Goal**: Update frontend and API to support new status system

**Tasks**:
- [ ] **API Updates**
  - [ ] Update fund API responses to include new status field
  - [ ] Add status transition endpoints for manual overrides
  - [ ] Update fund list endpoints to filter by status
- [ ] **Frontend Updates**
  - [ ] Update fund status display components
  - [ ] Add status indicators with appropriate colors/icons
  - [ ] Update fund list to show new status values
  - [ ] Add status filtering capabilities
- [ ] **Status Indicators**
  - [ ] Design visual indicators for each status
  - [ ] Implement consistent status display across all components
  - [ ] Add tooltips explaining status meanings

**Design Principles**:
- Clear visual distinction between statuses
- Consistent status display across all UI components
- Helpful tooltips explaining status meanings

### Phase 5: Testing and Validation
**Goal**: Ensure new status system works correctly across all scenarios

**Tasks**:
- [ ] **Unit Tests**
  - [ ] Test status determination logic for all scenarios
  - [ ] Test event-driven status updates
  - [ ] Test final tax statement detection
- [ ] **Integration Tests**
  - [ ] Test status updates after equity events
  - [ ] Test status updates after tax statement events
  - [ ] Test backward compatibility with existing data
- [ ] **Manual Testing**
  - [ ] Test with real fund data scenarios
  - [ ] Validate status transitions in UI
  - [ ] Test edge cases and manual overrides

**Design Principles**:
- Comprehensive test coverage for all status scenarios
- Real-world testing with actual fund data
- Clear test documentation for future maintenance

## Status Definitions

### **Active**
- **Definition**: Equity balance > 0
- **Business Meaning**: Fund is still invested, has capital at risk
- **Allowed Events**: All event types (capital calls, returns, distributions, etc.)
- **Visual Indicator**: Green dot/status

### **Realized**
- **Definition**: Equity balance = 0
- **Business Meaning**: All capital has been returned, may still receive final distributions
- **Allowed Events**: Distributions, tax payments, tax statements
- **Visual Indicator**: Yellow/orange dot/status

### **Completed**
- **Definition**: Final tax statement received after equity balance = 0
- **Business Meaning**: Fund is fully realized AND all tax obligations are complete
- **Allowed Events**: Read-only, no new events allowed
- **Visual Indicator**: Gray dot/status

## Status Transition Rules

### **Automatic Transitions**
1. **Active → Realized**: When equity balance reaches zero after any equity event
2. **Realized → Completed**: When final tax statement is received (fund is realized)

### **Manual Overrides**
- Allow manual status changes for edge cases
- Require reason/comment for manual changes
- Log all manual status changes for audit trail

### **Event Triggers**
- **Equity Events**: Capital calls, returns, unit purchases/sales
- **Tax Statement Events**: New tax statements added to realized funds
- **System Events**: Periodic checks for final tax statement detection

## Success Metrics
- [ ] All existing funds correctly mapped to new status system
- [ ] Status updates happen immediately after relevant events
- [ ] Clear visual distinction between statuses in UI
- [ ] No performance impact on existing functionality
- [ ] Comprehensive test coverage for all scenarios

## Example Implementation

### **Database Schema Update**
```python
class FundStatus(enum.Enum):
    ACTIVE = "active"
    REALIZED = "realized" 
    COMPLETED = "completed"

class Fund(Base):
    # Replace is_active with status
    status = Column(Enum(FundStatus), default=FundStatus.ACTIVE)
```

### **Status Update Methods**
```python
def update_status_after_equity_event(self, session=None):
    """Update status after equity balance changes"""
    if self.current_equity_balance == 0 and self.status == FundStatus.ACTIVE:
        self.status = FundStatus.REALIZED
        session.commit()
        print(f"Fund '{self.name}' status updated to REALIZED")

def update_status_after_tax_statement(self, session=None):
    """Update status after tax statement added"""
    if self.status == FundStatus.REALIZED and self.is_final_tax_statement():
        self.status = FundStatus.COMPLETED
        session.commit()
        print(f"Fund '{self.name}' status updated to COMPLETED")
```

## Migration Strategy
1. **Phase 1**: Add new status field alongside existing `is_active`
2. **Phase 2**: Migrate existing data to new status values
3. **Phase 3**: Remove old `is_active` field after validation
4. **Phase 4**: Update all code to use new status system

This specification provides a clear roadmap for implementing the enhanced fund status system while maintaining backward compatibility and ensuring accurate business logic. 