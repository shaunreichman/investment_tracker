# AI Agent Collaboration Guidelines

- **Testing:**
  - Run tests frequently, especially after any non-trivial change.
  - For `test_main.py`, always:
    - Save its output to `tests/output/test_main_output_new.txt`.
    - Compare this output to `tests/output/test_main_output1.txt`.
    - If outputs differ, inform the user immediately, as this likely indicates a problem.

- **Iteration:**
  - Prefer small, reviewable steps over large, sweeping changes.
  - Summarize each change clearly before and after making it.
  - When in doubt, ask for confirmation before making structural or potentially controversial changes.

- **Communication:**
  - Be explicit about what is being changed and why.
  - Default to autonomy for routine or obvious improvements, but pause for user input on ambiguous or high-impact decisions.
  - Use dedicated debug scripts for deep dives or complex logic issues.

- **Code & Architecture:**
  - Follow domain-driven design and project conventions.
  - All database operations must be handled by the core system, not by clients.
  - Use class methods and domain methods for object creation and manipulation (never direct constructors).

- **Documentation:**
  - Update documentation and code comments to reflect any significant changes or new patterns.

- **Proactive Debugging:**
  - When encountering unexpected behavior or logic issues, create a dedicated debug script to inspect the state and isolate the problem, rather than making speculative fixes.

- **Refactoring Philosophy:**
  - Only propose refactors that clearly improve code clarity, maintainability, or future extensibility—not for the sake of refactoring alone.

- **Session & State Management:**
  - Always treat the backend as the owner of session and state; clients should remain stateless and never perform direct database operations.

- **Commit Discipline:**
  - Only suggest committing changes after all tests have passed and the user has reviewed the changes, unless otherwise directed.

- **Documentation Consistency:**
  - When introducing new patterns or conventions, update both code comments and relevant documentation to keep everything in sync.

- **User Preferences First:**
  - When in doubt, defer to explicit user preferences or ask for clarification before proceeding with ambiguous tasks. 