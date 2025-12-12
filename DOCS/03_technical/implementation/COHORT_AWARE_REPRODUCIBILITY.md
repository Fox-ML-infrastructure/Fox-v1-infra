# Cohort-Aware Reproducibility Tracking

## Overview

The reproducibility system tracks run results and compares them to previous runs. However, **raw metric comparisons across different sample sizes are statistically meaningless**. This document describes a **cohort-aware** reproducibility system that:

1. **Organizes runs by cohort** (sample size, symbols, date range, config)
2. **Only compares runs within the same cohort**
3. **Uses sample-adjusted statistical tests** for drift detection
4. **Provides clear INCOMPARABLE labels** when cohorts differ

## Problem Statement

### Current System Limitations

The current `ReproducibilityTracker` compares runs by `stage:item_name` (e.g., `target_ranking:y_will_peak_60m_0.8`), but it doesn't account for:

- **Sample size differences**: Comparing AUC from 50k samples vs 10k samples is meaningless
- **Symbol universe changes**: Different symbols → different data distribution
- **Date range shifts**: Different time periods → different market regimes
- **Config changes**: Different `min_cs`, `max_cs_samples`, leakage filters → different cohorts

### Why This Matters

**Statistical variance scales with 1/N**:
- AUC variance ≈ `AUC * (1 - AUC) / N_effective`
- If N shrinks by 5× (50k → 10k), standard deviation grows by √5 ≈ 2.24×
- Same absolute ΔAUC becomes **less statistically meaningful** at smaller N

**Example of the problem**:
```text
Run 1: AUC=0.742, N=51,889 (10 symbols, 2023-01-01→2023-06-30)
Run 2: AUC=0.739, N=10,802 (5 symbols, 2024-01-01→2024-03-31)
ΔAUC = -0.003 → "DRIFTING" ❌ WRONG - these are different cohorts!
```

## Solution Architecture

### 1. Cohort Definition

A **cohort** is defined by:

```python
{
    "N_effective_cs": int,        # Number of rows in final training set
    "n_symbols": int,              # Number of unique symbols
    "symbols": List[str],          # Actual symbol list (sorted, deduplicated) - NEW!
    "date_range": {                # Time coverage
        "start_ts": str,           # ISO timestamp
        "end_ts": str
    },
    "cs_config_hash": str,         # Hash of cross-sectional config
    # Config includes: min_cs, max_cs_samples, leakage_filter_version, universe_id
}
```

**Cohort ID** = hash of `(N_effective_cs, n_symbols, date_range, cs_config_hash)`

### 2. Storage Structure

```
reproducibility/
  comparisons/                     # Main comparison directory
    {target_name}/
      {model_family}/
        cohorts/                  # Organized by cohort
          {cohort_id}/
            runs/                 # All runs for this cohort
              {run_id}.json
            latest.json           # Symlink to most recent run
            summary.json          # Cohort-level summary
        index.json                # Maps cohort_id → cohort metadata
```

**Example**:
```
reproducibility/
  comparisons/
    y_will_peak_60m_0.8/
      lightgbm_cs/
        cohorts/
          abc123def456/           # Cohort: N=52k, 10 symbols, 2023-01→2023-06
            runs/
              20251211_143022.json
              20251212_091545.json
            latest.json → runs/20251212_091545.json
            summary.json
          xyz789uvw012/           # Cohort: N=11k, 5 symbols, 2024-01→2024-03
            runs/
              20250115_120000.json
            latest.json → runs/20250115_120000.json
            summary.json
        index.json
```

### 3. Comparison Logic

**Before comparing runs**:

1. **Extract cohort metadata** from current run
2. **Find matching cohort** in storage (by cohort_id)
3. **If no match** → mark as `INCOMPARABLE (new cohort)`, save to new cohort directory
4. **If match found** → proceed with sample-adjusted comparison

**Sample-adjusted comparison**:

1. **Variance estimation**:
   ```python
   var_prev = auc_prev * (1 - auc_prev) / N_prev
   var_curr = auc_curr * (1 - auc_curr) / N_curr
   ```

2. **Z-score calculation**:
   ```python
   delta = auc_curr - auc_prev
   sigma = sqrt(var_prev + var_curr)
   z = delta / sigma
   ```

3. **Classification**:
   - `|z| < 1` → **STABLE (sample-adjusted)**
   - `1 ≤ |z| < 2` → **BORDERLINE (sample-adjusted)**
   - `|z| ≥ 2` → **DRIFTING (sample-adjusted)**

### 4. Reporting Categories

