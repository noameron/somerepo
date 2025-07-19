# Development Partnership

We're building production-quality Python applications. Your role is to create maintainable, efficient solutions while catching potential issues early.

**MOST IMPORTANTLY**! When you seem stuck or overly complex, I'll redirect you!! - my guidance helps you stay on track.

Product Definition : PRODUCT.md is the main file for this project. It contains the product definition, requirements, and architecture overview.

## 🚨 AUTOMATED CHECKS ARE MANDATORY
**ALL hook issues are BLOCKING - EVERYTHING must be ✅ GREEN!**  
No errors. No formatting issues. No linting problems. Zero tolerance.  
These are not suggestions. Fix ALL issues before continuing.

## 🔒 SECURITY - ZERO TOLERANCE POLICY
Development Security Rules
FORBIDDEN - SECURITY VIOLATIONS:

* NO hardcoded secrets - Use environment variables ONLY
* NO string concatenation for SQL queries or system commands
* NO custom encryption - Use established libraries
* NO direct user input in file paths or system commands
* NO sensitive data in logs - Never log passwords, tokens, or personal data
* NO outdated dependencies - Keep all packages updated

MANDATORY Security Practices:

Secrets Management:

Store ALL secrets in .env files
Add .env to .gitignore IMMEDIATELY when creating project
Use python-dotenv to load secrets
Never commit secrets, even temporarily


Input Validation:

Validate ALL user inputs at entry points
Use parameterized queries for databases
Sanitize inputs based on context (HTML, SQL, Shell)
Never trust external data


Dependency Security:

Regularly check for vulnerabilities: pip-audit
Keep dependencies updated
Review security advisories for used packages


File Operations:

Always validate file paths with pathlib
Never use user input directly in paths
Restrict file operations to specific directories


When Using External APIs/LLMs:

Never send personal/sensitive data
Always use API keys from environment variables
Implement proper error handling without exposing details
Use HTTPS for all external communications



### Security Validation Commands:
* Include in regular validation
* Check for secrets (add pre-commit hook)
```bash
pip-audit  # Check for known vulnerabilities
bandit -r src/  # Static security analysis
``` 

## CRITICAL WORKFLOW - ALWAYS FOLLOW THIS!

### Research → Plan → Implement
**NEVER JUMP STRAIGHT TO CODING!** Always follow this sequence:
1. **Research**: Explore the existing codebase, understand patterns and architecture
2. **Plan**: Create a detailed implementation plan and verify it with me  
3. **Implement**: Execute the plan with validation checkpoints

When asked to implement any feature, you'll first say: "🔍 Let me research the codebase and create a plan before implementing."

* For complex architectural decisions, use **"ultrathink"** to engage maximum reasoning capacity. Say: "🧠 Let me ultrathink about this architecture before proposing a solution."

### USE MULTIPLE AGENTS!
*Leverage subagents aggressively* for better results:

* Research existing patterns in the codebase
* Design API interfaces
* Investigate library options
* Analyze performance implications

Say: "I'll spawn agents to tackle different aspects of this problem" whenever a task has multiple independent parts.

## Project Structure Analysis

### First Time Setup or Review
When starting a new project or seeing an existing one for the first time:
1. **Analyze** the current structure
2. **Suggest improvements** if the structure could be better organized
3. **Discuss** the ideal structure before making changes

Common Python project patterns to consider:
```
project/
├── src/
│   └── package_name/
│       ├── __init__.py
│       ├── core/          # Business logic
│       ├── api/           # External interfaces
│       ├── models/        # Data models
│       └── utils/         # Helpers
├── tests/
│   ├── unit/
│   ├── integration/
│   └── conftest.py
├── docs/
├── .env.example
├── pyproject.toml
└── README.md
```

## Testing Strategy - pytest with TDD Focus

**STRICTLY pytest** - No other testing frameworks.

### TDD Cycle for Core Logic:
1. **Red Phase**: Write failing test first
2. **Green Phase**: Write minimal code to pass
3. **Refactor Phase**: Clean up while keeping tests green

### Test Coverage Requirements:
- **100% type coverage** with mypy
- Focus on business logic coverage (~80-90%)
- Integration tests for critical paths
- Don't over-test simple getters/setters

## Git Commit Management - MANDATORY PRACTICES

**Never commit cache/temp files** - Always exclude `__pycache__/`, `.pyc`, `.DS_Store`, IDE folders, and other generated files from commits.

### Commit Strategy - FREQUENT COMMITS
**Make many small, focused commits rather than few large ones!**

**Commit After Each:**
- ✅ Writing a failing test (Red phase)
- ✅ Making the test pass (Green phase)  
- ✅ Refactoring while keeping tests green
- ✅ Adding a new feature
- ✅ Fixing a bug
- ✅ Updating documentation

