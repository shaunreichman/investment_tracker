# Performance Baseline Analysis - Phase 1 Performance Analysis

## Overview

This document establishes performance baselines for the current fund system. Performance analysis is critical for identifying bottlenecks and ensuring the refactor improves rather than degrades system performance.

## Performance Test Environment

### **System Specifications**
- **Database**: PostgreSQL (version to be determined)
- **Backend**: Python/Flask with SQLAlchemy ORM
- **Hardware**: Development environment (specs to be determined)
- **Data Volume**: Current production data volumes

### **Test Data Requirements**
- **Funds**: Current count + projected growth to 500+
- **Events**: Current count + projected growth to 20,000+
- **Companies**: Current count + projected growth to 25+
- **Tax Statements**: Current count + projected growth

## Critical Performance Operations

### **1. Fund Event Creation & Updates**

#### **Operation**: `recalculate_capital_chain_from()`
- **Current Complexity**: O(n) where n = number of capital events
- **Performance Impact**: HIGH - affects every capital event
- **Scaling Factor**: Linear degradation with event count

#### **Operation**: `add_distribution()`
- **Current Complexity**: O(1) for single event, but triggers chain recalculation
- **Performance Impact**: HIGH - 174-line method with complex logic
- **Scaling Factor**: Affects all subsequent events

#### **Operation**: `add_capital_call()` / `add_return_of_capital()`
- **Current Complexity**: O(n) due to chain recalculation
- **Performance Impact**: HIGH - affects fund status and summary fields
- **Scaling Factor**: Linear degradation with event count

### **2. Fund Summary Calculations**

#### **Operation**: `update_fund_summary_fields_after_capital_event()`
- **Current Complexity**: O(n) for NAV-based, O(n) for cost-based
- **Performance Impact**: MEDIUM - called after every capital event
- **Scaling Factor**: Linear degradation with event count

#### **Operation**: `calculate_average_equity_balance()`
- **Current Complexity**: O(n) where n = number of events
- **Performance Impact**: MEDIUM - called for status updates
- **Scaling Factor**: Linear degradation with event count

#### **Operation**: `calculate_end_date()`
- **Current Complexity**: O(n) where n = number of events
- **Performance Impact**: MEDIUM - called for summary updates
- **Scaling Factor**: Linear degradation with event count

### **3. Tax Statement Operations**

#### **Operation**: `create_or_update_tax_statement()`
- **Current Complexity**: O(1) for creation, O(n) for updates
- **Performance Impact**: MEDIUM - affects fund status
- **Scaling Factor**: Depends on fund complexity

#### **Operation**: Tax statement grouping and calculations
- **Current Complexity**: O(n) for grouping, O(n) for calculations
- **Performance Impact**: MEDIUM - affects reporting and IRR calculations
- **Scaling Factor**: Linear degradation with event count

### **4. IRR Calculations**

#### **Operation**: `calculate_irr()`, `calculate_after_tax_irr()`, `calculate_real_irr()`
- **Current Complexity**: O(n) where n = number of cash flows
- **Performance Impact**: HIGH - complex mathematical calculations
- **Scaling Factor**: Linear degradation with event count

#### **Operation**: `_calculate_irr_base()`
- **Current Complexity**: O(n) for cash flow processing
- **Performance Impact**: HIGH - core IRR calculation engine
- **Scaling Factor**: Linear degradation with event count

## Performance Bottlenecks Identified

### **1. Chain Recalculation Bottleneck**
```
Problem: Every capital event triggers full recalculation of subsequent events
Impact: O(n) complexity for all capital operations
Risk: System becomes unusable with 20,000+ events
```

**Current Implementation:**
```python
def recalculate_capital_chain_from(self, event, session=None):
    # Get ALL capital events for this fund
    events = session.query(FundEvent).filter(
        FundEvent.fund_id == self.id,
        FundEvent.event_type.in_(CAPITAL_EVENT_TYPES)
    ).order_by(FundEvent.event_date, FundEvent.id).all()
    
    # Recalculate ALL subsequent events
    self._recalculate_subsequent_capital_fund_events_after_capital_event(events, idx, session=session)
```

**Performance Issues:**
- Loads all capital events into memory
- Processes all events sequentially
- No caching of intermediate results
- Database queries in tight loops

### **2. Database Query Bottlenecks**
```
Problem: Multiple database queries in single operations
Impact: Increased latency and database load
Risk: Database becomes bottleneck at scale
```

**Examples:**
```python
# Multiple queries in summary update
events = session.query(FundEvent).filter(...).all()  # Query 1
latest_nav_event = session.query(FundEvent).filter(...).first()  # Query 2
latest_unit_event = events[-1] if events else None  # In-memory processing
```

### **3. Memory Usage Bottlenecks**
```
Problem: Large datasets loaded into memory
Impact: High memory usage and potential OOM errors
Risk: System crashes with large datasets
```

**Examples:**
```python
# Load all events into memory
events = session.query(FundEvent).filter(...).all()  # Could be 10,000+ events

# Build FIFO in memory
fifo = []  # Could grow to thousands of entries
for i in range(start_idx):
    # Process all events in memory
```

### **4. Transaction Scope Bottlenecks**
```
Problem: Large transactions for complex operations
Impact: Long lock times and potential deadlocks
Risk: Database contention at scale
```

**Examples:**
```python
def recalculate_capital_chain_from(self, event, session=None):
    # ... complex operations ...
    session.commit()  # Commits entire recalculation chain
```

## Performance Metrics to Measure

### **1. Response Time Metrics**
- **Event Creation Time**: Time to create and process a fund event
- **Chain Recalculation Time**: Time to recalculate capital chain
- **Summary Update Time**: Time to update fund summary fields
- **IRR Calculation Time**: Time to calculate IRR values

