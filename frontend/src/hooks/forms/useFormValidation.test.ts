import { renderHook, act } from '@testing-library/react';
import { useFormValidation } from './useFormValidation';

describe('useFormValidation', () => {
  it('validates fields and full form', () => {
    const validators = {
      a: (v: string) => (!v ? 'A required' : undefined),
      b: (v: string) => (v && v.length < 2 ? 'Too short' : undefined),
    } as const;

    const { result } = renderHook(() => useFormValidation<typeof validators>(({ a: validators.a, b: validators.b } as any)));

    act(() => {
      result.current.validateField('a' as any, '');
    });
    expect(result.current.errors.a).toBe('A required');

    act(() => {
      result.current.validateField('b' as any, 'x');
    });
    expect(result.current.errors.b).toBe('Too short');

    act(() => {
      const ok = result.current.validateAll({ a: 'z', b: 'xx' } as any);
      expect(ok).toBe(true);
    });

    expect(result.current.isValid).toBe(true);
  });
});


