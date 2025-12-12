# Reproducibility System Self-Test Checklist

## Overview

This checklist helps verify the reproducibility tracking system is working correctly after code changes or deployments.

## Quick Smoke Test

Run these checks after any changes to reproducibility tracking:

### 1. Basic Functionality

```bash
# Test that tracker can be imported
python -c "from TRAINING.utils.reproducibility_tracker import ReproducibilityTracker, Stage, RouteType; print('✅ Import successful')"

# Test that enums work
python -c "from TRAINING.utils.reproducibility_tracker import Stage, RouteType; assert Stage.FEATURE_SELECTION.value == 'FEATURE_SELECTION'; print('✅ Enums work')"
```

### 2. File Creation

After a run, verify files are created:

```bash
# Check structure exists
ls -la REPRODUCIBILITY/FEATURE_SELECTION/CROSS_SECTIONAL/*/cohort=*/

# Check files exist
find REPRODUCIBILITY -name "metadata.json" | head -5
find REPRODUCIBILITY -name "metrics.json" | head -5
find REPRODUCIBILITY -name "drift.json" | head -5
find REPRODUCIBILITY -name "index.parquet"
find REPRODUCIBILITY -name "stats.json"
```

### 3. Schema Validation

```bash
# Check metadata.json has required fields
python -c "
import json
from pathlib import Path
meta = json.load(open('REPRODUCIBILITY/FEATURE_SELECTION/CROSS_SECTIONAL/*/cohort=*/metadata.json'))
required = ['schema_version', 'cohort_id', 'run_id', 'stage', 'target', 'N_effective']
assert all(k in meta for k in required), f'Missing fields: {[k for k in required if k not in meta]}'
print('✅ metadata.json schema valid')
"

# Check metrics.json has reproducibility_mode
python -c "
import json
from pathlib import Path
metrics = json.load(open('REPRODUCIBILITY/FEATURE_SELECTION/CROSS_SECTIONAL/*/cohort=*/metrics.json'))
assert 'reproducibility_mode' in metrics
assert metrics['reproducibility_mode'] in ['COHORT_AWARE', 'LEGACY']
print('✅ metrics.json has reproducibility_mode')
"
```

### 4. Stats Tracking

```bash
# Check stats.json exists and has counters
python -c "
import json
from pathlib import Path
stats = json.load(open('REPRODUCIBILITY/stats.json'))
assert 'modes' in stats or 'errors' in stats
print('✅ stats.json exists with counters')
print(f'   Modes: {stats.get(\"modes\", {})}')
print(f'   Errors: {stats.get(\"errors\", {})}')
"
```

### 5. Index Integrity

```bash
# Check index.parquet is readable and has required columns
python -c "
import pandas as pd
df = pd.read_parquet('REPRODUCIBILITY/index.parquet')
required_cols = ['phase', 'target', 'cohort_id', 'run_id', 'N_effective']
assert all(col in df.columns for col in required_cols), f'Missing columns: {[c for c in required_cols if c not in df.columns]}'
print(f'✅ index.parquet valid with {len(df)} rows')
"
```

## Integration Test

### Test Error Handling

1. **Simulate disk full** (if possible):
   ```python
   # Temporarily make directory read-only
   import os
   os.chmod('REPRODUCIBILITY', 0o444)
   # Run tracking - should log warning, not crash
   # Restore: os.chmod('REPRODUCIBILITY', 0o755)
   ```

2. **Test with invalid data**:
   ```python
   tracker.log_comparison(
       stage="test",
       item_name="test",
       metrics={"mean_score": float('inf')}  # Invalid value
   )
   # Should handle gracefully, not crash
   ```

3. **Test missing cohort metadata**:
   ```python
   tracker.log_comparison(
       stage="test",
       item_name="test",
       metrics={"mean_score": 0.5}  # No N_effective_cs
   )
   # Should fall back to legacy mode, log appropriately
   ```

### Test Cohort Matching

1. **Same cohort should match**:
   ```python
   # Run 1
   tracker.log_comparison(..., metrics={"N_effective_cs": 1000}, additional_data={"n_symbols": 10})
   
   # Run 2 (same cohort)
   tracker.log_comparison(..., metrics={"N_effective_cs": 1000}, additional_data={"n_symbols": 10})
   # Should find previous run, compute drift
   ```

2. **Different cohorts should not match**:
   ```python
   # Run 1
   tracker.log_comparison(..., metrics={"N_effective_cs": 1000})
   
   # Run 2 (different N)
   tracker.log_comparison(..., metrics={"N_effective_cs": 100})
   # Should create new cohort, not compare
   ```

## Operational Checks

### Check Error Rates

```bash
# View stats
cat REPRODUCIBILITY/stats.json | jq '.'

# Check error rates
python -c "
import json
stats = json.load(open('REPRODUCIBILITY/stats.json'))
errors = stats.get('errors', {})
modes = stats.get('modes', {})
total_runs = sum(modes.values())
if errors:
    print(f'⚠️  Errors detected: {errors}')
else:
    print('✅ No errors recorded')
print(f'   Total runs: {total_runs}')
print(f'   Cohort-aware: {modes.get(\"COHORT_AWARE\", 0)} ({100*modes.get(\"COHORT_AWARE\", 0)/max(total_runs, 1):.1f}%)')
print(f'   Legacy fallback: {modes.get(\"LEGACY\", 0)} ({100*modes.get(\"LEGACY\", 0)/max(total_runs, 1):.1f}%)')
"
```

### Check Logs

```bash
# Search for warnings/errors
grep -i "reproducibility.*failed\|reproducibility.*error\|falling back to legacy" logs/*.log | tail -20

# Should see clear error_type labels
grep "error_type=" logs/*.log | tail -10
```

## Regression Test

After major changes, run:

1. **Full pipeline run** (target ranking → feature selection → training)
2. **Verify all stages create reproducibility files**
3. **Check stats.json shows expected mode distribution**
4. **Verify no unexpected errors in logs**

## Expected Behavior

### Success Case

- ✅ All files created (metadata.json, metrics.json, drift.json, index.parquet, stats.json)
- ✅ `reproducibility_mode: "COHORT_AWARE"` in metrics.json (when cohort metadata provided)
- ✅ Stats show mode usage
- ✅ No errors in logs

### Fallback Case

- ✅ Logs show: "falling back to legacy mode" with error_type
- ✅ `reproducibility_mode: "LEGACY"` in metrics.json
- ✅ Stats increment `LEGACY` counter
- ✅ Pipeline continues normally

### Error Case

- ✅ Errors logged with `error_type` label
- ✅ Stats increment appropriate error counter
- ✅ Pipeline continues (never breaks)

## Troubleshooting

### If files aren't created:

1. Check `output_dir` path is correct
2. Check write permissions
3. Check logs for IO_ERROR messages

### If cohort matching fails:

1. Check `N_effective_cs` is in metrics
2. Check `cs_config` is in additional_data
3. Check logs for cohort extraction errors

### If stats.json missing:

1. Check `REPRODUCIBILITY/` directory exists
2. Check write permissions
3. Stats are best-effort (won't break if they fail)

## Automation

Consider adding to CI/CD:

```yaml
# .github/workflows/reproducibility_test.yml
- name: Test Reproducibility System
  run: |
    python -c "from TRAINING.utils.reproducibility_tracker import ReproducibilityTracker; print('✅ Import works')"
    # Run minimal test
    # Check stats.json created
```
