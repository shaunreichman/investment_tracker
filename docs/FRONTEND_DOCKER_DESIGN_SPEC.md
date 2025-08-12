# Frontend Design Specification – Docker Desktop–Inspired UI (MUI v7)

## 1. Overview

Transform our entire frontend to adopt a **modern, clean, and professional UI** inspired by the Docker Desktop application. The goal is **clarity, visual polish, and intuitive usability**, especially for **data-heavy views** (tables, charts, dashboards).

This implementation will create enterprise-grade UI with deep dark themes, precise color palettes, sophisticated visual hierarchy, and consistent design language across all components while maintaining all existing functionality.

## 1.1 TypeScript Memory Management Principles

> **⚠️ CRITICAL**: Follow these principles to avoid development server memory crashes

**NEVER DO THIS** (causes 2GB+ memory usage and crashes):
```typescript
// ❌ PROBLEMATIC: Type intersection with MUI
} as ThemeOptions & { customSpacing: typeof dockerSpacing });
```

**ALWAYS DO THIS** (safe, no memory issues):
```typescript
// ✅ SOLUTION: Composition pattern
export const dockerTheme = createTheme({ ... });
export const dockerThemeWithConfig = {
  theme: dockerTheme,
  colors: dockerColors,
  spacing: dockerSpacing,
} as const;
```

**Key Rules:**
- ✅ **Use composition** instead of type intersections with large libraries
- ❌ **Never intersect** with MUI, React, or other large framework types
- ❌ **Never modify** global module declarations of large libraries
- ✅ **Keep types simple** and focused on your own code

> **📚 For detailed analysis and best practices, see:** `docs/guidlines/TYPESCRIPT_MEMORY_MANAGEMENT.md`

## 2. Core Design Principles

- **Clean and Minimal**: Avoid clutter; emphasize whitespace and clear visual hierarchy
- **Dark/Neutral Base Palette**: Predominantly deep gray backgrounds with white text and high-contrast accent colors
- **Soft Rounding**: Consistent border-radius for cards, tables, buttons
- **Visual Depth**: Subtle shadows for separation (no heavy outlines)
- **Consistency**: Use MUI theme overrides to keep all components cohesive
- **Responsive**: Layout must adapt smoothly to various screen sizes

## 3. Color Palette

### Primary Background
- **Main App Background**: Deep charcoal/blue-black (`#0D1117` to `#1B1F23` range)
- **Surface Background (Panels/Cards)**: Slightly lighter dark (`#1B1F23` to `#21262D` range)
- **Sidebar Background**: Deep dark (`#0D1117` to `#161B22` range)

### Header & Navigation
- **Header Bar**: Rich gradient blue (`#0066CC` to deeper navy `#004499`)
- **Active Navigation**: Bright blue accent (`#007FFF`)

### Accent Colors
- **Primary Accent**: Blue (`#007FFF` to lighter blues `#1E90FF`)
- **Success/Status**: Green (`#28A745`)
- **Warning**: `#FFC107`
- **Error**: `#DC3545`

### Text Colors
- **Primary Text**: High-contrast white (`#FFFFFF`) for titles and key metrics
- **Secondary Text**: Soft gray (`#8B949E`) for descriptive text
- **Borders/Dividers**: `rgba(255,255,255,0.08)`

> **Design Principle**: Bright accent colors (blue, green, red) reserved only for high-importance cues and interactive elements.

> Use MUI's `createTheme` to centralize these colors.

## 4. Typography

- **Font Family**: `"Inter", "Roboto", sans-serif`
- **Font Sizes**:
  - Headings: Larger, bold, minimal color variation (e.g., `h1` 28px, `h2` 22px)
  - Body: 14–16px
  - Captions: 12px, lighter color
- **Weight**:
  - Headings: `600`
  - Body: `400`
  - Buttons: `500`

## 5. Layout & Structure

- **Main Sidebar Navigation** (Docker-style):
  - Collapsible vertical nav on the left
  - Solid dark background (`#0D1117` to `#161B22` range)
  - Icons first, labels second
  - Active item highlighted with blue accent (`#007FFF`) + subtle background
