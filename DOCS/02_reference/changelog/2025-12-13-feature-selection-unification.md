# Changelog — 2025-12-13 (Feature Selection Unification)

**Feature Selection Now Uses Same Harness, Config System, and Comprehensive Functionality as Target Ranking**

For a quick overview, see the [root changelog](../../../CHANGELOG.md).  
For other dates, see the [changelog index](README.md).

---

## Added

### Shared Ranking Harness

**Unified Evaluation Contract for Target Ranking and Feature Selection**
- **Enhancement**: Created `RankingHarness` class that both target ranking and feature selection now use
- **Purpose**: Ensures identical evaluation contracts to prevent "in-sample-ish" mistakes from scaling
- **Features**:
  - Same split generator (PurgedTimeSeriesSplit with time-based purging)
  - Same scoring function + metric normalization
  - Same leakage-safe imputation policy
  - Same RunContext + reproducibility tracker payload
  - Same logging/artifact writer
- **Implementation**:
  - `TRAINING/ranking/shared_ranking_harness.py` - New shared harness class
  - `TRAINING/ranking/feature_selector.py` - Refactored to use shared harness
  - `TRAINING/ranking/predictability/model_evaluation.py` - Uses same harness methods
- **Benefits**:
  - ✅ Identical evaluation contracts (no divergence between target ranking and feature selection)
  - ✅ Same stability snapshot machinery (overlap, Kendall tau)
  - ✅ Same sanitization + dtype canonicalization (prevents CatBoost object column errors)
  - ✅ Same cleaning and audit checks (ghost busters, leak scan, target validation)

### Feature Selection Comprehensive Hardening

**Feature Selection Now Has Complete Parity with Target Ranking**
- **Enhancement**: Feature selection now includes all the same comprehensive checks and functionality as target ranking
- **Added Functionality**:
  - **Linear Models**: Lasso, Ridge, and ElasticNet now enabled in feature selection (same as target ranking)
  - **Ghost Busters**: Final gatekeeper enforcement (drops problematic features before training)
  - **Pre-training Leak Scan**: Detects near-copy features that are highly correlated with target
  - **Target-Conditional Exclusions**: Per-target exclusion lists tailored to target physics
  - **Duplicate Column Detection**: Hard-fails on duplicate feature names
  - **Target Validation**: Checks for degenerate targets and class imbalance
  - **Stability Tracking**: Per-model snapshots + aggregated consensus snapshots
  - **Leak Detection Summary**: Saves `leak_detection_summary.txt` (same format as target ranking)
  - **Stability Analysis Hook**: Calls `analyze_all_stability_hook()` at end of run
- **Files**:
  - `TRAINING/ranking/shared_ranking_harness.py` - Centralized cleaning and audit checks
  - `TRAINING/ranking/feature_selector.py` - Integrated shared harness for both CROSS_SECTIONAL and SYMBOL_SPECIFIC views
  - `CONFIG/ranking/features/multi_model.yaml` - Enabled Ridge and ElasticNet (Lasso was already enabled)
- **Benefits**:
  - ✅ Feature selection is now as hardened as target ranking
  - ✅ Same comprehensive safety checks prevent data leakage
  - ✅ Same stability tracking enables reproducibility analysis
  - ✅ Same leak detection enables proactive feature review

### Feature Selection Reporting Module

**Same Output Structure as Target Ranking**
- **Enhancement**: Created `feature_selection_reporting.py` module that saves results in same format as target ranking
- **Features**:
  - `save_feature_selection_rankings()` - Saves CSV and YAML files (same format as target ranking)
  - `save_dual_view_feature_selections()` - Saves dual-view structure in REPRODUCIBILITY/FEATURE_SELECTION/
  - `save_feature_importances_for_reproducibility()` - Saves feature importances (same structure as target ranking)
- **Output Structure**:
  ```
  RESULTS/{run_id}/
    feature_selections/
      {target_column}/
        feature_selection_rankings.csv          # Same format as target ranking
        feature_selection_rankings.yaml         # Same format as target ranking
        selected_features.txt                   # Same as target ranking
        feature_importance_multi_model.csv     # Detailed multi-model summary
        feature_importances/                    # Same structure as target ranking
          {target_column}/
            CROSS_SECTIONAL/
              {model_family}_importances.csv
            SYMBOL_SPECIFIC/
              {symbol}/
                {model_family}_importances.csv
        feature_exclusions/                     # Target-conditional exclusions
          {target_name}_exclusions.yaml
    REPRODUCIBILITY/
      FEATURE_SELECTION/                        # Same structure as TARGET_RANKING
        CROSS_SECTIONAL/
          {target_column}/
            cohort={cohort_id}/
              metrics.json
              metadata.json
        SYMBOL_SPECIFIC/
          {target_column}/
            symbol={symbol}/
              cohort={cohort_id}/
                metrics.json
                metadata.json
  ```
- **Files**:
  - `TRAINING/ranking/feature_selection_reporting.py` - New reporting module
  - `TRAINING/ranking/feature_selector.py` - Integrated reporting functions
- **Benefits**:
  - ✅ Consistent output structure across target ranking and feature selection
  - ✅ Same artifacts enable easy comparison and analysis
  - ✅ Same reproducibility structure enables cohort tracking

## Changed

### Feature Selection Config Integration

