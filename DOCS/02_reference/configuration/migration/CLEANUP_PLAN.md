# CONFIG Folder Cleanup and Centralization Plan

## Current Problems

1. **Scattered root-level configs**: 10+ config files at CONFIG root that should be organized
2. **Inconsistent organization**: Similar configs in different locations
3. **Legacy files still present**: Deprecated files not cleaned up
4. **Unclear purpose**: Some files marked "potentially unused" but still present
5. **Multiple paths for same config**: Code checks multiple locations with fallbacks

## Proposed Clean Structure

```
CONFIG/
├── README.md                    # Main documentation
├── defaults.yaml                # Global defaults (SST)
├── config_loader.py             # Main config loader
├── config_builder.py            # Config builder utilities
├── config_schemas.py            # Type definitions
│
├── core/                        # Core system configs
│   ├── logging.yaml             # Logging configuration
│   ├── system.yaml             # System resources & paths
│   └── paths.yaml              # Path configuration (if needed)
│
├── data/                        # Data-related configs
│   ├── feature_registry.yaml   # Feature registry (allowed/excluded)
│   ├── excluded_features.yaml  # Always-excluded features
│   ├── feature_groups.yaml     # Feature groups (if used)
│   └── feature_target_schema.yaml  # Feature-target schema
│
├── experiments/                 # Experiment configs (user-created)
│   ├── README.md
│   ├── _template.yaml
│   └── *.yaml                  # Individual experiments
│
├── models/                      # Model hyperparameters
│   ├── lightgbm.yaml
│   ├── xgboost.yaml
│   └── ...                     # All model families
│
├── pipeline/                    # Pipeline execution configs
│   ├── training/               # Training pipeline
│   │   ├── intelligent.yaml    # Intelligent training (main)
│   │   ├── safety.yaml         # Safety & temporal
│   │   ├── preprocessing.yaml  # Data preprocessing
│   │   ├── optimizer.yaml      # Optimizer settings
│   │   ├── callbacks.yaml      # Training callbacks
│   │   ├── routing.yaml        # Target routing
│   │   ├── stability.yaml      # Stability analysis
│   │   ├── decisions.yaml      # Decision policies
│   │   └── families.yaml       # Model family configs
│   │
│   ├── gpu.yaml                # GPU settings
│   ├── memory.yaml              # Memory management
│   ├── threading.yaml          # Threading policy
│   └── system.yaml              # System config (if not in core/)
│
├── ranking/                     # Ranking & selection configs
│   ├── targets/                # Target ranking
│   │   ├── multi_model.yaml    # Multi-model target ranking
│   │   └── configs.yaml        # Target configs (legacy name)
│   │
│   └── features/               # Feature selection
│       ├── multi_model.yaml     # Multi-model feature selection
│       └── config.yaml          # Feature selection config (legacy)
│
└── archive/                     # Archived/deprecated files
    ├── comprehensive_feature_ranking.yaml
    ├── fast_target_ranking.yaml
    ├── multi_model_feature_selection.yaml.deprecated
    └── README.md                # Archive documentation
```

## Migration Steps

### Phase 1: Create New Structure (Non-Breaking)

1. Create new directories:
   ```bash
   mkdir -p CONFIG/{core,data,models,pipeline/training,ranking/{targets,features},archive}
   ```

2. Move files to new locations (keep originals for now):
   - `logging_config.yaml` → `core/logging.yaml`
   - `feature_registry.yaml` → `data/feature_registry.yaml`
   - `excluded_features.yaml` → `data/excluded_features.yaml`
   - `feature_target_schema.yaml` → `data/feature_target_schema.yaml`
   - `model_config/*` → `models/*`
   - `training_config/*` → `pipeline/training/*` (with renamed files)
   - `target_ranking/*` → `ranking/targets/*`
   - `feature_selection/*` → `ranking/features/*`

3. Archive unused files:
   - Move to `archive/` with README explaining why

### Phase 2: Update Config Loaders (Backward Compatible)