- **Fund Navigation Sidebar** (Enhanced Navigation - Phase 7):
  - Contextual navigation between funds and companies
  - Company header and fund list with active states
  - Other companies section (collapsible/expandable)
  - Width: 280px (collapsible to 64px)
- **Top Bar**:
  - Fixed position
  - Contains page title, action buttons, optional search
  - Background: slightly darker than main content
- **Main Content Area**:
  - **Three-Column Layout** (Enhanced Navigation - Phase 7):
    - Left: Fund navigation sidebar (funds + companies)
    - Center: Summary section (performance, metrics, quick stats) - 320px fixed width
    - Right: Fund events table (smaller, focused on events) - flexible width
  - Uses cards and panels to group information
  - Max width constraints for better readability
  - Consistent padding: 24px outer, 16px inner
  - Responsive: Sidebar collapses on smaller screens, summary moves below sidebar

## 6. Components

### 6.1 Cards & Panels
- Background: `#252537`
- Border-radius: `8px`
- Box-shadow: subtle, `rgba(0,0,0,0.2) 0px 4px 12px`
- Padding: `16px`

### 6.2 Tables
- **Use**: MUI DataGrid (free)
- Remove heavy borders
- Alternating row background: slightly lighter dark shade
- Header row: bold, slightly larger text, dark background
- Hover effect: subtle highlight
- Pagination controls styled to match theme

### 6.3 Charts
- Chart container inside a Card
- Background transparent, labels in light gray
- Accent colors: Blue, Green, Orange, Red (see palette)
- Grid lines minimal, subtle opacity

### 6.4 Buttons
- Primary button: Accent blue background, white text
- Secondary button: Transparent with white border
- Hover: Slightly lighter blue or background darkening

### 6.5 Forms & Inputs
- Rounded corners, no sharp edges
- Focus state: Blue border glow
- Background: slightly lighter dark gray than panel

## 7. Animation & Interaction
- Hover states: Smooth 150–200ms transitions
- Sidebar collapse/expand animation
- Card hover: minimal lift shadow

## 8. Accessibility
- Minimum contrast ratio: WCAG AA
- Larger clickable areas for buttons
- Keyboard navigation supported

## 9. Implementation Strategy

### Phase 1: Docker Theme Foundation (Week 1)
**Goal**: Establish exact Docker Desktop color scheme and typography system

**Tasks**:
- [ ] **Create Docker Color Palette**: Implement exact color codes from design principles
  - Background: Deep charcoal/blue-black (`#0D1117` to `#1B1F23` range)
  - Surface: Slightly lighter dark (`#1B1F23` to `#21262D` range)
  - Sidebar: Deep dark (`#0D1117` to `#161B22` range)
  - Header: Rich gradient blue (`#0066CC` to `#004499`)
  - Accent: Blue (`#007FFF` to `#1E90FF`)
  - Text: `#FFFFFF` (primary), `#8B949E` (secondary)
- [ ] **Implement Typography Scale**: Set up precise font hierarchy
  - Headings: 28px h1, 22px h2, 18px h3
  - Body: 14-16px
  - Captions: 12px
  - Font family: Inter + Roboto fallback
- [ ] **Create MUI Theme Override**: Customize Material-UI theme to match Docker aesthetic
- [ ] **Establish Spacing System**: Implement 16-24px padding and margin system
- [ ] **Add ThemeProvider**: Wrap entire application with custom theme

**Design Principles**:
- Use exact color codes from Docker design principles for authenticity
- Implement systematic typography scale for consistent hierarchy
- Override MUI defaults rather than custom CSS for maintainability
- Establish spacing system that matches Docker's generous padding approach

### Phase 2: Application Layout Architecture (Week 1-2)
**Goal**: Implement Docker-style navigation and layout structure

**Tasks**:
- [ ] **Implement Sidebar Navigation**: Create collapsible left sidebar
  - Dark background (`#0D1117` to `#161B22` range)
  - Navigation items with icons and labels
  - Active state highlighting with blue accent (`#007FFF`)
  - Collapse/expand functionality with smooth animation
- [ ] **Create Top Bar**: Fixed position header with page context
  - Page title and breadcrumbs
  - Action buttons and search (where applicable)
  - Slightly darker background than main content