**Same Config-Driven Setup as Target Ranking**
- **Enhancement**: Feature selection now uses same config hierarchy and loading methods as target ranking
- **Config System**:
  - Uses `get_cfg()` from `CONFIG.config_loader` (same as target ranking)
  - Uses `get_safety_config()` for safety thresholds (same as target ranking)
  - Uses `create_resolved_config()` for purge/embargo derivation (same as target ranking)
  - Accepts `experiment_config` parameter (same as target ranking)
  - Uses same config paths: `pipeline_config`, `safety_config`, `preprocessing_config`
- **Safety Configs**:
  - `MIN_FEATURES_REQUIRED` (from `safety.leakage_detection.ranking.min_features_required`)
  - `MIN_FEATURES_AFTER_LEAK_REMOVAL` (from `safety.leakage_detection.ranking.min_features_after_leak_removal`)
  - `MIN_FEATURES_FOR_MODEL` (from `safety.leakage_detection.ranking.min_features_for_model`)
  - `default_purge_minutes` (from `safety.temporal.default_purge_minutes`)
- **Files**:
  - `TRAINING/ranking/shared_ranking_harness.py` - Uses same config loading methods
  - `TRAINING/ranking/feature_selector.py` - Loads configs same way as target ranking
- **Benefits**:
  - ✅ Single source of truth for all safety thresholds
  - ✅ Consistent config-driven behavior across ranking and selection
  - ✅ Easy to maintain and update safety rules

### Feature Selection Dual-View Support

**Maintains Cross-Sectional and Symbol-Specific Views**
- **Enhancement**: Feature selection now properly supports both CROSS_SECTIONAL and SYMBOL_SPECIFIC views using shared harness
- **Implementation**:
  - CROSS_SECTIONAL: Single harness instance for all symbols (pooled data)
  - SYMBOL_SPECIFIC: Loop through symbols, create harness instance per symbol
  - Both views use same harness methods (build_panel, split_policy, run_importance_producers)
- **Files**:
  - `TRAINING/ranking/feature_selector.py` - Refactored to use shared harness for both views
- **Benefits**:
  - ✅ View consistency: Target ranking → feature selection → training uses same view
  - ✅ Same evaluation contract regardless of view
  - ✅ Proper per-symbol processing for SYMBOL_SPECIFIC view

## Fixed

### Feature Selection Stability Tracking

**Per-Model Snapshots Now Saved**
- **Issue**: Feature selection was only saving aggregated consensus snapshots, not per-model snapshots
- **Fix**: Now saves stability snapshots for each model family (LightGBM, XGBoost, Random Forest, etc.) after training
- **Implementation**:
  - CROSS_SECTIONAL: Saves snapshots with `universe_id="CROSS_SECTIONAL"`
  - SYMBOL_SPECIFIC: Saves snapshots with `universe_id=symbol_name` (per symbol)
- **Files**:
  - `TRAINING/ranking/feature_selector.py` - Added per-model snapshot saving
- **Benefits**:
  - ✅ Same stability tracking as target ranking
  - ✅ Can analyze stability per model family
  - ✅ Enables comprehensive stability analysis

### Feature Selection Leak Detection

**Leak Detection Summary Now Saved**
- **Issue**: Feature selection detected suspicious features but didn't save summary report
- **Fix**: Now saves `leak_detection_summary.txt` in same format as target ranking
- **Implementation**:
  - Collects suspicious features from all model families and symbols
  - Saves summary with recommendations (same format as target ranking)
- **Files**:
  - `TRAINING/ranking/feature_selector.py` - Added leak detection summary saving
- **Benefits**:
  - ✅ Easy to review suspicious features across all models
  - ✅ Same format enables comparison with target ranking results
  - ✅ Proactive leak detection and review

## Documentation

### Updated Feature Selection Documentation

- **TRAINING/ranking/feature_selection_reporting.py** - New module with comprehensive docstrings
- **TRAINING/ranking/shared_ranking_harness.py** - Comprehensive docstrings explaining shared contract
- **DOCS/02_reference/changelog/2025-12-13-feature-selection-unification.md** - This changelog

### Updated Target Ranking Documentation

- **DOCS/02_reference/target_ranking/README.md** - Updated to mention shared harness and feature selection integration

## Testing

### Verification

To verify feature selection uses same harness:
1. Run feature selection - should see "Using shared ranking harness" in logs
2. Check output structure - should match target ranking structure
3. Verify stability snapshots - should see per-model snapshots in `artifacts/feature_importance/`
4. Check leak detection summary - should see `leak_detection_summary.txt` in output directory

To verify config system:
1. Set safety thresholds in `safety_config.yaml`
2. Run feature selection - should use same thresholds as target ranking
3. Check logs - should show config trace with same config paths

## Migration Notes

### For Users

- **No action required** - Feature selection automatically uses shared harness
- **Recommended**: Review feature selection output structure - now matches target ranking
- **New**: Feature selection now saves stability snapshots and leak detection summaries

### For Developers

- **Shared harness**: Use `RankingHarness` class for any new ranking operations
- **Config system**: Use same config loading methods (`get_cfg()`, `get_safety_config()`)
- **Reporting**: Use `feature_selection_reporting.py` module for consistent output format

## Files Modified

### Core Ranking System
- `TRAINING/ranking/shared_ranking_harness.py` - New shared harness class
- `TRAINING/ranking/feature_selector.py` - Refactored to use shared harness
- `TRAINING/ranking/feature_selection_reporting.py` - New reporting module
- `CONFIG/ranking/features/multi_model.yaml` - Enabled Ridge and ElasticNet

### Documentation
- `DOCS/02_reference/changelog/2025-12-13-feature-selection-unification.md` - This changelog
- `DOCS/02_reference/target_ranking/README.md` - Updated integration section
