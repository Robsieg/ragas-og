# Ragas Monorepo Implementation Plan

## Proposed Structure

```
/
├── ragas/           # Main ragas project
│   ├── src/         # Original source code
│   ├── tests/       # Original tests
│   ├── pyproject.toml  # ragas-specific build config
│
├── experimental/    # nbdev-based experimental project
│   ├── nbs/         # Notebooks for nbdev  
│   ├── ragas_experimental/  # Generated code
│   ├── pyproject.toml  # experimental-specific config
│   ├── settings.ini    # nbdev config
│
├── docs/            # Combined documentation
│   ├── main/        # Main ragas docs
│   ├── experimental/  # Experimental docs (generated by nbdev)
│
├── scripts/         # Shared build/CI scripts
│
├── pyproject.toml   # Root project config (for dev tools)
├── Makefile         # Combined build commands
└── README.md        # Monorepo overview
```

## Implementation Tasks

### 1. Setup Root Project Configuration
- [x] Create workspace-level pyproject.toml for shared dev tools
- [x] Update Makefile to support both projects
- [x] Create monorepo README.md with project overview

### 2. Reorganize Project Structure
- [x] Move src/ragas_experimental to experimental/ at the root
- [x] Ensure ragas package still builds correctly after restructuring
- [x] Update relative imports if needed
- [x] Setup experimental/ as a standalone package

### 3. Configure Documentation
- [ ] Reorganize docs/ to support both projects
- [ ] Create docs/main/ for existing ragas documentation
- [ ] Configure nbdev to generate docs to docs/experimental/
- [ ] Setup navigation between both doc sets

### 4. Update Build System
- [x] Add make commands for both projects
- [ ] Create unified commands that build both packages
- [ ] Configure CI to build both projects

### 5. Development Workflow
- [x] Configure dev environment setup for both projects
- [x] Document how to work on each project independently
- [x] Support Git-based versioning for both packages
- [x] Create installation instructions for monorepo

### 6. Testing
- [ ] Ensure tests for both projects run independently
- [ ] Create combined test command
- [ ] Verify CI can run tests for both projects

## Implementation Notes

- Each project maintains isolated dependencies while sharing development tools
- Documentation will be unified but each project keeps its existing doc generation process
- Development can happen on either project independently
- Build/test processes will support working on a single project or both

## Versioning Implementation

We've successfully implemented Git-based versioning for both packages in the monorepo using setuptools_scm:

1. Both packages now use Git tags for versioning, with consistent version numbers derived from the repository's commit history.
2. Version numbers include:
   - Base version from Git tag (e.g., 0.2.16)
   - Development tag showing commits since last tag (e.g., dev5)
   - Git commit ID (e.g., g6229def)
   - Date (e.g., d20250508)

3. Key configuration files:
   - ragas/pyproject.toml: Configures setuptools_scm for the main package
   - experimental/pyproject.toml: Configures setuptools_scm for the experimental package
   - experimental/settings.ini: Disables nbdev's version management
   - Both packages import version from _version.py files generated by setuptools_scm

4. Example versions:
   - ragas: 0.2.16.dev4+g7fd5473.d20250507
   - ragas_experimental: 0.2.16.dev5+g6229def.d20250508

This approach ensures that both packages stay in sync with the repository's version history while maintaining independent versioning when needed.
