# Config Path Consolidation Status

## Overview

After migrating config files to the new structure, we need to update all code references to use the new paths or the config loaders (which already check both old and new locations).

## Status

### ✅ Updated (Using Config Loaders or New Paths)

- `CONFIG/config_loader.py` - Updated to check new locations first
- `CONFIG/config_builder.py` - Updated to check new locations first  
- `TRAINING/utils/leakage_filtering.py` - Updated to check `data/` first
- `TRAINING/orchestration/intelligent_trainer.py` - Updated to check `pipeline/training/` first
- `TRAINING/ranking/multi_model_feature_selection.py` - Updated to check `ranking/features/` first
- `TRAINING/ranking/predictability/data_loading.py` - Updated to check `ranking/targets/` first
- `TRAINING/ranking/target_ranker.py` - Updated to read from experiment config

### ⚠️ Needs Update (Comments/Log Messages Only - Low Priority)

These are mostly in comments or log messages, not actual code paths:

- Model trainers (`TRAINING/model_fun/*.py`) - Log messages reference `model_config/` but code uses `load_model_config()` which already checks new locations
- Documentation strings - Reference old paths in help text
- Error messages - Reference old paths in user-facing messages

### 📝 Action Items

1. **High Priority** (Actual code paths):
   - ✅ Done - All critical loaders updated

2. **Medium Priority** (User-facing messages):
   - Update help text in argument parsers
   - Update error messages to reference new paths
   - Update documentation strings

3. **Low Priority** (Comments):
   - Update inline comments that reference old paths
   - Update README files in subdirectories

## Helper Function

Use `CONFIG.config_loader.get_config_path(config_name)` to get the correct path for any config file. It automatically checks new locations first, then falls back to old.

Example:
```python
from CONFIG.config_loader import get_config_path

excluded_path = get_config_path("excluded_features")
# Returns: CONFIG/data/excluded_features.yaml (if exists)
#          or CONFIG/excluded_features.yaml (fallback)
```

## Migration Checklist

- [x] Update config loaders to check new locations
- [x] Update critical code paths (leakage_filtering, intelligent_trainer, ranking)
- [ ] Update help text and error messages (optional)
- [ ] Update comments and documentation (optional)

## Notes

- **Symlinks maintain backward compatibility** - Old paths still work
- **Config loaders check both locations** - Code using loaders is already compatible
- **Direct path references** - Only need updating if they bypass the loaders

