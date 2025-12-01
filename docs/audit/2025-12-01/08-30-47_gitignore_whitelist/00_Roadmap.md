# .gitignore Whitelist Update — Roadmap (2025-12-01)

**Prompt:** "Update .gitignore to ignore everything except core files and docs folder"

## Context
- Previous .gitignore used blacklist approach (ignore specific patterns)
- User wants whitelist approach (ignore everything, keep only core source and docs)
- Core files include: source code directories, config files, consulting docs
- Must preserve docs/ folder entirely

## Plan (now)
1) Replace .gitignore with whitelist pattern
2) Ignore everything with `*`
3) Un-ignore core directories: ALPACA_trading/, IBKR_trading/, DATA_PROCESSING/, TRAINING/, CONFIG/, scripts/, SETUP/, INFORMATION/, NOTES/, docs/
4) Un-ignore root-level docs: README.md, LICENSE, requirements.txt, consulting docs
5) Keep standard ignores for cache, data, models, logs, system files
6) Within kept dirs, keep source files (*.py, *.yaml, *.md, etc.) but ignore artifacts

## Success criteria
- .gitignore uses whitelist approach
- Core source directories are tracked
- docs/ folder is tracked
- Data, models, logs, cache are ignored
- System files and build artifacts are ignored
