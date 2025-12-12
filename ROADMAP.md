# Fox ML Infrastructure — Strategic Roadmap

FoxML Core is the core research and training engine of Fox ML Infrastructure.

Direction and priorities for ongoing development. Timelines are aspirational and subject to change.

---

## Development Philosophy

FoxML Core is maintained with an **enterprise reliability mindset**:
* Critical issues are fixed immediately.
* Documentation and legal compliance are treated as first-class deliverables.
* Stability always precedes new features.
* GPU acceleration, orchestration, and model tooling will remain backwards-compatible.
* **UI integration approach** — UI is intentionally decoupled from the core. FoxML Core provides Python programmatic interfaces and integration points so teams can plug into their existing dashboards, monitoring tools, or UX layers. *As always, priorities are subject to change based upon client demand.*

---

# Current Status — Winter 2025

---

## What Works Today

**You can use these capabilities right now:**

* ✅ **Full TRAINING Pipeline** — Complete one-command workflow: target ranking → feature selection → training plan generation → model training
* ✅ **Training Routing & Planning System** — Config-driven routing decisions, automatic training plan generation, 2-stage training pipeline (CPU → GPU), plan-aware filtering
* ✅ **GPU-Accelerated Model Training** — Train all 20 model families (LightGBM, XGBoost, MLP, LSTM, Transformer, CNN1D, etc.) with GPU acceleration where available
* ✅ **Centralized YAML Configuration** — Complete Single Source of Truth (SST) system with structured configs for experiments, model families, and system parameters
* ✅ **Reproducibility Tracking** — End-to-end reproducibility tracking with STABLE/DRIFTING/DIVERGED classification across ranking, feature selection, and training
* ✅ **Leakage Detection & Auto-Fix** — Pre-training leak detection with automatic feature exclusion and comprehensive diagnostics
* ✅ **Complete Documentation & Legal** — Full 4-tier docs hierarchy + enterprise legal package for commercial evaluation

**This is production-grade ML infrastructure, not a prototype.**

---

## Core System Status

* **TRAINING Pipeline — Phase 1** ✅ — Fully operational. Intelligent training framework (target ranking, feature selection, automated leakage detection) integrated and working. **End-to-end testing currently underway** to validate full pipeline from target ranking → feature selection → training plan → model training. **NEW** (2025-12-12): ResolvedConfig system ensures consistent logging and correct purge/embargo calculation across all modules.

* **Training Routing & Planning System** 🔄 (2025-12-11) — **NEW - Currently being tested**: 
  - Config-driven routing decisions (cross-sectional vs symbol-specific vs both vs experimental vs blocked)
  - Automatic routing plan and training plan generation
  - 2-stage training pipeline (CPU models first, then GPU models) for all 20 model families
  - One-command end-to-end flow: `intelligent_trainer` orchestrates complete pipeline
  - Training plan auto-detection and filtering
  - See [Training Routing Guide](DOCS/02_reference/training_routing/README.md)

* **Single Source of Truth (SST) & Determinism** ✅ (2025-12-10) — Complete config centralization for TRAINING; SST enforcement test; all hyperparameters and seeds load from YAML; centralized determinism system. 30+ hardcoded `random_state` and defaults removed.

* **Reproducibility Tracking** ✅ (2025-12-11) — End-to-end reproducibility tracking across ranking, feature selection, and training with per-model metrics and three-tier classification (STABLE/DRIFTING/DIVERGED). Module-specific logs and cross-run comparison.

* **Model Parameter Sanitization** ✅ (2025-12-11) — Shared `config_cleaner.py` utility using `inspect.signature()` to prevent parameter passing errors. Eliminates entire class of "got multiple values" / "unexpected keyword" failures.

* **Code Refactoring** ✅ (2025-12-09) — Large monolithic files split into modular components (4.5k → 82 lines, 3.4k → 56 lines, 2.5k → 66 lines) while maintaining 100% backward compatibility. Largest file now: 2,542 lines (cohesive subsystem, not monolithic).

* **Model Family Status Tracking** ✅ — Comprehensive debugging system to identify which families succeed/fail in multi-model feature selection. Status persisted to JSON for analysis.

