# Reproducibility Error Handling

## Overview

The reproducibility tracking system is designed to **never break the main pipeline**. All errors are caught, logged, and handled gracefully.

## Error Handling Strategy

### 1. Never Raise Exceptions

The `log_comparison()` method is wrapped in a top-level try/except that ensures it never raises:

```python
def log_comparison(...):
    try:
        # All tracking logic here
    except Exception as e:
        logger.error(f"Reproducibility tracking failed: {e}")
        # Don't re-raise - never break the main pipeline
```

### 2. Graceful Degradation

If cohort-aware tracking fails, the system falls back to legacy mode:

```python
try:
    # Cohort-aware save
    self._save_to_cohort(...)
except Exception as e:
    logger.warning(f"Failed to save cohort data: {e}")
    # Fall back to legacy mode
    self.save_run(...)
```

### 3. File Operation Errors

All file operations (JSON writes, parquet updates) are wrapped in try/except:

- **Critical files** (metadata.json, metrics.json): Log warning and re-raise (but caught by outer try/except)
- **Non-critical files** (drift.json, index.parquet): Log warning and continue

### 4. Silent Error Prevention

All previously silent errors now log at appropriate levels:

- **DEBUG**: Non-critical failures (e.g., git commit, date parsing fallback)
- **WARNING**: Important failures that don't break functionality (e.g., index update, drift file)
- **ERROR**: Critical failures (caught by outer try/except, never re-raised)

## Error Categories

### Config Loading Errors

**Location**: `_load_thresholds()`, `_load_cohort_aware()`, etc.

**Handling**: Return sensible defaults, log at DEBUG level

```python
try:
    # Load from config
except Exception as e:
    logger.debug(f"Could not load from config: {e}, using defaults")
    return defaults
```

### File I/O Errors

**Location**: `_save_to_cohort()`, `_update_index()`, etc.

**Handling**: 
- Critical files: Log WARNING, re-raise (caught by outer handler)
- Non-critical files: Log WARNING, continue

```python
try:
    with open(metadata_file, 'w') as f:
        json.dump(data, f)
except (IOError, OSError) as e:
    logger.warning(f"Failed to save {metadata_file}: {e}")
    raise  # Re-raise for critical files
```

### Data Processing Errors

**Location**: `_compute_cohort_id()`, `_extract_cohort_metadata()`, etc.

**Handling**: Log at DEBUG/WARNING, use fallbacks

```python
try:
    dt = pd.Timestamp(date_start)
    date_str = f"{dt.year}Q{(dt.month-1)//3 + 1}"
except Exception as e:
    logger.debug(f"Failed to parse date: {e}, using YYYY-MM format")
    date_str = date_start[:7]  # Fallback
```

### Index Query Errors

**Location**: `get_last_comparable_run()`, `_find_matching_cohort()`

**Handling**: Log at DEBUG, return None (no previous run found)

```python
try:
    df = pd.read_parquet(index_file)
    # Query logic
except Exception as e:
    logger.debug(f"Failed to query index: {e}")
    return None
```

## Integration Points

All call sites already have error handling:

### Target Ranking

```python
try:
    tracker.log_comparison(...)
except Exception as e:
    logger.warning(f"Reproducibility tracking failed: {e}")
    logger.debug(f"Traceback: {traceback.format_exc()}")
```

### Feature Selection

```python
try:
    tracker.log_comparison(...)
except Exception as e:
    logger.warning(f"Reproducibility tracking failed: {e}")
    logger.debug(f"Traceback: {traceback.format_exc()}")
```

### Model Training

```python
try:
    tracker.log_comparison(...)
except Exception as e:
    logger.warning(f"Reproducibility tracking failed: {e}")
    logger.debug(f"Traceback: {traceback.format_exc()}")
```

## Verification Checklist

✅ **No silent errors**: All exceptions are logged  
✅ **Never breaks pipeline**: Top-level try/except in `log_comparison()`  
✅ **Graceful degradation**: Falls back to legacy mode on cohort-aware failures  
✅ **Appropriate log levels**: DEBUG for non-critical, WARNING for important, ERROR for critical  
✅ **Call site protection**: All integration points have try/except blocks  

## Testing Error Scenarios

To verify error handling:

1. **Disk full**: Should log warning, not crash
2. **Invalid JSON**: Should log warning, not crash
3. **Missing config**: Should use defaults, log at DEBUG
4. **Corrupted index.parquet**: Should log warning, create new index
5. **Permission errors**: Should log warning, not crash

All scenarios should result in:
- Pipeline continues normally
- Error logged at appropriate level
- No unhandled exceptions
