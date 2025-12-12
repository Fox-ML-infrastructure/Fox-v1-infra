# Feature Pruning Execution Order

**Formalized hierarchy of feature pruning operations in the training pipeline.**

This document defines the exact order of operations for quick importance-based feature pruning to reduce dimensionality before expensive model training.

## Execution Order (Chronological)

### Phase 1: Initialization and Validation
1. **Validate inputs**:
   - Check `X.shape[1] == len(feature_names)` (feature count matches)
   - Verify `X` and `y` are numpy arrays
   - Check `task_type` is 'regression' or 'classification'
2. **Load config** (if parameters not provided):
   - `cumulative_threshold` (default: 0.0001 from `preprocessing_config.yaml`)
   - `min_features` (default: 50 from config)
   - `n_estimators` (default: 50 from config)
   - `max_depth` (default: 5 from config)
   - `learning_rate` (default: 0.1 from config)
3. **Early exit check**:
   - If `len(feature_names) <= min_features`: Skip pruning, return all features
   - If LightGBM not available: Log warning, return all features

**Location**: `TRAINING/utils/feature_pruning.py` - `quick_importance_prune()` (lines ~41-125)

### Phase 2: Quick Model Training
4. **Determine task type**:
   - **Regression**: Use `LGBMRegressor`
   - **Classification**: Detect binary vs multiclass, use `LGBMClassifier`
5. **Train lightweight LightGBM model**:
   - **Shallow trees** (`max_depth=5`) for speed
   - **Few estimators** (`n_estimators=50`) for quick training
   - **Single thread** (`n_jobs=1`) to avoid overhead
   - **Low verbosity** (`verbosity=-1`) to reduce noise
6. **Extract feature importance**:
   - Get `model.feature_importances_` (native LightGBM importance)
   - Normalize to sum to 1.0 (percentage importance)

**Location**: `TRAINING/utils/feature_pruning.py` (lines ~138-191)

### Phase 3: Importance Ranking
7. **Sort features by importance** (descending order)
8. **Calculate cumulative importance**:
   - `cumulative_importance[i] = sum(importance[0:i+1])`
   - Tracks how much signal is captured by top N features
9. **Identify features to drop**:
   - **Rule 1**: Drop features below cumulative threshold
     - If `cumulative_importance[i] <= (1.0 - cumulative_threshold)`, feature is in bottom tail
   - **Rule 2**: Always keep top `min_features` features
     - Even if they're below threshold, keep them for model diversity
10. **Build keep mask**:
    - `keep_mask[i] = True` if feature should be kept
    - `keep_mask[:min_features] = True` (force keep top N)

**Location**: `TRAINING/utils/feature_pruning.py` (lines ~193-208)

### Phase 4: Feature Extraction
11. **Extract kept features**:
    - Get indices of features to keep (in original order)
    - `X_pruned = X[:, keep_indices]`
    - `pruned_names = [feature_names[i] for i in keep_indices]`
12. **Validate no duplicates**:
    - Check `len(pruned_names) == len(set(pruned_names))`
    - Raise error if duplicates found (indicates bug)
13. **Build dropped features list**:
    - `dropped_features = [feature_names[i] for i not in keep_indices]`

**Location**: `TRAINING/utils/feature_pruning.py` (lines ~210-222)

### Phase 5: Logging and Statistics
14. **Log pruning statistics**:
    - Original count → Pruned count (dropped N)
    - Top 10 importance range (min to max)
    - Sample of dropped features (first 10)
15. **Build importance dict** (for stability tracking):
    - `full_importance_dict = {feature: importance for all features}`
    - Includes both kept and dropped features
16. **Return results**:
    - `X_pruned`: Pruned feature matrix
    - `pruned_names`: Names of kept features
    - `pruning_stats`: Dict with counts, dropped features, importance dict

**Location**: `TRAINING/utils/feature_pruning.py` (lines ~223-246)

## Key Principles

### 1. Quick and Lightweight
- **Purpose**: Pre-processing step to reduce dimensionality before expensive multi-model training
- **Method**: Fast LightGBM model (shallow, few trees, single thread)
- **Trade-off**: Speed over accuracy (this is just for pruning, not final model)

### 2. Cumulative Threshold Strategy
- **Purpose**: Remove "garbage features" with < 0.01% cumulative importance
- **Method**: Drop features in bottom tail (below `1.0 - cumulative_threshold`)
- **Result**: Removes noise features that dilute split candidates

### 3. Minimum Feature Guarantee
- **Purpose**: Ensure model has enough features for diversity
- **Method**: Always keep top `min_features` features (default: 50)
- **Result**: Prevents over-aggressive pruning that hurts model performance

