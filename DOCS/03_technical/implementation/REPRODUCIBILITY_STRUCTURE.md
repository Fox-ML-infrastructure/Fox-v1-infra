# Reproducibility Directory Structure

## Overview

The reproducibility system uses a structured directory layout that organizes runs by **phase**, **mode**, **target**, **symbol/model_family** (where applicable), and **cohort**.

## Top-Level Structure

```
REPRODUCIBILITY/
  TARGET_RANKING/
  FEATURE_SELECTION/
  TRAINING/
  PLANNING/
  index.parquet  # Global index for fast lookups
```

## Phase-Specific Layouts

### 1. TARGET_RANKING

```
REPRODUCIBILITY/
  TARGET_RANKING/
    y_will_peak_60m_0.8/
      cohort=cs_2023Q1_universeA_min_cs3_v1_a1b2c3d4/
        metadata.json
        metrics.json
        drift.json
```

### 2. FEATURE_SELECTION

Split by **CROSS_SECTIONAL** vs **INDIVIDUAL**:

```
REPRODUCIBILITY/
  FEATURE_SELECTION/
    CROSS_SECTIONAL/
      y_will_peak_60m_0.8/
        cohort=cs_2023Q1_universeA_min_cs3_v1_a1b2c3d4/
          metadata.json
          metrics.json
          drift.json
          feature_importances.parquet  # (optional artifact)
    INDIVIDUAL/
      y_will_peak_60m_0.8/
        symbol=AAPL/
          cohort=in_2023Q1_universeA_v1_e5f6g7h8/
            metadata.json
            metrics.json
            drift.json
            feature_importances.parquet
        symbol=MSFT/
          cohort=in_2023Q1_universeA_v1_e5f6g7h8/
            ...
```

### 3. TRAINING

Split by **CROSS_SECTIONAL** vs **INDIVIDUAL**, then by **model_family**:

```
REPRODUCIBILITY/
  TRAINING/
    CROSS_SECTIONAL/
      y_will_peak_60m_0.8/
        model_family=lightgbm/
          cohort=cs_2023Q1_universeA_min_cs3_v1_a1b2c3d4/
            metadata.json
            metrics.json
            drift.json
            model_hash.txt
    INDIVIDUAL/
      y_will_peak_60m_0.8/
        symbol=AAPL/
          model_family=lightgbm/
            cohort=in_2023Q1_universeA_v1_e5f6g7h8/
              metadata.json
              metrics.json
              drift.json
              model_hash.txt
```

### 4. PLANNING

```
REPRODUCIBILITY/
  PLANNING/
    TRAINING_PLAN/
      y_will_peak_60m_0.8/
        cohort=cs_2023Q1_universeA_min_cs3_v1_a1b2c3d4/
          metadata.json
          plan.json
          drift.json
```

## Cohort ID Format

Cohort IDs are **readable** and include:
- Mode prefix: `cs_` (cross-sectional) or `in_` (individual)
- Date range: `2023Q1` (year + quarter)
- Universe: `universeA`
- Config: `min_cs3`, `max100000` (if non-default)
- Version: `v1` (leakage filter version)
- Hash: `a1b2c3d4` (8-char hash for uniqueness)

**Example**: `cs_2023Q1_universeA_min_cs3_v1_a1b2c3d4`

## File Contents

### metadata.json

Full cohort metadata for reproducibility:

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
  "symbols": ["AAPL", "AMZN", "GOOGL", "MSFT", "NVDA", "TSLA", "META", "NFLX", "AMD", "INTC"],  // NEW
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

Run-specific metrics:

```json
{
  "run_id": "20251211T143015_lightgbm_cs_fs",
  "timestamp": "2025-12-11T14:30:15.123456",
  "mean_score": 0.751,
  "std_score": 0.029,
  "mean_importance": 0.23,
  "composite_score": 0.764,
  "metric_name": "ROC-AUC"
}
```

### drift.json

Comparison to previous run:

```json
{
  "status": "STABLE",
  "delta_auc": 0.0019,
  "abs_diff": 0.0019,
  "rel_diff": 0.25,
  "z_score": 0.62,
  "n_prev": 51889,
  "n_curr": 52105,
  "n_ratio": 0.996,
  "sample_adjusted": true,
  "prev_auc": 0.7421,
  "curr_auc": 0.7440,
  "timestamp": "2025-12-11T14:30:15.123456"
}
```

**Status values**:
- `STABLE`: Within noise (z < 1.0)
- `DRIFTING`: Small but noticeable (1.0 ≤ z < 2.0)
- `DIVERGED`: Significant change (z ≥ 2.0)
- `INCOMPARABLE`: Different cohorts (n_ratio < 0.90)

## Index Table (index.parquet)

Global index for fast lookups:

| phase | mode | target | symbol | model_family | cohort_id | run_id | N_effective | auc | date | path |
|-------|------|--------|--------|--------------|-----------|--------|-------------|-----|------|------|
| FEATURE_SELECTION | CROSS_SECTIONAL | y_will_peak_60m_0.8 | null | null | cs_2023Q1_... | 20251211_... | 52011 | 0.751 | 2023-01-01 | FEATURE_SELECTION/CROSS_SECTIONAL/y_will_peak_60m_0.8/cohort=... |

Used by the reproducibility engine to:
1. Find previous runs with same `(phase, mode, target, symbol, model_family, cohort_id)`
2. Load metrics for comparison
3. Compute drift.json

## Usage

### Automatic (Recommended)

The system automatically uses this structure when cohort metadata is provided:

```python
tracker.log_comparison(
    stage="feature_selection",
    item_name="y_will_peak_60m_0.8",
    metrics={
        "mean_score": 0.751,
        "std_score": 0.029,
        "N_effective_cs": 52011
    },
    additional_data={
        "route_type": "CROSS_SECTIONAL",  # or "INDIVIDUAL"
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
    stage="feature_selection",
    item_name="y_will_peak_60m_0.8",
    metrics={...},
    additional_data={
        "route_type": "INDIVIDUAL",
        "symbol": "AAPL",  # Required for INDIVIDUAL
        ...
    }
)
```

### For TRAINING

```python
tracker.log_comparison(
    stage="model_training",  # or "training"
    item_name="y_will_peak_60m_0.8",
    metrics={...},
    additional_data={
        "route_type": "CROSS_SECTIONAL",
        "model_family": "lightgbm",  # Required for TRAINING
        ...
    }
)
```

## Benefits

1. **Clear organization**: Easy to navigate by phase → mode → target → symbol/model → cohort
2. **Readable cohort IDs**: Human-readable identifiers (e.g., `cs_2023Q1_universeA_min_cs3_v1`)
3. **Fast lookups**: index.parquet enables quick previous-run lookups
4. **Sample-aware**: Only compares runs within the same cohort
5. **Artifact storage**: Can store feature importances, model hashes, plans alongside metrics

## Migration

Existing runs (legacy structure) continue to work. New runs automatically use the new structure when cohort metadata is provided.
