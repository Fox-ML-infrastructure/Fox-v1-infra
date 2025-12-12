# Configuration System

This directory contains all configuration files for the FoxML Core pipeline.

## Directory Structure

The configuration system uses a modular structure to prevent config "crossing" between pipeline components:

```
CONFIG/
├── experiments/              # Experiment-level configs (what are we running?)
│   ├── e2e_ranking_test.yaml
│   └── fwd_ret_60m_test.yaml
├── feature_selection/        # Feature selection module configs
│   └── multi_model.yaml
├── target_ranking/           # Target ranking module configs
│   └── multi_model.yaml
├── training_config/          # Training pipeline configs (SST: Single Source of Truth)
│   ├── intelligent_training_config.yaml  # Main intelligent trainer config
│   ├── decision_policies.yaml            # Decision policy thresholds (NEW)
│   ├── stability_config.yaml             # Stability analysis thresholds (NEW)
│   ├── safety_config.yaml                # Safety & temporal configs
│   ├── system_config.yaml                # System resources
│   ├── pipeline_config.yaml              # Pipeline behavior
│   ├── preprocessing_config.yaml         # Data preprocessing
│   ├── optimizer_config.yaml             # Optimizer settings
│   ├── gpu_config.yaml                   # GPU settings
│   ├── memory_config.yaml                # Memory management
│   ├── threading_config.yaml             # Threading policy
│   ├── routing_config.yaml               # Target routing
│   ├── callbacks_config.yaml             # Training callbacks
│   ├── family_config.yaml                # Model family configs
│   ├── sequential_config.yaml            # Sequential training
│   └── first_batch_specs.yaml            # First batch specs
├── model_config/             # Model-specific hyperparameters
│   ├── lightgbm.yaml
│   ├── xgboost.yaml
│   ├── neural_network.yaml
│   └── ... (all model families)
├── routing/                  # Routing configs
│   └── default.yaml
├── logging_config.yaml       # Structured logging configuration
├── feature_registry.yaml     # Feature registry (allowed/excluded)
├── excluded_features.yaml    # Always-excluded features
├── defaults.yaml             # Global defaults (SST)
└── config_loader.py          # Configuration loader
```

## Config Files Status

### ✅ Active Config Files
All files in `training_config/`, `model_config/`, `feature_selection/`, `target_ranking/`, and `experiments/` are actively used.

### ⚠️ Potentially Unused Files (Verify Before Removing)
- `comprehensive_feature_ranking.yaml` - May be legacy
- `fast_target_ranking.yaml` - May be legacy
- `feature_selection_config.yaml` - May be legacy
- `target_configs.yaml` - Referenced in code, verify usage
- `feature_target_schema.yaml` - Referenced in code, verify usage
- `feature_groups.yaml` - Verify usage
- `training/models.yaml` - May be superseded by `model_config/`

### 🗑️ Deprecated Files (Safe to Remove)
- `multi_model_feature_selection.yaml.deprecated` - Explicitly deprecated, moved to `feature_selection/multi_model.yaml`

## Quick Start

### Using Experiment Configs (Recommended)

Create an experiment config in `CONFIG/experiments/`:

```yaml
experiment:
  name: my_experiment
  description: "Test run"

data:
  data_dir: data/data_labeled/interval=5m
  symbols: [AAPL, MSFT]
  interval: 5m
  max_samples_per_symbol: 3000

targets:
  primary: fwd_ret_60m

feature_selection:
  top_n: 30
  model_families: [lightgbm, xgboost]

training:
  model_families: [lightgbm, xgboost]
  cv_folds: 5
```

Then run:

```bash
python TRAINING/train.py --experiment-config my_experiment
```

### Legacy Usage (Still Supported)

You can still use individual config files:

```bash
python TRAINING/train.py \
    --data-dir data/data_labeled/interval=5m \
    --symbols AAPL MSFT \
    --targets fwd_ret_60m
```

## Migration Guide

### Feature Selection Config

**Old location:** `CONFIG/multi_model_feature_selection.yaml`  
**New location:** `CONFIG/feature_selection/multi_model.yaml`

The config loader automatically checks the new location first, then falls back to legacy. You'll see a deprecation warning if using the old location.

### Target Ranking Config

**Old location:** Uses feature selection config  
**New location:** `CONFIG/target_ranking/multi_model.yaml`

### Training Config

**Old location:** Various files in `CONFIG/training_config/`  
**New location:** `CONFIG/training/models.yaml` (for model families)

Training still uses `CONFIG/training_config/` for pipeline, GPU, memory, etc. settings.

## Documentation

- **Configuration Reference:** See `DOCS/02_reference/configuration/`
- **Experiment Configs:** See `CONFIG/experiments/README.md`
- **Feature Selection:** See `CONFIG/feature_selection/README.md`

## Backward Compatibility

All legacy config locations are still supported with deprecation warnings. The system will:
1. Check new location first
2. Fall back to legacy location if new doesn't exist
3. Show deprecation warning when using legacy location

This ensures existing code continues to work while encouraging migration to the new structure.
