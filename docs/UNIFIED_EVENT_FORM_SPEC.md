# Unified Event Form Specification

## Overview

Consolidate the separate `CreateFundEventModal` and `EditFundEventModal` components into a single `UnifiedFundEventForm` component that can handle both create and edit modes. This will eliminate code duplication, ensure UI consistency, and improve maintainability while preserving all existing functionality.

## Design Philosophy

### **Core Principles**
- **Single Source of Truth**: One form component handles both create and edit operations
- **Template-Driven UX**: Leverage the existing template selection system for both modes
- **Mode-Aware Validation**: Shared validation logic with mode-specific rules
- **Backward Compatibility**: All existing functionality must be preserved exactly
- **Create Form Preservation**: Existing create form functionality and UI must remain unchanged
- **Incremental Migration**: Implement alongside existing forms to minimize risk

### **Problems We're Solving**
- **Code Duplication**: ~70% of create and edit form logic is identical
- **UI Inconsistency**: Changes to form design require updates in two places
- **Maintenance Overhead**: Bug fixes and improvements must be applied twice
- **User Experience**: Edit mode doesn't leverage the intuitive template selection system
- **Incomplete Edit Form**: Current edit form is a stub, missing comprehensive validation
- **Validation Inconsistency**: Edit form has incomplete validation compared to create form
- **Backend Alignment**: Edit mode validation doesn't match domain method constraints

### **Success Criteria**
- ✅ Single form component handles both create and edit modes
- ✅ Template selection system shows current template in edit mode (locked)
- ✅ **Complete create form validation used for both modes**
- ✅ **Existing create form functionality and UI remains exactly the same**
- ✅ No regression in functionality or user experience
- ✅ Reduced codebase size and improved maintainability
- ✅ Comprehensive test coverage for both modes
- ✅ **Edit form now has complete validation (upgrade from stub)**
- ✅ Backend domain method constraints are properly respected

## Implementation Strategy

### **Phase 1: Extract Shared Components** ✅ **Foundation**
**Goal**: Create reusable components and hooks based on the complete create form validation

**Tasks**:
- [ ] Extract `useUnifiedEventValidation` hook from create form validation logic
  - [ ] Use `useEventForm` validation as the foundation (complete validation)
  - [ ] Add mode parameter (`'create' | 'edit'`) to validation config
  - [ ] Implement simplified mode-specific rules (template locking for edit mode)
  - [ ] **TESTING**: Ensure all create form validation scenarios work correctly
- [ ] Create `useUnifiedEventForm` hook for state management
  - [ ] Use `useEventForm` state management as the foundation (complete implementation)
  - [ ] Add mode-specific initialization logic for edit mode
  - [ ] Handle template selection for both modes
  - [ ] **TESTING**: Verify state management works for both modes
- [ ] Extract `EventFormFields` component for form rendering
  - [ ] Use create form field logic as the foundation (complete implementation)
  - [ ] Add mode-aware field rendering for edit mode
  - [ ] Handle conditional field display based on mode
  - [ ] **TESTING**: Ensure all form fields render correctly

**Design Principles**:
- **Create Form Foundation**: Use the complete create form as the base implementation
- **Create Form Preservation**: Existing create form functionality and UI must remain unchanged
- **Edit Mode Simplification**: Add edit-specific logic on top of complete create form
- **Type Safety**: Use TypeScript to ensure mode-specific props are handled correctly
- **Backward Compatibility**: All existing create functionality must work identically

### **Phase 2: Create Template Mapping System** ✅ **Core Logic**
**Goal**: Map existing event data to fixed template selection for edit mode

**Tasks**:
- [ ] Create `mapEventToTemplates` utility function
  - [ ] Map event type to template selection state using create form logic
  - [ ] Handle distribution type mapping (INTEREST, DIVIDEND, OTHER)
  - [ ] Handle sub-distribution type mapping (WITHHOLDING_TAX, FRANKED, etc.)
  - [ ] Determine withholding tax configuration from existing data
  - [ ] **TESTING**: Test with all event types and configurations
- [ ] Create `mapEventToFormData` utility function
  - [ ] Convert event data to form field values using create form field structure
  - [ ] Handle complex scenarios (withholding tax, NAV updates, etc.)
  - [ ] Preserve all existing field mappings exactly
  - [ ] **TESTING**: Verify all field values are mapped correctly
- [ ] Update `EventTypeSelector` for edit mode
  - [ ] Add `mode` prop to component interface
  - [ ] Show current template selection as read-only in edit mode
  - [ ] Disable all template selection interactions in edit mode
  - [ ] Add visual indication that template is fixed (e.g., disabled state, info text)
  - [ ] **TESTING**: Ensure template selection is properly locked in edit mode

**Design Principles**:
- **Fixed Template**: Template selection is locked to the original event type in edit mode
- **Clear Indication**: Users understand they cannot change the event type/template
- **Intuitive UX**: If users want different template, they delete and recreate
- **Backend Alignment**: Simplified validation matches domain method constraints

### **Phase 3: Build Unified Form Component** ✅ **Main Implementation**
**Goal**: Create the main `UnifiedFundEventForm` component that handles both modes