* **GPU Families** ✅ — All GPU model families operational and producing artifacts. Expect some noise and warnings during training (harmless, do not affect functionality).

* **Sequential Models** ✅ — All sequential models (CNN1D, LSTM, Transformer, TabCNN, TabLSTM, TabTransformer) working and producing outputs. 3D preprocessing issues resolved.

* **Target Ranking & Selection** ✅ — Integrated and operational as part of Phase 1 pipeline.

* **Documentation Overhaul** ✅ — 55+ new files created, 50+ rewritten, standardized across all tiers. Internal docs organized into `INTERNAL_DOCS/` for planning/architecture, public docs in `DOCS/` for operational use.

* **Legal Compliance** ✅ — Enhanced with IP assignment agreement, regulatory disclaimers, and compliance documentation. Compliance assessment: 95% complete (after IP assignment signing).

---

# Phase 0 — Stability & Documentation ✅

**Status**: Complete

**Deliverables:**
* ✅ Full 4-tier documentation hierarchy
* ✅ Enterprise-grade legal docs
* ✅ Navigation and cross-linking
* ✅ Internal docs organized (moved to `INTERNAL_DOCS/`)
* ✅ Consistent formatting, naming, and structure
* ✅ Stable release for evaluators and enterprise inquiries

**Outcome:** Established FoxML Core as an evaluable, commercial-grade product.

---

# Phase 1 — Intelligent Training Framework ✅

**Status**: Functioning properly. **End-to-end testing underway** (2025-12-10).

**Completed:**
* ✅ TRAINING pipeline restored and validated
* ✅ GPU acceleration functional across all 20 model families
* ✅ XGBoost source-build stability fixes
* ✅ Readline and child-process dependency issues resolved
* ✅ Sequential models 3D preprocessing fix
* ✅ Scaffolded base trainers for 2D and 3D models
* ✅ Intelligent training pipeline — target ranking, feature selection, and automated leakage detection integrated into unified workflow
* ✅ Target ranking and selection modules operational
* ✅ VAE serialization fixed — all models appear to be working correctly
* ✅ Structured logging configuration system implemented
* ✅ **Large file refactoring** (2025-12-09) — Split monolithic files into modular components
* ✅ **Model family status tracking** — Added debugging for multi-model feature selection
* ✅ **Interval detection robustness** — Fixed timestamp gap filtering, added fixed interval mode
* ✅ **Import fixes** — Resolved all missing imports in refactored modules (polars, type hints, etc.)
* ✅ **STEP 2 → STEP 3 transition robustness** (2025-12-10) — Fixed missing polars imports and added feature list validation
* ✅ **Complete F821 undefined name error elimination** (2025-12-10) — Fixed all 194 undefined name errors across TRAINING and CONFIG directories
* ✅ **Single Source of Truth (SST) enforcement** (2025-12-10) — Complete config centralization, SST enforcement test, centralized determinism system
* ✅ **Reproducibility tracking** (2025-12-11) — End-to-end tracking with three-tier classification (STABLE/DRIFTING/DIVERGED)
* ✅ **Model parameter sanitization** (2025-12-11) — Systematic parameter validation to prevent errors
* ✅ **Leakage detection improvements** (2025-12-11) — Critical confidence calculation fix, on-the-fly importance computation, enhanced diagnostics
* ✅ **Training routing & planning system** (2025-12-11) — Config-driven routing, automatic plan generation, 2-stage training pipeline
* ✅ **ResolvedConfig system & logging consistency** (2025-12-12) — Centralized configuration resolution, fixed purge/embargo calculation bug, consistent requested/effective value logging, fixed reproducibility tracker parameter errors

**Current Testing:**
* 🔄 **End-to-end testing underway** (2025-12-10) — Full pipeline validation from target ranking → feature selection → model training. Testing initiated after SST enforcement, Determinism system fixes, and complete F821 error elimination.
* 🔄 **Training Routing System** (2025-12-11) — **NEW - Currently being tested**: One-command pipeline (target ranking → feature selection → training plan → training), 2-stage training (CPU → GPU), automatic plan detection and filtering. See [Training Routing Guide](DOCS/02_reference/training_routing/README.md).
* Testing with multiple symbols and model families
* Validating data flow through complete pipeline
* Verifying model family status tracking output
* Validating 2-stage training order and resource usage

