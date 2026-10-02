---
tags: [standards]
---

# Code Standards — {{PROJECT_NAME}}

Canonical, universal engineering standards. All review skills review against these, and follow them while writing code. (Referenced from AGENTS.md.)

## Principles
### OOP (Object-Oriented Programming)
Structure software by organizing code into distinct, reusable objects that combine data (attributes) and behavior (methods). All OOP implementations must leverage its four core pillars to maximize modularity and maintainability:
*   **Encapsulation:** Hide internal object states and restrict direct external access. Expose data only through controlled, public methods to protect state integrity.
*   **Abstraction:** Conceal complex implementation details and expose only the essential operational interface. This reduces conceptual complexity for consuming code.
*   **Inheritance:** Create hierarchical relationships between classes to reuse code. Derive new child classes from existing parent classes to share attributes and behaviors.
*   **Polymorphism:** Allow different objects to respond to the same interface or method call in their own specific way. This enables uniform handling of varying data types.

### SOLID
Ensure all object-oriented architecture adheres to the five SOLID principles to maximize maintainability, scalability, and testability:
*   **Single Responsibility (SRP):** A class must have only one reason to change, meaning it performs exactly one job or encapsulates one distinct responsibility.
*   **Open/Closed (OCP):** Software entities must be open for extension but closed for modification. Enhance behavior via inheritance, interfaces, or composition without altering existing code.
*   **Liskov Substitution (LSP):** Subtypes must be completely substitutable for their base types without altering the correctness of the program.
*   **Interface Segregation (ISP):** Clients should not be forced to depend on interfaces or methods they do not use. Split bloated interfaces into smaller, specific ones.
*   **Dependency Inversion (DIP):** Depend on abstractions (interfaces/abstract classes), not on concrete implementations. High-level modules must not depend on low-level modules.

### DRY (Don't Repeat Yourself)
Every distinct piece of knowledge, business logic, or algorithm must have a single, authoritative representation within the codebase. Do not duplicate code blocks or logic paths. Instead, eliminate repetition by abstracting shared functionality into reusable methods, classes, modules, or utilities. Only allow structural duplication if the underlying concepts have distinct reasons to change independently.

### KISS (Keep it simple stupid)
Prioritize simplicity and readability over clever or complex engineering. Write clean, predictable code that directly solves the immediate requirement without introducing unnecessary abstractions, over-engineered design patterns, or speculative features for future use. If a solution can be implemented with fewer moving parts, native language features, or simpler logic structures, choose the simpler path.

## Functions & classes
- Use clear, single-purpose helper functions.
- No more than 75 lines per function. If a function exceeds 50 lines, it must be refactored into helper functions unless it is a linear configuration or UI layout block.
- Reuse helpers when the underlying business concept is identical; prioritize readability over aggressive abstraction.
- Sections of code that have a clear isolated purpose should be converted into a helper fuction for readability.
- Use dataclasses when the input or output of a function exceeds 5 or more parameters
- Functions must use language appropriate private conventions when used only within the same script.
- Nested or inner classes should be private.

## Scripts & Folders
Scripts shouldn't be longer than 500 LoC with wiggle room if code is clearly relevant to the rest of the script
If scripts start to get long, consider breaking up into subscripts inside a directory.
Scripts should be named appropriately and organized in appropriate files making sure the overall repo continues to be well organized.

## Naming
Names are clear and concise so the code reads itself and comments stay minimal.

## Comments
- Use comments only when appropriate.
- Inline comments are ≤ 2 lines. Only when a name cannot carry the meaning and the code can't read itself.
    - Comments are not a resolution to bad naming. Try fixing naming before writing a comment.
- Docstrings only on public classes/functions; review them hard for accuracy and staleness.
- When appropriate, add correct typehints to all input and output parameters

## Dead code & redundancy
Hunt orphaned code. Remove redundancy; consolidate duplication under uniform classes/helpers.
Never output placeholders, truncated snippets, or TODO comments in production-ready files. All generated code must be syntactically complete and fully realized.

## Logging & error handling
Verbose, consistent logging and error handling throughout, with appropriate log levels and error types. More information out is better, especially for debugging.
Errors should be handled gracefully and clearly logged with traceability back to the root cause of the error.

## Testing
Every public function or API route must have at least one correspond unit or integration test mirroring the source folder structure.

## Documentation
- Keep documentation current, especially when new run/entrypoint/shell-script/API surfaces are created.
- **Every Markdown link points to a specific openable file** — a relative `[text](path.md)` resolved from the linking file's location. Never link a bare folder (link its `README.md`/`INDEX.md`, or use inline code for the path), and never use `[[wikilinks]]` in body text (only the `related:` frontmatter property may). See [ONBOARDING.md](ONBOARDING.md) → "Markdown conventions".
