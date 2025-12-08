# Configuration System

Centralized configuration management for FoxML Core training pipeline, model families, feature selection, and leakage detection.

## Overview

The configuration system provides a single source of truth for all training parameters, system settings, model hyperparameters, feature management, and safety controls. All configurations are stored as YAML files and loaded programmatically via `config_loader.py`.

## Complete Directory Structure

```
CONFIG/
├── config_loader.py              # Configuration loader implementation
├── README.md                      # This file
│
├── backups/                       # Automatic config backups (auto-fixer)
│   └── {target_name}/
│       └── {timestamp}/
│           ├── excluded_features.yaml
│           ├── feature_registry.yaml
│           └── manifest.json
│
├── model_config/                  # Model-specific hyperparameters (17 models)
│   ├── lightgbm.yaml
│   ├── xgboost.yaml
│   ├── mlp.yaml
│   ├── transformer.yaml
│   ├── lstm.yaml
│   ├── cnn1d.yaml
│   ├── ensemble.yaml
│   ├── multi_task.yaml
│   ├── vae.yaml
│   ├── gan.yaml
│   ├── gmm_regime.yaml
│   ├── ngboost.yaml
│   ├── quantile_lightgbm.yaml
│   ├── change_point.yaml
│   ├── ftrl_proximal.yaml
│   ├── reward_based.yaml
│   └── meta_learning.yaml
│
├── training_config/               # Training pipeline and system settings (11 configs)
│   ├── pipeline_config.yaml      # Main pipeline orchestration
│   ├── gpu_config.yaml            # GPU/CUDA configuration
│   ├── memory_config.yaml         # Memory management
│   ├── preprocessing_config.yaml # Data preprocessing
│   ├── threading_config.yaml     # Threading policies
│   ├── safety_config.yaml         # Numerical stability + leakage detection
│   ├── callbacks_config.yaml      # Training callbacks
│   ├── optimizer_config.yaml     # Optimizer defaults
│   ├── system_config.yaml         # System-level settings (paths, backups, env)
│   ├── family_config.yaml         # Model family policies
│   ├── sequential_config.yaml    # Sequential model settings
│   └── first_batch_specs.yaml    # First batch specifications
│
├── excluded_features.yaml         # Patterns for always-excluded features
├── feature_registry.yaml          # Feature metadata (lag_bars, allowed_horizons)
├── feature_target_schema.yaml     # Explicit schema (metadata/targets/features)
├── feature_groups.yaml            # Feature grouping definitions
├── feature_selection_config.yaml  # Feature selection settings
├── multi_model_feature_selection.yaml  # Multi-model consensus config
├── comprehensive_feature_ranking.yaml  # Comprehensive ranking config
├── fast_target_ranking.yaml       # Fast ranking config
└── target_configs.yaml            # Target definitions (63 targets)
```

## Configuration Categories

### 1. Root-Level Feature & Target Configs

#### `excluded_features.yaml`
**Purpose:** Defines patterns for features that are always excluded from training.

**Structure:**
- `always_exclude.regex_patterns` - Regex patterns matching leaky features
- `always_exclude.prefix_patterns` - Prefix patterns (e.g., `y_*`, `fwd_ret_*`)
- `always_exclude.exact_patterns` - Exact feature names to exclude

**Key Patterns:**
- `^y_*` - All target columns
- `^fwd_ret_*` - Forward returns (future information)
- `^barrier_*` - Barrier-related features
- `^mfe_*`, `^mdd_*` - Maximum favorable/adverse excursion

**Auto-Fixer Integration:** Auto-fixer can add patterns here when leakage is detected.

#### `feature_registry.yaml`
**Purpose:** Defines temporal metadata for features to prevent leakage.

**Structure:**
- `features.{feature_name}`:
  - `source` - Data source (price, volume, etc.)
  - `lag_bars` - Number of bars lagged (must be ≥ 0)
  - `allowed_horizons` - List of target horizons this feature is safe for
  - `rejected` - If true, feature is rejected (with reason)
  - `description` - Human-readable description

**Example:**
```yaml
features:
  ret_1:
    source: price
    lag_bars: 1
    allowed_horizons: [1, 2, 3, 5, 12, 24, 60]
    description: 1-bar lagged return
```

**Usage:** Features are filtered based on target horizon. Only features with `allowed_horizons` including the target's horizon are used.

#### `feature_target_schema.yaml`
**Purpose:** Explicitly defines which columns are metadata, targets, or features.