### 4. Task-Aware Pruning
- **Purpose**: Handle regression and classification differently
- **Method**: Detect task type, use appropriate LightGBM model
- **Result**: Pruning respects target distribution (binary vs multiclass)

### 5. Stability Tracking Integration
- **Purpose**: Track feature importance consistency across runs
- **Method**: Return full importance dict (all features, not just kept)
- **Result**: Enables regression detection (importance drift)

## Configuration

### Pruning Config (`CONFIG/training_config/preprocessing_config.yaml`)
```yaml
feature_pruning:
  cumulative_threshold: 0.0001  # Drop features below 0.01% cumulative importance
  min_features: 50              # Always keep at least 50 features
  n_estimators: 50               # Trees for quick importance (shallow model)
  max_depth: 5                   # Shallow trees for speed
  learning_rate: 0.1             # Learning rate for quick model
```

## Integration Points

### With Feature Filtering
- Pruning runs **after** feature filtering (leakage filtering, registry filtering)
- Input: Already-filtered features (safe, leakage-free)
- Output: Pruned subset of safe features

### With Model Training
- Pruning runs **before** expensive multi-model training
- Reduces dimensionality from ~300 features to ~50-100 features
- Speeds up training by 3-5x (fewer split candidates)

### With Stability Tracking
- Full importance dict returned for stability snapshots
- Tracks importance consistency across runs
- Enables regression detection (features that were important but now aren't)

### With Target Ranking
- Pruning runs **after** feature filtering, **before** target evaluation
- Location: `TRAINING/ranking/predictability/model_evaluation.py` (line ~3034)
- Reduces feature set before `train_and_evaluate_models()`

## Execution Context

### When Pruning Runs
1. **Target Ranking Pipeline**:
   - After feature filtering (leakage, registry, target-conditional)
   - After Final Gatekeeper (last-mile safety)
   - Before model training (LightGBM, Random Forest, Neural Network)

2. **Feature Selection Pipeline**:
   - Not used (feature selection already reduces dimensionality)
   - Feature selection is more sophisticated (multi-model consensus)

3. **Training Pipeline**:
   - Not used (training uses pre-selected features)
   - Feature selection handles dimensionality reduction

### Pruning vs Feature Selection

| Aspect | Feature Pruning | Feature Selection |
|--------|----------------|-------------------|
| **Purpose** | Quick pre-processing | Sophisticated selection |
| **Method** | Single LightGBM model | Multi-model consensus |
| **Speed** | Very fast (~seconds) | Slower (~minutes) |
| **Accuracy** | Approximate | High (multi-model) |
| **When Used** | Before expensive training | Standalone or before ranking |
| **Output** | Top N by importance | Top N by consensus |

## Troubleshooting

### Issue: Pruning drops too many features

**Symptom**: `pruned_count < min_features` (shouldn't happen due to guarantee)

**Root Cause**: Bug in keep mask logic

**Fix**: Check `keep_mask[:min_features] = True` is applied correctly

### Issue: Pruning doesn't reduce features

**Symptom**: All features kept (no reduction)

**Root Cause**: `cumulative_threshold` too high, or features all have similar importance

**Fix**:
1. Lower `cumulative_threshold` (e.g., 0.001 → 0.0001)
2. Check if features truly have different importance (may indicate data issue)

### Issue: Pruning fails with "All feature importances are zero"

**Symptom**: Model returns zero importance for all features

**Root Cause**: Model failed to train (no signal, all NaN, etc.)

**Fix**:
1. Check data has sufficient samples
2. Verify target has variance
3. Check for all-NaN features (should be filtered earlier)
4. Review model training logs

### Issue: Duplicate feature names after pruning

**Symptom**: Error: "Duplicate feature names after pruning"

**Root Cause**: Bug in feature extraction logic (shouldn't happen)

**Fix**: Check `keep_indices` logic, ensure no duplicate indices

## Current Implementation Status

✅ **Implemented**:
- Phase 1-5: Complete pruning pipeline
- Config-driven parameters (SST)
- Stability tracking integration
- Error handling and fallbacks

🔧 **Future Enhancements**:
- Adaptive pruning (adjust threshold based on data size)
- Multi-task pruning (prune for multiple targets simultaneously)
- Feature interaction preservation (keep features that interact)

## Related Documentation

- [Feature Filtering Execution Order](FEATURE_FILTERING_EXECUTION_ORDER.md) - Pre-pruning filtering
- [Feature Selection Execution Order](FEATURE_SELECTION_EXECUTION_ORDER.md) - Alternative to pruning
- [Feature Importance Stability](../../03_technical/implementation/FEATURE_IMPORTANCE_STABILITY.md) - Stability tracking
