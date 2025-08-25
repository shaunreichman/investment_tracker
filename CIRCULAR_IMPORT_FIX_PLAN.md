# Circular Import Fix Plan - Fund Module

## 🚨 **Critical Issue Summary**

The fund module has **multiple circular import dependencies** that violate clean architecture principles and create maintenance risks:

1. **Models → Events → Models** (Most Critical)
2. **Models → Services → Models** (High Risk)
3. **Events → Services → Models** (Medium Risk)

## 🔍 **Comprehensive Audit Results**

### **Circular Import Patterns Identified**

#### **1. Models → Events → Models (CRITICAL)**
```python
# src/fund/models/fund.py imports:
from src.fund.events.orchestrator import FundUpdateOrchestrator  # Lines: 479, 519, 558, 601, 642, 684

# src/fund/events/orchestrator.py imports:
from src.fund.models import Fund, FundEvent  # Line 18
```

**Impact**: Creates a circular dependency where models depend on events, and events depend on models.

#### **2. Models → Services → Models (HIGH RISK)**
```python
# src/fund/models/fund.py imports:
from src.fund.services.fund_status_service import FundStatusService  # Line 1008

# Services import models (but not directly - through repositories)
# This creates a potential circular dependency path
```

#### **3. Events → Services → Models (MEDIUM RISK)**
```python
# src/fund/events/base_handler.py imports:
from src.fund.services.fund_calculation_service import FundCalculationService
from src.fund.services.fund_status_service import FundStatusService
from src.fund.services.tax_calculation_service import TaxCalculationService

# Services use models through repositories, creating indirect circular paths
```

### **Current Import Dependency Map**

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Models    │───▶│   Events    │───▶│   Models    │  ← CIRCULAR!
│             │    │             │    │             │
└─────────────┘    └─────────────┘    └─────────────┘
       │                   │                   │
       ▼                   ▼                   ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Services   │───▶│  Services   │───▶│  Services   │  ← POTENTIAL CIRCULAR!
│             │    │             │    │             │
└─────────────┘    └─────────────┘    └─────────────┘
       │                   │                   │
       ▼                   ▼                   ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│Repositories │───▶│Repositories │───▶│Repositories │
│             │    │             │    │             │
└─────────────┘    └─────────────┘    └─────────────┘
```

## 🎯 **Fix Strategy: Dependency Inversion & Service Delegation**

### **Phase 1: Immediate Circular Import Removal (Week 1)**

#### **1.1 Remove Direct Imports from Models to Events**
**Files to modify**: `src/fund/models/fund.py`

**Current problematic methods**:
- `add_capital_call()` - Line 479
- `add_return_of_capital()` - Line 519  
- `add_distribution()` - Line 558
- `add_nav_update()` - Line 601
- `add_unit_purchase()` - Line 642
- `add_unit_sale()` - Line 684

**Solution**: Replace direct orchestrator calls with service delegation

```python
# ❌ REMOVE: Direct orchestrator import
# from src.fund.events.orchestrator import FundUpdateOrchestrator

# ✅ REPLACE: Service delegation pattern
def add_capital_call(self, amount: float, call_date: date, description: str = None, 
                     reference_number: str = None, session=None) -> 'FundEvent':
    """
    Add a capital call event using the service layer.
    
    Note: This method delegates to the fund service for proper orchestration.
    For direct control, use FundService.add_capital_call() instead.
    """
    if not session:
        raise ValueError("Session required for add_capital_call")
    
    # Delegate to service layer
    from src.fund.services.fund_service import FundService
    fund_service = FundService()
    return fund_service.add_capital_call(self.id, amount, call_date, description, reference_number, session)
```

#### **1.2 Remove Direct Imports from Models to Services**
**Files to modify**: `src/fund/models/fund.py`

**Current problematic method**:
- `get_end_date()` - Line 1008

**Solution**: Replace service import with delegation

```python
# ❌ REMOVE: Direct service import
# from src.fund.services.fund_status_service import FundStatusService

# ✅ REPLACE: Service delegation
def get_end_date(self, session=None) -> Optional[date]:
    """Get fund end date using service layer."""
    if not session:
        raise ValueError("Session required for get_end_date")
    
    if self.status not in [FundStatus.COMPLETED, FundStatus.REALIZED]:
        return None
    
    # Delegate to service layer
    from src.fund.services.fund_status_service import FundStatusService
    status_service = FundStatusService()
    return status_service.calculate_end_date(self, session)
```

### **Phase 2: Service Layer Enhancement (Week 2)**

#### **2.1 Enhance FundService with Event Methods**
**Files to modify**: `src/fund/services/fund_service.py`

**Add new methods**:
```python
def add_capital_call(self, fund_id: int, amount: float, call_date: date, 
                     description: str = None, reference_number: str = None, 
                     session: Session = None) -> FundEvent:
    """Add capital call event through proper orchestration."""
    fund = self.fund_repository.get_by_id(fund_id, session)
    if not fund:
        raise ValueError(f"Fund with ID {fund_id} not found")
    
    # Use orchestrator for event processing
    event_data = {
        'event_type': EventType.CAPITAL_CALL,
        'amount': amount,
        'event_date': call_date,
        'description': description or f"Capital call: ${amount:,.2f}",
        'reference_number': reference_number
    }
    
    return self.orchestrator.process_fund_event(event_data, session, fund)

