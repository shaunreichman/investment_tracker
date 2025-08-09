import { useCallback, useMemo, useRef, useState } from 'react';

export interface UseFormStateReturn<TValues extends Record<string, any>> {
  values: TValues;
  touched: Partial<Record<keyof TValues, boolean>>;
  isDirty: boolean;
  setFieldValue: <K extends keyof TValues>(field: K, value: TValues[K]) => void;
  setValues: (updater: TValues | ((prev: TValues) => TValues)) => void;
  markTouched: <K extends keyof TValues>(field: K, touched?: boolean) => void;
  markAllTouched: () => void;
  reset: (nextInitialValues?: TValues) => void;
}

export function useFormState<TValues extends Record<string, any>>(
  initialValues: TValues
): UseFormStateReturn<TValues> {
  const initialRef = useRef<TValues>(initialValues);
  const [values, setValuesState] = useState<TValues>(initialValues);
  const [touched, setTouched] = useState<Partial<Record<keyof TValues, boolean>>>({});

  const setValues = useCallback((updater: TValues | ((prev: TValues) => TValues)) => {
    setValuesState((prev) => (typeof updater === 'function' ? (updater as any)(prev) : updater));
  }, []);

  const setFieldValue = useCallback(<K extends keyof TValues>(field: K, value: TValues[K]) => {
    setValuesState((prev) => ({ ...prev, [field]: value }));
    setTouched((prev) => ({ ...prev, [field]: true }));
  }, []);

  const markTouched = useCallback(<K extends keyof TValues>(field: K, nextTouched: boolean = true) => {
    setTouched((prev) => ({ ...prev, [field]: nextTouched }));
  }, []);

  const markAllTouched = useCallback(() => {
    const next: Partial<Record<keyof TValues, boolean>> = {};
    (Object.keys(values) as Array<keyof TValues>).forEach((k) => {
      next[k] = true;
    });
    setTouched(next);
  }, [values]);

  const reset = useCallback((nextInitialValues?: TValues) => {
    const nv = nextInitialValues ?? initialRef.current;
    initialRef.current = nv;
    setValuesState(nv);
    setTouched({});
  }, []);

  const isDirty = useMemo(() => {
    const a = initialRef.current as Record<string, unknown>;
    const b = values as Record<string, unknown>;
    const dedup: Record<string, true> = {};
    Object.keys(a).forEach((k) => {
      dedup[k] = true;
    });
    Object.keys(b).forEach((k) => {
      dedup[k] = true;
    });
    for (const key in dedup) {
      if (Object.prototype.hasOwnProperty.call(dedup, key)) {
        if (a[key] !== b[key]) return true;
      }
    }
    return false;
  }, [values]);

  return {
    values,
    touched,
    isDirty,
    setFieldValue,
    setValues,
    markTouched,
    markAllTouched,
    reset,
  };
}


