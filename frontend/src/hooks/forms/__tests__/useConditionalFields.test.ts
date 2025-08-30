import { renderHook, act } from '@testing-library/react';
import { useConditionalFields } from '../useConditionalFields';
import { ConditionalFieldConfig } from '../useConditionalFields';

describe('useConditionalFields', () => {
  const mockFieldConfigs: ConditionalFieldConfig[] = [
    {
      field: 'field1',
      visible: true,
      required: false,
      disabled: false,
      dependencies: []
    },
    {
      field: 'field2',
      visible: true,
      required: true,
      disabled: false,
      dependencies: [
        { field: 'field1', value: 'value1', operator: 'equals' }
      ]
    },
    {
      field: 'field3',
      visible: true,
      required: false,
      disabled: false,
      dependencies: [
        { field: 'field1', value: ['value1', 'value2'], operator: 'in' }
      ]
    },
    {
      field: 'field4',
      visible: true,
      required: false,
      disabled: false,
      dependencies: [
        { field: 'field2', value: 'value2', operator: 'equals' }
      ]
    },
    {
      field: 'field5',
      visible: true,
      required: false,
      disabled: false,
      dependencies: [
        { field: 'field1', value: 'value1', operator: 'equals' },
        { field: 'field2', value: 'value2', operator: 'equals' }
      ]
    }
  ];

  const initialValues = {
    field1: '',
    field2: '',
    field3: '',
    field4: '',
    field5: ''
  };

  it('should initialize with default field states', () => {
    const { result } = renderHook(() =>
      useConditionalFields({
        fieldConfigs: mockFieldConfigs,
        values: initialValues
      })
    );

    // Only field1 should be visible initially (no dependencies)
    // field2 depends on field1 = 'value1'
    // field3 depends on field1 = 'value1' or 'value2'
    // field4 depends on field2 = 'value2'
    // field5 depends on both field1 = 'value1' and field2 = 'value2'
    expect(result.current.visibleFields).toEqual(['field1']);
    expect(result.current.requiredFields).toEqual([]);
    expect(result.current.disabledFields).toEqual([]);
  });

  it('should handle equals operator correctly', () => {
    const { result } = renderHook(() =>
      useConditionalFields({
        fieldConfigs: mockFieldConfigs,
        values: { ...initialValues, field1: 'value1' }
      })
    );

    expect(result.current.isFieldVisible('field2')).toBe(true);
    expect(result.current.isFieldRequired('field2')).toBe(true);
  });

  it('should handle in operator correctly', () => {
    const { result } = renderHook(() =>
      useConditionalFields({
        fieldConfigs: mockFieldConfigs,
        values: { ...initialValues, field1: 'value1' }
      })
    );

    expect(result.current.isFieldVisible('field3')).toBe(true);
  });

  it('should handle multiple dependencies with AND logic', () => {
    const { result } = renderHook(() =>
      useConditionalFields({
        fieldConfigs: mockFieldConfigs,
        values: { ...initialValues, field1: 'value1', field2: 'value2' }
      })
    );

    expect(result.current.isFieldVisible('field5')).toBe(true);
  });

  it('should handle not_equals operator', () => {
    const configsWithNotEquals: ConditionalFieldConfig[] = [
      {
        field: 'conditional_field',
        visible: true,
        required: false,
        disabled: false,
        dependencies: [
          { field: 'field1', value: 'value1', operator: 'not_equals' }
        ]
      }
    ];

    const { result } = renderHook(() =>
      useConditionalFields({
        fieldConfigs: configsWithNotEquals,
        values: { field1: 'different_value' }
      })
    );

    expect(result.current.isFieldVisible('conditional_field')).toBe(true);
  });

  it('should handle exists operator', () => {
    const configsWithExists: ConditionalFieldConfig[] = [
      {
        field: 'conditional_field',
        visible: true,
        required: false,
        disabled: false,
        dependencies: [
          { field: 'field1', value: true, operator: 'exists' }
        ]
      }
    ];

    const { result } = renderHook(() =>
      useConditionalFields({
        fieldConfigs: configsWithExists,
        values: { field1: 'any_value' }
      })
    );

    expect(result.current.isFieldVisible('conditional_field')).toBe(true);
  });

  it('should handle not_exists operator', () => {
    const configsWithNotExists: ConditionalFieldConfig[] = [
      {
        field: 'conditional_field',
        visible: true,
        required: false,
        disabled: false,
        dependencies: [
          { field: 'field1', value: true, operator: 'not_exists' }
        ]
      }
    ];

    const { result } = renderHook(() =>
      useConditionalFields({
        fieldConfigs: configsWithNotExists,
        values: { field1: '' }
      })
    );

    expect(result.current.isFieldVisible('conditional_field')).toBe(true);
  });

  it('should handle custom visibility function', () => {
    const configsWithCustomVisibility: ConditionalFieldConfig[] = [
      {
        field: 'custom_field',
        visible: true,
        required: false,
        disabled: false,
        dependencies: [],
        customVisibility: (values) => values.field1 === 'custom_value'
      }
    ];

    const { result } = renderHook(() =>
      useConditionalFields({
        fieldConfigs: configsWithCustomVisibility,
        values: { field1: 'custom_value' }
      })
    );

    expect(result.current.isFieldVisible('custom_field')).toBe(true);
  });

  it('should handle custom required function', () => {
    const configsWithCustomRequired: ConditionalFieldConfig[] = [
      {
        field: 'custom_required_field',
        visible: true,
        required: false,
        disabled: false,
        dependencies: [],
        customRequired: (values) => values.field1 === 'required_value'
      }
    ];

    const { result } = renderHook(() =>
      useConditionalFields({
        fieldConfigs: configsWithCustomRequired,
        values: { field1: 'required_value' }
      })
    );

    expect(result.current.isFieldRequired('custom_required_field')).toBe(true);
  });

  it('should handle custom disabled function', () => {
    const configsWithCustomDisabled: ConditionalFieldConfig[] = [
      {
        field: 'custom_disabled_field',
        visible: true,
        required: false,
        disabled: false,
        dependencies: [],
        customDisabled: (values) => values.field1 === 'disabled_value'
      }
    ];

    const { result } = renderHook(() =>
      useConditionalFields({
        fieldConfigs: configsWithCustomDisabled,
        values: { field1: 'disabled_value' }
      })
    );

    expect(result.current.isFieldDisabled('custom_disabled_field')).toBe(true);
  });

  it('should get field dependencies correctly', () => {
    const { result } = renderHook(() =>
      useConditionalFields({
        fieldConfigs: mockFieldConfigs,
        values: { ...initialValues, field1: 'value1', field2: 'value2' }
      })
    );

    const field2Dependencies = result.current.getFieldDependencies('field2');
    expect(field2Dependencies).toHaveLength(1);
    const dependency = field2Dependencies[0];
    expect(dependency).toBeDefined();
    if (dependency) {
      expect(dependency.isMet).toBe(true);
      expect(dependency.actualValue).toBe('value1');
      expect(dependency.expectedValue).toBe('value1');
    }
  });

  it('should get dependent fields correctly', () => {
    const { result } = renderHook(() =>
      useConditionalFields({
        fieldConfigs: mockFieldConfigs,
        values: initialValues
      })
    );

    const dependentFields = result.current.getDependentFields('field1');
    expect(dependentFields).toContain('field2');
    expect(dependentFields).toContain('field3');
    expect(dependentFields).toContain('field5');
  });

  it('should get dependency graph correctly', () => {
    const { result } = renderHook(() =>
      useConditionalFields({
        fieldConfigs: mockFieldConfigs,
        values: initialValues
      })
    );

    const dependencyGraph = result.current.getDependencyGraph();
    expect(dependencyGraph.field2).toEqual(['field1']);
    expect(dependencyGraph.field3).toEqual(['field1']);
    expect(dependencyGraph.field4).toEqual(['field2']);
    expect(dependencyGraph.field5).toEqual(['field1', 'field2']);
  });

  it('should get conditional validation rules correctly', () => {
    const { result } = renderHook(() =>
      useConditionalFields({
        fieldConfigs: mockFieldConfigs,
        values: { ...initialValues, field1: 'value1' }
      })
    );

    const validationRules = result.current.getConditionalValidationRules();
    expect(validationRules.field2).toBeDefined();
    expect(typeof validationRules.field2).toBe('function');
  });

  it('should update field configuration correctly', () => {
    const { result } = renderHook(() =>
      useConditionalFields({
        fieldConfigs: mockFieldConfigs,
        values: initialValues
      })
    );

    act(() => {
      result.current.updateFieldConfig('field1', { required: true });
    });

    expect(result.current.isFieldRequired('field1')).toBe(true);
  });

  it('should add new field configuration correctly', () => {
    const { result } = renderHook(() =>
      useConditionalFields({
        fieldConfigs: mockFieldConfigs,
        values: initialValues
      })
    );

    const newConfig: ConditionalFieldConfig = {
      field: 'new_field',
      visible: true,
      required: false,
      disabled: false,
      dependencies: []
    };

    act(() => {
      result.current.addFieldConfig(newConfig);
    });

    expect(result.current.isFieldVisible('new_field')).toBe(true);
  });

  it('should remove field configuration correctly', () => {
    const { result } = renderHook(() =>
      useConditionalFields({
        fieldConfigs: mockFieldConfigs,
        values: initialValues
      })
    );

    act(() => {
      result.current.removeFieldConfig('field1');
    });

    expect(result.current.isFieldVisible('field1')).toBe(false);
  });

  it('should handle empty dependencies array', () => {
    const configsWithEmptyDeps: ConditionalFieldConfig[] = [
      {
        field: 'no_deps_field',
        visible: true,
        required: false,
        disabled: false,
        dependencies: []
      }
    ];

    const { result } = renderHook(() =>
      useConditionalFields({
        fieldConfigs: configsWithEmptyDeps,
        values: initialValues
      })
    );

    expect(result.current.isFieldVisible('no_deps_field')).toBe(true);
  });

  it('should handle undefined values gracefully', () => {
    const { result } = renderHook(() =>
      useConditionalFields({
        fieldConfigs: mockFieldConfigs,
        values: { field1: undefined, field2: null, field3: '', field4: 'value4', field5: 'value5' }
      })
    );

    // Fields with undefined/null dependencies should not be visible
    expect(result.current.isFieldVisible('field2')).toBe(false);
    expect(result.current.isFieldVisible('field3')).toBe(false);
    expect(result.current.isFieldVisible('field5')).toBe(false);
  });

  it('should handle complex dependency chains', () => {
    const complexConfigs: ConditionalFieldConfig[] = [
      {
        field: 'chain1',
        visible: true,
        required: false,
        disabled: false,
        dependencies: []
      },
      {
        field: 'chain2',
        visible: true,
        required: false,
        disabled: false,
        dependencies: [
          { field: 'chain1', value: 'value1', operator: 'equals' }
        ]
      },
      {
        field: 'chain3',
        visible: true,
        required: false,
        disabled: false,
        dependencies: [
          { field: 'chain2', value: 'value2', operator: 'equals' }
        ]
      }
    ];

    const { result } = renderHook(() =>
      useConditionalFields({
        fieldConfigs: complexConfigs,
        values: { chain1: 'value1', chain2: 'value2', chain3: 'value3' }
      })
    );

    expect(result.current.isFieldVisible('chain1')).toBe(true);
    expect(result.current.isFieldVisible('chain2')).toBe(true);
    expect(result.current.isFieldVisible('chain3')).toBe(true);
  });

  it('should handle mixed dependency types correctly', () => {
    const mixedConfigs: ConditionalFieldConfig[] = [
      {
        field: 'mixed_field',
        visible: true,
        required: false,
        disabled: false,
        dependencies: [
          { field: 'field1', value: 'value1', operator: 'equals' },
          { field: 'field2', value: ['value2', 'value3'], operator: 'in' },
          { field: 'field3', value: true, operator: 'exists' }
        ]
      }
    ];

    const { result } = renderHook(() =>
      useConditionalFields({
        fieldConfigs: mixedConfigs,
        values: { field1: 'value1', field2: 'value2', field3: 'any_value' }
      })
    );

    expect(result.current.isFieldVisible('mixed_field')).toBe(true);
  });
});