**Structure:**
- `metadata_columns` - Always excluded (symbol, ts, date, etc.)
- `target_patterns` - Regex patterns for target columns
- `feature_families` - Feature family definitions with mode-specific rules
  - `ranking_mode` - More permissive rules for target ranking
  - `training_mode` - Strict rules for actual training

**Modes:**
- **Ranking Mode:** Allows basic OHLCV/TA features even if in `always_exclude`
- **Training Mode:** Enforces all leakage filters strictly

#### `target_configs.yaml`
**Purpose:** Defines all available targets (63 total).

**Structure:**
- `targets.{target_name}`:
  - `target_column` - Column name in dataset
  - `description` - What the target predicts
  - `use_case` - Trading use case
  - `top_n` - Number of top features to select
  - `method` - Feature selection method
  - `enabled` - Enable/disable flag

**Categories:**
- Triple Barrier (peak/valley/first_touch)
- Swing High/Low
- MFE (Maximum Favorable Excursion)
- MDD (Maximum Drawdown)

#### `multi_model_feature_selection.yaml`
**Purpose:** Configures multi-model consensus for feature selection.

**Structure:**
- `model_families.{family}`:
  - `enabled` - Enable/disable this model family
  - `importance_method` - native/SHAP/permutation
  - `weight` - Weight in consensus aggregation
  - `config` - Model-specific hyperparameters

**Model Families:**
- Tree-based: LightGBM, XGBoost, Random Forest
- Neural: MLP, Transformer, LSTM, CNN1D
- Ensemble: Ensemble, MultiTask

#### `feature_selection_config.yaml`
**Purpose:** General feature selection settings.

**Settings:**
- Feature importance aggregation methods
- Selection criteria
- Minimum feature requirements

#### `feature_groups.yaml`
**Purpose:** Defines feature groups for organization and analysis.

#### `comprehensive_feature_ranking.yaml` & `fast_target_ranking.yaml`
**Purpose:** Alternative ranking configurations for different use cases.

### 2. Training Configuration (`training_config/`)

#### `pipeline_config.yaml`
**Purpose:** Main training pipeline orchestration.

**Key Settings:**
- `isolation_timeout_seconds` - Maximum time per training job
- `max_rows_per_symbol` - Data loading limits
- `deterministic` - Reproducibility settings
- Sequential model configuration

#### `gpu_config.yaml`
**Purpose:** GPU device management and CUDA settings.

**Key Settings:**
- `vram_cap_mb` - Maximum VRAM usage
- `device_visibility` - Which GPUs to use
- TensorFlow/PyTorch GPU options
- CUDA device selection

#### `memory_config.yaml`
**Purpose:** Memory thresholds and cleanup policies.

**Key Settings:**
- `memory_cap_mb` - Maximum memory usage
- `chunk_size` - Data chunking for large datasets
- `cleanup_aggressiveness` - How aggressively to free memory

#### `preprocessing_config.yaml`
**Purpose:** Data preprocessing settings.

**Key Settings:**
- Normalization methods
- Missing value handling
- Feature scaling
- Data validation

#### `threading_config.yaml`
**Purpose:** Thread allocation and OpenMP/MKL policies.

**Key Settings:**
- `default_threads` - Default thread count
- `per_family_policies` - Thread allocation per model family
- OpenMP/MKL thread planning

#### `safety_config.yaml`
**Purpose:** Numerical stability guards and leakage detection.

**Key Settings:**
- **Numerical Stability:**
  - Feature clipping thresholds
  - Target capping limits
  - Gradient clipping
  - NaN/inf handling

- **Leakage Detection:**
  - `pre_scan` - Pre-training leak scan thresholds
  - `ranking` - Feature count requirements for ranking
  - `warning_thresholds` - Classification/regression warning thresholds
  - `auto_fix_thresholds` - CV score, training accuracy, R², correlation thresholds
  - `auto_fix_min_confidence` - Minimum confidence for auto-fix (default: 0.8)
  - `auto_fix_max_features_per_run` - Max features to fix per run (default: 20)
  - `auto_fix_enabled` - Enable/disable auto-fixer

- **Auto-Rerun:**
  - `auto_rerun.enabled` - Enable automatic rerun after fixes
  - `auto_rerun.max_reruns` - Maximum reruns per target (default: 3)
  - `auto_rerun.rerun_on_perfect_train_acc` - Rerun on perfect training accuracy
  - `auto_rerun.rerun_on_high_auc_only` - Rerun on high AUC alone

#### `callbacks_config.yaml`
**Purpose:** Training callback configuration.

