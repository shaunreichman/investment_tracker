# Phase 6.1 Performance Testing Infrastructure

## Overview

This directory contains the complete performance testing infrastructure for Phase 6.1 of the Fund Architecture Refactor. The infrastructure establishes performance baselines, identifies optimization opportunities, and prepares the system for Phase 6.2-6.4 performance optimizations.

## 🎯 Phase 6.1 Objectives

- **Establish Performance Baselines**: Measure current system performance characteristics
- **Identify Bottlenecks**: Find slow operations and optimization opportunities  
- **Generate Load Test Data**: Create realistic datasets for performance testing
- **Analyze Database Performance**: Identify slow queries and missing indexes
- **Set Up Testing Infrastructure**: Prepare tools for ongoing performance monitoring

## 📁 Scripts Overview

### 1. `run_phase6_1_baseline.py` - Main Runner Script
**Purpose**: Orchestrates all Phase 6.1 activities in sequence

**Features**:
- Generates load test data
- Runs performance baseline tests
- Analyzes database queries
- Generates comprehensive reports
- Provides success/failure summary

**Usage**:
```bash
# Run complete Phase 6.1 baseline
python scripts/performance/run_phase6_1_baseline.py

# Check script status
python scripts/performance/run_phase6_1_baseline.py --help
```

### 2. `phase6_performance_baseline.py` - Performance Testing Engine
**Purpose**: Measures performance of critical system operations

**Tests Performed**:
- **Event Creation Performance**: Single event creation timing
- **Fund Summary Updates**: Fund summary calculation performance
- **Database Queries**: Common query performance analysis
- **API Endpoint Performance**: Simulated API operation timing
- **Memory Usage Patterns**: Memory consumption tracking

**Metrics Collected**:
- Mean, median, min, max durations
- Standard deviation analysis
- Memory usage deltas
- Performance categorization (excellent/good/acceptable/slow/very_slow)

### 3. `load_test_data_generator.py` - Test Data Generator
**Purpose**: Creates realistic test datasets for performance testing

**Data Generated**:
- **15 Investment Companies**: Realistic company profiles
- **25 Entities**: Various entity types and characteristics
- **75 Funds**: Mix of cost-based and NAV-based funds
- **1,500 Events**: Realistic event patterns and distributions
- **200 Tax Statements**: Complete tax statement coverage

**Realistic Patterns**:
- Event type distribution (25% capital calls, 30% distributions, etc.)
- Fund type distribution (70% cost-based, 30% NAV-based)
- Fund status distribution (60% active, 30% realized, 10% completed)
- Realistic amounts and dates within fund lifetimes

### 4. `database_query_analyzer.py` - Database Performance Analyzer
**Purpose**: Analyzes database performance and identifies optimization opportunities

**Analysis Performed**:
- **Index Analysis**: Identifies missing critical indexes
- **Query Performance**: Tests common query patterns
- **Connection Pool Analysis**: Examines connection management
- **Optimization Recommendations**: Generates actionable improvement suggestions

**Critical Indexes Checked**:
- `funds`: status+tracking_type, investment_company_id, entity_id
- `fund_events`: fund_id+event_date, event_type+event_date
- `tax_statements`: fund_id+financial_year, statement_date
- `investment_companies`: name, abn, acn
- `entities`: name, abn, acn

## 🚀 Quick Start

### Prerequisites
- Python 3.13+ with virtual environment activated
- Database connection configured
- Required dependencies installed (`psutil`)

### Step 1: Generate Load Test Data
```bash
cd scripts/performance
python load_test_data_generator.py
```

### Step 2: Run Performance Baseline
```bash
python phase6_performance_baseline.py
```

### Step 3: Analyze Database Performance
```bash
python database_query_analyzer.py
```

### Step 4: Run Complete Phase 6.1
```bash
python run_phase6_1_baseline.py
```

## 📊 Expected Outputs

### Performance Baseline Report
- Event creation performance metrics
- Fund summary update timing
- Database query performance analysis
- API endpoint response times
- Memory usage patterns

### Database Analysis Report
- Missing index identification
- Slow query detection
- Connection pool analysis
- Optimization recommendations
- Priority-based improvement suggestions

### Load Test Data Summary
- 15 companies created
- 25 entities created
- 75 funds created
- 1,500 events created
- 200 tax statements created

## 🎯 Performance Targets

### Current Baseline Targets
- **Single Event Creation**: < 100ms (baseline measurement)
- **Fund Summary Updates**: < 200ms (baseline measurement)
- **API Response Times**: < 500ms (baseline measurement)
- **Database Queries**: < 100ms (baseline measurement)

### Phase 6.2-6.4 Targets
- **Single Event Creation**: < 50ms (50% improvement)
- **Fund Summary Updates**: < 25ms (87.5% improvement)
- **API Response Times**: < 100ms (80% improvement)
- **Database Queries**: < 50ms (50% improvement)

## 🔍 Troubleshooting

### Common Issues

#### 1. Import Errors
**Problem**: Module import failures
**Solution**: Ensure virtual environment is activated and project root is in Python path

#### 2. Database Connection Issues
**Problem**: Cannot connect to database
**Solution**: Verify database configuration and connection settings

#### 3. Memory Issues
**Problem**: Out of memory during large dataset generation
**Solution**: Reduce dataset sizes in generator scripts

#### 4. Permission Errors
**Problem**: Cannot write to logs or reports directories
**Solution**: Ensure write permissions on project directories

### Debug Mode
Enable detailed logging by modifying logging level in scripts:
```python
logging.basicConfig(level=logging.DEBUG, ...)
```

## 📈 Next Steps

### Phase 6.2: Incremental Calculations
- Implement O(1) updates for capital events
- Replace full chain recalculations
- Optimize fund summary updates

### Phase 6.3: Redis Caching
- Set up Redis infrastructure
- Implement caching strategies
- Add cache invalidation logic

### Phase 6.4: Database Optimization
- Add missing indexes
- Optimize slow queries
- Improve connection pooling

## 📝 File Structure

```
scripts/performance/
├── README.md                           # This file
├── run_phase6_1_baseline.py           # Main orchestrator
├── phase6_performance_baseline.py      # Performance testing engine
├── load_test_data_generator.py         # Test data generator
├── database_query_analyzer.py          # Database performance analyzer
└── baseline_results_*.txt              # Generated performance reports
```

## 🤝 Contributing

When adding new performance tests or analysis:

1. **Follow Naming Conventions**: Use descriptive names for new scripts
2. **Add Documentation**: Include docstrings and comments
3. **Update README**: Document new functionality
4. **Test Thoroughly**: Ensure scripts work in isolation
5. **Handle Errors**: Implement proper error handling and logging

## 📞 Support

For issues or questions about Phase 6.1 performance testing:

1. Check the logs in `logs/` directory
2. Review generated reports for specific issues
3. Verify database connectivity and permissions
4. Check Python environment and dependencies

---

**Phase 6.1 Status**: ✅ **Infrastructure Ready** - All scripts created and tested
**Next Phase**: 🚀 **Phase 6.2** - Incremental Calculations & O(1) Updates
