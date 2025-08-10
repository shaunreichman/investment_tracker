# Companies UI API Contract

## **Overview**
This document defines the API contract between frontend and backend for the enhanced Companies UI. It serves as the single source of truth for data structures, field names, and API endpoints that both teams must implement.

## **Base URL**
All endpoints are relative to `/api/companies/{company_id}` where `{company_id}` is the numeric ID of the investment company.

## **Authentication & Headers**
- **Content-Type**: `application/json`
- **Authentication**: Standard session-based authentication (existing system)
- **Error Responses**: Standard error format with HTTP status codes

## **API Endpoints**

### **1. Company Overview Endpoint**
**URL**: `GET /api/companies/{company_id}/overview`  
**Purpose**: Provides portfolio summary data for the Overview tab

**Response Structure**:
```json
{
  "company": {
    "id": "number",
    "name": "string",
    "company_type": "string | null",
    "business_address": "string | null",
    "website": "string | null",
    "contracts": "string | null",
    "direct_numbers": "string | null",
    "direct_emails": "string | null"
  },
  "portfolio_summary": {
    "total_committed_capital": "number",
    "total_current_value": "number",
    "total_invested_capital": "number",
    "active_funds_count": "number",
    "completed_funds_count": "number",
    "fund_status_breakdown": {
      "active": "number",
      "completed": "number",
      "suspended": "number"
    }
  },
  "performance_summary": {
    "average_completed_irr": "number | null",
    "total_realized_gains": "number | null",
    "total_realized_losses": "number | null"
  },
  "last_activity": {
    "last_activity_date": "string (ISO 8601) | null",
    "days_since_last_activity": "number | null"
  }
}
```

**Notes**:
- `performance_summary` fields are `null` when no completed funds exist
- `last_activity_date` is the most recent activity across all funds
- All monetary values are in the fund's base currency

### **2. Enhanced Funds Endpoint**
**URL**: `GET /api/companies/{company_id}/funds/enhanced`  
**Purpose**: Provides comprehensive fund comparison data for the Funds tab

**Query Parameters**:
- `sort_by`: `string` (default: "start_date")
- `sort_order`: `"asc" | "desc"` (default: "desc")
- `status_filter`: `"all" | "active" | "completed" | "suspended"` (default: "all")
- `search`: `string` (optional, searches fund names and descriptions)
- `page`: `number` (default: 1)
- `per_page`: `number` (default: 25, max: 100)

**Response Structure**:
```json
{
  "funds": [
    {
      "id": "number",
      "name": "string",
      "description": "string | null",
      "currency": "string",
      "fund_type": "string",
      "status": "string",
      "tracking_type": "string",
      
      "fund_details": {
        "start_date": "string (ISO 8601)",
        "end_date": "string (ISO 8601) | null",
        "actual_duration_days": "number | null",
        "days_since_last_activity": "number"
      },
      
      "equity": {
        "commitment": "number",
        "invested_capital": "number",
        "current_value": "number",
        "current_equity_balance": "number"
      },
      
      "estimated_return": {
        "expected_irr": "number | null",
        "duration_months": "number | null"
      },
      
      "distributions": {
        "distribution_count": "number",
        "total_distribution_amount": "number",
        "last_distribution_date": "string (ISO 8601) | null",
        "distribution_frequency_months": "number | null"
      },
      
      "returns": {
        "completed_irr": "number | null",
        "performance_vs_expected": "number | null"
      },
      
      "performance": {
        "unrealized_gains_losses": "number",
        "realized_gains_losses": "number",
        "total_profit_loss": "number"
      }
    }
  ],
  "pagination": {
    "current_page": "number",
    "total_pages": "number",
    "total_funds": "number",
    "per_page": "number"
  },
  "filters": {
    "applied_status_filter": "string",
    "applied_search": "string | null"
  }
}
```

**Notes**:
- `performance_vs_expected` is `completed_irr - expected_irr` (null if either is null)
- `days_since_last_activity` is calculated from the most recent FundEvent
- `distribution_frequency_months` is calculated from historical distribution events
- All monetary values are in the fund's base currency

### **3. Company Details Endpoint**
**URL**: `GET /api/companies/{company_id}/details`  
**Purpose**: Provides comprehensive company information for the Company Details tab

**Response Structure**:
```json
{
  "company": {
    "id": "number",
    "name": "string",
    "company_type": "string | null",
    "business_address": "string | null",
    "website": "string | null",
    "contracts": "string | null",
    "direct_numbers": "string | null",
    "direct_emails": "string | null"
  }
}
```