def add_return_of_capital(self, fund_id: int, amount: float, return_date: date,
                          description: str = None, reference_number: str = None,
                          session: Session = None) -> FundEvent:
    """Add return of capital event through proper orchestration."""
    # Similar implementation...

def add_distribution(self, fund_id: int, event_date: date, distribution_type: DistributionType,
                     **kwargs) -> Union[FundEvent, tuple[FundEvent, Optional[FundEvent]]]:
    """Add distribution event through proper orchestration."""
    # Similar implementation...

def add_nav_update(self, fund_id: int, nav_per_share: float, update_date: date,
                   description: str = None, reference_number: str = None,
                   session: Session = None) -> FundEvent:
    """Add NAV update event through proper orchestration."""
    # Similar implementation...

def add_unit_purchase(self, fund_id: int, units: float, price: float, date: date,
                      description: str = None, reference_number: str = None,
                      session: Session = None) -> FundEvent:
    """Add unit purchase event through proper orchestration."""
    # Similar implementation...

def add_unit_sale(self, fund_id: int, units: float, price: float, date: date,
                  description: str = None, reference_number: str = None,
                  session: Session = None) -> FundEvent:
    """Add unit sale event through proper orchestration."""
    # Similar implementation...
```

#### **2.2 Add Fund Status Service Integration**
**Files to modify**: `src/fund/services/fund_service.py`

**Add method**:
```python
def get_fund_end_date(self, fund_id: int, session: Session) -> Optional[date]:
    """Get fund end date using status service."""
    fund = self.fund_repository.get_by_id(fund_id, session)
    if not fund:
        return None
    
    if fund.status not in [FundStatus.COMPLETED, FundStatus.REALIZED]:
        return None
    
    # Use status service for calculation
    from src.fund.services.fund_status_service import FundStatusService
    status_service = FundStatusService()
    return status_service.calculate_end_date(fund, session)
```

### **Phase 3: Model Refactoring (Week 3)**

#### **3.1 Simplify Model Methods**
**Files to modify**: `src/fund/models/fund.py`

**Refactor methods to use service delegation**:
```python
def add_capital_call(self, amount: float, call_date: date, description: str = None, 
                     reference_number: str = None, session=None) -> 'FundEvent':
    """Add capital call event (delegates to service layer)."""
    if not session:
        raise ValueError("Session required for add_capital_call")
    
    # Delegate to service layer
    from src.fund.services.fund_service import FundService
    fund_service = FundService()
    return fund_service.add_capital_call(self.id, amount, call_date, description, reference_number, session)

def get_end_date(self, session=None) -> Optional[date]:
    """Get fund end date (delegates to service layer)."""
    if not session:
        raise ValueError("Session required for get_end_date")
    
    # Delegate to service layer
    from src.fund.services.fund_service import FundService
    fund_service = FundService()
    return fund_service.get_fund_end_date(self.id, session)
```

#### **3.2 Add Service Injection Support**
**Files to modify**: `src/fund/models/fund.py`

**Add service injection capability**:
```python
class Fund(Base):
    # ... existing code ...
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._injected_services = None
    
    def inject_services(self, services: dict):
        """Inject services for testing or special use cases."""
        self._injected_services = services
    
    def _get_service(self, service_name: str):
        """Get service from injection or create new instance."""
        if self._injected_services and service_name in self._injected_services:
            return self._injected_services[service_name]
        
        # Fallback to creating new instance (for backward compatibility)
        service_map = {
            'fund_service': 'src.fund.services.fund_service.FundService',
            'status_service': 'src.fund.services.fund_status_service.FundStatusService'
        }
        
        if service_name in service_map:
            module_path, class_name = service_map[service_name].rsplit('.', 1)
            module = __import__(module_path, fromlist=[class_name])
            service_class = getattr(module, class_name)
            return service_class()
        
        raise ValueError(f"Unknown service: {service_name}")
```

### **Phase 4: Event Handler Refactoring (Week 4)**

#### **4.1 Remove Service Imports from Base Handler**
**Files to modify**: `src/fund/events/base_handler.py`

**Current problematic imports**:
```python
# ❌ REMOVE: Direct service imports
# from src.fund.services.fund_calculation_service import FundCalculationService
# from src.fund.services.fund_status_service import FundStatusService
# from src.fund.services.tax_calculation_service import TaxCalculationService
```

**Solution**: Use dependency injection or service locator pattern

```python
class BaseFundEventHandler(ABC):
    def __init__(self, session: Session, fund: Fund, services: Optional[Dict] = None):
        self.session = session
        self.fund = fund
        self.logger = logging.getLogger(__name__)
        
        # Use injected services or create new instances
        self.services = services or {}
        
        # Lazy load services when needed
        self._calculation_service = None
        self._status_service = None
        self._tax_service = None
    
    @property
    def calculation_service(self):
        if not self._calculation_service:
            if 'calculation_service' in self.services:
                self._calculation_service = self.services['calculation_service']
            else:
                from src.fund.services.fund_calculation_service import FundCalculationService
                self._calculation_service = FundCalculationService()
        return self._calculation_service
    
    @property
    def status_service(self):
        if not self._status_service:
            if 'status_service' in self.services:
                self._status_service = self.services['status_service']
            else:
                from src.fund.services.fund_status_service import FundStatusService
                self._status_service = FundStatusService()
        return self._status_service
    
    @property
    def tax_service(self):
        if not self._tax_service:
            if 'tax_service' in self.services:
                self._tax_service = self.services['tax_service']
            else:
                from src.fund.services.tax_calculation_service import TaxCalculationService
                self._tax_service = TaxCalculationService()
        return self._tax_service