1. **INCOMPARABLE (N mismatch)**
   ```
   N_prev=52,000, N_curr=10,800 (n_ratio=0.21)
   Sample sizes diverged; skipping drift comparison.
   ```

2. **INCOMPARABLE (new cohort)**
   ```
   No previous cohort found for N=10,800, symbols=5, date_range=2024-01-01→2024-03-31
   Saving as new cohort baseline.
   ```

3. **DRIFTING (sample-adjusted)**
   ```
   ΔAUC = -0.012, z = -2.4 → statistically significant degradation
   ```

4. **STABLE (sample-adjusted)**
   ```
   ΔAUC = +0.001, z = +0.3 → within noise
   ```

## Implementation Plan

### Phase 1: Cohort Metadata Extraction

**Location**: `TRAINING/utils/reproducibility_tracker.py`

**New method**: `_extract_cohort_metadata(metrics, additional_data) -> Dict`

Extract from:
- `metrics`: `N_effective_cs`, `n_symbols`
- `additional_data`: `date_range`, `cs_config` (min_cs, max_cs_samples, etc.)

**Hash function**: `_compute_cohort_id(metadata) -> str`

### Phase 2: Cohort-Aware Storage

**New class**: `CohortAwareReproducibilityTracker(ReproducibilityTracker)`

**Storage methods**:
- `_get_cohort_dir(cohort_id) -> Path`
- `_save_to_cohort(cohort_id, run_data) -> None`
- `_load_cohort_runs(cohort_id) -> List[Dict]`
- `_find_matching_cohort(metadata) -> Optional[str]`

### Phase 3: Sample-Adjusted Comparison

**New method**: `_compare_within_cohort(prev_run, curr_run) -> Dict`

- Compute sample-adjusted z-scores
- Return classification + statistics

### Phase 4: Integration Points

**Update call sites** to pass cohort metadata:

1. **Target ranking** (`TRAINING/ranking/predictability/model_evaluation.py`)
   - Extract: N from training data, symbols from config, date_range from data

2. **Feature selection** (`TRAINING/ranking/feature_selector.py`)
   - Extract: N from CS data, symbols from input, date_range from data

3. **Model training** (`TRAINING/training_strategies/training.py`)
   - Extract: N from training data, symbols from mtf_data, date_range from data

## Migration Strategy

### Backward Compatibility

1. **Legacy runs** (no cohort metadata):
   - Attempt to infer cohort from existing metadata
   - If impossible → mark as `INCOMPARABLE (legacy)`
   - Store in `cohorts/legacy/` directory

2. **Gradual rollout**:
   - Phase 1: Extract and log cohort metadata (no storage change)
   - Phase 2: Store in new structure (parallel to old)
   - Phase 3: Migrate old runs, deprecate old structure

### Configuration

Add to `CONFIG/training_config/safety_config.yaml`:

```yaml
safety:
  reproducibility:
    cohort_aware: true
    n_ratio_threshold: 0.90  # Min ratio for comparability
    cohort_config_keys:      # Keys to include in cohort hash
      - min_cs
      - max_cs_samples
      - leakage_filter_version
      - universe_id
```

## Benefits

1. **Statistically meaningful comparisons**: Only compare apples to apples
2. **Clear INCOMPARABLE labels**: Explicit when cohorts differ
3. **Sample-adjusted drift**: Z-scores account for N differences
4. **Auditable structure**: Cohort organization makes it easy to find related runs
5. **Defensible logs**: Can explain why comparisons are valid/invalid

## Example Output

```
[REPROD] target=y_will_peak_60m_0.8, model=lightgbm_cs
  Cohort: N=51,889, symbols=10, date_range=2023-01-01→2023-06-30
  prev: AUC=0.7421±0.029, N=51,889
  curr: AUC=0.7440±0.029, N=52,105
  ΔAUC=+0.0019, z=0.62 → STABLE (sample-adjusted)
```

or

```
[REPROD] target=y_will_peak_60m_0.8, model=lightgbm_cs
  prev: AUC=0.7421, N=51,889 (cohort: abc123)
  curr: AUC=0.7390, N=10,802 (cohort: xyz789)
  n_ratio=0.21 → INCOMPARABLE (N mismatch, skipping drift)
```

## Next Steps

1. **Design review**: Validate cohort definition and storage structure
2. **Implementation**: Start with Phase 1 (metadata extraction)
3. **Testing**: Unit tests for cohort matching, z-score calculation
4. **Integration**: Update call sites to pass cohort metadata
5. **Migration**: Migrate existing runs to new structure
