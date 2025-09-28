"""
Company IRR Service.
"""

from typing import Optional, List
from sqlalchemy.orm import Session

from src.shared.services.shared_irr_service import SharedIrRService
from src.investment_company.models import InvestmentCompany
from src.investment_company.enums.company_enums import CompanyStatus
from src.fund.models.domain_fund_event import FundFieldChange
from src.fund.repositories import FundEventRepository


class CompanyIrRService:
    """
    Company IRR Service.
    """
    def __init__(self):
        """
        Initialize the CompanyIrRService.
        """
        self.shared_irr_service = SharedIrRService()
        self.fund_event_repository = FundEventRepository()
        
    def update_irrs(self, company: InvestmentCompany, fund_ids: List[int], session: Session) -> Optional[List[FundFieldChange]]:
        """
        Update the IRRs for a company.
        """
        old_completed_irr_gross = company.completed_irr_gross
        old_completed_irr_after_tax = company.completed_irr_after_tax
        old_completed_irr_real = company.completed_irr_real

        if company.status == CompanyStatus.ACTIVE:
            # ACTIVE: No IRRs meaningful (company has capital at risk)
            company.completed_irr_gross = None
            company.completed_irr_after_tax = None
            company.completed_irr_real = None
            
        elif company.status == CompanyStatus.COMPLETED:
            # COMPLETED: All IRRs are meaningful (tax obligations complete)
            events = self.fund_event_repository.get_fund_events(session, fund_ids=fund_ids)
            company.completed_irr_gross = self.shared_irr_service.calculate_irr_base(events, include_tax_payments=False, include_risk_free_charges=False, include_eofy_debt_cost=False)
            company.completed_irr_after_tax = self.shared_irr_service.calculate_irr_base(events, include_tax_payments=True, include_risk_free_charges=False, include_eofy_debt_cost=False)
            company.completed_irr_real = self.shared_irr_service.calculate_irr_base(events, include_tax_payments=True, include_risk_free_charges=True, include_eofy_debt_cost=True)

        irr_changes = []
        if old_completed_irr_gross != company.completed_irr_gross:
            irr_changes.append(FundFieldChange(company_or_company='COMPANY', object_id=company.id, field_name='completed_irr_gross', old_value=old_completed_irr_gross, new_value=company.completed_irr_gross))
        if old_completed_irr_after_tax != company.completed_irr_after_tax:
            irr_changes.append(FundFieldChange(company_or_company='COMPANY', object_id=company.id, field_name='completed_irr_after_tax', old_value=old_completed_irr_after_tax, new_value=company.completed_irr_after_tax))
        if old_completed_irr_real != company.completed_irr_real:
            irr_changes.append(FundFieldChange(company_or_company='COMPANY', object_id=company.id, field_name='completed_irr_real', old_value=old_completed_irr_real, new_value=company.completed_irr_real))
        
        return irr_changes if irr_changes else None