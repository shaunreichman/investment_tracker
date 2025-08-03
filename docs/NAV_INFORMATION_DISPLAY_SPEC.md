# NAV Information Display Specification

## Overview
Add a new NAV information card to the Fund Detail page that displays current NAV data for NAV-based funds. This will provide users with real-time insights into their NAV-based fund positions, showing current NAV per unit, total units owned, and total current value.

## Design Philosophy
- **Contextual Display**: Only show NAV information for NAV-based funds where it's relevant
- **Consistent Styling**: Follow existing card design patterns for visual consistency
- **Real-time Data**: Display current calculated values from the database
- **Clear Information Hierarchy**: Present the most important NAV metrics prominently

## Implementation Strategy

### Phase 1: Backend Foundation
**Goal**: Ensure NAV data is properly exposed through the API
**Tasks**:
- [x] Verify NAV fields are included in fund API responses
- [x] Confirm NAV data is being calculated and updated correctly
- [x] Test API endpoints return current NAV information

**Design Principles**:
- Leverage existing `current_units`, `current_unit_price`, and `current_nav_total` fields
- Ensure data consistency with existing fund calculations
- Maintain API response format consistency

### Phase 2: Frontend Component Development
**Goal**: Create the NAV information display component
**Tasks**:
- [ ] Create new `NavInformationSection` component
- [ ] Implement conditional rendering for NAV-based funds only
- [ ] Display current NAV per unit, total units, and total value
- [ ] Apply consistent styling with existing cards

**Design Principles**:
- Follow existing section component patterns
- Use consistent Material-UI styling and spacing
- Implement proper loading states and error handling
- Match visual hierarchy of other summary sections

### Phase 3: Integration and Layout
**Goal**: Integrate NAV information into the Fund Detail page layout
**Tasks**:
- [ ] Add NAV information section to Fund Detail sidebar
- [ ] Position appropriately within the existing card hierarchy
- [ ] Ensure responsive design works on all screen sizes
- [ ] Test with various NAV-based fund scenarios

**Design Principles**:
- Maintain sidebar layout consistency
- Ensure proper spacing and visual flow
- Support responsive design patterns
- Follow existing component integration patterns

### Phase 4: Testing and Validation
**Goal**: Ensure NAV information displays correctly and updates properly
**Tasks**:
- [ ] Test with NAV-based funds that have NAV update events
- [ ] Verify calculations match expected values
- [ ] Test conditional rendering (hidden for cost-based funds)
- [ ] Validate responsive design on different screen sizes

**Design Principles**:
- Ensure data accuracy and consistency
- Validate user experience across different scenarios
- Confirm proper error handling and edge cases

## Success Metrics
- **Functionality**: NAV information displays correctly for NAV-based funds
- **User Experience**: Information is clearly presented and easy to understand
- **Performance**: No impact on page load times or responsiveness
- **Consistency**: Visual design matches existing components
- **Reliability**: Data updates correctly when NAV events are added/modified

## Technical Requirements

### Data Fields
- `current_unit_price`: Current NAV per unit (from latest NAV update)
- `current_units`: Total number of units owned
- `current_nav_total`: Total current value (units × NAV)

### Component Structure
```typescript
interface NavInformationSectionProps {
  fund: ExtendedFund;
  formatCurrency: (amount: number | null, currency?: string) => string;
  formatDate: (dateString: string | null) => string;
}
```

### Display Logic
- **Conditional Rendering**: Only show for `fund.tracking_type === 'nav_based'`
- **Data Validation**: Handle null/undefined values gracefully
- **Formatting**: Use consistent currency and number formatting

### Styling Guidelines
- **Card Design**: Match existing Paper component styling
- **Typography**: Use consistent font sizes and weights
- **Colors**: Follow existing color scheme and hierarchy
- **Icons**: Use appropriate icons for NAV-related metrics
- **Spacing**: Maintain consistent padding and margins

## Future Enhancements
- **Gains/Losses**: Add unrealized gains/losses calculation
- **Historical NAV**: Show NAV performance over time
- **Cost Basis**: Display average cost per unit
- **Performance Metrics**: Add NAV-based performance indicators 