**Tasks**:
- [ ] Create `UnifiedFundEventForm` component
  - [ ] Accept `mode` prop (`'create' | 'edit'`)
  - [ ] Use shared hooks for state management and validation
  - [ ] Render template selection for create mode and appropriate edit scenarios
  - [ ] Handle mode-specific form submission logic
  - [ ] **TESTING**: Test component in both modes with all event types
- [ ] Implement mode-specific API integration
  - [ ] Use `useCreateFundEvent` for create mode
  - [ ] Use `useUpdateFundEvent` for edit mode
  - [ ] Handle different payload structures for create vs edit
  - [ ] Preserve all existing API behavior exactly
  - [ ] **TESTING**: Verify API calls work correctly for both modes
- [ ] Add mode-specific UI elements
  - [ ] Different dialog titles ("Add Event" vs "Edit Event")
  - [ ] Different button text ("Add Event" vs "Update Event")
  - [ ] Mode-specific loading states and error handling
  - [ ] **TESTING**: Ensure UI elements are appropriate for each mode

**Design Principles**:
- **Consistent UX**: Same form experience for both create and edit
- **Clear Mode Indication**: Users understand whether they're creating or editing
- **Appropriate Constraints**: Edit mode may have different validation rules

### **Phase 4: Replace Existing Modals** ✅ **Integration**
**Goal**: Replace existing modal components with the unified form

**Tasks**:
- [ ] Update `CreateFundEventModal` to use unified form
  - [ ] Replace modal content with `UnifiedFundEventForm`
  - [ ] Pass `mode="create"` prop
  - [ ] Preserve all existing props and callbacks
  - [ ] **TESTING**: Ensure create functionality and UI works identically to current implementation
- [ ] Update `EditFundEventModal` to use unified form
  - [ ] Replace modal content with `UnifiedFundEventForm`
  - [ ] Pass `mode="edit"` and `event` props
  - [ ] Preserve all existing props and callbacks
  - [ ] **TESTING**: Ensure edit functionality works identically
- [ ] Update all parent components that use these modals
  - [ ] Ensure prop interfaces remain compatible
  - [ ] Update any direct references to modal internals
  - [ ] **TESTING**: Verify all parent components work correctly
- [ ] Remove old modal components
  - [ ] Delete `CreateFundEventModal.tsx` and `EditFundEventModal.tsx`
  - [ ] Remove unused imports and dependencies
  - [ ] Update documentation and type definitions
  - [ ] **TESTING**: Ensure no broken references remain

**Design Principles**:
- **Zero Regression**: All existing functionality must work exactly as before
- **Create Form Preservation**: Existing create form functionality and UI must remain unchanged
- **Clean Migration**: Remove old components only after successful replacement
- **Comprehensive Testing**: Test all scenarios before removing old code

### **Phase 5: Polish and Optimization** ✅ **Final Touches**
**Goal**: Optimize performance and user experience

**Tasks**:
- [ ] Optimize form performance
  - [ ] Memoize expensive calculations
  - [ ] Optimize re-renders for large forms
  - [ ] **TESTING**: Verify performance is at least as good as before
- [ ] Enhance user experience
  - [ ] Add smooth transitions between template selection and form fields
  - [ ] Improve error message clarity for mode-specific scenarios
  - [ ] Add helpful tooltips for complex edit scenarios
  - [ ] **TESTING**: Ensure UX improvements don't break functionality
- [ ] Update documentation
  - [ ] Update component documentation
  - [ ] Add examples for both create and edit modes
  - [ ] Update design guidelines
  - [ ] **TESTING**: Verify documentation is accurate and helpful

**Design Principles**:
- **Performance First**: Optimizations must not break functionality
- **User-Centric**: Enhancements should improve user experience
- **Well-Documented**: Clear documentation for future maintainers

## Technical Architecture

### **Component Structure**
```
UnifiedFundEventForm/
├── UnifiedFundEventForm.tsx          # Main component
├── hooks/
│   ├── useUnifiedEventForm.ts        # State management
│   ├── useUnifiedEventValidation.ts  # Validation logic
│   └── useUnifiedEventSubmission.ts  # API integration
├── utils/
│   ├── eventTemplateMapping.ts       # Template mapping logic
│   └── eventFormDataMapping.ts       # Form data mapping
└── components/
    ├── EventFormFields.tsx           # Form field rendering
    └── EventTypeSelector.tsx         # Template selection (updated)
```

### **Key Interfaces**
```typescript
interface UnifiedFundEventFormProps {
  mode: 'create' | 'edit';
  event?: ExtendedFundEvent; // Only for edit mode
  fundId: number;
  fundTrackingType: 'nav_based' | 'cost_based';
  onSubmit: (data: any) => void;
  onCancel: () => void;
  onSuccess?: () => void;
}

interface ValidationConfig {
  mode: 'create' | 'edit';
  eventType: EventType | '';
  distributionType: string;
  subDistributionType: string;
  withholdingAmountType: 'gross' | 'net' | '';
  withholdingTaxType: 'amount' | 'rate' | '';
}
```

