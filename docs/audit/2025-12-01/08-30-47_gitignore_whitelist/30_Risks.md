# Risks & Assumptions

- Assumption: User wants all source code in core directories tracked, regardless of subdirectory structure
- Risk: If new core directories are added, they need to be explicitly added to .gitignore whitelist
- Risk: Large files in tracked directories (if not in ignored subdirs) will be tracked
- Rollback: `git checkout HEAD -- .gitignore` (restores previous blacklist version)
