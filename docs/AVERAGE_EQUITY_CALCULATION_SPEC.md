# Average Equity Calculation Specification

## Overview
The investment tracking system has a critical architectural flaw where `average_equity_balance` fields become stale over time. These fields are only recalculated when specific events occur (capital calls, unit purchases, NAV updates), but they should continuously reflect accurate time-weighted averages as days pass. This creates misleading portfolio reporting, inaccurate performance metrics, and potential compliance issues.

## Problem Classification

### Time-Dependent Calculations (Primary Focus)
- **`average_equity_balance`**: This is the only field that is truly time-dependent because it calculates a time-weighted average across periods. If you change an event date, the time periods change, so the calculation needs to be redone.

### Stale Field Calculations (Secondary Concern)
These fields become stale when events are modified, but not because of time dependencies:
- `current_equity_balance` - Becomes stale if you change the amount of a capital call/return
- `current_units` - Becomes stale if you change units in a purchase/sale
- `nav_change_absolute/percentage` - Become stale if you change NAV values
- `units_owned` - Becomes stale if you change unit transactions
- `current_nav_total` - Becomes stale if either units or unit price changes
- `total_cost_basis` - Becomes stale if capital call/return amounts change

**Note**: The backend already handles all these stale fields correctly through its unified recalculation system. When you modify any event, it triggers a full recalculation chain that updates everything. This spec focuses specifically on the time-dependent calculation problem.

## Design Philosophy
- **Accuracy First**: Calculations must be mathematically correct and current
- **Business Value**: Prioritize immediate fixes that improve user experience
- **Progressive Enhancement**: Build quick wins first, then enhance architecture
- **Performance**: Optimize for accuracy initially, then optimize for performance
- **Reliability**: System must handle failures gracefully and maintain data integrity

## Implementation Strategy

### Phase 1: Scheduled Background Updates
**Goal**: Automate daily updates to maintain data freshness without user intervention
**Timeline**: 2-4 weeks

**Tasks**:
- [ ] Design background job system architecture
- [ ] Implement daily cron job/scheduled task infrastructure
- [ ] Create `DailyFundUpdateJob` class for orchestrated daily updates
- [ ] Implement `update_all_fund_summaries_daily()` orchestration method
- [ ] Add proper error handling and retry logic for failed updates
- [ ] Implement monitoring and alerting for job execution
- [ ] Add logging for audit trail of daily updates
- [ ] Test with sample funds to validate accuracy

**Class Design**:
```python
class DailyFundUpdateJob:
    """Orchestrates daily updates of all fund summary fields that depend on time."""
    
    def __init__(self, session_factory):
        self.session_factory = session_factory
    
    def run_daily_update(self, target_date: date) -> UpdateResult:
        """Main entry point for daily fund updates."""
        
    def update_all_fund_summaries(self, target_date: date) -> List[UpdateResult]:
        """Update all active fund summaries for the given date."""
        
    def update_fund_summary(self, fund_id: int, target_date: date) -> UpdateResult:
        """Update a single fund's summary fields."""
        
    def _calculate_fresh_average_equity_balance(self, fund, target_date: date) -> Decimal:
        """Calculate fresh average equity balance as of target date."""
        
    def _handle_update_conflicts(self, fund_id: int) -> ConflictResolution:
        """Handle conflicts between scheduled and event-driven updates."""
```

**Design Principles**:
- Use existing calculation methods, don't rebuild from scratch
- Implement proper locking to prevent conflicts with event-driven updates
- Handle failures gracefully with retry mechanisms
- Maintain full audit trail of all updates

**Success Metrics**:
- All fund summaries updated daily without manual intervention
- Zero conflicts between scheduled and event-driven updates
- Full visibility into update execution and any failures

### Phase 2: Real-Time Calculation Engine
**Goal**: Replace stored fields with calculated properties for ultimate accuracy
**Timeline**: 1-2 months

**Tasks**:
- [ ] Design database view or materialized view architecture
- [ ] Implement real-time calculation engine using existing logic
- [ ] Add caching strategy with short TTL (1 hour)
- [ ] Create cache invalidation on events
- [ ] Migrate existing stored fields to calculated properties
- [ ] Add performance monitoring and optimization
- [ ] Implement data validation and consistency checks

**Design Principles**:
- Leverage existing calculation logic, don't rewrite
- Use materialized views for performance with periodic refresh
- Implement intelligent caching that balances accuracy and performance
- Maintain backward compatibility during migration

