# Data Loading and Preprocessing Execution Order

**Formalized hierarchy of data loading and preprocessing operations in the intelligent training pipeline.**

This document defines the exact order of operations for loading, validating, and preprocessing data before feature engineering and model training.

## Execution Order (Chronological)

### Phase 1: Pipeline Initialization
1. **Load experiment config** from `CONFIG/experiments/*.yaml`
2. **Extract data configuration**:
   - `data_dir`: Path to labeled data directory
   - `data.bar_interval`: Explicit interval (5m, 15m, etc.) or auto-detect
   - `data.max_rows_per_symbol`: Data cap per symbol
3. **Load symbols list** (from config or discover from data directory)
4. **Initialize output directory** (create `RESULTS/{cohort}/{run}/` structure)

**Location**: `TRAINING/orchestration/intelligent_trainer.py` - `__init__()` and `rank_targets_auto()`

### Phase 2: Symbol Data Discovery
5. **For each symbol**:
   - **Check data directory structure**:
     - `data_dir/interval={interval}/symbol={symbol}/{symbol}.parquet`
     - Or: `data_dir/symbol={symbol}/{symbol}.parquet` (legacy)
   - **Validate data file exists**
   - **Load file metadata** (row count, columns, date range)
6. **Filter symbols** (if data file missing or invalid)
7. **Log discovered symbols** and data availability

**Location**: `TRAINING/orchestration/intelligent_trainer.py` - `_load_mtf_data()` (lines ~1380-1407)

### Phase 3: Data Loading (Per Symbol)
8. **Load parquet file** for symbol:
   - **Read with polars** (if available, faster) or pandas
   - **Apply row cap** (`max_rows_per_symbol`, default: 50000)
   - **Extract columns** (features, targets, metadata)
9. **Validate data structure**:
   - Check required columns exist (timestamp, symbol, etc.)
   - Verify data types (numeric for features, appropriate for targets)
   - Check for empty dataframes
10. **Store in `mtf_data` dict**:
    - Key: symbol name
    - Value: DataFrame with all columns

**Location**: `TRAINING/utils/data_loading.py` (if exists) or `TRAINING/orchestration/intelligent_trainer.py`  
**Module**: `TRAINING/ranking/predictability/data_loading.py` - `prepare_features_and_target()`

### Phase 4: Interval Detection
11. **Auto-detect data interval** (if not explicitly provided):
    - **Method 1**: Extract from directory path (`interval=5m/`)
    - **Method 2**: Calculate from timestamp differences
    - **Method 3**: Use explicit config value (`data.bar_interval`)
12. **Normalize interval** (convert to minutes: 5m → 5, 15m → 15)
13. **Validate interval** (must be > 0, reasonable range: 1m to 1d)

**Location**: `TRAINING/utils/data_interval.py` - `detect_data_interval()`  
**Called from**: `TRAINING/utils/leakage_filtering.py` and `TRAINING/ranking/predictability/model_evaluation.py`

### Phase 5: Feature and Target Extraction
14. **Extract target column**:
    - **Validate target exists** in dataframe
    - **Check target type** (classification vs regression)
    - **Extract target array** (handle NaN, convert to numpy)
15. **Extract feature columns**:
    - **Exclude metadata** (symbol, interval, source, timestamp)
    - **Exclude target columns** (y_*, p_*, fwd_ret_*, barrier_*)
    - **Get feature names** (all remaining columns)
16. **Validate feature count**:
    - Check `len(feature_names) > 0` (at least one feature)
    - Check `len(feature_names) < 10000` (reasonable upper bound)

**Location**: `TRAINING/ranking/predictability/data_loading.py` - `prepare_features_and_target()` (lines ~302-378)

### Phase 6: Data Quality Checks
17. **Check for all-NaN features**:
    - Identify columns that are NaN for all rows
    - Log warning if found (will be dropped later)
18. **Check for constant features**:
    - Identify columns with zero variance
    - Log warning if found (may be dropped by feature selection)