**Planned Investigation:**
* Feature engineering review and validation (temporal alignment, lag structure, leakage validation)
* Symbol-specific training execution integration (plan generated, execution pending)

**Planned Enhancements:**
* Symbol-specific training execution filtering (plan generated, needs pipeline integration)
* Model-family-level filtering per job (plan includes families, needs execution integration)
* Advanced routing logic enhancements (stability states, experimental lane, feature safety)
* Intelligent training orchestration improvements
* Smarter model/ensemble selection
* **Feature Engineering Revamp** — Thorough review and validation of:
  * Proper temporal alignment and lag structure
  * Leakage prevention and validation
  * Statistical significance and predictive power
  * Cross-sectional vs. time-series feature design
  * Integration with the feature registry and schema system
* Automated hyperparameter search
* Robust cross-sectional + time-series workflows
* Refactor trainers to use scaffolded base classes for centralized dimension-specific logic

**Outcome:** TRAINING pipeline operational with intelligent framework and training routing system. Phase 2 work substantially complete.

---

# Phase 2 — Centralized Configuration & UX Modernization ✅

**Status:** Substantially complete

**Completed:**
* ✅ YAML-based config schema (single source of truth) — 9+ training config files created
* ✅ Config loader with nested access and family-specific overrides
* ✅ Integration into all model trainers (preprocessing, callbacks, optimizers, safety guards)
* ✅ Pipeline, threading, memory, GPU, and system configs integrated
* ✅ Backward compatibility maintained with hardcoded defaults
* ✅ SST enforcement test — Automated test prevents accidental reintroduction of hardcoded hyperparameters
* ✅ Config parameter sanitization — Systematic validation to prevent parameter passing errors
* ✅ Config cleaner utility — Shared `config_cleaner.py` using `inspect.signature()` for validation

**In Progress:**
* Validation layer + example templates
* Unified logging + consistent output formatting
* Optional LLM-friendly structured logs
* Naming and terminology cleanup across modules

**Outcome:** Faster onboarding, easier enterprise deployment, more predictable behavior. Configuration system is production-ready.

---

# Phase 3 — Memory & Data Efficiency

**Status:** Planned

**Automated Memory Batching:**
* Fix current unstable behavior
* Add monitoring & adaptive batching
* Ensure clean memory reuse across model families

**Polars Cross-Sectional Optimization:**
* Streaming build operations
* Large-universe symbol handling
* Memory-efficient aggregation patterns

**Outcome:** Enables large-scale training without OOM failures.

---

# Phase 4 — Multi-GPU & NVLink Exploration (Future)

**Status:** Research phase

**NVLink Compatibility Research:**
* Explore NVLink support for multi-GPU training workflows
* Evaluate performance benefits for large model families (LSTM, Transformer, large MLPs)
* Test multi-GPU data parallelism patterns
* Benchmark NVLink vs PCIe bandwidth for model parameter synchronization
* Investigate framework support (TensorFlow, PyTorch, XGBoost multi-GPU)

**Multi-GPU Training Architecture:**
* Design multi-GPU training patterns for cross-sectional + sequential models
* Evaluate model parallelism vs data parallelism trade-offs
* Test gradient aggregation strategies across GPUs
* Memory-efficient multi-GPU batch distribution

**Outcome:** Foundation for scaling to multi-GPU systems when needed, with validated performance characteristics.

---

# Phase 5 — Model Integration Interfaces

**Status:** Planned

**Focus:** Standard interfaces for integrating trained models with external systems and applications. The system focuses on ML research infrastructure and model training.

---

# Phase 6 — Web Presence & Payments

**Status:** Planned

**Website + Stripe Checkout:**
* Public Fox ML Infrastructure homepage
* Pricing tiers + purchase flow
* "Request Access / Contact Sales" onboarding
* Hosted docs + system overview

**Outcome:** Enterprise-ready commercial experience.