**Key Settings:**
- Early stopping criteria
- Learning rate scheduling
- Model checkpointing
- Progress monitoring

#### `optimizer_config.yaml`
**Purpose:** Optimizer default settings.

**Key Settings:**
- Default optimizer parameters
- Learning rate schedules
- Weight decay
- Momentum settings

#### `system_config.yaml`
**Purpose:** System-level settings.

**Key Settings:**
- **Paths:**
  - `data_dir` - Default data directory
  - `output_dir` - Output directory (null = auto-generated)
  - `config_dir` - Main config directory
  - `excluded_features` - Path to excluded_features.yaml
  - `feature_registry` - Path to feature_registry.yaml
  - `feature_target_schema` - Path to feature_target_schema.yaml
  - `config_backup_dir` - Backup directory (null = CONFIG/backups/)

- **Backup System:**
  - `max_backups_per_target` - Maximum backups to keep (default: 20, 0 = no limit)
  - `enable_retention` - Enable automatic pruning

- **Environment:**
  - Shell settings (subprocess suppression)
  - Python settings (PYTHONPATH, hash seed)
  - Joblib settings (start method, temp folder)

- **Logging:**
  - Logging level (DEBUG, INFO, WARNING, ERROR)

#### `family_config.yaml`
**Purpose:** Model family policies and defaults.

**Key Settings:**
- Family-specific defaults
- Enabled/disabled families
- Family-specific overrides

#### `sequential_config.yaml`
**Purpose:** Sequential model (LSTM, Transformer) settings.

**Key Settings:**
- Sequence length
- Batch size
- Padding strategies
- Attention mechanisms

#### `first_batch_specs.yaml`
**Purpose:** First batch specifications for training.

### 3. Model Configuration (`model_config/`)

Each model has its own YAML file with hyperparameters.

**Supported Models (17 total):**
- **Tree-based:** LightGBM, XGBoost
- **Neural Networks:** MLP, Transformer, LSTM, CNN1D
- **Ensemble:** Ensemble, MultiTask
- **Feature Engineering:** VAE, GAN, GMMRegime
- **Probabilistic:** NGBoost, QuantileLightGBM
- **Advanced:** ChangePoint, FTRL, RewardBased, MetaLearning

**Variants:**
Each model config supports variants:
- `conservative` - Lower risk, more stable
- `aggressive` - Higher performance, more experimental
- `default` - Balanced settings

**Example Structure:**
```yaml
default:
  n_estimators: 100
  learning_rate: 0.1
  # ... more params

conservative:
  n_estimators: 200
  learning_rate: 0.05
  # ... more stable params

aggressive:
  n_estimators: 50
  learning_rate: 0.2
  # ... more experimental params
```

### 4. Backup System (`backups/`)

**Purpose:** Automatic backups of config files before auto-fixer modifications.

**Structure:**
```
CONFIG/backups/
└── {target_name}/              # Per-target organization
    └── {timestamp}/            # Timestamped snapshots (YYYYMMDD_HHMMSS_microseconds)
        ├── excluded_features.yaml
        ├── feature_registry.yaml
        └── manifest.json       # Backup metadata
```

**Manifest Contents:**
- `backup_version` - Schema version
- `source` - What created the backup (auto_fix_leakage)
- `target_name` - Target being evaluated
- `timestamp` - Backup timestamp
- `git_commit` - Git commit hash at backup time
- `backup_files` - List of backed-up files
- `excluded_features_path` - Original config path
- `feature_registry_path` - Original config path

**Retention Policy:**
- Keeps last N backups per target (configurable, default: 20)
- Automatic pruning of old backups
- Configurable via `system_config.yaml`

**Restoration:**
Use `LeakageAutoFixer.list_backups()` and `LeakageAutoFixer.restore_backup()` methods.

## Usage

### Loading Configurations

```python
from CONFIG.config_loader import (
    load_model_config,
    get_pipeline_config,
    get_gpu_config,
    get_safety_config,
    get_system_config,
    get_cfg
)

# Load model-specific config with variant
lightgbm_config = load_model_config("lightgbm", variant="aggressive")

# Load training configs
pipeline = get_pipeline_config()
gpu = get_gpu_config()
safety = get_safety_config()
system = get_system_config()

# Access nested values with dot notation
timeout = get_cfg("pipeline.isolation_timeout_seconds", default=7200)
vram_cap = get_cfg("gpu.vram_cap_mb", default=4096, config_name="gpu_config")
max_backups = get_cfg("system.backup.max_backups_per_target", default=20)
```

### Loading Feature/Target Configs