- [ ] **Establish Main Content Area**: Card-based layout system
  - Consistent 24px outer padding
  - 16px inner padding for cards
  - Max width constraints for readability
- [ ] **Update App Structure**: Modify main App.tsx for new layout
  - Wrap with ThemeProvider
  - Implement sidebar + main content structure
  - Ensure responsive behavior

**Design Principles**:
- Sidebar should be collapsible for space efficiency
- Top bar should provide clear page context and actions
- Main content should use cards and panels for information grouping
- Layout should be responsive across all screen sizes

### Phase 3: Core Component Modernization (Week 2-3)
**Goal**: Transform all core components with Docker's professional appearance

**Tasks**:
- [ ] **Modernize Cards & Panels**: Apply Docker styling to all containers
  - Background: Slightly lighter dark (`#1B1F23` to `#21262D` range)
  - Border-radius: 8px
  - Subtle shadows: `rgba(0,0,0,0.2) 0px 4px 12px`
  - Consistent 16px padding
- [ ] **Update Tables**: Transform all table components
  - Use MUI DataGrid where appropriate
  - Remove heavy borders and outlines
  - Implement alternating row backgrounds
  - Add subtle hover effects
  - Style pagination controls to match theme
- [ ] **Enhance Forms & Inputs**: Modernize all form elements
  - Rounded corners (no sharp edges)
  - Focus states with blue border glow
  - Backgrounds slightly lighter than panels
  - Consistent spacing and typography
- [ ] **Style Buttons**: Create professional button designs
  - Primary: Accent blue background (`#007FFF`) with white text
  - Secondary: Transparent with white border
  - Hover states with smooth transitions
  - Consistent sizing and spacing

**Design Principles**:
- All components should use the new color palette consistently
- Typography should follow the established scale
- Spacing should be systematic (16px, 24px)
- Hover states should be subtle and smooth

### Phase 4: Fund Page Specific Enhancement (Week 3)
**Goal**: Apply Docker styling specifically to fund page tables and components

**Tasks**:
- [ ] **Transform TableContainer**: Modernize fund table containers
  - Deep dark theme with card-based design
  - Full-width tables for maximum data visibility
  - Rounded corners and soft shadows
- [ ] **Enhance Table Headers**: Professional header styling
  - Uppercase text with proper spacing
  - Dark backgrounds with high contrast
  - Subtle column separation
- [ ] **Modernize Table Rows**: Enhanced row styling
  - Alternating row backgrounds
  - Generous padding (16-24px)
  - Smooth hover transitions
  - Professional status indicators
- [ ] **Update Event Rows**: Modernize individual event display
  - Enhanced status indicators using Docker colors
  - Professional action button designs
  - Improved data formatting and hierarchy
- [ ] **Style Grouped Events**: Sophisticated grouping design
  - Visual separation for grouped events
  - Smooth expand/collapse animations
  - Clear visual hierarchy

**Design Principles**:
- Tables should achieve professional, enterprise-grade appearance
- Data readability should be significantly improved
- Visual hierarchy should guide user attention effectively
- All interactions should feel smooth and professional

### Phase 5: Dashboard & Overview Modernization (Week 3-4)
**Goal**: Apply Docker styling to dashboard and overview components

**Tasks**:
- [ ] **Update OverallDashboard**: Modernize main dashboard
  - Card-based layout for all sections
  - Consistent spacing and typography
  - Professional summary cards
  - Enhanced data visualization
- [ ] **Transform Companies Page**: Update companies overview
  - Modern tab navigation
  - Card-based content organization
  - Professional data presentation
  - Consistent styling with main theme
- [ ] **Enhance Charts & Graphs**: Modernize data visualizations
  - Chart containers inside cards
  - Transparent backgrounds with light gray labels
  - Docker accent colors for data series
  - Minimal grid lines with subtle opacity

**Design Principles**:
- Dashboard should feel cohesive with the new design system
- Data visualization should be clear and professional
- Navigation should be intuitive and visually consistent
- All components should follow the established design patterns

