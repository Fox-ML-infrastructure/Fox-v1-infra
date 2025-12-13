# Config Trace & Max Samples Fix

## Problem Identified

The user was setting `max_samples_per_symbol: 1000` in their experiment config, but the logs showed:
- "Loading data ... (max 10000 rows per symbol)..." 
- `max_cs_samples=1000`

**Root Cause**: Two different config keys control two different limits:
1. **`max_rows_per_symbol`** (data loader) - was defaulting to 50000 from `pipeline.data_limits.default_max_rows_per_symbol_ranking`
2. **`max_cs_samples`** (cross-sectional builder) - was defaulting to 1000 from `pipeline.data_limits.max_cs_samples`

Neither was checking the experiment config first!

## Fixes Applied

### 1. Updated `evaluate_target_predictability` in `model_evaluation.py`
- Now checks `experiment_config.max_samples_per_symbol` first
- Falls back to reading from experiment YAML `data.max_samples_per_symbol`
- Then falls back to pipeline config
- Added comprehensive config trace logging showing source of each value

### 2. Updated `rank_targets` and `evaluate_target_predictability` in `target_ranker.py`
- Already fixed to check experiment config first
- Reads from YAML `data` section for `min_cs`, `max_cs_samples`, `max_rows_per_symbol`

### 3. Added Config Trace Logging
- Shows working directory
- Shows experiment config name
- Shows resolved values with source provenance
- Logs before data loading so you can see exactly where values come from

## Config Trace Output

You'll now see output like:

```
================================================================================
📋 CONFIG TRACE: Data Loading Limits (with provenance)
================================================================================
   Working directory: /home/Jennifer/trader
   Experiment config: e2e_ranking_test

   🔍 Resolved values:
      max_rows_per_symbol: 1000
         Source: experiment YAML data.max_samples_per_symbol = 1000
      max_cs_samples: 1000
         Source: experiment YAML data.max_cs_samples = 1000
      min_cs: 3
================================================================================
```

## What to Check

If you still see wrong values, the trace will show:
- **Source**: Where the value actually came from
- **Working directory**: To catch CWD issues
- **Experiment config**: To verify it's being loaded

This makes it immediately obvious if:
- Experiment config isn't being loaded
- A different config is being used
- CLI overrides are winning
- Hardcoded defaults are being used

## Remaining Hardcoded Defaults (for reference)

These are fallbacks only (used if config unavailable):
- `max_rows_per_symbol`: 50000 (in `target_ranker.py`, `model_evaluation.py`)
- `max_cs_samples`: 1000 (in multiple places)
- `min_cs`: 10 (in multiple places)

These should never be hit if experiment config is properly loaded.