```python
import yaml
from pathlib import Path

# Load excluded features
with open("CONFIG/excluded_features.yaml") as f:
    excluded = yaml.safe_load(f)

# Load feature registry
with open("CONFIG/feature_registry.yaml") as f:
    registry = yaml.safe_load(f)

# Load target configs
with open("CONFIG/target_configs.yaml") as f:
    targets = yaml.safe_load(f)
```

## Configuration Hierarchy

1. **Model Configs** (`model_config/`) - Hyperparameters for specific model families
2. **Training Configs** (`training_config/`) - Pipeline, system, and resource settings
3. **Feature Configs** (root) - Feature filtering, registry, and schema
4. **Target Configs** (root) - Target definitions and settings
5. **Backup System** (`backups/`) - Automatic config backups

## Environment Variable Overrides

Most configuration values can be overridden via environment variables:

```bash
# Override GPU device
export CUDA_VISIBLE_DEVICES=0

# Override thread count
export OMP_NUM_THREADS=8

# Override timeout
export TRAINER_ISOLATION_TIMEOUT=10800

# Override data directory
export FOXML_DATA_DIR=/path/to/data
```

## Configuration Workflow

### 1. Feature Filtering Flow

```
Dataset Columns
    ↓
[feature_target_schema.yaml] → Classify as metadata/target/feature
    ↓
[excluded_features.yaml] → Remove always-excluded patterns
    ↓
[feature_registry.yaml] → Filter by allowed_horizons for target
    ↓
Pre-training leak scan (safety_config.yaml thresholds)
    ↓
Final Feature Set
```

### 2. Target Ranking Flow

```
[target_configs.yaml] → Discover available targets
    ↓
For each target:
    ↓
Filter features (using schema + excluded + registry)
    ↓
Pre-training leak scan
    ↓
Train models (multi_model_feature_selection.yaml)
    ↓
Detect leakage (safety_config.yaml thresholds)
    ↓
Auto-fix if needed (creates backup in backups/)
    ↓
Auto-rerun if enabled (safety_config.yaml)
    ↓
Rank targets by predictability score
```

### 3. Auto-Fixer Flow

```
Leakage Detected
    ↓
Create backup (backups/{target}/{timestamp}/)
    ↓
Detect leaking features
    ↓
Update excluded_features.yaml or feature_registry.yaml
    ↓
Reload configs
    ↓
Re-evaluate target (if auto-rerun enabled)
```

## Best Practices

1. **Never hardcode values** - Always load from config files
2. **Use defaults** - Provide sensible fallbacks when config unavailable
3. **Validate inputs** - Check config values before use
4. **Document changes** - Update configs with clear comments
5. **Test variants** - Verify all config variants work correctly
6. **Backup before manual edits** - The auto-fixer creates backups automatically, but manual edits should be backed up too
7. **Use feature registry** - Always specify `lag_bars` and `allowed_horizons` for new features
8. **Review backups** - Check `CONFIG/backups/` to understand what auto-fixer changed

## Migration Status

✅ **Complete** - All hardcoded configurations have been migrated to YAML files. The system maintains backward compatibility with hardcoded defaults during the transition period.

## Support

For configuration questions or issues, refer to:
- `config_loader.py` - Implementation details
- Individual config files - Inline documentation
- Training pipeline code - Usage examples
- [Config Loader API](../docs/02_reference/configuration/CONFIG_LOADER_API.md) - Complete API reference

## Related Documentation

- [Config Basics](../docs/01_tutorials/configuration/CONFIG_BASICS.md) - Configuration fundamentals tutorial
- [Config Examples](../docs/01_tutorials/configuration/CONFIG_EXAMPLES.md) - Example configurations
- [Advanced Config](../docs/01_tutorials/configuration/ADVANCED_CONFIG.md) - Advanced configuration guide
- [Config Loader API](../docs/02_reference/configuration/CONFIG_LOADER_API.md) - Complete API reference
- [Config Schema](../docs/02_reference/api/CONFIG_SCHEMA.md) - Configuration schema documentation
- [Environment Variables](../docs/02_reference/configuration/ENVIRONMENT_VARIABLES.md) - Environment variable overrides
- [Model Config Reference](../docs/02_reference/models/MODEL_CONFIG_REFERENCE.md) - Model-specific configurations
- [Intelligence Layer Overview](../docs/03_technical/research/INTELLIGENCE_LAYER.md) - How configs are used in intelligent training
- [Leakage Analysis](../docs/03_technical/research/LEAKAGE_ANALYSIS.md) - Leakage detection configuration details
