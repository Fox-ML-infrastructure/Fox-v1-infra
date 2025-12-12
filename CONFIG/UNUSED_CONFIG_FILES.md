# Unused Config Files Analysis

## Verification Results

### ✅ Files That ARE Used (Keep)

1. **`target_configs.yaml`** - ✅ USED
   - Referenced in: `TRAINING/ranking/predictability/data_loading.py` (line 121)
   - Referenced in: `TRAINING/ranking/target_ranker.py` (line 187)
   - **Action**: Keep

2. **`feature_target_schema.yaml`** - ✅ USED
   - Referenced in: `TRAINING/utils/leakage_filtering.py` (lines 69, 75, 413)
   - **Action**: Keep

3. **`feature_selection_config.yaml`** - ✅ USED (Legacy)
   - Referenced in: `TRAINING/EXPERIMENTS/run_all_phases.sh` (line 125)
   - Used by: `TRAINING/EXPERIMENTS/phase1_feature_engineering/run_phase1.py`
   - **Action**: Keep (legacy experiment support)

4. **`training/models.yaml`** - ✅ USED (Documentation/Reference)
   - Contains documentation about model family structure
   - May be referenced by config builders or documentation
   - **Action**: Keep (documentation purposes)

### ❌ Files That Are NOT Used (Can Remove)

1. **`comprehensive_feature_ranking.yaml`** - ❌ NOT USED
   - **Search results**: No references found in TRAINING codebase
   - **Content**: Contains feature ranking weights and model families
   - **Action**: **SAFE TO REMOVE** (or archive to `CONFIG/archive/`)

2. **`fast_target_ranking.yaml`** - ❌ NOT USED
   - **Search results**: No references found in TRAINING codebase
   - **Content**: Contains fast ranking configuration with reduced model params
   - **Action**: **SAFE TO REMOVE** (or archive to `CONFIG/archive/`)

3. **`feature_groups.yaml`** - ❌ NOT USED
   - **Search results**: No references found in TRAINING codebase
   - **Action**: **SAFE TO REMOVE** (or archive to `CONFIG/archive/`)

4. **`multi_model_feature_selection.yaml.deprecated`** - ❌ DEPRECATED
   - **Status**: Explicitly marked as deprecated
   - **Migration**: Moved to `CONFIG/feature_selection/multi_model.yaml`
   - **Action**: **SAFE TO REMOVE** (migration complete)

## Recommended Actions

### Immediate (Safe to Remove)
```bash
# Archive unused files (recommended) or delete
mkdir -p CONFIG/archive
mv CONFIG/comprehensive_feature_ranking.yaml CONFIG/archive/
mv CONFIG/fast_target_ranking.yaml CONFIG/archive/
mv CONFIG/feature_groups.yaml CONFIG/archive/
mv CONFIG/multi_model_feature_selection.yaml.deprecated CONFIG/archive/
```

### Keep (Active Usage)
- `target_configs.yaml` - Active in target ranking
- `feature_target_schema.yaml` - Active in leakage filtering
- `feature_selection_config.yaml` - Legacy experiment support
- `training/models.yaml` - Documentation/reference

## Summary

**Total files analyzed**: 7
**Files to keep**: 4
**Files safe to remove**: 4 (including deprecated)
