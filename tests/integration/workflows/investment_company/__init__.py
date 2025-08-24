"""
Investment Company Workflow Integration Tests.

This package contains integration tests for investment company workflows,
testing complete end-to-end processes from API to database.

Test Modules:
- test_company_creation_workflow.py: Company setup workflow
- test_company_portfolio_workflow.py: Portfolio management workflow  
- test_company_contact_workflow.py: Contact management workflow
- test_cross_domain_coordination.py: Fund-company-entity coordination
- test_event_driven_workflows.py: Event-driven operation flows

These tests ensure all layers (API, Services, Repositories, Models) work together
correctly and maintain data consistency across the system.
"""

__all__ = [
    'test_company_creation_workflow',
    'test_company_portfolio_workflow', 
    'test_company_contact_workflow',
    'test_cross_domain_coordination',
    'test_event_driven_workflows'
]
