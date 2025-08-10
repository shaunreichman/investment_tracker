import { renderHook, act } from '@testing-library/react';
import { useFormState } from './useFormState';

describe('useFormState', () => {
  it('updates values and marks fields as touched', () => {
    const { result } = renderHook(() => useFormState({ a: '', b: '' }));

    act(() => {
      result.current.setFieldValue('a', 'x');
    });

    expect(result.current.values.a).toBe('x');
    expect(result.current.touched.a).toBe(true);
    expect(result.current.isDirty).toBe(true);
  });

  it('resets to initial values', () => {
    const { result } = renderHook(() => useFormState({ a: '1', b: '2' }));

    act(() => {
      result.current.setFieldValue('a', 'z');
      result.current.reset();
    });

    expect(result.current.values).toEqual({ a: '1', b: '2' });
    expect(result.current.touched).toEqual({});
    expect(result.current.isDirty).toBe(false);
  });
});


