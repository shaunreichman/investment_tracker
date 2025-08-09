import { useCallback, useMemo, useState } from 'react';

export type FieldValidator = (value: string) => string | undefined;

export type ValidatorMap<TValues extends Record<string, any>> = Partial<{
  [K in keyof TValues]: FieldValidator;
}>;

export interface UseFormValidationReturn<TValues extends Record<string, any>> {
  errors: Partial<Record<keyof TValues, string | undefined>>;
  isValid: boolean;
  validateField: <K extends keyof TValues>(field: K, value: TValues[K]) => string | undefined;
  validateAll: (values: TValues) => boolean;
  setErrors: (updater: Partial<Record<keyof TValues, string | undefined>>) => void;
}

export function useFormValidation<TValues extends Record<string, any>>(
  validators: ValidatorMap<TValues>
): UseFormValidationReturn<TValues> {
  const [errors, setErrorsState] = useState<Partial<Record<keyof TValues, string | undefined>>>({});

  const shallowEqual = useCallback((a: Partial<Record<keyof TValues, string | undefined>>, b: Partial<Record<keyof TValues, string | undefined>>) => {
    const dedup: Partial<Record<keyof TValues, true>> = {};
    (Object.keys(a) as Array<keyof TValues>).forEach((k) => { dedup[k] = true; });
    (Object.keys(b) as Array<keyof TValues>).forEach((k) => { dedup[k] = true; });
    for (const k in dedup) {
      if ((a as any)[k] !== (b as any)[k]) return false;
    }
    return true;
  }, []);

  const validateField = useCallback(
    <K extends keyof TValues>(field: K, value: TValues[K]) => {
      const validator = validators[field];
      const message = validator ? validator(String(value ?? '')) : undefined;
      setErrorsState((prev) => ({ ...prev, [field]: message }));
      return message;
    },
    [validators]
  );

  const validateAll = useCallback(
    (values: TValues) => {
      const next: Partial<Record<keyof TValues, string | undefined>> = {};
      (Object.keys(values) as Array<keyof TValues>).forEach((k) => {
        const validator = validators[k];
        next[k] = validator ? validator(String(values[k] ?? '')) : undefined;
      });
      // Avoid infinite update loops by only setting when different
      setErrorsState((prev) => (shallowEqual(prev, next) ? prev : next));
      return Object.values(next).every((m) => !m);
    },
    [validators, shallowEqual]
  );

  const isValid = useMemo(() => Object.values(errors).every((m) => !m), [errors]);

  const setErrors = useCallback((updater: Partial<Record<keyof TValues, string | undefined>>) => {
    setErrorsState((prev) => ({ ...prev, ...updater }));
  }, []);

  return { errors, isValid, validateField, validateAll, setErrors };
}


