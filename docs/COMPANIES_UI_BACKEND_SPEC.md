# Companies UI Backend Enhancement Specification

## **Overview**
This specification defines the backend changes required to support the enhanced Companies UI with tabbed interface. The changes focus on adding company-level aggregations, profit/loss calculations, and enhanced data structures to support the new frontend requirements.

**Note**: This spec should be implemented in conjunction with the `COMPANIES_UI_API_CONTRACT.md` document, which defines the exact API interface that the frontend will consume.

## **Design Philosophy**
- **Investor-Centric Data**: Provide comprehensive portfolio metrics for investors, not fund managers
- **Performance-First**: Optimize calculations and queries for real-time portfolio analysis
- **Backward Compatibility**: Maintain existing API functionality while adding new capabilities
- **Data Consistency**: Ensure calculated values are accurate and consistent across all endpoints
- **Scalable Architecture**: Design for companies with 100+ funds and 1000+ events

## **Implementation Strategy**

### **Phase 1: Foundation & Data Model Extensions**
**Goal**: Extend data models to support company-level aggregations and profit/loss calculations
**Tasks**:
- [ ] Add new fields to InvestmentCompany model (company_type, business_address, website, contracts, direct_numbers, direct_emails)
- [ ] Add calculated properties to Fund model for profit/loss metrics
- [ ] Implement new calculation methods for unrealized/realized gains
- [ ] Add distribution tracking fields for enhanced fund comparison
- [ ] Create database migration scripts for new fields
**Design Principles**:
- All new fields are nullable to maintain backward compatibility
- Calculated properties use existing data relationships
- Profit/loss calculations handle both NAV-based and cost-based funds
- Distribution metrics aggregate from existing FundEvent data

### **Phase 2: Company-Level Aggregations**
**Goal**: Implement company-wide portfolio metrics and summary calculations
**Tasks**:
- [ ] Create get_company_summary_data method for Overview tab
- [ ] Implement get_company_performance_summary method (completed funds only)
- [ ] Add fund status distribution metrics
- [ ] Implement last activity tracking across company portfolio
**Design Principles**:
- Company performance metrics only include completed funds (IRR calculations)
- Status distribution provides quick portfolio health overview
- Last activity tracking helps identify stale investments

### **Phase 3: Enhanced Fund Metrics**
**Goal**: Provide comprehensive fund comparison data for the Funds tab table
**Tasks**:
- [ ] Implement get_enhanced_summary_data method for individual funds
- [ ] Create get_distribution_summary method for distribution metrics
- [ ] Add days_since_last_activity calculation
- [ ] Implement distribution frequency analysis
- [ ] Create performance vs. expected metrics
**Design Principles**:
- All metrics are standardized between NAV-based and cost-based funds
- Distribution analysis uses historical event data from FundEvent records
- Performance metrics compare actual vs. expected outcomes
- Activity tracking helps identify funds needing attention
- Backend provides calculated values to ensure consistency and performance

### **Phase 4: API Endpoint Enhancements**
**Goal**: Create new API endpoints and enhance existing ones to support the enhanced UI
**Tasks**:
- [ ] Implement /api/companies/{id}/overview endpoint for Overview tab
- [ ] Create /api/companies/{id}/funds/enhanced endpoint for Funds tab
- [ ] Enhance existing company funds endpoint with new metrics
- [ ] Add sorting and filtering parameters to enhanced endpoints
- [ ] Implement pagination for large fund portfolios
**Design Principles**:
- New endpoints maintain consistent response format
- Enhanced endpoints include all existing data plus new metrics
- Sorting and filtering support common investor use cases
- Pagination prevents performance issues with large datasets

### **Phase 5: Performance Optimization (Deferred)**
**Goal**: Optimize calculations and queries for production performance
**Note**: This phase will be implemented after initial deployment and performance monitoring reveals specific bottlenecks
**Tasks**:
- [ ] Add database indexes for common query patterns
- [ ] Implement caching strategy for expensive calculations
- [ ] Optimize queries with eager loading and batch operations
- [ ] Add performance monitoring and metrics
- [ ] Create materialized views for complex aggregations
**Design Principles**:
- Database indexes target most common query patterns
- Caching strategy balances performance with data freshness
- Query optimization focuses on reducing database round trips
- Performance monitoring ensures scalability

## **Data Requirements**

### **New Data Fields**
- **Company Metadata**: company_type, business_address, website, contracts, direct_numbers, direct_emails
- **Fund Performance**: unrealized_gains_losses, realized_gains_losses, total_profit_loss
- **Distribution Tracking**: distribution_count, last_distribution_date, distribution_frequency_months
- **Activity Tracking**: days_since_last_activity, last_activity_date

### **Distribution Tracking Details**
Distribution tracking aggregates FundEvent data to provide:
- **distribution_count**: Total number of distribution events per fund
- **last_distribution_date**: Most recent distribution event date
- **distribution_frequency_months**: Average months between distributions (calculated from historical data)