### **State Management Flow**
1. **Initialization**: Mode determines initial state and validation rules
2. **Template Selection**: Create mode shows full selection, edit mode shows locked current selection
3. **Form Data**: Shared form fields with mode-specific validation
4. **Submission**: Mode-specific API calls with appropriate payloads

## Validation Rules

### **Shared Validations** (Both Create and Edit)
- **Complete create form validation** used as the foundation
- Event date is required
- Amount validation for capital events
- Unit validation for NAV-based events
- NAV per share validation for NAV updates
- Distribution type validation (complete from create form)
- Withholding tax validation (complete from create form)
- Template selection validation (complete from create form)

### **Create-Specific Validations**
- Template selection is required
- Distribution type selection is required for distributions
- Sub-distribution type selection is required when applicable
- Withholding tax configuration must be complete

### **Edit-Specific Validations**
- Template selection is locked to original event type (no template changes allowed)
- **All other validation rules identical to create mode**
- Existing event constraints (can't change certain fields after creation)
- Mode-specific field requirements based on existing event data

## Success Metrics

### **Technical Metrics**
- [ ] **Code Reduction**: Reduce total lines of code by at least 30%
- [ ] **Component Count**: Reduce from 2 modal components to 1 unified component
- [ ] **Test Coverage**: Maintain or improve test coverage (target: 90%+)
- [ ] **Performance**: No performance regression compared to existing forms

### **User Experience Metrics**
- [ ] **Consistency**: Identical form behavior between create and edit modes
- [ ] **Usability**: Template selection system works intuitively for editing
- [ ] **Error Handling**: Clear, mode-appropriate error messages
- [ ] **Accessibility**: Maintain or improve accessibility standards

### **Maintainability Metrics**
- [ ] **Bug Reduction**: Fewer bugs due to shared code
- [ ] **Feature Velocity**: Faster implementation of new form features
- [ ] **Code Quality**: Improved readability and maintainability
- [ ] **Documentation**: Clear, comprehensive documentation

## Risk Mitigation

### **Technical Risks**
- **Complex State Management**: Mitigate with thorough testing and incremental implementation
- **Validation Logic**: Mitigate by using complete create form validation as foundation
- **API Integration**: Mitigate by testing both create and edit APIs thoroughly
- **Edit Form Upgrade**: Mitigate by ensuring edit form gets complete validation from create form
- **Create Form Regression**: Mitigate by preserving existing create form functionality exactly

### **User Experience Risks**
- **Template Mapping Accuracy**: Mitigate with comprehensive testing of all event types
- **Performance Impact**: Mitigate with performance testing and optimization
- **User Confusion**: Mitigate with clear mode indication and locked template UX
- **Template Change Desire**: Mitigate with clear messaging about delete/recreate workflow

### **Migration Risks**
- **Breaking Changes**: Mitigate by implementing alongside existing forms
- **Data Loss**: Mitigate by preserving all existing data handling logic
- **Regression**: Mitigate with comprehensive testing before removing old components

## Testing Strategy

### **Unit Testing**
- [ ] Test all shared hooks with both create and edit modes
- [ ] Test template mapping logic with all event types
- [ ] Test validation rules for both modes
- [ ] Test API integration for both create and edit operations

### **Integration Testing**
- [ ] Test complete form workflows for both modes
- [ ] Test all event types and configurations
- [ ] Test error handling and edge cases
- [ ] Test performance with large datasets

### **User Acceptance Testing**
- [ ] **Verify create functionality and UI works identically to current implementation**
- [ ] Verify edit functionality works identically to current implementation
- [ ] Verify template selection is properly locked in edit mode
- [ ] Verify users understand they must delete/recreate to change event type
- [ ] Verify all existing user workflows are preserved
- [ ] **Verify create form user experience is unchanged (same UI, same behavior)**

## Dependencies

### **Required Changes**
- Update `EventTypeSelector` to support edit mode
- Update validation utilities to support mode-specific rules
- Update API hooks to handle unified form interface

### **Optional Enhancements**
- Add performance optimizations for large forms
- Enhance error messages for mode-specific scenarios
- Add helpful tooltips and guidance for complex edit scenarios

## Timeline

### **Phase 1**: 1-2 weeks
- Extract shared components and hooks
- Implement basic mode-aware logic

### **Phase 2**: 1-2 weeks
- Create template mapping system
- Test with all event types

### **Phase 3**: 2-3 weeks
- Build unified form component
- Implement mode-specific API integration

### **Phase 4**: 1-2 weeks
- Replace existing modals
- Comprehensive testing

### **Phase 5**: 1 week
- Polish and optimization
- Documentation updates

**Total Estimated Time**: 6-10 weeks

## Conclusion

This specification provides a clear roadmap for consolidating the create and edit event forms into a unified component. The phased approach minimizes risk while delivering significant benefits in code maintainability and user experience consistency. The key success factors are thorough testing, incremental implementation, and preserving all existing functionality exactly as users expect. **Most importantly, the existing create form functionality and UI must remain completely unchanged** - this is a non-negotiable requirement that ensures users continue to have the same experience they currently enjoy. 