#!/usr/bin/env python3
"""
Database Query Analyzer for Phase 6.1 Performance Testing.

This script analyzes database query performance to identify:
- Slow queries and bottlenecks
- Missing indexes
- Query optimization opportunities
- Connection and session management issues
"""

import time
import statistics
from typing import List, Dict, Any, Tuple
import logging
from sqlalchemy import text, inspect
from sqlalchemy.orm import Session

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Database imports
from src.database import get_database_session
from src.fund.models import Fund, FundEvent, FundStatus
from src.fund.enums import FundType, EventType
from src.investment_company.models import InvestmentCompany
from src.entity.models import Entity
from src.tax.models import TaxStatement

class DatabaseQueryAnalyzer:
    """Analyzes database query performance and identifies optimization opportunities."""
    
    def __init__(self):
        self.analysis_results = {}
        self.slow_queries = []
        self.missing_indexes = []
        self.optimization_recommendations = []
    
    def analyze_table_indexes(self, session: Session) -> Dict[str, Any]:
        """Analyze current table indexes and identify missing ones."""
        logger.info("Analyzing table indexes...")
        
        inspector = inspect(session.bind)
        index_analysis = {}
        
        # Analyze key tables
        key_tables = ['funds', 'fund_events', 'tax_statements', 'investment_companies', 'entities']
        
        for table_name in key_tables:
            try:
                indexes = inspector.get_indexes(table_name)
                columns = [col['name'] for col in inspector.get_columns(table_name)]
                
                index_analysis[table_name] = {
                    'indexes': indexes,
                    'columns': columns,
                    'missing_indexes': []
                }
                
                # Check for missing critical indexes
                self._identify_missing_indexes(table_name, columns, indexes, index_analysis[table_name])
                
            except Exception as e:
                logger.warning(f"Could not analyze table {table_name}: {e}")
                index_analysis[table_name] = {'error': str(e)}
        
        self.analysis_results['index_analysis'] = index_analysis
        return index_analysis
    
    def _identify_missing_indexes(self, table_name: str, columns: List[str], 
                                existing_indexes: List[Dict], analysis: Dict) -> None:
        """Identify missing critical indexes for a table."""
        
        # Define critical index patterns for each table
        critical_indexes = {
            'funds': [
                ('status', 'tracking_type'),
                ('investment_company_id',),
                ('entity_id',),
                ('current_equity_balance', 'status'),
                ('start_date', 'end_date')
            ],
            'fund_events': [
                ('fund_id', 'event_date'),
                ('event_type', 'event_date'),
                ('fund_id', 'event_type'),
                ('event_date',),
                ('reference_number',)
            ],
            'tax_statements': [
                ('fund_id', 'financial_year'),
                ('financial_year',),
                ('statement_date',)
            ],
            'investment_companies': [
                ('name',),
                ('abn',),
                ('acn',)
            ],
            'entities': [
                ('name',),
                ('abn',),
                ('acn',)
            ]
        }
        
        if table_name not in critical_indexes:
            return
        
        existing_index_columns = set()
        for idx in existing_indexes:
            if 'column_names' in idx:
                existing_index_columns.add(tuple(sorted(idx['column_names'])))
        
        for critical_index in critical_indexes[table_name]:
            if critical_index not in existing_index_columns:
                analysis['missing_indexes'].append({
                    'columns': critical_index,
                    'type': 'single' if len(critical_index) == 1 else 'composite',
                    'priority': 'high' if len(critical_index) == 1 else 'medium'
                })
    
    def analyze_query_performance(self, session: Session) -> Dict[str, Any]:
        """Analyze performance of common database queries."""
        logger.info("Analyzing query performance...")
        
        query_tests = [
            # Simple lookups
            ("fund_by_id", "SELECT * FROM funds WHERE id = 1", lambda: session.query(Fund).filter(Fund.id == 1).first()),
            ("fund_by_name", "SELECT * FROM funds WHERE name LIKE '%Test%'", lambda: session.query(Fund).filter(Fund.name.like('%Test%')).first()),
            
            # Filtered queries
            ("active_funds", "SELECT * FROM funds WHERE status = 'ACTIVE'", lambda: session.query(Fund).filter(Fund.status == FundStatus.ACTIVE).all()),
            ("cost_based_funds", "SELECT * FROM funds WHERE tracking_type = 'COST_BASED'", lambda: session.query(Fund).filter(Fund.tracking_type == FundType.COST_BASED).all()),
            
            # Event queries
            ("fund_events", "SELECT * FROM fund_events WHERE fund_id = 1 ORDER BY event_date DESC", lambda: session.query(FundEvent).filter(FundEvent.fund_id == 1).order_by(FundEvent.event_date.desc()).all()),
            ("events_by_type", "SELECT * FROM fund_events WHERE event_type = 'CAPITAL_CALL'", lambda: session.query(FundEvent).filter(FundEvent.event_type == EventType.CAPITAL_CALL).all()),
            ("recent_events", "SELECT * FROM fund_events ORDER BY event_date DESC LIMIT 100", lambda: session.query(FundEvent).order_by(FundEvent.event_date.desc()).limit(100).all()),
            
            # Join queries
            ("fund_with_company", "SELECT f.*, ic.* FROM funds f JOIN investment_companies ic ON f.investment_company_id = ic.id", lambda: session.query(Fund, InvestmentCompany).join(InvestmentCompany, Fund.investment_company_id == InvestmentCompany.id).limit(10).all()),
            ("fund_with_entity", "SELECT f.*, e.* FROM funds f JOIN entities e ON f.entity_id = e.id", lambda: session.query(Fund, Entity).join(Entity, Fund.entity_id == Entity.id).limit(10).all()),
            
            # Complex queries
            ("fund_summary", "SELECT f.*, COUNT(fe.id) as event_count FROM funds f LEFT JOIN fund_events fe ON f.id = fe.fund_id GROUP BY f.id", lambda: session.query(Fund, session.query(FundEvent).filter(FundEvent.fund_id == Fund.id).count().label('event_count')).limit(10).all()),
            ("tax_statements_by_fund", "SELECT f.name, ts.* FROM funds f JOIN tax_statements ts ON f.id = ts.fund_id", lambda: session.query(Fund.name, TaxStatement).join(TaxStatement, Fund.id == TaxStatement.fund_id).limit(10).all()),
        ]
        
        query_results = {}
        
        for test_name, sql_query, test_func in query_tests:
            logger.info(f"Testing query: {test_name}")
            
            durations = []
            for i in range(10):  # Run each query 10 times for averaging
                start_time = time.time()
                try:
                    result = test_func()
                    duration = (time.time() - start_time) * 1000  # Convert to milliseconds
                    durations.append(duration)
                except Exception as e:
                    logger.warning(f"Query {test_name} failed: {e}")
                    durations.append(0)
            
            # Calculate statistics
            if durations and any(d > 0 for d in durations):
                valid_durations = [d for d in durations if d > 0]
                query_results[test_name] = {
                    'sql': sql_query,
                    'iterations': len(valid_durations),
                    'mean_duration_ms': statistics.mean(valid_durations),
                    'median_duration_ms': statistics.median(valid_durations),
                    'min_duration_ms': min(valid_durations),
                    'max_duration_ms': max(valid_durations),
                    'total_duration_ms': sum(valid_durations),
                    'performance_category': self._categorize_performance(statistics.mean(valid_durations))
                }
                
                # Track slow queries
                if statistics.mean(valid_durations) > 100:  # > 100ms is slow
                    self.slow_queries.append({
                        'query_name': test_name,
                        'sql': sql_query,
                        'avg_duration_ms': statistics.mean(valid_durations),
                        'priority': 'high' if statistics.mean(valid_durations) > 500 else 'medium'
                    })
        
        self.analysis_results['query_performance'] = query_results
        return query_results
    
    def _categorize_performance(self, duration_ms: float) -> str:
        """Categorize query performance."""
        if duration_ms < 10:
            return "excellent"
        elif duration_ms < 50:
            return "good"
        elif duration_ms < 100:
            return "acceptable"
        elif duration_ms < 500:
            return "slow"
        else:
            return "very_slow"
    
    def analyze_connection_usage(self, session: Session) -> Dict[str, Any]:
        """Analyze database connection and session usage patterns."""
        logger.info("Analyzing connection usage patterns...")
        
        connection_analysis = {}
        
        try:
            # Get connection info
            engine = session.bind
            connection_analysis['engine_info'] = {
                'name': engine.name,
                'driver': engine.driver,
                'pool_size': engine.pool.size(),
                'pool_checked_in': engine.pool.checkedin(),
                'pool_checked_out': engine.pool.checkedout(),
                'pool_overflow': engine.pool.overflow()
            }
            
            # Test connection pool behavior
            pool_tests = []
            for i in range(5):
                start_time = time.time()
                with engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
                    duration = (time.time() - start_time) * 1000
                    pool_tests.append(duration)
            
            connection_analysis['pool_performance'] = {
                'connection_time_ms': statistics.mean(pool_tests),
                'pool_efficiency': 'good' if statistics.mean(pool_tests) < 10 else 'needs_optimization'
            }
            
        except Exception as e:
            logger.warning(f"Could not analyze connection usage: {e}")
            connection_analysis['error'] = str(e)
        
        self.analysis_results['connection_analysis'] = connection_analysis
        return connection_analysis
    
    def generate_optimization_recommendations(self) -> List[Dict[str, Any]]:
        """Generate optimization recommendations based on analysis."""
        logger.info("Generating optimization recommendations...")
        
        recommendations = []
        
        # Index recommendations
        if 'index_analysis' in self.analysis_results:
            for table_name, analysis in self.analysis_results['index_analysis'].items():
                if 'missing_indexes' in analysis and analysis['missing_indexes']:
                    for missing_idx in analysis['missing_indexes']:
                        recommendations.append({
                            'type': 'index',
                            'priority': missing_idx['priority'],
                            'table': table_name,
                            'columns': missing_idx['columns'],
                            'description': f"Add {'composite' if missing_idx['type'] == 'composite' else 'single'} index on {table_name}.{', '.join(missing_idx['columns'])}",
                            'impact': 'high' if missing_idx['priority'] == 'high' else 'medium'
                        })
        
        # Query optimization recommendations
        if 'query_performance' in self.analysis_results:
            for query_name, performance in self.analysis_results['query_performance'].items():
                if performance['performance_category'] in ['slow', 'very_slow']:
                    recommendations.append({
                        'type': 'query_optimization',
                        'priority': 'high' if performance['performance_category'] == 'very_slow' else 'medium',
                        'query': query_name,
                        'current_performance': f"{performance['mean_duration_ms']:.2f}ms",
                        'description': f"Optimize {query_name} query - currently {performance['performance_category']}",
                        'impact': 'high' if performance['performance_category'] == 'very_slow' else 'medium'
                    })
        
        # Connection optimization recommendations
        if 'connection_analysis' in self.analysis_results:
            conn_analysis = self.analysis_results['connection_analysis']
            if 'pool_performance' in conn_analysis:
                pool_perf = conn_analysis['pool_performance']
                if pool_perf['pool_efficiency'] == 'needs_optimization':
                    recommendations.append({
                        'type': 'connection_optimization',
                        'priority': 'medium',
                        'description': "Optimize database connection pool configuration",
                        'impact': 'medium'
                    })
        
        # General recommendations
        recommendations.extend([
            {
                'type': 'general',
                'priority': 'high',
                'description': "Implement Redis caching for frequently accessed fund summaries",
                'impact': 'high'
            },
            {
                'type': 'general',
                'priority': 'high',
                'description': "Replace full chain recalculations with incremental updates",
                'impact': 'high'
            },
            {
                'type': 'general',
                'priority': 'medium',
                'description': "Add query result caching for expensive operations",
                'impact': 'medium'
            }
        ])
        
        self.optimization_recommendations = recommendations
        return recommendations
    
    def generate_report(self) -> str:
        """Generate comprehensive database analysis report."""
        if not self.analysis_results:
            return "No analysis results available. Run analyze_database() first."
        
        report = []
        report.append("=" * 80)
        report.append("PHASE 6.1 DATABASE QUERY ANALYSIS REPORT")
        report.append("=" * 80)
        report.append("")
        
        # Index Analysis
        if 'index_analysis' in self.analysis_results:
            report.append("INDEX ANALYSIS:")
            report.append("-" * 40)
            for table_name, analysis in self.analysis_results['index_analysis'].items():
                if 'missing_indexes' in analysis and analysis['missing_indexes']:
                    report.append(f"  {table_name.upper()}:")
                    for missing_idx in analysis['missing_indexes']:
                        report.append(f"    Missing {missing_idx['type']} index on: {', '.join(missing_idx['columns'])} (Priority: {missing_idx['priority']})")
                else:
                    report.append(f"  {table_name.upper()}: All critical indexes present")
            report.append("")
        
        # Query Performance
        if 'query_performance' in self.analysis_results:
            report.append("QUERY PERFORMANCE ANALYSIS:")
            report.append("-" * 40)
            
            # Group by performance category
            performance_groups = {}
            for query_name, perf in self.analysis_results['query_performance'].items():
                category = perf['performance_category']
                if category not in performance_groups:
                    performance_groups[category] = []
                performance_groups[category].append((query_name, perf))
            
            for category in ['excellent', 'good', 'acceptable', 'slow', 'very_slow']:
                if category in performance_groups:
                    report.append(f"  {category.upper()} PERFORMANCE:")
                    for query_name, perf in performance_groups[category]:
                        report.append(f"    {query_name}: {perf['mean_duration_ms']:.2f}ms avg")
                    report.append("")
        
        # Slow Queries
        if self.slow_queries:
            report.append("SLOW QUERIES (Require Immediate Attention):")
            report.append("-" * 40)
            for slow_query in sorted(self.slow_queries, key=lambda x: x['avg_duration_ms'], reverse=True):
                report.append(f"  {slow_query['query_name']}: {slow_query['avg_duration_ms']:.2f}ms avg (Priority: {slow_query['priority']})")
            report.append("")
        
        # Connection Analysis
        if 'connection_analysis' in self.analysis_results:
            report.append("CONNECTION POOL ANALYSIS:")
            report.append("-" * 40)
            conn_analysis = self.analysis_results['connection_analysis']
            if 'engine_info' in conn_analysis:
                engine_info = conn_analysis['engine_info']
                report.append(f"  Pool Size: {engine_info['pool_size']}")
                report.append(f"  Checked In: {engine_info['pool_checked_in']}")
                report.append(f"  Checked Out: {engine_info['pool_checked_out']}")
                report.append(f"  Overflow: {engine_info['pool_overflow']}")
            if 'pool_performance' in conn_analysis:
                pool_perf = conn_analysis['pool_performance']
                report.append(f"  Connection Time: {pool_perf['connection_time_ms']:.2f}ms")
                report.append(f"  Pool Efficiency: {pool_perf['pool_efficiency']}")
            report.append("")
        
        # Optimization Recommendations
        if self.optimization_recommendations:
            report.append("OPTIMIZATION RECOMMENDATIONS:")
            report.append("-" * 40)
            
            # Group by priority
            priority_groups = {}
            for rec in self.optimization_recommendations:
                priority = rec['priority']
                if priority not in priority_groups:
                    priority_groups[priority] = []
                priority_groups[priority].append(rec)
            
            for priority in ['high', 'medium', 'low']:
                if priority in priority_groups:
                    report.append(f"  {priority.upper()} PRIORITY:")
                    for rec in priority_groups[priority]:
                        report.append(f"    [{rec['type'].upper()}] {rec['description']}")
                    report.append("")
        
        # Next Steps
        report.append("NEXT STEPS:")
        report.append("-" * 40)
        report.append("  1. Address high-priority missing indexes")
        report.append("  2. Optimize slow queries identified above")
        report.append("  3. Implement Phase 6.2 incremental calculations")
        report.append("  4. Add Phase 6.3 Redis caching layer")
        report.append("  5. Optimize database connection pooling")
        report.append("")
        report.append("=" * 80)
        
        return "\n".join(report)
    
    def analyze_database(self, session: Session) -> Dict[str, Any]:
        """Run comprehensive database analysis."""
        logger.info("Starting comprehensive database analysis...")
        
        try:
            # Run all analyses
            self.analyze_table_indexes(session)
            self.analyze_query_performance(session)
            self.analyze_connection_usage(session)
            self.generate_optimization_recommendations()
            
            logger.info("Database analysis completed successfully")
            return self.analysis_results
            
        except Exception as e:
            logger.error(f"Error during database analysis: {e}")
            raise

def main():
    """Main function to run database analysis."""
    logger.info("Starting Phase 6.1 Database Query Analysis")
    
    try:
        # Get database session
        engine, session_factory, scoped_session = get_database_session()
        session = scoped_session()
        
        try:
            # Create analyzer
            analyzer = DatabaseQueryAnalyzer()
            
            # Run comprehensive analysis
            results = analyzer.analyze_database(session)
            
            # Generate and display report
            report = analyzer.generate_report()
            print(report)
            
            # Save results to file
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"scripts/performance/database_analysis_{timestamp}.txt"
            
            with open(filename, 'w') as f:
                f.write(report)
            
            logger.info(f"Database analysis report saved to {filename}")
            logger.info("Phase 6.1 Database Analysis completed successfully")
            
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"Error in database analysis: {e}")
        raise

if __name__ == "__main__":
    main()