### **Calculated Metrics**
- **Company Portfolio**: total_committed_capital, total_current_value, total_invested_capital
- **Fund Status**: active_funds_count, completed_funds_count, fund_status_breakdown
- **Performance Summary**: average_completed_irr, total_realized_gains, total_realized_losses

### **Data Relationships**
- **Fund to Company**: All fund metrics roll up to company portfolio totals
- **Events to Fund**: Distribution and activity metrics derived from FundEvent data
- **Tax to Performance**: Realized gains/losses calculated from tax and distribution events
- **Status to Calculations**: Fund status determines which performance metrics are available

## **Technical Architecture**

### **Model Extensions**
- **InvestmentCompany**: New fields and company-level calculation methods
- **Fund**: Enhanced properties and profit/loss calculation methods
- **FundEvent**: Distribution and activity tracking enhancements
- **New Methods**: Centralized calculation logic for portfolio metrics

### **API Implementation**
- **Endpoints**: Implement the three new endpoints defined in `COMPANIES_UI_API_CONTRACT.md`
- **Response Format**: Ensure all responses match the exact structure specified in the contract
- **Data Types**: Follow the data type specifications for numbers, dates, and enums
- **Error Handling**: Implement the standard error response format

### **API Structure**
- **Overview Endpoint**: Company summary with portfolio metrics
- **Enhanced Funds Endpoint**: Comprehensive fund comparison data
- **Backward Compatibility**: Existing endpoints continue to work unchanged
- **Response Format**: Consistent structure across all new endpoints

### **Database Design**
- **New Columns**: Optional extensions to existing tables
- **Indexes**: Performance optimization for common query patterns
- **Migrations**: Alembic-based schema evolution
- **Data Integrity**: Constraints and validation for new fields

## **Performance Considerations**

### **Calculation Strategy**
- **Lazy Calculation**: Compute metrics on-demand rather than storing
- **Batch Processing**: Calculate multiple fund metrics in single operations
- **Caching**: Cache expensive calculations with appropriate TTL
- **Incremental Updates**: Update metrics when underlying data changes

### **Query Optimization**
- **Eager Loading**: Reduce N+1 query problems
- **Composite Indexes**: Support common sorting and filtering patterns
- **Partial Indexes**: Optimize status-based queries
- **Covering Indexes**: Include frequently accessed columns

### **Scalability Targets**
- **Fund Count**: Support 100+ funds per company
- **Event Count**: Handle 1000+ events per fund
- **Response Time**: API responses under 500ms
- **Concurrent Users**: Support 10+ simultaneous users

## **Testing Strategy**

### **Unit Testing**
- **Model Methods**: Test all new calculation methods
- **Edge Cases**: Test with empty portfolios, single funds, etc.
- **Performance**: Test calculation performance with large datasets
- **Data Consistency**: Verify calculated values match expected results

### **Integration Testing**
- **API Endpoints**: Test new and enhanced endpoints
- **Data Flow**: Ensure data consistency across endpoints
- **Error Handling**: Test with invalid data and edge cases
- **Performance**: Monitor response times and resource usage

### **Data Validation**
- **Calculation Accuracy**: Verify financial calculations against manual verification
- **Data Integrity**: Ensure new fields maintain referential integrity
- **Backward Compatibility**: Verify existing functionality unchanged
- **Migration Safety**: Test database migrations with production-like data

## **Success Metrics**

### **Performance Targets**
- **API Response Time**: Company overview under 500ms, fund list under 1000ms
- **Calculation Performance**: Fund metrics calculated in under 100ms
- **Database Efficiency**: Maximum 5 queries per API request
- **Memory Usage**: Calculations stay within reasonable memory bounds

### **Data Quality**
- **Accuracy**: Calculated values match manual verification within 0.01%
- **Completeness**: All required fields populated for active funds
- **Consistency**: Data consistent across different endpoints and views
- **Timeliness**: Real-time calculations reflect current portfolio state

### **User Experience**
- **Portfolio Overview**: Investors can quickly assess portfolio health
- **Fund Comparison**: Easy comparison of fund performance and metrics
- **Data Discovery**: Clear presentation of key performance indicators
- **Navigation**: Intuitive access to detailed fund information

## **Technical Gaps - To Be Addressed Later**

### **Data Consistency & Error Handling**
- Data consistency between real-time calculations and cached values
- Comprehensive error handling for complex financial calculations
- Graceful degradation when calculations fail or timeout

### **Performance Monitoring & Optimization**
- Real-time performance monitoring for API endpoints
- Caching strategy implementation details
- Database query optimization based on actual usage patterns

### **Advanced Features**
- Currency breakdown calculations (if needed)
- Materialized views for complex aggregations
- Advanced caching strategies

## **Next Steps**

1. **Review and Approve**: Get stakeholder approval on backend architecture
2. **Database Design**: Finalize database schema changes and migration strategy
3. **Implementation**: Begin with Phase 1 (data model extensions)
4. **Testing**: Implement comprehensive testing strategy
5. **Deployment**: Deploy changes incrementally with monitoring
6. **Documentation**: Update API documentation and developer guides