### Phase 6: Integration and Polish (Week 4-5)
**Goal**: Ensure seamless integration and final visual polish

**Tasks**:
- [ ] **Test Theme Integration**: Verify all components use the new design system
  - Check for any remaining default MUI styling
  - Ensure color consistency across all components
  - Validate typography hierarchy
- [ ] **Validate Responsive Behavior**: Ensure design works across all screen sizes
  - Test sidebar collapse/expand on mobile
  - Verify card layouts adapt properly
  - Check table responsiveness
- [ ] **Performance Optimization**: Verify no performance impact from styling changes
  - Test with large datasets
  - Monitor rendering performance
  - Optimize any heavy styling operations
- [ ] **Accessibility Validation**: Ensure design improvements enhance accessibility
  - Verify contrast ratios meet WCAG AA standards
  - Test keyboard navigation
  - Ensure screen reader compatibility
- [ ] **Final Visual Polish**: Fine-tune all components
  - Consistent spacing and alignment
  - Smooth animations and transitions
  - Professional hover states
  - Perfect visual hierarchy

**Design Principles**:
- All components should consistently use the new design system
- Responsive behavior should maintain Docker's aesthetic across screen sizes
- Performance should be maintained or improved with new styling
- Accessibility should be enhanced, not compromised, by design changes

### Phase 7: Enhanced Navigation Sidebar (Week 5-6) - STRETCH GOAL
**Goal**: Implement Docker-style contextual navigation sidebar for seamless fund/company switching and improved layout

**Tasks**:
- [ ] **Create Fund Navigation Sidebar**: Implement contextual navigation between funds and companies
  - Company header with company name and logo
  - Fund list with active state highlighting (current company funds always visible)
  - Other companies section (collapsible/expandable) showing all funds across companies
  - Quick navigation to company overview and other fund pages
  - Collapsible design with smooth animations
- [ ] **Implement Three-Column Layout**: Restructure fund page layout for optimal information hierarchy
  - Left: Enhanced navigation sidebar (funds + companies)
  - Center: Summary section (performance, metrics, quick stats)
  - Right: Fund events table (smaller, focused on events)
- [ ] **Integrate with Existing Layout**:
  - Position sidebar between main sidebar and content
  - Ensure responsive behavior on smaller screens
  - Maintain consistent spacing and typography with Docker theme
- [ ] **Enhanced Navigation Features**:
  - Breadcrumb-style navigation context
  - Quick actions for each fund (view, edit, etc.)
  - Visual indicators for fund status/performance
  - Smooth transitions between different fund contexts
- [ ] **State Management Integration**:
  - Sync sidebar state with current fund/company
  - Handle navigation between different contexts
  - Maintain user's navigation history
  - Ensure sidebar reflects current page context

**Design Principles**:
- Sidebar should feel like a natural extension of the main navigation
- Use Docker's exact color scheme and typography
- Three-column layout should provide clear information hierarchy
- Summary section should be prominent but not overwhelming
- Events table should be focused and easily scannable
- Maintain visual hierarchy with the main content area

**Layout Specifications**:
- **Sidebar Width**: 280px (collapsible to 64px for icon-only view)
- **Summary Section Width**: 320px (fixed, contains performance cards and key metrics)
- **Events Table Width**: Flexible (fills remaining space)
- **Spacing**: 24px between sections, 16px internal padding
- **Responsive**: Sidebar collapses on smaller screens, summary moves below sidebar

## 10. Technical Architecture

### Theme System
- **MUI Theme Override**: Customize Material-UI theme to match Docker specifications
- **Color Palette**: Implement exact color codes from design principles
- **Typography Scale**: Establish consistent font sizes, weights, and spacing
- **Component Overrides**: Customize MUI component defaults for Docker aesthetic
- **ThemeProvider**: Wrap entire application for consistent theming

### Component Structure
- **App Layout**: Sidebar + Top Bar + Main Content structure
- **Sidebar Navigation**: Collapsible navigation with active states
- **Top Bar**: Page context and actions
- **Main Content**: Card-based layout system
- **Table Components**: Modernized with DataGrid and Docker styling
- **Form Components**: Enhanced inputs and controls
- **Button System**: Consistent primary/secondary designs

