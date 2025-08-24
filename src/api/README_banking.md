# Enhanced Banking API Documentation

## Overview

The Enhanced Banking API provides enterprise-grade REST endpoints for banking operations with standardized response formats, comprehensive error handling, and performance optimization. This API is designed to achieve sub-50ms response times and maintain professional standards for enterprise applications.

## API Version

**Current Version**: v2  
**Base URL**: `/api/v2`

## Response Format

All API responses follow a standardized format for consistency and ease of integration.

### Success Response Format

```json
{
  "success": true,
  "message": "Operation completed successfully",
  "data": {
    // Response data specific to the operation
  },
  "timestamp": "2025-01-16T10:30:00.000Z"
}
```

### Error Response Format

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {
      // Additional error details if available
    },
    "timestamp": "2025-01-16T10:30:00.000Z"
  },
  "timestamp": "2025-01-16T10:30:00.000Z"
}
```

### List Response Format

```json
{
  "success": true,
  "message": "Retrieved 25 banks",
  "data": {
    "data": [
      // Array of items
    ],
    "total_count": 100,
    "page": 1,
    "page_size": 25,
    "has_next": true,
    "has_previous": false
  },
  "timestamp": "2025-01-16T10:30:00.000Z"
}
```

## Error Codes

| Code | Description | HTTP Status |
|------|-------------|-------------|
| `VALIDATION_ERROR` | Input validation failed | 400 |
| `MISSING_REQUIRED_FIELD` | Required field is missing | 400 |
| `INVALID_FORMAT` | Invalid data format | 400 |
| `INVALID_VALUE` | Invalid field value | 400 |
| `BANK_NOT_FOUND` | Bank not found | 404 |
| `BANK_ACCOUNT_NOT_FOUND` | Bank account not found | 404 |
| `ENTITY_NOT_FOUND` | Entity not found | 404 |
| `DUPLICATE_BANK` | Bank already exists | 409 |
| `DUPLICATE_ACCOUNT` | Bank account already exists | 409 |
| `INTERNAL_ERROR` | Internal server error | 500 |
| `DATABASE_ERROR` | Database operation failed | 500 |
| `SERVICE_UNAVAILABLE` | Service temporarily unavailable | 503 |

## Endpoints

### Banks

#### Get All Banks

**GET** `/api/v2/banks`

Retrieve a paginated list of all banks with summary data.

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `page_size` (optional): Number of items per page (default: 50, max: 100)

**Response:**
```json
{
  "success": true,
  "message": "Retrieved 25 banks",
  "data": {
    "data": [
      {
        "id": 1,
        "name": "Commonwealth Bank",
        "country": "AU",
        "swift_bic": "CTBAAU2S",
        "created_at": "2025-01-01T00:00:00.000Z",
        "updated_at": "2025-01-01T00:00:00.000Z"
      }
    ],
    "total_count": 100,
    "page": 1,
    "page_size": 25,
    "has_next": true,
    "has_previous": false
  }
}
```

#### Create Bank

**POST** `/api/v2/banks`

Create a new bank.

**Request Body:**
```json
{
  "name": "Commonwealth Bank",
  "country": "AU",
  "swift_bic": "CTBAAU2S"
}
```

**Required Fields:**
- `name`: Bank name
- `country`: ISO 3166-1 alpha-2 country code

**Optional Fields:**
- `swift_bic`: SWIFT/BIC identifier

**Response:**
```json
{
  "success": true,
  "message": "Bank created successfully",
  "data": {
    "id": 1,
    "name": "Commonwealth Bank",
    "country": "AU",
    "swift_bic": "CTBAAU2S",
    "created_at": "2025-01-16T10:30:00.000Z",
    "updated_at": "2025-01-16T10:30:00.000Z"
  }
}
```

#### Update Bank

**PUT** `/api/v2/banks/{bank_id}`

Update an existing bank.

**Path Parameters:**
- `bank_id`: ID of the bank to update

**Request Body:** (all fields optional)
```json
{
  "name": "Updated Bank Name",
  "country": "US",
  "swift_bic": "NEWBIC12"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Bank updated successfully",
  "data": {
    "id": 1,
    "name": "Updated Bank Name",
    "country": "US",
    "swift_bic": "NEWBIC12",
    "created_at": "2025-01-01T00:00:00.000Z",
    "updated_at": "2025-01-16T10:30:00.000Z"
  }
}
```

#### Delete Bank

**DELETE** `/api/v2/banks/{bank_id}`

Delete a bank.

**Path Parameters:**
- `bank_id`: ID of the bank to delete

**Response:**
```json
{
  "success": true,
  "message": "Bank deleted successfully",
  "timestamp": "2025-01-16T10:30:00.000Z"
}
```

### Bank Accounts

#### Get All Bank Accounts

**GET** `/api/v2/bank-accounts`

Retrieve a paginated list of all bank accounts with summary data.

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `page_size` (optional): Number of items per page (default: 50, max: 100)

**Response:**
```json
{
  "success": true,
  "message": "Retrieved 25 bank accounts",
  "data": {
    "data": [
      {
        "id": 1,
        "account_name": "Main Operating Account",
        "account_number": "123456789",
        "currency": "AUD",
        "is_active": true,
        "entity_id": 1,
        "bank": {
          "id": 1,
          "name": "Commonwealth Bank",
          "country": "AU",
          "swift_bic": "CTBAAU2S",
          "created_at": "2025-01-01T00:00:00.000Z",
          "updated_at": "2025-01-01T00:00:00.000Z"
        },
        "created_at": "2025-01-01T00:00:00.000Z",
        "updated_at": "2025-01-01T00:00:00.000Z"
      }
    ],
    "total_count": 100,
    "page": 1,
    "page_size": 25,
    "has_next": true,
    "has_previous": false
  }
}
```

#### Create Bank Account

**POST** `/api/v2/bank-accounts`

Create a new bank account.

**Request Body:**
```json
{
  "entity_id": 1,
  "bank_id": 1,
  "account_name": "Main Operating Account",
  "account_number": "123456789",
  "currency": "AUD",
  "is_active": true
}
```

**Required Fields:**
- `entity_id`: Owner entity ID
- `bank_id`: Linked bank ID
- `account_name`: Human-readable account name
- `account_number`: Account number
- `currency`: ISO-4217 currency code

**Optional Fields:**
- `is_active`: Active status flag (default: true)

**Response:**
```json
{
  "success": true,
  "message": "Bank account created successfully",
  "data": {
    "id": 1,
    "account_name": "Main Operating Account",
    "account_number": "123456789",
    "currency": "AUD",
    "is_active": true,
    "entity_id": 1,
    "bank": {
      "id": 1,
      "name": "Commonwealth Bank",
      "country": "AU",
      "swift_bic": "CTBAAU2S",
      "created_at": "2025-01-01T00:00:00.000Z",
      "updated_at": "2025-01-01T00:00:00.000Z"
    },
    "created_at": "2025-01-16T10:30:00.000Z",
    "updated_at": "2025-01-16T10:30:00.000Z"
  }
}
```

#### Update Bank Account

**PUT** `/api/v2/bank-accounts/{account_id}`

Update an existing bank account.

**Path Parameters:**
- `account_id`: ID of the account to update

**Request Body:** (all fields optional)
```json
{
  "account_name": "Updated Account Name",
  "currency": "USD",
  "is_active": false
}
```

**Response:**
```json
{
  "success": true,
  "message": "Bank account updated successfully",
  "data": {
    "id": 1,
    "account_name": "Updated Account Name",
    "account_number": "123456789",
    "currency": "USD",
    "is_active": false,
    "entity_id": 1,
    "bank": {
      "id": 1,
      "name": "Commonwealth Bank",
      "country": "AU",
      "swift_bic": "CTBAAU2S",
      "created_at": "2025-01-01T00:00:00.000Z",
      "updated_at": "2025-01-01T00:00:00.000Z"
    },
    "created_at": "2025-01-01T00:00:00.000Z",
    "updated_at": "2025-01-16T10:30:00.000Z"
  }
}
```

#### Delete Bank Account

**DELETE** `/api/v2/bank-accounts/{account_id}`

Delete a bank account.

**Path Parameters:**
- `account_id`: ID of the account to delete

**Response:**
```json
{
  "success": true,
  "message": "Bank account deleted successfully",
  "timestamp": "2025-01-16T10:30:00.000Z"
}
```

#### Get Bank Account Balance

**GET** `/api/v2/bank-accounts/{account_id}/balance`

Get current balance information for a bank account.

**Path Parameters:**
- `account_id`: ID of the account

**Response:**
```json
{
  "success": true,
  "message": "Account balance information retrieved",
  "data": {
    "account_id": 1,
    "account_number": "123456789",
    "currency": "AUD",
    "balance": null,
    "last_updated": "2025-01-16T10:30:00.000Z",
    "message": "Balance tracking not yet implemented - transaction system required"
  }
}
```

#### Get Bank Account Transactions

**GET** `/api/v2/bank-accounts/{account_id}/transactions`

Get transaction history for a bank account.

**Path Parameters:**
- `account_id`: ID of the account

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `page_size` (optional): Number of items per page (default: 50, max: 100)

**Response:**
```json
{
  "success": true,
  "message": "Transaction history not yet implemented - transaction system required",
  "data": {
    "account_id": 1,
    "account_number": "123456789",
    "currency": "AUD",
    "transactions": [],
    "total_count": 0,
    "page": 1,
    "page_size": 50
  }
}
```

## Performance Monitoring

The API includes built-in performance monitoring to ensure sub-50ms response times.

### Performance Metrics

- **Response Time Tracking**: All operations are monitored for response time
- **Error Rate Monitoring**: Tracks success/failure rates for all endpoints
- **Bottleneck Identification**: Automatically identifies performance issues
- **Optimization Recommendations**: Provides actionable performance improvement suggestions

### Performance Targets

- **Response Time**: < 50ms for all operations
- **Error Rate**: < 5% for all operations
- **Availability**: 99.9% uptime
- **Scalability**: Support for 1000+ banks, 5000+ accounts

## Validation

All API endpoints use comprehensive validation middleware:

- **Input Validation**: Validates all request data against business rules
- **Type Checking**: Ensures proper data types for all fields
- **Business Rule Validation**: Enforces banking-specific business rules
- **Error Handling**: Provides clear, actionable error messages

## Caching

The API implements intelligent caching strategies:

- **Repository-Level Caching**: Caches frequently accessed data
- **Response Caching**: Caches API responses for improved performance
- **Cache Invalidation**: Automatic cache invalidation on data changes
- **Cache TTL**: Configurable time-to-live for cached data

## Security

- **Input Sanitization**: All input data is sanitized and validated
- **SQL Injection Protection**: Uses parameterized queries throughout
- **Error Information**: Limited error details in production responses
- **Rate Limiting**: Built-in rate limiting for API protection

## Migration from v1

The enhanced banking API (v2) maintains backward compatibility while providing significant improvements:

### New Features
- Standardized response formats
- Comprehensive error handling
- Performance monitoring
- Enhanced validation
- Pagination support
- Detailed API documentation

### Breaking Changes
- **None** - All existing functionality preserved
- New endpoints available at `/api/v2/*`
- Original endpoints remain at `/api/*`

### Migration Path
1. **Phase 1**: Deploy v2 alongside v1
2. **Phase 2**: Update clients to use v2 endpoints
3. **Phase 3**: Deprecate v1 endpoints (future release)

## Support

For API support and questions:
- **Documentation**: This README file
- **Performance Issues**: Use performance monitoring endpoints
- **Error Codes**: Reference error code table above
- **Validation**: Check request body against field requirements

## Future Enhancements

- **Real-time Balance Updates**: WebSocket support for balance changes
- **Transaction History**: Full transaction tracking and reporting
- **Multi-currency Support**: Enhanced currency conversion and validation
- **Banking Integration**: External banking system connectivity
- **Advanced Analytics**: Banking performance and trend analysis