19. **Check target distribution**:
    - **Classification**: Check class balance (warn if highly imbalanced)
    - **Regression**: Check for extreme outliers (warn if > 5 sigma)
20. **Check data size**:
    - Verify `n_samples >= min_samples` (default: 100)
    - Verify `n_samples <= max_samples` (cap applied if needed)

**Location**: `TRAINING/utils/validation.py` (if exists) or inline in data loading

### Phase 7: Cross-Sectional Data Preparation (If Applicable)
21. **Check view type** (CROSS_SECTIONAL vs SYMBOL_SPECIFIC)
22. **If CROSS_SECTIONAL**:
    - **Pool samples across symbols**:
      - Combine dataframes from all symbols
      - Add symbol identifier column (for cross-sectional features)
    - **Apply cross-sectional sampling**:
      - `min_cs`: Minimum symbols per timestamp (default: 10)
      - `max_cs_samples`: Maximum samples per timestamp (default: 1000)
    - **Filter timestamps** (keep only timestamps with >= min_cs symbols)
23. **If SYMBOL_SPECIFIC**:
    - Use single symbol data (no pooling)

**Location**: `TRAINING/utils/cross_sectional_data.py` - `build_cross_sectional_data()`  
**Called from**: `TRAINING/ranking/predictability/model_evaluation.py` (line ~2570)

### Phase 8: Data Cleaning
24. **Drop all-NaN features**:
    - Remove columns that are NaN for all rows
    - Update feature names list
25. **Handle missing values**:
    - **Preserve NaN** for CV-safe imputation (no leakage)
    - **Log NaN statistics** (count per feature, percentage)
26. **Clean data types**:
    - Convert features to float64 (for numerical stability)
    - Convert target to appropriate type (float64 for regression, int for classification)
27. **Remove duplicate rows** (if any)

**Location**: `TRAINING/utils/cross_sectional_data.py` (lines ~200-300)  
**Also**: `TRAINING/ranking/predictability/model_evaluation.py` (inline cleaning)

### Phase 9: Feature Filtering (Leakage Prevention)
28. **Apply leakage filtering** (see [Feature Filtering Execution Order](FEATURE_FILTERING_EXECUTION_ORDER.md)):
    - Metadata exclusion
    - Pattern-based exclusion
    - Feature registry filtering
    - Target-conditional exclusions
    - Active sanitization
29. **Update feature names** (remove filtered features)
30. **Log filtering results** (counts, reasons)

**Location**: `TRAINING/utils/leakage_filtering.py` - `filter_features_for_target()`  
**Called from**: `TRAINING/ranking/predictability/model_evaluation.py` (line ~2555)

### Phase 10: Final Validation
31. **Validate final data shape**:
    - Check `X.shape[0] > 0` (at least one sample)
    - Check `X.shape[1] > 0` (at least one feature)
    - Check `y.shape[0] == X.shape[0]` (target matches samples)
32. **Validate feature names**:
    - Check `len(feature_names) == X.shape[1]` (names match columns)
    - Check no duplicates in feature names
33. **Log final statistics**:
    - Samples: N
    - Features: M (after filtering)
    - Target distribution (for classification: class counts)

**Location**: `TRAINING/ranking/predictability/model_evaluation.py` - `evaluate_target_predictability()` (lines ~2760-2800)

## Key Principles

### 1. Lazy Loading
- **Purpose**: Load data only when needed (per symbol, per target)
- **Method**: Load symbols on-demand, not all at once
- **Result**: Lower memory footprint, faster startup

### 2. Data Capping
- **Purpose**: Prevent memory issues with large datasets
- **Method**: Apply `max_rows_per_symbol` cap during loading
- **Result**: Consistent memory usage across symbols

### 3. Interval Consistency
- **Purpose**: Ensure all data uses same bar interval
- **Method**: Auto-detect from path/timestamps, validate consistency
- **Result**: Prevents mixing 5m and 15m data

### 4. Leakage Prevention First
- **Purpose**: Remove leaky features before any processing
- **Method**: Apply leakage filtering immediately after extraction
- **Result**: Clean feature set for downstream operations