### **2. Throughput Metrics**
- **Events Per Second**: Maximum events that can be processed
- **Concurrent Users**: Maximum concurrent fund operations
- **Database Queries Per Second**: Database load capacity

### **3. Resource Usage Metrics**
- **Memory Usage**: Peak memory usage during operations
- **CPU Usage**: CPU utilization during calculations
- **Database Connections**: Connection pool utilization

### **4. Scaling Metrics**
- **Performance vs. Event Count**: How performance degrades with scale
- **Performance vs. Fund Count**: How performance degrades with fund count
- **Performance vs. Company Count**: How performance degrades with company count

## Performance Test Scenarios

### **Scenario 1: Single Fund Operations**
- **Objective**: Measure baseline performance for single fund
- **Data**: 1 fund with 100-1,000 events
- **Metrics**: Response time, resource usage
- **Expected**: O(n) performance degradation

### **Scenario 2: Multi-Fund Operations**
- **Objective**: Measure performance with multiple funds
- **Data**: 10-100 funds with varying event counts
- **Metrics**: Concurrent operation performance
- **Expected**: Resource contention and degradation

### **Scenario 3: Large Scale Operations**
- **Objective**: Measure performance at target scale
- **Data**: 500+ funds, 20,000+ events, 25+ companies
- **Metrics**: System stability and performance
- **Expected**: Significant performance degradation

### **Scenario 4: Concurrent Operations**
- **Objective**: Measure concurrent user performance
- **Data**: Multiple simultaneous fund operations
- **Metrics**: Throughput and response time
- **Expected**: Resource contention and queue buildup

## Performance Baseline Targets

### **Current System (Baseline)**
- **Single Event Creation**: < 100ms (target)
- **Chain Recalculation**: < 500ms for 100 events (target)
- **Summary Updates**: < 200ms (target)
- **IRR Calculations**: < 300ms (target)

### **Target System (Post-Refactor)**
- **Single Event Creation**: < 50ms (50% improvement)
- **Chain Recalculation**: < 100ms for 100 events (80% improvement)
- **Summary Updates**: < 100ms (50% improvement)
- **IRR Calculations**: < 150ms (50% improvement)

### **Scaling Targets**
- **500 Funds**: Maintain < 100ms response time
- **20,000 Events**: Maintain < 200ms response time
- **25 Companies**: Maintain < 150ms response time
- **Concurrent Users**: Support 10+ concurrent operations

## Performance Testing Tools

### **1. Python Profiling**
```python
import cProfile
import pstats

def profile_operation():
    profiler = cProfile.Profile()
    profiler.enable()
    # ... operation code ...
    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats()
```

### **2. Database Query Profiling**
```python
# Enable SQLAlchemy query logging
import logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
```

### **3. Memory Profiling**
```python
import tracemalloc

def profile_memory():
    tracemalloc.start()
    # ... operation code ...
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return current, peak
```

### **4. Load Testing**
```python
import time
import threading

def load_test(operation, concurrent_users=10, iterations=100):
    results = []
    def worker():
        for i in range(iterations):
            start = time.time()
            operation()
            end = time.time()
            results.append(end - start)
    
    threads = [threading.Thread(target=worker) for _ in range(concurrent_users)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    
    return results
```

## Performance Optimization Opportunities

### **1. Immediate Optimizations**
- **Database Indexes**: Add indexes on frequently queried fields
- **Query Optimization**: Reduce N+1 query problems
- **Connection Pooling**: Optimize database connection management

### **2. Refactor Optimizations**
- **Incremental Updates**: Replace full chain recalculation
- **Caching Strategy**: Implement Redis caching for expensive calculations
- **Background Processing**: Move heavy calculations to background jobs

### **3. Architecture Optimizations**
- **Event Sourcing**: Consider event sourcing for audit trails
- **Read Models**: Implement read models for reporting
- **Materialized Views**: Use materialized views for complex aggregations

## Next Steps

### **Week 2 Tasks**
- [ ] **Performance Test Setup**: Create performance testing infrastructure
- [ ] **Baseline Measurements**: Measure current performance metrics
- [ ] **Bottleneck Profiling**: Profile specific bottleneck operations
- [ ] **Load Testing**: Test with realistic data volumes

### **Week 3 Tasks**
- [ ] **Performance Analysis**: Analyze performance test results
- [ ] **Optimization Planning**: Plan performance optimizations
- [ ] **Target Setting**: Set performance targets for refactor

### **Week 4 Tasks**
- [ ] **Optimization Implementation**: Implement immediate optimizations
- [ ] **Performance Validation**: Validate optimization improvements
- [ ] **Refactor Planning**: Plan performance-focused refactor approach

## Conclusion

The current system has significant performance bottlenecks that will prevent scaling to the target volumes (500+ funds, 20,000+ events, 25+ companies). The O(n) complexity in chain recalculation operations is particularly problematic.

Performance analysis is critical for:
1. **Establishing Baselines**: Understanding current performance
2. **Identifying Bottlenecks**: Finding specific performance issues
3. **Setting Targets**: Defining performance goals for refactor
4. **Validating Improvements**: Ensuring refactor improves performance

The refactor must address these performance issues through:
1. **Incremental Updates**: Replace O(n) operations with O(1) operations
2. **Caching Strategy**: Implement intelligent caching for expensive calculations
3. **Background Processing**: Move heavy calculations to background jobs
4. **Database Optimization**: Optimize queries and add proper indexes

**Risk Level**: HIGH - Performance issues will prevent system scaling
**Priority**: CRITICAL - Must be addressed in refactor planning
