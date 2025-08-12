# Performance Analysis Template

## Operation Information
- **Operation Name**: `[OPERATION_NAME]`
- **Operation Type**: [CRUD/Calculation/Query/Update]
- **Primary Model**: `[MODEL_NAME]`
- **API Endpoint**: `[API_ENDPOINT]` (if applicable)

## Current Performance Metrics
### Baseline Measurements
- **Test Environment**: [Development/Staging/Production]
- **Data Volume**: [Number of records used in testing]
- **Response Time**: [Average/Min/Max in milliseconds]
- **Throughput**: [Operations per second]
- **Memory Usage**: [Peak memory usage in MB/GB]
- **Database Connections**: [Number of concurrent connections]

### Performance Test Results
| Test Scenario | Data Volume | Response Time | Throughput | Memory Usage | Notes |
|---------------|-------------|---------------|------------|--------------|-------|
| [SCENARIO_1] | [VOLUME] | [TIME]ms | [OPS]/s | [MEMORY]MB | [NOTES] |
| [SCENARIO_2] | [VOLUME] | [TIME]ms | [OPS]/s | [MEMORY]MB | [NOTES] |
| [SCENARIO_3] | [VOLUME] | [TIME]ms | [OPS]/s | [MEMORY]MB | [NOTES] |

## Scaling Analysis
### Current Scaling Characteristics
- **Linear Scaling**: [Yes/No] - [Explanation]
- **Bottleneck Point**: [Where performance degrades]
- **Degradation Rate**: [How quickly performance degrades with scale]

### Target Scale Requirements
- **Target Volume**: [Number of records/operations]
- **Target Response Time**: [Maximum acceptable response time]
- **Target Throughput**: [Minimum required operations per second]
- **Growth Rate**: [Expected growth rate per month]

## Bottleneck Identification
### Primary Bottlenecks
1. **[BOTTLENECK_1]**: [Description and impact]
2. **[BOTTLENECK_2]**: [Description and impact]
3. **[BOTTLENECK_3]**: [Description and impact]

### Bottleneck Analysis
#### Database Bottlenecks
- **Query Performance**: [Specific slow queries identified]
- **Index Issues**: [Missing or inefficient indexes]
- **Connection Pool**: [Connection pool configuration issues]
- **Transaction Size**: [Large transaction issues]

#### Application Bottlenecks
- **Algorithm Complexity**: [O(n), O(n²), etc. issues]
- **Memory Usage**: [Memory allocation/deallocation issues]
- **CPU Usage**: [CPU-intensive operations]
- **I/O Operations**: [File/network I/O issues]

#### Infrastructure Bottlenecks
- **Server Resources**: [CPU/Memory/Disk limitations]
- **Network Latency**: [Network-related delays]
- **External Services**: [Third-party service dependencies]

## Performance Profiling Results
### Profiling Tools Used
- [List of profiling tools and versions]

### Key Findings
1. **[FINDING_1]**: [Description and impact]
2. **[FINDING_2]**: [Description and impact]
3. **[FINDING_3]**: [Description and impact]

### Hot Paths Identified
- **[PATH_1]**: [Description of frequently executed code path]
- **[PATH_2]**: [Description of frequently executed code path]
- **[PATH_3]**: [Description of frequently executed code path]

## Optimization Opportunities
### Immediate Optimizations
1. **[OPTIMIZATION_1]**: [Description and expected impact]
2. **[OPTIMIZATION_2]**: [Description and expected impact]
3. **[OPTIMIZATION_3]**: [Description and expected impact]

### Architectural Optimizations
1. **[ARCH_OPTIMIZATION_1]**: [Description and expected impact]
2. **[ARCH_OPTIMIZATION_2]**: [Description and expected impact]
3. **[ARCH_OPTIMIZATION_3]**: [Description and expected impact]

### Caching Opportunities
1. **[CACHE_1]**: [What to cache and expected impact]
2. **[CACHE_2]**: [What to cache and expected impact]
3. **[CACHE_3]**: [What to cache and expected impact]

## Performance Targets
### Phase 2 Targets
- **Response Time**: [Target response time]
- **Throughput**: [Target throughput]
- **Memory Usage**: [Target memory usage]

### Phase 3 Targets
- **Response Time**: [Target response time]
- **Throughput**: [Target throughput]
- **Memory Usage**: [Target memory usage]

### Phase 4 Targets
- **Response Time**: [Target response time]
- **Throughput**: [Target throughput]
- **Memory Usage**: [Target memory usage]

### Phase 5 Targets
- **Response Time**: [Target response time]
- **Throughput**: [Target throughput]
- **Memory Usage**: [Target memory usage]

## Testing Strategy
### Performance Test Scenarios
1. **[SCENARIO_1]**: [Description and test data]
2. **[SCENARIO_2]**: [Description and test data]
3. **[SCENARIO_3]**: [Description and test data]

### Load Testing
- **Concurrent Users**: [Number of concurrent users to test]
- **Ramp-up Time**: [Time to ramp up to full load]
- **Sustained Load**: [Duration of sustained load testing]
- **Peak Load**: [Maximum load to test]

### Stress Testing
- **Breaking Point**: [Identify when system breaks]
- **Recovery Time**: [Time to recover from overload]
- **Degradation Pattern**: [How performance degrades under stress]

## Monitoring and Alerting
### Key Metrics to Monitor
1. **[METRIC_1]**: [Description and threshold]
2. **[METRIC_2]**: [Description and threshold]
3. **[METRIC_3]**: [Description and threshold]

### Alerting Thresholds
- **Warning Level**: [When to send warnings]
- **Critical Level**: [When to send critical alerts]
- **Escalation**: [Escalation procedures]

## Risk Assessment
### Performance Risks
- **Scaling Risk**: [Low/Medium/High] - [Explanation]
- **Bottleneck Risk**: [Low/Medium/High] - [Explanation]
- **Optimization Risk**: [Low/Medium/High] - [Explanation]

### Mitigation Strategies
1. **[MITIGATION_1]**: [Description of mitigation approach]
2. **[MITIGATION_2]**: [Description of mitigation approach]
3. **[MITIGATION_3]**: [Description of mitigation approach]

## Notes
[Additional observations, concerns, or insights about performance]

---

**Template Usage**: Copy this template for each operation analyzed. Focus on establishing accurate baselines and identifying specific bottlenecks that can be addressed in the refactor.
