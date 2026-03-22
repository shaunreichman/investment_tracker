# Spec Writing Best Practices

## 🎯 Core Rules

1. **Never start development without a spec**
2. **Keep specs code-free** - focus on what, not how
3. **Use phase-based development** - Foundation → Feature → Polish → Integration → Optimization

---

## 📋 Template

```markdown
# [Feature Name] Specification

## Overview
[What we're building and why]

## Design Philosophy
- [Core principles]
- [Problems we're solving]

## Implementation Strategy
### Phase 1: [Foundation]
**Goal**: [Clear objective]
**Design Principles**:
- [Key architectural decision and rationale]
- [Technical constraints or patterns to follow]
**Tasks**:
- [ ] [Specific, actionable task]  <!-- Use checkboxes to track progress -->
- [ ] [Specific, actionable task]  <!-- Use checkboxes to track progress -->
**Success Criteria**:
- [Measurable outcome for this phase]
- [Quality gate for phase completion]

### Phase 2: [Next Phase]
**Goal**: [Clear objective]
**Design Principles**:
- [Key architectural decision and rationale]
- [Technical constraints or patterns to follow]
**Tasks**:
- [ ] [Specific, actionable task]
- [ ] [Specific, actionable task]
**Success Criteria**:
- [Measurable outcome for this phase]
- [Quality gate for phase completion]

## Overall Success Metrics
- [Measurable outcome 1]
- [Measurable outcome 2]
```

---

## 📝 Example Usage

```markdown
### Phase 1: Database Schema Foundation
**Goal**: Establish core data models for fund tracking
**Design Principles**:
- Use domain-driven design with clear entity boundaries
- All calculated fields must be computed, never manually set
- Follow existing naming conventions from Company model
**Tasks**:
- [ ] Create Fund model with required fields
- [ ] Implement FundEvent model for capital movements
- [ ] Add database migration scripts
**Success Criteria**:
- All models pass validation tests
- Database schema matches design diagrams
- Zero linting errors in new code

### Phase 2: API Endpoints
**Goal**: Create RESTful API for fund operations
**Design Principles**:
- All endpoints must use domain methods, never direct database access
- Consistent error response format across all endpoints
- Follow existing API patterns from /api/funds endpoint
**Tasks**:
- [ ] Implement GET /api/funds/{id} endpoint
- [ ] Add POST /api/funds endpoint for creation
- [ ] Create PUT /api/funds/{id} for updates
**Success Criteria**:
- All endpoints return responses within 200ms
- 100% test coverage for new endpoints
- API documentation matches implementation
```

---

## ✍️ Writing Guidelines

### **Be Specific & Measurable**
```markdown
# ❌ BAD
- Improve user experience
- Make it faster

# ✅ GOOD  
- Reduce fund creation time from 3 minutes to under 1 minute
- Implement responsive grid for screens 320px-1920px
```

### **Clear Task Language**
```markdown
# ❌ BAD
- Handle errors
- Add validation

# ✅ GOOD
- Implement try-catch in all API endpoints with consistent error format
- Add input validation for fund name (required, max 255 chars)
```

**Note**: Always use `- [ ]` checkboxes for tasks so you can track progress as you implement (`- [x]` when complete).

### **Define Success Criteria**
```markdown
# ❌ BAD
- Users will like it better
- It will work properly

# ✅ GOOD
- All API endpoints respond within 200ms
- 100% test coverage for new functionality
- Zero console errors in production
```

---

## 🔍 Review Checklist

- [ ] Clear problem statement
- [ ] Specific, measurable goals
- [ ] Logical phases that build on each other
- [ ] **Each phase has design principles** (architectural decisions and constraints)
- [ ] **Each phase has success criteria** (measurable outcomes and quality gates)
- [ ] Actionable tasks (developer knows exactly what to build)
- [ ] Overall success metrics (how do we know the entire project is done?)
- [ ] No unnecessary code examples
- [ ] References existing patterns

---

## 🚫 Common Mistakes

1. **Too much code** - Focus on what, not how
2. **Vague requirements** - "Make it user-friendly" vs "Form validation with real-time feedback"
3. **Missing success criteria** - No way to measure completion

---

## 📝 Quick Reference

**Task Formula**: `[Action Verb] + [Specific Thing] + [Measurable Criteria]`

**Examples**:
- Implement fund creation API that accepts required fields and returns 201 status
- Add form validation that prevents submission with empty required fields
- Create responsive grid that adapts to screen sizes 320px-1920px

---

## 🎯 Remember

**Good specs enable great development. Great specs enable great products.**

- **Be specific** - Vague specs lead to wrong implementations
- **Be measurable** - Success criteria must be testable  
- **Be actionable** - Developers should know exactly what to build

**Reference**: See `docs/DESIGN_GUIDELINES.md` for comprehensive architectural guidelines and patterns.