### Styling Approach
- **SX Prop Overrides**: Use MUI's sx prop for component-specific styling
- **Theme Integration**: Leverage custom theme for consistent design tokens
- **Responsive Design**: Maintain Docker aesthetic across all screen sizes
- **Performance**: Optimize styling for smooth interactions and rendering
- **Accessibility**: Ensure high contrast and keyboard navigation support

## 11. Success Metrics

### Visual Quality
- [ ] Application achieves professional, enterprise-grade appearance
- [ ] Color scheme matches specified deep charcoal/blue-black theme with rich blue gradients
- [ ] Typography hierarchy is clear and consistent
- [ ] Spacing and layout follow Docker's generous padding approach
- [ ] All components use consistent design language

### User Experience
- [ ] Data readability is significantly improved
- [ ] Visual hierarchy guides user attention effectively
- [ ] Navigation is intuitive and visually consistent
- [ ] Interactions feel smooth and professional
- [ ] Tables and data are easier to scan and navigate

### Technical Achievement
- [ ] Design system is consistent across all components
- [ ] Performance is maintained or improved
- [ ] Accessibility is enhanced by design improvements
- [ ] Code maintainability is improved through consistent theming
- [ ] Responsive design works across all screen sizes

### Integration Success
- [ ] All existing functionality is preserved
- [ ] New design integrates seamlessly with existing components
- [ ] Theme system can be applied to future components
- [ ] Design patterns are documented for development team

## 12. Risk Mitigation

### Technical Risks
1. **Theme Override Complexity**: Use MUI's theme customization patterns for maintainability
2. **Performance Impact**: Test styling changes with large datasets to ensure no degradation
3. **Responsive Issues**: Validate design across all screen sizes during development
4. **Component Compatibility**: Test all components with new theme system

### Design Risks
1. **Color Accessibility**: Ensure high contrast ratios meet accessibility standards
2. **Visual Consistency**: Use design tokens and theme system for consistency
3. **User Familiarity**: Maintain existing interaction patterns while improving visual design
4. **Scope Creep**: Focus on core design system before adding advanced features

### Integration Risks
1. **State Management**: Ensure styling changes don't affect existing functionality
2. **Browser Compatibility**: Verify design works across all supported browsers
3. **Testing Coverage**: Maintain comprehensive testing during redesign
4. **Team Adoption**: Provide clear documentation and examples for development team

## 13. Implementation Notes

- Use MUI `ThemeProvider` to centralize styling
- Use `sx` props for one-off overrides
- Avoid mixing Tailwind or other CSS frameworks in this refactor
- Create **custom component wrappers** for Card, Table, Chart to enforce design consistency
- Focus on systematic implementation rather than component-by-component updates
- Test each phase thoroughly before proceeding to the next

## 14. Conclusion

This specification provides a comprehensive roadmap for transforming our entire frontend to match Docker Desktop's professional aesthetic. By following the exact design principles and implementing a systematic approach, we can achieve enterprise-grade visual quality while maintaining all existing functionality.

The implementation will create a sophisticated, modern design system that enhances user experience, improves data readability, and establishes a foundation for consistent design across all components. The phased approach ensures systematic progress while minimizing risk and maintaining quality.

The outcome will be a frontend that feels as polished and modern as Docker Desktop — clean, responsive, and visually consistent — while remaining fully in the MUI v7 ecosystem.

## 15. Appendix

### **A. Docker Design Reference**
- Deep charcoal/blue-black color scheme (`#0D1117` to `#1B1F23` range)
- Rich blue gradient header system (`#0066CC` to `#004499`)
- Professional accent color palette (`#007FFF` to `#1E90FF`)
- Layout principles and interaction patterns
- Component design guidelines and spacing systems

### **B. MUI Theme Customization**
- Material-UI theme override patterns
- Component customization approaches
- Responsive design implementation
- Performance optimization techniques

### **C. Design System Implementation**
- Color palette implementation guide
- Typography scale setup
- Spacing system establishment
- Component override patterns

### **D. Component Library Standards**
- Card and panel design specifications
- Table styling guidelines
- Button and form component standards
- Navigation component requirements
