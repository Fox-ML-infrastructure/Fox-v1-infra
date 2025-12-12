# Reproducibility API Reference

## Overview

The reproducibility tracking system provides a clean API for recording and comparing runs across pipeline stages. It automatically organizes runs by cohort and only compares runs within the same cohort.

## Core Concepts

### Stages

Use the `Stage` enum for pipeline stages:

```python
from TRAINING.utils.reproducibility_tracker import Stage, RouteType

Stage.TARGET_RANKING
Stage.FEATURE_SELECTION
Stage.TRAINING
Stage.PLANNING
```

### Route Types

Use the `RouteType` enum for cross-sectional vs individual:

```python
RouteType.CROSS_SECTIONAL
RouteType.INDIVIDUAL
```

## Basic Usage

### Recording a Run

```python
from pathlib import Path
from TRAINING.utils.reproducibility_tracker import ReproducibilityTracker, Stage, RouteType

tracker = ReproducibilityTracker(output_dir=Path("results"))

tracker.log_comparison(
    stage=Stage.FEATURE_SELECTION,  # or "feature_selection" (string also works)
    item_name="y_will_peak_60m_0.8",
    metrics={
        "metric_name": "Consensus Score",
        "mean_score": 0.751,
        "std_score": 0.029,
        "mean_importance": 0.23,
        "composite_score": 0.764,
        "N_effective_cs": 52011  # Required for cohort-aware tracking
    },
    additional_data={
        "route_type": RouteType.CROSS_SECTIONAL,  # or "CROSS_SECTIONAL"
        "n_symbols": 10,
        "date_range": {
            "start_ts": "2023-01-01T00:00:00Z",
            "end_ts": "2023-06-30T23:59:59Z"
        },
        "cs_config": {
            "min_cs": 3,
            "max_cs_samples": 100000,
            "universe_id": "universeA",
            "leakage_filter_version": "v1.2.0"
        }
    }
)
```

### For INDIVIDUAL Mode

```python
tracker.log_comparison(
    stage=Stage.FEATURE_SELECTION,
    item_name="y_will_peak_60m_0.8",
    metrics={...},
    additional_data={
        "route_type": RouteType.INDIVIDUAL,
        "symbol": "AAPL",  # Required for INDIVIDUAL
        "n_symbols": 1,
        ...
    }
)
```

### For TRAINING

```python
tracker.log_comparison(
    stage=Stage.TRAINING,
    item_name="y_will_peak_60m_0.8",
    metrics={...},
    additional_data={
        "route_type": RouteType.CROSS_SECTIONAL,
        "model_family": "lightgbm",  # Required for TRAINING
        ...
    }
)
```

## Finding Previous Runs

### Get Last Comparable Run

```python
prev = tracker.get_last_comparable_run(
    stage=Stage.FEATURE_SELECTION,
    item_name="y_will_peak_60m_0.8",
    route_type=RouteType.CROSS_SECTIONAL,
    symbol=None,
    model_family=None,
    cohort_id="cs_2023Q1_universeA_min_cs3_v1_a1b2c3d4",  # Optional: if already computed
    current_N=52011,  # For N ratio check
    n_ratio_threshold=0.90  # Optional: override default
)

if prev:
    print(f"Previous AUC: {prev.get('mean_score')}")
    print(f"Previous N: {prev.get('N_effective')}")
else:
    print("No comparable previous run found")
```

**Key behavior**: This function:
1. Only looks for runs with the **same cohort_id** (if provided)
2. Applies N ratio filter (if `current_N` provided)
3. Returns `None` if no comparable run found

## File Structure

After calling `log_comparison`, files are created at:

```
REPRODUCIBILITY/
  {STAGE}/
    {MODE}/  (for FEATURE_SELECTION, TRAINING)
      {target}/
        {symbol}/  (for INDIVIDUAL)
          {model_family}/  (for TRAINING)
            cohort={cohort_id}/
              metadata.json
              metrics.json
              drift.json
```

### metadata.json

```json
{
  "schema_version": 1,
  "cohort_id": "cs_2023Q1_universeA_min_cs3_v1_a1b2c3d4",
  "run_id": "20251211T143015_lightgbm_cs_fs",
  "stage": "FEATURE_SELECTION",
  "route_type": "CROSS_SECTIONAL",
  "target": "y_will_peak_60m_0.8",
  "symbol": null,
  "model_family": null,
  "N_effective": 52011,
  "n_symbols": 10,
  "date_start": "2023-01-01T00:00:00Z",
  "date_end": "2023-06-30T23:59:59Z",
  "universe_id": "universeA",
  "min_cs": 3,
  "max_cs_samples": 100000,
  "leakage_filter_version": "v1.2.0",
  "cs_config_hash": "c8f4a7b2",
  "seed": 123,
  "git_commit": "479b075",
  "created_at": "2025-12-11T14:30:15.123456"
}
```

