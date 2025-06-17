# Inquiro Repository Restructuring Plan

## Current Structure Assessment
The current structure is **fundamentally sound** but needs refinement.

## Recommended Improvements

### 1. Add Project Configuration
```
pyproject.toml          # Modern Python packaging
setup.py               # Fallback setup script
```

### 2. Improve Directory Structure
```
inquiro/                # Main package directory
├── __init__.py
├── core/              # Core business logic (keep as-is)
├── ui/                # Rename from 'win' to be platform-agnostic
│   ├── cli/          # Command-line interface
│   ├── tui/          # Terminal UI
│   └── common/       # Shared UI utilities
├── tests/             # Rename from 'test' (pytest convention)
├── scripts/           # Utility scripts
└── docs/              # Documentation
```

### 3. Add Missing Files
```
.env.example           # Environment variables template
CHANGELOG.md           # Version history
CONTRIBUTING.md        # Development guidelines
LICENSE               # License file
Makefile              # Common development tasks
```

### 4. Improve .gitignore
```
# Add more comprehensive Python ignores
# Add OS-specific ignores
# Add IDE-specific ignores
```

### 5. Entry Points
```
inquiro/cli.py         # Main CLI entry point
inquiro/tui.py         # Main TUI entry point
```

## Priority Order
1. **High**: Fix incomplete CLI code, add .gitignore entries
2. **Medium**: Add pyproject.toml, rename directories
3. **Low**: Add documentation files, improve structure

## Benefits
- More professional and maintainable structure
- Better packaging and distribution
- Clearer entry points for users
- Industry-standard conventions
