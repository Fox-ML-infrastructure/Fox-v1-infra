# Reproducibility System Improvements

## Summary

Enhanced the reproducibility tracking system with operational visibility, error classification, and metrics tracking.

## Improvements Implemented

### 1. Explicit Legacy Fallback Logging

**Before**: Silent fallback to legacy mode  
**After**: Explicit warning with error type

```python
logger.warning(
    f"Reproducibility: Cohort-aware tracking failed for {stage}:{item_name}, "
    f"falling back to legacy mode. error_type={error_type}, reason={str(e)}"
)
```

### 2. Reproducibility Mode Tracking

**Added**: `reproducibility_mode` field to track which mode was used

- `metadata.json`: Not applicable (cohort metadata)
- `metrics.json`: `"reproducibility_mode": "COHORT_AWARE"` or `"LEGACY"`
- Legacy `save_run()`: `"reproducibility_mode": "LEGACY"`

**Benefit**: Can inspect runs later to see which mode was actually used

### 3. Error Type Classification

**Added**: Error type labels in all error messages

- `IO_ERROR`: File system issues (disk full, permissions)
- `SERIALIZATION_ERROR`: JSON/parquet serialization issues
- `UNKNOWN_ERROR`: Other failures

**Example**:
```python
logger.warning(f"Failed to save metadata.json: {e}, error_type=IO_ERROR")
```

**Benefit**: Distinguishes environment failures (IO_ERROR) from code bugs (SERIALIZATION_ERROR)

### 4. Stats Counter System

**Added**: `REPRODUCIBILITY/stats.json` with counters

**Structure**:
```json
{
  "modes": {
    "COHORT_AWARE": 1523,
    "LEGACY": 7
  },
  "errors": {
    "write_failures": {
      "IO_ERROR": 2,
      "SERIALIZATION_ERROR": 0
    },
    "index_update_failures": {
      "IO_ERROR": 1
    },
    "total_failures": {
      "UNKNOWN_ERROR": 1
    }
  },
  "last_updated": "2025-12-11T14:30:15.123456"
}
```

**Counters tracked**:
- `modes.COHORT_AWARE`: Number of runs using cohort-aware mode
- `modes.LEGACY`: Number of runs falling back to legacy mode
- `errors.write_failures.{error_type}`: Write operation failures
- `errors.index_update_failures.{error_type}`: Index update failures
- `errors.total_failures.{error_type}`: Complete tracking failures

**Benefit**: 
- See mode distribution: "99.9% cohort-aware, 0.1% legacy"
- Detect regressions: "30% of runs now failing"
- Operational visibility without Prometheus

### 5. Enhanced Error Messages

All error messages now include:
- `error_type`: Classification (IO_ERROR, SERIALIZATION_ERROR, etc.)
- `reason`: Human-readable error message
- Context: Stage, item_name, file path

**Example**:
```
WARNING: Reproducibility: Cohort-aware tracking failed for feature_selection:y_will_peak_60m_0.8, 
falling back to legacy mode. error_type=IO_ERROR, reason=Permission denied: '/path/to/metadata.json'
```

## Usage

### Viewing Stats

```bash
# View stats
cat REPRODUCIBILITY/stats.json | jq '.'

# Check mode distribution
python -c "
import json
stats = json.load(open('REPRODUCIBILITY/stats.json'))
modes = stats.get('modes', {})
total = sum(modes.values())
print(f'Cohort-aware: {modes.get(\"COHORT_AWARE\", 0)} ({100*modes.get(\"COHORT_AWARE\", 0)/max(total, 1):.1f}%)')
print(f'Legacy: {modes.get(\"LEGACY\", 0)} ({100*modes.get(\"LEGACY\", 0)/max(total, 1):.1f}%)')
"
```

### Checking Reproducibility Mode

```bash
# Check which mode was used for a run
cat REPRODUCIBILITY/FEATURE_SELECTION/CROSS_SECTIONAL/y_will_peak_60m_0.8/cohort=*/metrics.json | jq '.reproducibility_mode'
```

### Monitoring Error Rates

```bash
# Check for errors
python -c "
import json
stats = json.load(open('REPRODUCIBILITY/stats.json'))
errors = stats.get('errors', {})
if errors:
    print('⚠️  Errors detected:')
    for counter, types in errors.items():
        for error_type, count in types.items():
            print(f'   {counter}[{error_type}]: {count}')
else:
    print('✅ No errors recorded')
"
```

## Future Enhancements

### Strict Mode (Not Implemented Yet)

Future addition for production environments:

```yaml
reproducibility:
  mode: "permissive"  # or "strict"
```

- **permissive** (current): Log + continue
- **strict**: Abort training if reproducibility tracking fails

### Prometheus Integration (Not Implemented Yet)

Could expose stats as Prometheus metrics:

```python
reproducibility_errors_total{error_type="IO_ERROR", counter="write_failures"} 2
reproducibility_mode_total{mode="COHORT_AWARE"} 1523
reproducibility_mode_total{mode="LEGACY"} 7
```

## Testing

See `REPRODUCIBILITY_SELF_TEST.md` for:
- Smoke tests
- Integration tests
- Operational checks
- Regression tests

## Benefits

1. **Operational visibility**: Can see mode distribution and error rates
2. **Debugging**: Error types help distinguish environment vs code issues
3. **Regression detection**: Stats show when error rates spike
4. **Audit trail**: `reproducibility_mode` field shows which mode was used
5. **Non-breaking**: All improvements are backward compatible

## Backward Compatibility

✅ All changes are backward compatible:
- Existing runs continue to work
- New fields are optional
- Stats are best-effort (won't break if they fail)
- Error handling remains non-breaking