### metrics.json

```json
{
  "run_id": "20251211T143015_lightgbm_cs_fs",
  "timestamp": "2025-12-11T14:30:15.123456",
  "mean_score": 0.751,
  "std_score": 0.029,
  "mean_importance": 0.23,
  "composite_score": 0.764,
  "metric_name": "Consensus Score"
}
```

### drift.json

```json
{
  "schema_version": 1,
  "stage": "FEATURE_SELECTION",
  "route_type": "CROSS_SECTIONAL",
  "target": "y_will_peak_60m_0.8",
  "symbol": null,
  "model_family": null,
  "current": {
    "run_id": "20251211T143015_lightgbm_cs_fs",
    "cohort_id": "cs_2023Q1_universeA_min_cs3_v1_a1b2c3d4",
    "N_effective": 52011,
    "auc": 0.7511
  },
  "previous": {
    "run_id": "20251209T221030_lightgbm_cs_fs",
    "cohort_id": "cs_2023Q1_universeA_min_cs3_v1_a1b2c3d4",
    "N_effective": 51890,
    "auc": 0.7498
  },
  "delta_auc": 0.0013,
  "abs_diff": 0.0013,
  "rel_diff": 0.17,
  "z_score": 0.62,
  "status": "STABLE_SAMPLE_ADJUSTED",
  "reason": "n_ratio=0.997, |z|=0.62 → stable",
  "n_ratio": 0.997,
  "sample_adjusted": true,
  "created_at": "2025-12-11T14:30:15.123456"
}
```

**Status values**:
- `STABLE_SAMPLE_ADJUSTED`: Within noise (|z| < 1.0)
- `DRIFTING_SAMPLE_ADJUSTED`: Small but noticeable (1.0 ≤ |z| < 2.0)
- `DIVERGED_SAMPLE_ADJUSTED`: Significant change (|z| ≥ 2.0)
- `INCOMPARABLE`: Different cohorts (n_ratio < threshold)

## Index Table

The global `index.parquet` file contains:

| phase | mode | target | symbol | model_family | cohort_id | run_id | N_effective | auc | date | created_at | path |
|-------|------|--------|--------|--------------|-----------|--------|-------------|-----|------|------------|------|
| FEATURE_SELECTION | CROSS_SECTIONAL | y_will_peak_60m_0.8 | null | null | cs_2023Q1_... | 20251211_... | 52011 | 0.751 | 2023-01-01 | 2025-12-11T... | FEATURE_SELECTION/CROSS_SECTIONAL/... |

Used internally by `get_last_comparable_run()` to find previous runs.

## Important Guarantees

### Same-Cohort Only

**The system only compares runs within the same cohort.**

This is enforced by:
1. `cohort_id` in the directory path: `cohort={cohort_id}/`
2. `get_last_comparable_run()` filters by `cohort_id` when provided
3. `log_comparison()` computes `cohort_id` from metadata and only looks for previous runs with the same `cohort_id`

### Sample-Aware Comparisons

Within the same cohort, comparisons use sample-adjusted z-scores:
- Variance: `var ≈ AUC * (1 - AUC) / N`
- Z-score: `z = |ΔAUC| / sqrt(var_prev + var_curr)`
- Classification based on |z| thresholds

### N Ratio Check

Even within the same cohort, if N_effective differs significantly (n_ratio < 0.90), the run is marked as `INCOMPARABLE` in `drift.json`.

## Migration from Legacy

The system is backward compatible:
- String stage names still work (e.g., `"feature_selection"`)
- If cohort metadata is not provided, falls back to legacy flat structure
- Existing runs continue to work

## Best Practices

1. **Always provide cohort metadata** for new runs:
   - `N_effective_cs` in metrics
   - `route_type`, `n_symbols`, `date_range`, `cs_config` in additional_data

2. **Use enums** to avoid typos:
   ```python
   stage=Stage.FEATURE_SELECTION  # ✅
   stage="feature_selection"      # ✅ (but less safe)
   stage="FEATURE_SELECTION"       # ✅ (normalized)
   stage="fs"                      # ❌ (won't match)
   ```

3. **Check drift.json** after runs to understand reproducibility status

4. **Use get_last_comparable_run()** for programmatic access to previous runs