## **Data Types & Formats**

### **Monetary Values**
- **Type**: `number` (decimal)
- **Precision**: 2 decimal places
- **Currency**: Each fund has its own base currency
- **Null Values**: `null` when calculation is not applicable

### **Dates**
- **Format**: ISO 8601 string (`YYYY-MM-DDTHH:mm:ss.sssZ`)
- **Timezone**: UTC
- **Null Values**: `null` when date is not applicable

### **Percentages**
- **Type**: `number` (decimal)
- **Format**: 0.15 represents 15%
- **Precision**: 4 decimal places
- **Null Values**: `null` when calculation is not applicable

### **Enums**
- **fund_type**: `"NAV-based" | "cost-based"`
- **status**: `"active" | "completed" | "suspended"`
- **tracking_type**: `"units" | "capital"`

## **Error Response Format**

**Standard Error Response**:
```json
{
  "error": {
    "code": "string",
    "message": "string",
    "details": "object | null"
  }
}
```

**Common HTTP Status Codes**:
- `200`: Success
- `400`: Bad Request (invalid parameters)
- `401`: Unauthorized (authentication required)
- `403`: Forbidden (insufficient permissions)
- `404`: Not Found (company or fund not found)
- `500`: Internal Server Error

**Error Codes**:
- `INVALID_COMPANY_ID`: Company ID is not a valid number
- `COMPANY_NOT_FOUND`: Company with specified ID does not exist
- `INSUFFICIENT_PERMISSIONS`: User cannot access this company
- `INVALID_SORT_PARAMETER`: Invalid sorting parameter
- `INVALID_FILTER_PARAMETER`: Invalid filter parameter

## **Performance Requirements**

### **Response Time Targets**
- **Company Overview**: < 500ms
- **Enhanced Funds**: < 1000ms (first page)
- **Company Details**: < 300ms

### **Data Limits**
- **Funds per page**: Maximum 100
- **Total funds per company**: Support up to 1000 funds
- **Events per fund**: Support up to 10,000 events

## **Data Consistency Rules**

### **Calculation Consistency**
- All calculated values must be consistent across endpoints
- Real-time calculations reflect current portfolio state
- Performance metrics only include completed funds where applicable

### **Null Value Handling**
- Use `null` for missing or inapplicable data
- Empty strings (`""`) are not allowed for missing data
- Zero values (`0`) represent actual zero amounts, not missing data

### **Currency Handling**
- Each fund maintains its own currency
- No automatic currency conversion
- Portfolio totals are calculated per currency

## **Versioning & Backward Compatibility**

### **API Versioning**
- Current version: v1 (no version prefix required)
- Future versions will use `/api/v2/companies/{id}/...` format
- Backward compatibility maintained within major versions

### **Field Deprecation**
- Deprecated fields will be marked in response headers
- Deprecated fields will continue to work for 6 months
- Clear deprecation notices in API documentation

## **Testing & Validation**

### **Required Test Cases**
- Valid company ID with existing data
- Valid company ID with no funds
- Invalid company ID (404 response)
- Unauthorized access (401/403 response)
- Invalid query parameters (400 response)
- Pagination edge cases (empty pages, last page)
- Sorting with various field combinations
- Filtering with various status values

### **Data Validation**
- All required fields must be present
- Numeric fields must be valid numbers
- Date fields must be valid ISO 8601 format
- Enum fields must contain valid values
- Monetary values must be non-negative

## **Implementation Notes**

### **Frontend Responsibilities**
- Handle loading states during API calls
- Implement error handling for all response types
- Manage pagination state and navigation
- Format and display data according to contract
- Handle null values gracefully in UI

### **Backend Responsibilities**
- Ensure all calculated values are accurate
- Implement efficient database queries
- Provide consistent error responses
- Maintain data integrity and consistency
- Optimize for response time targets

## **Future Considerations**

### **Planned Enhancements**
- Real-time updates via WebSocket
- Advanced filtering and search capabilities
- Export functionality (CSV, PDF)
- Bulk operations on multiple funds
- Advanced analytics and reporting

### **Scalability Considerations**
- Database indexing for common query patterns
- Caching strategies for expensive calculations
- Horizontal scaling for high-traffic scenarios
- Rate limiting and request throttling

---

**Document Version**: 1.0  
**Last Updated**: [Current Date]  
**Maintained By**: Backend Team  
**Reviewed By**: Frontend Team, Product Team