---

# Phase 7 — Production Hardening

**Status:** Ongoing

**Tasks:**
* Full test coverage (expanding following SST + determinism changes)
* Monitoring & observability
* Deployment guides
* Disaster recovery patterns
* Performance tuning
* Comprehensive error handling and defensive programming

**Recent Progress:**
* ✅ Comprehensive error handling added to training routing system
* ✅ Defensive programming practices implemented
* ✅ Graceful degradation for missing/corrupted training plans
* ✅ Extensive input validation across all entry points

**Outcome:** Ready for institutional deployment.

---

# Phase 8 — High-Performance Rewrite Track (Long-Term)

**Status:** Research phase

**Low-Level Rewrites (C/C++/Rust):**
* Rewrite performance-critical paths
* HPC alignment + low-latency architecture (planned/WIP - single-node optimized currently)
* GPU-first and multi-GPU scaling

**Advanced Features:**
* Model ensemble architecture
* Multi-entity cross-sectional support
* Advanced inference and prediction engines
* Real-time analytics pipeline

**ROCm Support (Future):**
* AMD GPU backend
* TensorFlow/XGBoost/LightGBM support via ROCm
* Parity with CUDA workflows

**Outcome:** FoxML Core becomes an HPC-aligned, cross-platform ML stack. (Note: Currently single-node optimized; distributed HPC features are planned/WIP)

---

# Development Priorities

## Near-Term Focus

**Active development priorities — commercially leverageable work:**

1. **Training Routing System Testing & Validation** 🔄 — Complete end-to-end testing of routing system, validate 2-stage training pipeline, verify plan filtering behavior
2. **Symbol-Specific Training Execution** — Integrate symbol-specific job execution filtering (plan generated, needs pipeline integration)
3. **Model-Family-Level Filtering** — Use per-job model families from training plan in execution phase
4. **Configuration system validation & logging revamp** — Complete validation layer, unified logging, naming cleanup (mostly complete, validation in progress)
5. **Memory batching + Polars optimizations** — Fix unstable batching behavior, enable large-scale training without OOM
6. **Model integration interfaces** — Standard interfaces for integrating trained models with external systems
7. **Website + Stripe checkout** — Public homepage, pricing tiers, purchase flow, hosted docs

**Guideline:** These priorities build on the completed Phase 0–2 foundation and represent the next commercially-leverageable deltas. Focus remains on validation, polish, and strategic sequencing rather than new major subsystems.

## Longer-Term / R&D

**Research and future-track work — not blocking near-term goals:**

8. **GPU + ranking regression testing** — Ongoing validation and edge-case coverage
9. **Production readiness** — Full test coverage, monitoring, deployment guides, disaster recovery
10. **Exploratory modules** — Experimental features and research tracks
11. **NVLink & multi-GPU exploration** — Research phase, performance benchmarking, architecture design
12. **High-performance rewrite track** — Low-level rewrites (C/C++/Rust), HPC alignment (planned/WIP), ROCm support (planned)

**Guideline:** These items represent longer-horizon research and infrastructure work. They are valuable but not prerequisites for near-term commercial readiness.

---

# Vision

Fox ML Infrastructure is evolving into:
* A full-scale enterprise ML cross-sectional infrastructure stack
* Multi-strategy, multi-model, GPU-accelerated
* Well-documented, configurable, and production-grade
* A foundation for future HPC and cross-platform ML systems (single-node HPC currently implemented; distributed HPC planned/WIP)

This roadmap reflects the maturation of FoxML Core from a high-powered solo project into a **commercially viable, enterprise-class ML platform.**

**Development Approach:** Phases 0–2 (documentation, intelligent training, configuration) are complete or substantially complete. Development is ahead of schedule on infrastructure and documentation. Current focus is validation, polish, and strategic sequencing of next-phase work. Priorities emphasize commercially-leverageable improvements over exploratory research.

**Recent Milestones:**
* **2025-12-11**: Training Routing & Planning System added (currently being tested)
* **2025-12-11**: Reproducibility tracking with three-tier classification
* **2025-12-11**: Model parameter sanitization system
* **2025-12-10**: Complete SST enforcement and determinism system
* **2025-12-09**: Large file refactoring and modular architecture

