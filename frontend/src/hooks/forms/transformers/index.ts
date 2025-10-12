/**
 * Form Transformers Barrel Export
 * 
 * Central export point for all form-to-API transformers.
 * 
 * Transformers follow the enterprise pattern:
 * - Input: Validated form data (from Zod schema via z.infer)
 * - Output: API request type (from types/models)
 * - Logic: Filter empty optionals, trim strings, convert types
 * 
 * @example
 * ```typescript
 * import { transformNavUpdateForm } from '@/hooks/forms/transformers';
 * 
 * const form = useForm<NavUpdateFormData>({...});
 * 
 * onSubmit: async (data) => {
 *   const request = transformNavUpdateForm(data);
 *   await createNavUpdate(request);
 * }
 * ```
 */

// Fund transformers (includes fund creation and all event types)
export {
  transformCreateFundForm,
  transformNavUpdateForm,
  transformCapitalCallForm,
  transformReturnOfCapitalForm,
  transformDistributionForm,
  transformUnitPurchaseForm,
  transformUnitSaleForm,
  transformFundEventCashFlowForm,
  transformFundTaxStatementForm
} from './fundTransformers';

// Company transformers
export {
  transformCreateCompanyForm,
  transformCreateContactForm
} from './companyTransformers';

// Entity transformers
export {
  transformCreateEntityForm
} from './entityTransformers';

// Banking transformers
export {
  transformCreateBankForm,
  transformCreateBankAccountForm,
  transformBankAccountBalanceForm
} from './bankingTransformers';

// Rate transformers
export {
  transformFxRateForm,
  transformRiskFreeRateForm
} from './rateTransformers';

