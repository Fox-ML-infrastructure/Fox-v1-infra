# Changes

## Actions
- .gitignore: Complete rewrite from blacklist to whitelist approach
  - Ignore everything with `*` pattern
  - Explicitly un-ignore core directories and docs/
  - Un-ignore source file extensions (*.py, *.yaml, *.md, etc.)
  - Keep standard ignores for data, models, logs, cache, system files

## Commands run
```bash
# File rewrite via write tool
# Verified with: git status --short
```
