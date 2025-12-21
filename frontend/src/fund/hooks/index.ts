/**
 * Fund Data Hooks - Barrel Export
 * 
 * All hooks for fund domain operations, organized by resource type:
 * - Funds (CRUD)
 * - Fund Events (CRUD with specific event types)
 * - Fund Event Cash Flows (CRUD)
 * - Fund Tax Statements (CRUD)
 * - Fund Financial Years (utility)
 * - Event Submission (orchestration)
 * 
 * @module fund/hooks
 */

// Fund hooks
export {
  useFunds,
  useFund,
  useCreateFund,
  useDeleteFund,
} from './useFunds';

// Fund Event hooks
export {
  useFundEvents,
  useFundEventsByFundId,
  useFundEvent,
  useCreateCapitalCall,
  useCreateReturnOfCapital,
  useCreateUnitPurchase,
  useCreateUnitSale,
  useCreateNavUpdate,
  useCreateDistribution,
  useDeleteFundEvent,
} from './useFundEvents';

// Event Submission hook (orchestration)
export { useEventSubmission } from './useEventSubmission';

// Fund Event Cash Flow hooks
export {
  useFundEventCashFlows,
  useFundEventCashFlowsByEvent,
  useFundEventCashFlow,
  useCreateFundEventCashFlow,
  useDeleteFundEventCashFlow,
} from './useFundEventCashFlows';

// Fund Tax Statement hooks
export {
  useFundTaxStatements,
  useFundTaxStatementsByFundId,
  useFundTaxStatement,
  useCreateFundTaxStatement,
  useDeleteFundTaxStatement,
} from './useFundTaxStatements';

// Fund Financial Years utility
export {
  useFundFinancialYears,
  type UseFundFinancialYearsResult,
} from './useFundFinancialYears';

// Fund Filters hook
export {
  useFundsFilters,
  type UseFundsFiltersProps,
  type UseFundsFiltersResult,
  type FundFilters,
  type FundFilterValue,
} from './useFundsFilters';

// Form validation schemas
export * from './schemas';

// Form transformers
export * from './transformers';