### Commit Message Format:
```
type(scope): brief description

Longer explanation if needed
- What changed
- Why it changed
- Any side effects
```

**Types:** `feat`, `test`, `refactor`, `fix`, `docs`, `style`, `chore`

## Python-Specific Standards

### Environment Setup
- **Python Version**: 3.12 (strict requirement)
- **Virtual Environment**: Always work within venv
- **Dependencies**: "Batteries included" - use best-in-class libraries

### FORBIDDEN - NEVER DO THESE:
- **NO bare except:** clauses - always catch specific exceptions!
- **NO mutable default arguments** - use `None` and create inside function!
- **NO string concatenation** for paths - use `pathlib.Path`!
- **NO keeping old and new code together** - delete when replacing
- **NO TODOs in final code**
- **NO missing type hints** - 100% coverage required

### Required Standards:

#### Code Quality:
- **Type hints everywhere**: Full annotations on all functions/methods
- **Meaningful names**: Be explicit - `user_email` not `email`
- **Early returns** to reduce nesting
- **Context managers**: Always use `with` for resource management
- **Path handling**: Always use `pathlib.Path`

#### Documentation:

1. Docstrings: Sphinx style for complex functions only
2. Document: Complex logic, non-obvious behavior, public APIs, exceptions
3. Skip: Self-explanatory functions, getters/setters, standard constructors
4. If the code is clear, don't document it

#### Patterns & Architecture:

**Design Patterns** (suggest when appropriate, never auto-implement):
- Factory Pattern: Only when centralizing object creation or creating related objects together
- Dependency Injection: Generally avoid
- Other patterns: Suggest when they genuinely improve the solution

**Data Modeling**:
- Use dataclasses/Pydantic for structured data
- Keep models readable and not overly complex
- Validate data at boundaries

**Configuration**:
- Use python-dotenv for environment variables
- Always include .env.example

**Logging**:
- Use structured logging (e.g., structlog or configured stdlib)
- Include context for debugging
- Log at appropriate levels

**Error Handling**:
- Custom exceptions for core business logic
- Standard exceptions for common cases
- Helpful error messages

**Threading/Async**:
- Use `asyncio` for I/O-bound operations
- Use `ThreadPoolExecutor` for CPU-bound parallel work
- Always handle concurrent access to shared resources

## Working Memory Management

### When context gets long:
- Re-read this CLAUDE.md file
- Summarize progress in a PROGRESS.md file
- Document current state before major changes

### Maintain TODO.md:
```
## Current Task
- [ ] What we're doing RIGHT NOW

## Completed  
- [x] What's actually done and tested

## Next Steps
- [ ] What comes next
```

**For Complex Projects:**
- Create detailed TODO files: `TODO-YYYY-MM-DD-short-description.md`
- Store in `/todo` directory (create if not present)
- Organize by phases with atomic tasks and checkboxes

## Implementation Standards

### Our code is complete when:
- ✅ All tests pass (pytest)
- ✅ 100% type coverage (mypy)
- ✅ All linting passes
- ✅ Code is properly formatted
- ✅ Documentation is complete
- ✅ Commits are clean and descriptive
- ✅ Error handling is comprehensive
- ✅ Logging provides good observability

### Quality Tools:
```bash
# Standard validation command
pytest -v && mypy . --strict && [linter] && [formatter]
```

Common tool combinations:
- ruff (linting + formatting)
- black + flake8/pylint
- blue + pylint

## Problem-Solving Together

When you're stuck or confused:
1. **Stop** - Don't spiral into complex solutions
2. **Delegate** - Consider spawning agents for parallel investigation
3. **Ultrathink** - For complex problems, say "I need to ultrathink through this challenge"
4. **Step back** - Re-read the requirements
5. **Simplify** - The simple solution is usually correct
6. **Ask** - "I see two approaches: [A] vs [B]. Which do you prefer?"

## Communication Protocol

### Progress Updates:
```
✓ [COMMIT abc123] test(auth): add failing test for token validation
✓ [COMMIT def456] feat(auth): implement JWT token validation
✗ Working on refresh token logic - considering approach
```

### Pattern Suggestions:
When I see an opportunity to improve your code with a pattern:
"I notice this could benefit from [pattern]. Would you like me to refactor using [pattern] because [reason]?"

## Working Together

- Focus on clean, maintainable architecture
- Prioritize code clarity over cleverness
- **REMINDER**: If this file hasn't been referenced in 30+ minutes, RE-READ IT!
- Always suggest improvements, never implement them silently
- Demonstrate professional software engineering practices

The goal is production-quality solutions that are maintainable, well-tested, and properly documented.