1. Update `config_loader.py` to check new locations first, then fallback to old
2. Add deprecation warnings when old paths are used
3. Update all references in codebase

### Phase 3: Clean Up (After Migration Period)

1. Remove old files after migration period (e.g., 1-2 releases)
2. Remove fallback code paths
3. Update documentation

## File Mapping

### Core System Configs
| Old Location | New Location | Status |
|-------------|-------------|--------|
| `logging_config.yaml` | `core/logging.yaml` | Move |
| `training_config/system_config.yaml` | `core/system.yaml` | Move/merge |

### Data Configs
| Old Location | New Location | Status |
|-------------|-------------|--------|
| `feature_registry.yaml` | `data/feature_registry.yaml` | Move |
| `excluded_features.yaml` | `data/excluded_features.yaml` | Move |
| `feature_target_schema.yaml` | `data/feature_target_schema.yaml` | Move |
| `feature_groups.yaml` | `data/feature_groups.yaml` or archive | Check usage |

### Model Configs
| Old Location | New Location | Status |
|-------------|-------------|--------|
| `model_config/*.yaml` | `models/*.yaml` | Move |

### Pipeline Configs
| Old Location | New Location | Status |
|-------------|-------------|--------|
| `training_config/intelligent_training_config.yaml` | `pipeline/training/intelligent.yaml` | Move |
| `training_config/safety_config.yaml` | `pipeline/training/safety.yaml` | Move |
| `training_config/preprocessing_config.yaml` | `pipeline/training/preprocessing.yaml` | Move |
| `training_config/optimizer_config.yaml` | `pipeline/training/optimizer.yaml` | Move |
| `training_config/callbacks_config.yaml` | `pipeline/training/callbacks.yaml` | Move |
| `training_config/routing_config.yaml` | `pipeline/training/routing.yaml` | Move |
| `training_config/stability_config.yaml` | `pipeline/training/stability.yaml` | Move |
| `training_config/decision_policies.yaml` | `pipeline/training/decisions.yaml` | Move |
| `training_config/family_config.yaml` | `pipeline/training/families.yaml` | Move |
| `training_config/gpu_config.yaml` | `pipeline/gpu.yaml` | Move |
| `training_config/memory_config.yaml` | `pipeline/memory.yaml` | Move |
| `training_config/threading_config.yaml` | `pipeline/threading.yaml` | Move |
| `training_config/pipeline_config.yaml` | `pipeline/pipeline.yaml` | Move |
| `training_config/sequential_config.yaml` | `pipeline/training/sequential.yaml` | Move |
| `training_config/first_batch_specs.yaml` | `pipeline/training/first_batch.yaml` | Move |

### Ranking Configs
| Old Location | New Location | Status |
|-------------|-------------|--------|
| `target_ranking/multi_model.yaml` | `ranking/targets/multi_model.yaml` | Move |
| `target_configs.yaml` | `ranking/targets/configs.yaml` | Move |
| `feature_selection/multi_model.yaml` | `ranking/features/multi_model.yaml` | Move |
| `feature_selection_config.yaml` | `ranking/features/config.yaml` | Move |
| `multi_model_feature_selection.yaml` | Archive (deprecated) | Archive |

### Archive
| Old Location | New Location | Status |
|-------------|-------------|--------|
| `comprehensive_feature_ranking.yaml` | `archive/comprehensive_feature_ranking.yaml` | Archive |
| `fast_target_ranking.yaml` | `archive/fast_target_ranking.yaml` | Archive |
| `multi_model_feature_selection.yaml.deprecated` | `archive/multi_model_feature_selection.yaml.deprecated` | Archive |

## Benefits

1. **Clear organization**: Related configs grouped together
2. **Easier navigation**: Logical directory structure
3. **Reduced confusion**: No scattered root-level files
4. **Better maintainability**: Clear separation of concerns
5. **Scalability**: Easy to add new config categories

## Implementation Notes

- All moves will be backward compatible (loaders check both old and new)
- Deprecation warnings will guide users to new locations
- Migration period: 2-3 releases before removing old paths
- Documentation updated to reflect new structure

