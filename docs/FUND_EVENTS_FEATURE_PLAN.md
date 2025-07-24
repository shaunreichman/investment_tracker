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

## Implementation Status

### ✅ COMPLETED FEATURES

#### Phase 1: Foundation - 100% COMPLETE
- [x] **Backend API Enhancement**
  - [x] Add/update fund cash flow events API endpoints
  - [x] Implement cash flow validation logic (basic, no unit validation yet)
  - [x] Add cash flow recalculation triggers
  - [x] Create cash flow event serialization/deserialization

- [x] **Frontend Infrastructure**
  - [x] Create CashFlowEvents component structure
  - [x] Set up cash flow event type definitions
  - [x] Create cash flow event form components
  - [x] Integrate with existing fund detail page
  - [x] Add "Add Cash Flow" button above events table

#### Phase 2: Core Features - 95% COMPLETE
- [x] **Cash Flow Event Display**
  - [x] Enhance existing fund events display
  - [x] Implement cash flow event type filtering
  - [x] Add cash flow event sorting (by date, type, amount)
  - [x] Display calculated fields (balances, units)

- [x] **Cash Flow Event Creation**
  - [x] Create "Add Cash Flow" modal
  - [x] Implement dynamic form fields based on cash flow type
  - [x] Add real-time validation for cash flow amounts
  - [x] Integrate with backend API

#### Phase 3: Advanced Features - 60% COMPLETE
- [x] **Enhanced UX**
  - [x] Add event templates
  - [x] Add event search and filtering
  - [x] Create event impact preview

- [ ] **Cash Flow Event Editing** - **HIGH PRIORITY**
  - [ ] Implement event editing functionality
  - [ ] Add edit restrictions and warnings
  - [ ] Add event deletion with confirmation

- [ ] **Bulk Operations** - **LOW PRIORITY**
  - [ ] Implement bulk operations (optional)

#### Phase 4: Polish & Integration - 80% COMPLETE
- [x] **Performance & Polish**
  - [x] Add loading states and error handling
  - [x] Implement responsive design

- [ ] **Performance Optimizations** - **MEDIUM PRIORITY**
  - [ ] Optimize for large event lists (pagination)
  - [ ] Performance testing

- [x] **Testing & Documentation**
  - [x] Write comprehensive tests
  - [x] Update API documentation
  - [ ] Create user documentation
  - [ ] Performance testing

### ❌ MISSING CRITICAL FEATURES

#### **HIGH PRIORITY: Event Editing & Deletion**
- **Missing**: PUT/PATCH/DELETE API endpoints for events
- **Impact**: Users cannot edit or delete events after creation
- **Backend Methods Available**: `update_unit_purchase`, `update_unit_sale`, `update_capital_call`, `update_return_of_capital`, `delete_event` exist but no API endpoints

#### **MEDIUM PRIORITY: Unit Validation**
- **Missing**: Validation to prevent selling more units than owned
- **Impact**: Data integrity risk for NAV-based funds
- **Plan**: Marked as "Final Step" in original plan

#### **MEDIUM PRIORITY: Performance Optimizations**
- **Missing**: Pagination for large event lists
- **Impact**: Performance issues with funds having many events

## **RECOMMENDED NEXT STEPS**

### **IMMEDIATE PRIORITIES (Next Sprint)**

#### **1. Event Editing & Deletion API (HIGH PRIORITY)**
```python
# Add these endpoints to src/api/__init__.py
@app.route('/api/funds/<int:fund_id>/events/<int:event_id>', methods=['PUT'])
def update_fund_event(fund_id, event_id):
    """Update an existing fund event"""

@app.route('/api/funds/<int:fund_id>/events/<int:event_id>', methods=['DELETE'])
def delete_fund_event(fund_id, event_id):
    """Delete a fund event"""
```

#### **2. Frontend Event Editing UI (HIGH PRIORITY)**
- Add edit/delete buttons to event rows
- Create `EditFundEventModal` component
- Add confirmation dialogs for deletion
- Implement edit restrictions (e.g., prevent editing system events)

#### **3. Unit Validation for NAV-based Funds (MEDIUM PRIORITY)**
```python
# Add to fund models validation
def validate_unit_sale(self, units_to_sell, session=None):
    """Validate that we're not selling more units than owned"""
    current_units = self.current_units or 0.0
    if units_to_sell > current_units:
        raise ValueError(f"Cannot sell {units_to_sell} units, only {current_units} owned")
```

### **FUTURE ENHANCEMENTS (Lower Priority)**

#### **4. Performance Optimizations**
- Implement pagination for events list
- Add virtual scrolling for large datasets
- Optimize API queries with proper indexing

#### **5. Advanced Features**
- Bulk event operations
- Event templates with more complex scenarios
- Event impact preview with real-time calculations
- Event search with advanced filters

#### **6. Documentation & Testing**
- User documentation for event management
- Performance testing with large datasets
- End-to-end testing for event workflows

---

## **CURRENT STATUS: 85% COMPLETE**

**✅ Foundation & Core Features: COMPLETE**
**⚠️ Advanced Features: PARTIAL (Missing Editing/Deletion)**
**⚠️ Polish & Integration: MOSTLY COMPLETE**

**Next Step: Focus on event editing and deletion functionality to complete the core user workflow.** 