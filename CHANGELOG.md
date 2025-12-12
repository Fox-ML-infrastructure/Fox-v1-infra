# Changelog

All notable changes to FoxML Core will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

**For more detailed information:**
- [Detailed Changelog](DOCS/02_reference/CHANGELOG_DETAILED.md) - Comprehensive change details with file paths and config references

---

## [Unreleased]

### Highlights

- **Reproducibility Tracking System** (2025-12-11) — **NEW**: Comprehensive reproducibility tracking across all pipeline stages with per-model granularity. Three-tier classification (STABLE/DRIFTING/DIVERGED) prevents alert fatigue. Module-specific storage with cross-run search. Per-model tracking in feature selection stores delta_score, Jaccard@K, importance_corr in `model_metadata.json`. See [Reproducibility Tracking Guide](DOCS/03_technical/implementation/REPRODUCIBILITY_TRACKING.md).
- **Model Parameter Sanitization** (2025-12-11) — **FIXED**: Resolved parameter validation issues for MLPRegressor (`verbose=-1`), CatBoost (iteration synonyms, random_state/random_seed conflicts), and univariate selection (signed F-statistics). Created shared `config_cleaner.py` utility using `inspect.signature()` to prevent parameter passing errors across all model constructors.
- **Interval Detection Improvements** (2025-12-11) — **FIXED**: Added median-based gap filtering to ignore overnight/weekend gaps. Added `interval_detection.mode=fixed` to skip auto-detection for known intervals. Downgraded warnings to INFO level. Eliminates false warnings on clean 5m data.
- **Leakage Detection Fixes** (2025-12-11) — **CRITICAL**: Fixed confidence calculation bug that filtered out valid detections. Enhanced detection to compute importances on-the-fly when missing. Improved diagnostics and logging.
- **Config & Determinism** (2025-12-10) — **ENHANCED**: Complete config centralization with SST enforcement. Centralized determinism system. Removed 30+ hardcoded random_state values. All pipeline parameters load from YAML files.
- **Code Quality** (2025-12-10) — Fixed 194 F821 errors, syntax errors, missing imports. Full end-to-end testing underway.
- **Architecture** (2025-12-09) — Large file refactoring into modular components. Intelligent training framework Phase 1 completed. Leakage Safety Suite with auto-fixer. Modular configuration system.

---

### Stability Guarantees

- **Training results reproducible** across hardware (deterministic seeds, config-driven hyperparameters)
- **Complete config centralization** — All pipeline parameters load from YAML files (single source of truth)
- **SST enforcement** — Automated test prevents hardcoded hyperparameters
- **Config schema backward compatible** (existing configs continue to work)
- **Modular architecture** (self-contained TRAINING module, zero external script dependencies)

### Known Issues & Limitations

- **Trading execution modules** removed from core repository; system focuses on ML research infrastructure
- **Feature engineering** requires human review and validation
- **End-to-end testing in progress** (2025-12-10) — Full pipeline validation underway after SST and Determinism fixes

---

### Added

- **Per-model reproducibility tracking** (2025-12-11) — Tracks delta_score, Jaccard@K, importance_corr per model family. Stores in `model_metadata.json` with compact logging.
- **Config cleaner utility** (2025-12-11) — `TRAINING/utils/config_cleaner.py` for systematic parameter validation using `inspect.signature()`. Prevents parameter passing errors across all model constructors.
- **Reproducibility tracking module** (2025-12-11) — Reusable `ReproducibilityTracker` class with tolerance-based verification and three-tier classification (STABLE/DRIFTING/DIVERGED).
- **CLI/Config separation** (2025-12-11) — Policy document and enforcement. CLI only provides inputs, config overrides, operational flags. All settings from config files.
- **Intelligent training config section** (2025-12-11) — Added `intelligent_training` section to `pipeline_config.yaml` with all settings configurable via YAML.
- **Feature Importance Stability Tracking** (2025-12-10) — Automatic snapshot capture and config-driven automation for feature importance stability analysis.
- **Observability improvements** (2025-12-10) — Enhanced logging for auto-fixer, config loading, defaults injection.
- **Target confidence & routing system** — Automatic quality assessment with configurable thresholds
- **Cross-sectional feature ranking** — Optional panel model for universe-level feature importance
- **Modular configuration system** — Typed schemas, experiment configs, validation
- **Leakage Safety Suite** — Production-grade backup system, automated detection and auto-fix

### Fixed

- **Interval detection** (2025-12-11) — Added median-based gap filtering (>10x median), fixed mode (`interval_detection.mode=fixed`), downgraded warnings to INFO. Eliminates false warnings on clean data.
- **Model parameter validation** (2025-12-11) — Fixed MLPRegressor `verbose=-1`, CatBoost iteration synonyms conflict, CatBoost `random_state`/`random_seed` conflict, univariate selection signed F-statistics handling. All via `config_cleaner.py` utility.
- **Leakage detection** (2025-12-11) — **CRITICAL**: Fixed confidence calculation bug (was using raw importance as confidence). Enhanced to compute importances on-the-fly when missing. Improved diagnostics and logging.
- **Reproducibility tracking** (2025-12-11) — Moved to computation modules, added three-tier classification (STABLE/DRIFTING/DIVERGED), module-specific directories, improved error handling. Added per-symbol debug logging.
- **Cross-sectional sampling** (2025-12-11) — **CRITICAL**: Fixed `max_cs_samples` filtering bug causing excessive memory usage.
- **Config parameter passing** (2025-12-11) — Fixed missing config values not passed to ranking pipeline.
- **Auto-fixer** (2025-12-11) — Fixed logging format error, backup creation bug, training accuracy detection bug.
- **Silent errors** (2025-12-11) — Added comprehensive logging to all previously silent failure paths.
- **Parameter passing errors** (2025-12-11) — Systematic fix prevents "got multiple values" and "unexpected keyword argument" errors across all model families.
- **Config & code quality** (2025-12-10) — Fixed config loading, YAML None handling, 194 F821 errors, missing imports, syntax errors.

### Changed

- **Reproducibility settings** (2025-12-10) — Removed 30+ hardcoded `random_state: 42` values. All now use centralized determinism system.
- **Config cleanup** (2025-12-10) — Removed ~35+ duplicate default values. All now auto-injected from `defaults.yaml`.
- **Internal documentation** (2025-12-10) — Moved all internal docs to `INTERNAL_DOCS/` (never tracked). Cleaned up `CONFIG/` directory by removing internal audit/verification docs.
- **Config loading patterns** (2025-12-10) — All function parameters now load from config instead of hardcoded defaults
- **Logging system** — Replaced hardcoded flags with structured YAML configuration

---

### Security

- Enhanced compliance documentation for production use
- License enforcement procedures documented
- Copyright notice requirements standardized

### Documentation

- Documentation restructured into 4-tier hierarchy
- 55+ new documentation files created, 50+ existing files rewritten
- Comprehensive cross-linking and navigation improvements

---

## Versioning

Releases follow [Semantic Versioning](https://semver.org/):
- **MAJOR** version for incompatible API changes
- **MINOR** version for functionality added in a backwards-compatible manner
- **PATCH** version for backwards-compatible bug fixes

## Categories

- **Added** – New features
- **Changed** – Changes in existing functionality
- **Fixed** – Bug fixes
- **Security** – Security improvements
- **Documentation** – Documentation changes