---

# Known Issues & Bugs

## Critical / High Priority

### Training Routing System Integration
* **Status:** 🔄 In Progress (2025-12-11)
* **Issue:** Symbol-specific training execution filtering not fully integrated
  - Training plan generates symbol-specific jobs correctly
  - Execution phase does not yet filter by symbol from plan
  - **Workaround:** All symbols trained regardless of plan (functional but inefficient)
* **Issue:** Model-family-level filtering not fully integrated
  - Training plan includes per-job model families
  - Execution phase does not yet respect per-job family filters
  - **Workaround:** All model families trained for each job (functional but inefficient)
* **Issue:** Advanced routing logic partially implemented
  - Basic routing (cross-sectional vs symbol-specific) working
  - Advanced features (stability states, experimental lane limits) may need enhancement
  - **Workaround:** Use basic routing for now

### Memory Batching Instability
* **Status:** 🔄 Known Issue
* **Issue:** Memory batching behavior can be unstable under certain conditions
  - May cause OOM failures on large datasets
  - Adaptive batching not fully implemented
* **Workaround:** Reduce batch size in config, monitor memory usage
* **Planned Fix:** Phase 3 - Memory & Data Efficiency

### Polars Cross-Sectional Optimization
* **Status:** 🔄 Known Limitation
* **Issue:** Large-universe symbol handling may be inefficient
  - Streaming build operations not fully optimized
  - Memory-efficient aggregation patterns need improvement
* **Workaround:** Process smaller symbol sets, use data limits in config
* **Planned Fix:** Phase 3 - Memory & Data Efficiency

## Medium Priority

### TensorFlow GPU Warnings
* **Status:** ⚠️ Non-Critical (Environment-Specific)
* **Issue:** Some TensorFlow warnings may appear during training
  - Version compatibility warnings (`use_unbounded_threadpool`) — Harmless version mismatch
  - Plugin registration warnings (cuFFT, cuDNN, cuBLAS) — Expected when TensorFlow initializes CUDA plugins multiple times
* **Impact:** Warnings only, functionality not affected
* **Status:** TensorFlow GPU support is functional. Warnings are being investigated and may be computer-specific.

### Feature Engineering Validation
* **Status:** 🔄 Planned Investigation
* **Issue:** Feature engineering review and validation needed
  - Temporal alignment and lag structure need validation
  - Leakage prevention in feature engineering needs review
  - Statistical significance and predictive power assessment needed
* **Planned Fix:** Phase 1 - Planned Investigation

### Test Coverage
* **Status:** 🔄 In Progress
* **Issue:** Full test coverage expanding following SST + determinism changes
  - Some edge cases may not be fully covered
  - Integration tests need expansion
* **Planned Fix:** Phase 7 - Production Hardening

## Low Priority / Environment Notes

### Module Status
* **Focus:** Training and ranking are stable and under ongoing validation
* **Current Active Work:** Training routing system testing, configuration validation, memory/polars optimization, model integration interfaces

### Configuration Validation
* **Status:** 🔄 In Progress
* **Issue:** Validation layer and example templates in progress
  - Config validation not fully complete
  - Some invalid configs may not be caught early
* **Workaround:** Follow config examples in documentation, validate manually

### Logging & Output Formatting
* **Status:** 🔄 In Progress
* **Issue:** Unified logging and consistent output formatting in progress
  - Log formats may vary between modules
  - Output formatting not fully standardized
* **Workaround:** Use structured logging config where available

## Reporting Issues

Report bugs or issues via:
* GitHub Issues (if available)
* Email: **jenn.lewis5789@gmail.com**
* Include: Error messages, config files (redacted), steps to reproduce, environment details

## See Also

* [Known Issues Documentation](DOCS/03_technical/fixes/KNOWN_ISSUES.md) - Detailed known issues
* [Bug Fixes History](DOCS/03_technical/fixes/BUG_FIXES.md) - Fix history
* [Testing Plan](DOCS/03_technical/testing/TESTING_PLAN.md) - Testing procedures