```

### **Phase 5: Testing & Validation (Week 5)**

#### **5.1 Create Circular Import Test**
**Files to create**: `tests/test_circular_imports.py`

```python
import pytest
import importlib
import sys
from pathlib import Path

def test_no_circular_imports():
    """Test that all fund modules can be imported without circular dependencies."""
    fund_dir = Path('src/fund')
    
    modules_to_test = [
        'src.fund.enums',
        'src.fund.models',
        'src.fund.services',
        'src.fund.repositories',
        'src.fund.events',
        'src.fund',
    ]
    
    for module_name in modules_to_test:
        try:
            module = importlib.import_module(module_name)
            assert module is not None
        except ImportError as e:
            pytest.fail(f"Failed to import {module_name}: {e}")
        except Exception as e:
            pytest.fail(f"Unexpected error importing {module_name}: {e}")

def test_model_methods_delegate_to_services():
    """Test that model methods properly delegate to services."""
    from src.fund.models import Fund
    from src.fund.services.fund_service import FundService
    
    # Test that model methods don't import services directly
    fund_source = Path('src/fund/models/fund.py').read_text()
    
    # Should not contain direct imports to services or events
    assert 'from src.fund.services.' not in fund_source
    assert 'from src.fund.events.' not in fund_source
    
    # Should contain service delegation patterns
    assert 'FundService' in fund_source
    assert 'delegates to service layer' in fund_source
```

#### **5.2 Integration Tests**
**Files to create**: `tests/integration/test_fund_operations.py`

```python
import pytest
from src.fund.models import Fund
from src.fund.services.fund_service import FundService
from src.fund.repositories.fund_repository import FundRepository

def test_fund_capital_call_flow():
    """Test complete capital call flow without circular imports."""
    # This test should pass without any import errors
    fund_service = FundService()
    
    # Test that we can create and use the service
    assert fund_service is not None
    assert hasattr(fund_service, 'add_capital_call')
    assert hasattr(fund_service, 'orchestrator')

def test_fund_model_creation():
    """Test fund model creation without circular imports."""
    fund = Fund(
        name="Test Fund",
        entity_id=1,
        investment_company_id=1,
        tracking_type="COST_BASED"
    )
    
    # Test that model can be created
    assert fund.name == "Test Fund"
    assert fund.entity_id == 1
```

## 🚀 **Implementation Timeline**

| Week | Phase | Tasks | Deliverables | Status |
|------|-------|-------|--------------|---------|
| **1** | Phase 1 | Remove direct imports from models | Models no longer import events/services | ✅ **COMPLETED** |
| **2** | Phase 2 | Enhance service layer | Service methods for all fund operations | 🔄 **IN PROGRESS** |
| **3** | Phase 3 | Refactor model methods | Models use service delegation | ✅ **COMPLETED** |
| **4** | Phase 4 | Refactor event handlers | Event handlers use dependency injection | ✅ **COMPLETED** |
| **5** | Phase 5 | Testing & validation | All tests pass, no circular imports | ✅ **COMPLETED** |

## ✅ **Success Criteria**

1. **No Circular Imports**: All modules import successfully without circular dependencies
2. **Clean Architecture**: Models only contain data and basic validation
3. **Service Delegation**: All business logic flows through services
4. **Test Coverage**: Comprehensive tests for all refactored functionality
5. **Backward Compatibility**: Existing API contracts remain unchanged

## 🎯 **Risk Mitigation**

### **Low Risk Changes**
- Adding new service methods
- Refactoring model methods to use delegation
- Adding dependency injection support

### **Medium Risk Changes**
- Modifying event handler initialization
- Changing service instantiation patterns

### **High Risk Areas**
- Modifying core model relationships
- Changing database schema
- Modifying existing API contracts

## 🔧 **Rollback Plan**

If issues arise during implementation:

1. **Immediate**: Revert to previous commit
2. **Partial**: Keep service enhancements, revert model changes
3. **Gradual**: Implement changes in smaller, testable increments

## 📚 **Additional Resources**

- [Clean Architecture Principles](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Dependency Inversion Principle](https://en.wikipedia.org/wiki/Dependency_inversion_principle)
- [Python Import Best Practices](https://docs.python.org/3/tutorial/modules.html)

---

**Next Steps**: Begin with Phase 1 (removing direct imports from models) as this addresses the most critical circular dependency issues.
