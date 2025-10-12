"""
Company Fund Event Secondary Service.
"""

from typing import List
from sqlalchemy.orm import Session
from src.shared.models import DomainFieldChange
from src.shared.enums.domain_update_event_enums import DomainObjectType
from src.company.repositories.company_repository import CompanyRepository
from src.company.enums.company_enums import CompanyStatus
from src.fund.enums.fund_enums import FundStatus
from src.company.services.company_irr_service import CompanyIrRService
from src.company.services.company_equity_service import CompanyEquityService

class CompanyFundEventSecondaryService:
    """
    Company Fund Event Secondary Service.
    """
    
    def __init__(self):
        """
        Initialize the CompanyFundEventSecondaryService.
        """
        self.company_repository = CompanyRepository()
        self.company_irr_service = CompanyIrRService()
        self.company_equity_service = CompanyEquityService()


    def handle_event_secondary_impact(self, company_id: int, fund_changes: List[DomainFieldChange], session: Session) -> list[DomainFieldChange]:
        """
        Handle the secondary impact of a company event.

        Args:
            company_id: ID of the company
            fund_changes: List of DomainFieldChange objects for the fund changes
            session: Database session
            
        Returns:
            List[DomainFieldChange] with updated values and metadata
            
        Raises:
            ValueError: If the company is not found
        """
        all_company_changes: list[DomainFieldChange] = []

        company = self.company_repository.get_company_by_id(company_id, session)
        if not company:
            raise ValueError(f"Company with ID {company_id} not found")

        # 0. Get all the fund ids for the company
        from src.fund.repositories.fund_repository import FundRepository
        fund_repository = FundRepository()
        funds = fund_repository.get_funds(session, company_ids=[company_id])
        fund_ids = [fund.id for fund in funds]

        for fund_change in fund_changes:
            fund_change_dict = fund_change.to_dict()

            # 1. Check the start date of the fund
            if fund_change_dict['field_name'] == 'start_date':
                # Convert serialized date string back to date object for comparison
                from datetime import date
                new_start_date = date.fromisoformat(fund_change_dict['new_value']) if isinstance(fund_change_dict['new_value'], str) else fund_change_dict['new_value']
                if company.start_date is None or company.start_date > new_start_date:
                    old_start_date = company.start_date
                    company.start_date = new_start_date
                    all_company_changes.append(DomainFieldChange(domain_object_type=DomainObjectType.COMPANY, domain_object_id=company_id, field_name='start_date', old_value=old_start_date, new_value=new_start_date))

                    # If the start date changes we need to update the duration
                    old_duration = company.current_duration
                    from src.shared.calculators.duration_months_calculator import DurationMonthsCalculator
                    end_date = company.end_date if company.end_date else date.today()
                    new_duration = DurationMonthsCalculator.calculate_duration_months(company.start_date, end_date)
                    if old_duration != new_duration:
                        all_company_changes.append(DomainFieldChange(domain_object_type=DomainObjectType.COMPANY, domain_object_id=company_id, field_name='current_duration', old_value=old_duration, new_value=new_duration))
                        company.current_duration = new_duration

            # 2. Check the pnl of the fund
            elif fund_change_dict['field_name'] == 'pnl':
                all_company_changes.append(DomainFieldChange(domain_object_type=DomainObjectType.COMPANY, domain_object_id=company_id, field_name='pnl', old_value=company.pnl, new_value=company.pnl+fund_change_dict['new_value']))
                company.pnl += fund_change_dict['new_value']
            elif fund_change_dict['field_name'] == 'realized_pnl':
                all_company_changes.append(DomainFieldChange(domain_object_type=DomainObjectType.COMPANY, domain_object_id=company_id, field_name='realized_pnl', old_value=company.realized_pnl, new_value=company.realized_pnl+fund_change_dict['new_value']))
                company.realized_pnl += fund_change_dict['new_value']
            elif fund_change_dict['field_name'] == 'unrealized_pnl':
                all_company_changes.append(DomainFieldChange(domain_object_type=DomainObjectType.COMPANY, domain_object_id=company_id, field_name='unrealized_pnl', old_value=company.unrealized_pnl, new_value=company.unrealized_pnl+fund_change_dict['new_value']))
                company.unrealized_pnl += fund_change_dict['new_value']
            elif fund_change_dict['field_name'] == 'realized_pnl_capital_gain':
                all_company_changes.append(DomainFieldChange(domain_object_type=DomainObjectType.COMPANY, domain_object_id=company_id, field_name='realized_pnl_capital_gain', old_value=company.realized_pnl_capital_gain, new_value=company.realized_pnl_capital_gain+fund_change_dict['new_value']))
                company.realized_pnl_capital_gain += fund_change_dict['new_value']
            elif fund_change_dict['field_name'] == 'unrealized_pnl_capital_gain':
                all_company_changes.append(DomainFieldChange(domain_object_type=DomainObjectType.COMPANY, domain_object_id=company_id, field_name='unrealized_pnl_capital_gain', old_value=company.unrealized_pnl_capital_gain, new_value=company.unrealized_pnl_capital_gain+fund_change_dict['new_value']))
                company.unrealized_pnl_capital_gain += fund_change_dict['new_value']
            elif fund_change_dict['field_name'] == 'realized_pnl_dividend':
                all_company_changes.append(DomainFieldChange(domain_object_type=DomainObjectType.COMPANY, domain_object_id=company_id, field_name='realized_pnl_dividend', old_value=company.realized_pnl_dividend, new_value=company.realized_pnl_dividend+fund_change_dict['new_value']))
                company.realized_pnl_dividend += fund_change_dict['new_value']
            elif fund_change_dict['field_name'] == 'realized_pnl_interest':
                all_company_changes.append(DomainFieldChange(domain_object_type=DomainObjectType.COMPANY, domain_object_id=company_id, field_name='realized_pnl_interest', old_value=company.realized_pnl_interest, new_value=company.realized_pnl_interest+fund_change_dict['new_value']))
                company.realized_pnl_interest += fund_change_dict['new_value']
            elif fund_change_dict['field_name'] == 'realized_pnl_distribution':
                all_company_changes.append(DomainFieldChange(domain_object_type=DomainObjectType.COMPANY, domain_object_id=company_id, field_name='realized_pnl_distribution', old_value=company.realized_pnl_distribution, new_value=company.realized_pnl_distribution+fund_change_dict['new_value']))
                company.realized_pnl_distribution += fund_change_dict['new_value']


            # 3. Check the status of the fund
            elif fund_change_dict['field_name'] == 'status':
                # Convert serialized enum values back to enum objects for comparison
                old_fund_status_str = fund_change_dict['old_value']
                new_fund_status_str = fund_change_dict['new_value']
                
                # Convert string values back to enum objects
                old_fund_status = FundStatus(old_fund_status_str) if isinstance(old_fund_status_str, str) else old_fund_status_str
                new_fund_status = FundStatus(new_fund_status_str) if isinstance(new_fund_status_str, str) else new_fund_status_str
                
                # Decrease count for old status
                if old_fund_status == FundStatus.ACTIVE:
                    all_company_changes.append(DomainFieldChange(domain_object_type=DomainObjectType.COMPANY, domain_object_id=company_id, field_name='total_funds_active', old_value=company.total_funds_active, new_value=company.total_funds_active-1))
                    company.total_funds_active -= 1
                elif old_fund_status == FundStatus.REALIZED:
                    all_company_changes.append(DomainFieldChange(domain_object_type=DomainObjectType.COMPANY, domain_object_id=company_id, field_name='total_funds_realized', old_value=company.total_funds_realized, new_value=company.total_funds_realized-1))
                    company.total_funds_realized -= 1
                elif old_fund_status == FundStatus.COMPLETED:
                    all_company_changes.append(DomainFieldChange(domain_object_type=DomainObjectType.COMPANY, domain_object_id=company_id, field_name='total_funds_completed', old_value=company.total_funds_completed, new_value=company.total_funds_completed-1))
                    company.total_funds_completed -= 1
                
                # Increase count for new status
                if new_fund_status == FundStatus.ACTIVE:
                    all_company_changes.append(DomainFieldChange(domain_object_type=DomainObjectType.COMPANY, domain_object_id=company_id, field_name='total_funds_active', old_value=company.total_funds_active, new_value=company.total_funds_active+1))
                    company.total_funds_active += 1
                elif new_fund_status == FundStatus.REALIZED:
                    all_company_changes.append(DomainFieldChange(domain_object_type=DomainObjectType.COMPANY, domain_object_id=company_id, field_name='total_funds_realized', old_value=company.total_funds_realized, new_value=company.total_funds_realized+1))
                    company.total_funds_realized += 1
                elif new_fund_status == FundStatus.COMPLETED:
                    all_company_changes.append(DomainFieldChange(domain_object_type=DomainObjectType.COMPANY, domain_object_id=company_id, field_name='total_funds_completed', old_value=company.total_funds_completed, new_value=company.total_funds_completed+1))
                    company.total_funds_completed += 1

                # Update company status based on active funds count
                if company.total_funds_active == 0 and old_fund_status == FundStatus.ACTIVE:
                    all_company_changes.append(DomainFieldChange(domain_object_type=DomainObjectType.COMPANY, domain_object_id=company_id, field_name='status', old_value=company.status, new_value=CompanyStatus.COMPLETED))
                    company.status = CompanyStatus.COMPLETED
                    all_company_changes.append(self.company_irr_service.update_irrs(company, fund_ids, session))
                elif company.total_funds_active == 1 and old_fund_status != FundStatus.ACTIVE:
                    all_company_changes.append(DomainFieldChange(domain_object_type=DomainObjectType.COMPANY, domain_object_id=company_id, field_name='status', old_value=company.status, new_value=CompanyStatus.ACTIVE))
                    company.status = CompanyStatus.ACTIVE
                    all_company_changes.append(self.company_irr_service.update_irrs(company, fund_ids, session))

            # 4. Check the average equity balance of the fund
            elif fund_change_dict['field_name'] == 'average_equity_balance' or fund_change_dict['field_name'] == 'current_equity_balance' or fund_change_dict['field_name'] == 'end_date':
                # check if this has already been updated
                for change in all_company_changes:
                    if change.field_name == 'average_equity_balance' or change.field_name == 'current_equity_balance' or change.field_name == 'end_date':
                        continue
                all_company_changes.append(self.company_equity_service.update_company_equity_fields(company_id, fund_ids, session))

        return all_company_changes


    def update_company_after_fund_creation(self, company_id: int, fund_commitment_amount: float, session: Session) -> list[DomainFieldChange]:
        """
        Update the company after a fund is created.

        Args:
            company_id: ID of the company
            fund_commitment_amount: Commitment amount of the fund
            session: Database session
            
        Returns:
            List[DomainFieldChange] with updated values and metadata
            
        Raises:
            ValueError: If the company is not found
        """
        all_company_changes: list[DomainFieldChange] = []

        company = self.company_repository.get_company_by_id(company_id, session)
        if not company:
            raise ValueError(f"Company with ID {company_id} not found")

        all_company_changes.append(DomainFieldChange(domain_object_type=DomainObjectType.COMPANY, domain_object_id=company_id, field_name='total_funds', old_value=company.total_funds, new_value=company.total_funds+1))
        all_company_changes.append(DomainFieldChange(domain_object_type=DomainObjectType.COMPANY, domain_object_id=company_id, field_name='total_funds_active', old_value=company.total_funds_active, new_value=company.total_funds_active+1))
        all_company_changes.append(DomainFieldChange(domain_object_type=DomainObjectType.COMPANY, domain_object_id=company_id, field_name='total_commitment_amount', old_value=company.total_commitment_amount, new_value=company.total_commitment_amount+fund_commitment_amount))

        # Update the company
        company.total_funds += 1
        company.total_funds_active += 1
        company.total_commitment_amount += fund_commitment_amount

        return all_company_changes

    def update_company_after_fund_deletion(self, company_id: int, fund_commitment_amount: float, fund_status: FundStatus, session: Session) -> list[DomainFieldChange]:
        """
        Update the company after a fund is deleted.

        Args:
            company_id: ID of the company
            fund_commitment_amount: Commitment amount of the fund
            fund_status: Status of the fund
            session: Database session
            
        Returns:
            List[DomainFieldChange] with updated values and metadata
            
        Raises:
            ValueError: If the company is not found
        """
        all_company_changes: list[DomainFieldChange] = []

        company = self.company_repository.get_company_by_id(company_id, session)
        if not company:
            raise ValueError(f"Company with ID {company_id} not found")

        all_company_changes.append(DomainFieldChange(domain_object_type=DomainObjectType.COMPANY, domain_object_id=company_id, field_name='total_funds', old_value=company.total_funds, new_value=company.total_funds-1))
        company.total_funds -= 1

        # Decrease count for old status
        if fund_status == FundStatus.ACTIVE:
            all_company_changes.append(DomainFieldChange(domain_object_type=DomainObjectType.COMPANY, domain_object_id=company_id, field_name='total_funds_active', old_value=company.total_funds_active, new_value=company.total_funds_active-1))
            company.total_funds_active -= 1
        elif fund_status == FundStatus.REALIZED:
            all_company_changes.append(DomainFieldChange(domain_object_type=DomainObjectType.COMPANY, domain_object_id=company_id, field_name='total_funds_realized', old_value=company.total_funds_realized, new_value=company.total_funds_realized-1))
            company.total_funds_realized -= 1
        elif fund_status == FundStatus.COMPLETED:
            all_company_changes.append(DomainFieldChange(domain_object_type=DomainObjectType.COMPANY, domain_object_id=company_id, field_name='total_funds_completed', old_value=company.total_funds_completed, new_value=company.total_funds_completed-1))
            company.total_funds_completed -= 1

        all_company_changes.append(DomainFieldChange(domain_object_type=DomainObjectType.COMPANY, domain_object_id=company_id, field_name='total_commitment_amount', old_value=company.total_commitment_amount, new_value=company.total_commitment_amount-fund_commitment_amount))
        company.total_commitment_amount -= fund_commitment_amount

        return all_company_changes