**Success Metrics**:
- Real-time accuracy for all average equity calculations
- Performance improvement over stored field approach
- Zero data inconsistencies or calculation errors

### Phase 3: Event Sourcing Architecture
**Goal**: Implement enterprise-level event sourcing for complete temporal accuracy
**Timeline**: 3-6 months

**Tasks**:
- [ ] Design event store architecture for all financial events
- [ ] Implement event sourcing patterns for fund operations
- [ ] Create projections that calculate derived fields from events
- [ ] Add real-time event streams for live updates
- [ ] Implement temporal queries ("as of any point in time")
- [ ] Add comprehensive testing and validation
- [ ] Performance optimization and scaling

**Design Principles**:
- Store all events with precise timestamps
- Use event streams for real-time projection updates
- Enable historical analysis and point-in-time queries
- Design for scalability and performance

**Success Metrics**:
- Complete temporal accuracy for all financial calculations
- Ability to query portfolio state at any historical point
- Enterprise-grade performance and reliability

## Success Metrics

### Business Impact
- **Short-term**: Automated daily updates eliminate manual intervention and stale data
- **Medium-term**: Real-time accuracy improves decision-making and compliance
- **Long-term**: Enterprise-grade event sourcing architecture for complete temporal accuracy

### Technical Achievement
- **Phase 1**: Reliable automated daily updates with full monitoring
- **Phase 2**: Real-time accuracy with performance optimization
- **Phase 3**: Enterprise-grade event sourcing architecture

### User Experience
- **Data Freshness**: Clear indication of when calculations were last updated
- **Accuracy**: Users trust the numbers they see for decision-making
- **Performance**: Fast access to accurate financial data
- **Transparency**: Full visibility into calculation methods and data sources

## Immediate Action Items

### This Week
- [ ] Audit current `average_equity_balance` usage in codebase
- [ ] Design `DailyFundUpdateJob` class structure for Phase 1
- [ ] Plan background job system architecture
- [ ] Research job scheduling options (Celery, APScheduler, system cron)

### Next Week
- [ ] Implement `DailyFundUpdateJob` class core functionality
- [ ] Create daily update orchestration logic
- [ ] Add error handling and retry mechanisms
- [ ] Test with sample fund data to validate accuracy

### Following Weeks
- [ ] Implement job scheduling infrastructure
- [ ] Add monitoring and alerting for job execution
- [ ] Test daily updates in development environment
- [ ] Prepare for production deployment

## Risk Mitigation

### Technical Risks
- **Performance Impact**: On-demand calculations may be slower than stored fields
  - *Mitigation*: Implement caching and optimize calculation algorithms
- **Data Consistency**: Conflicts between scheduled and event-driven updates
  - *Mitigation*: Proper locking mechanisms and conflict resolution
- **Migration Complexity**: Moving from stored to calculated fields
  - *Mitigation*: Gradual migration with backward compatibility

### Business Risks
- **User Confusion**: Different values shown in different parts of UI
  - *Mitigation*: Clear labeling and explanation of data sources
- **Performance Degradation**: Slower response times during transition
  - *Mitigation*: Implement in phases with performance monitoring
- **Data Accuracy**: Potential calculation errors during implementation
  - *Mitigation*: Comprehensive testing and validation

## Dependencies

### External Dependencies
- **Job Scheduler**: Celery, APScheduler, or system cron for Phase 2
- **Monitoring**: Logging and alerting infrastructure for production
- **Testing**: Comprehensive test data and validation procedures

### Internal Dependencies
- **Existing Calculation Logic**: Current methods in `src/fund/models.py`
- **Database Schema**: Current fund summary table structure
- **API Infrastructure**: Existing Flask API patterns and conventions

## Related Specifications

- **Data Integrity & Validation Spec**: For comprehensive data quality monitoring and validation procedures
- **Backend Testing Suite**: For calculation accuracy validation
- **Frontend Professional Excellence**: For user experience improvements

## Questions for Investigation

### Technical Questions
1. What is the current performance impact of existing calculations?
2. How many funds typically have balance changes in a given day?
3. What database constraints exist on the current schema?
4. How should we handle funds that are closed or suspended?

### Business Questions
1. What are the regulatory requirements for calculation frequency?
2. How critical is real-time accuracy vs. daily accuracy?
3. What is the business impact of current stale data?
4. What monitoring and alerting do we need for production?

---

*This specification will be updated as we implement each phase and discover additional requirements.*