### 5. Cross-Sectional Support
- **Purpose**: Enable cross-symbol training (pool samples across symbols)
- **Method**: Pool dataframes, apply cross-sectional sampling
- **Result**: More training data, better generalization

## Configuration

### Data Config (`CONFIG/experiments/*.yaml`)
```yaml
data:
  data_dir: "data/data_labeled_v2"
  bar_interval: "5m"  # or auto-detect
  max_rows_per_symbol: 50000
  min_samples: 100
```

### Cross-Sectional Config (`CONFIG/training_config/intelligent_training_config.yaml`)
```yaml
target_ranking:
  cross_sectional:
    min_cs: 10          # Minimum symbols per timestamp
    max_cs_samples: 1000  # Maximum samples per timestamp
```

## Integration Points

### With Feature Filtering
- Data loading provides raw feature list
- Feature filtering removes leaky features
- Filtered features passed to feature selection/pruning

### With Feature Selection
- Data loading provides clean feature set
- Feature selection reduces dimensionality
- Selected features passed to model training

### With Model Training
- Data loading provides final X, y, feature_names
- Model training uses preprocessed data
- No additional preprocessing in training (data is ready)

### With Target Ranking
- Data loading happens per target
- Each target gets its own data loading/preprocessing
- Results stored per target in RESULTS structure

## Troubleshooting

### Issue: Data file not found

**Symptom**: `FileNotFoundError` or "Data file not found" warning

**Root Cause**: Incorrect data directory path or missing parquet file

**Fix**:
1. Check `data_dir` in experiment config
2. Verify file exists: `data_dir/interval={interval}/symbol={symbol}/{symbol}.parquet`
3. Check file permissions (readable)

### Issue: Interval detection fails

**Symptom**: "Could not detect data interval" warning

**Root Cause**: No explicit interval, and timestamp differences inconsistent

**Fix**:
1. Set explicit `data.bar_interval` in config
2. Check timestamp column exists and is valid
3. Verify timestamps are sorted and consistent

### Issue: All features filtered out

**Symptom**: `len(feature_names) == 0` after filtering

**Root Cause**: Leakage filtering too aggressive, or no valid features in data

**Fix**:
1. Check leakage filtering logs (which patterns matched)
2. Review `excluded_features.yaml` (may be too restrictive)
3. Check feature registry (may exclude all features for this horizon)

### Issue: Cross-sectional sampling returns 0 samples

**Symptom**: "No valid cross-sectional samples" error

**Root Cause**: No timestamps with >= min_cs symbols

**Fix**:
1. Lower `min_cs` threshold (default: 10 → 5)
2. Check symbol data overlap (timestamps where multiple symbols have data)
3. Verify symbols list is correct (not empty, symbols exist)

### Issue: Memory error during data loading

**Symptom**: `MemoryError` when loading large symbols

**Root Cause**: `max_rows_per_symbol` too high, or too many symbols loaded

**Fix**:
1. Lower `max_rows_per_symbol` (default: 50000 → 25000)
2. Load symbols sequentially (not all at once)
3. Use data streaming (load in chunks)

## Current Implementation Status

✅ **Implemented**:
- Phase 1-10: Complete data loading and preprocessing pipeline
- Auto-interval detection
- Cross-sectional data preparation
- Data quality checks
- Integration with feature filtering

🔧 **Future Enhancements**:
- Data streaming (load in chunks for very large datasets)
- Incremental loading (load only new data since last run)
- Data validation rules (schema validation, range checks)

## Related Documentation

- [Feature Filtering Execution Order](FEATURE_FILTERING_EXECUTION_ORDER.md) - Post-loading filtering
- [Feature Selection Execution Order](FEATURE_SELECTION_EXECUTION_ORDER.md) - Post-loading selection
- [Intelligent Training Tutorial](../../01_tutorials/training/INTELLIGENT_TRAINING_TUTORIAL.md) - User guide
- [Data Processing Walkthrough](../../01_tutorials/pipelines/DATA_PROCESSING_WALKTHROUGH.md) - Data pipeline overview
