# Training Configuration Files

This directory contains centralized configuration files for the training pipeline. These configs will replace hardcoded values throughout the codebase during the Phase 2 refactor.

## Configuration Files

### Core Pipeline Configs

- **`pipeline_config.yaml`** - Main training pipeline settings
  - Timeouts, data processing limits
  - Sequential model settings
  - Test/production defaults
  - Paths and determinism settings
  - Model family lists

- **`gpu_config.yaml`** - GPU and CUDA configuration
  - Device selection and visibility
  - TensorFlow/PyTorch GPU settings
  - VRAM management and caps
  - Mixed precision settings
  - XGBoost GPU configuration

- **`memory_config.yaml`** - Memory management
  - Memory thresholds and warnings
  - Chunking settings
  - Memory caps for child processes
  - Cleanup and monitoring settings

- **`preprocessing_config.yaml`** - Data preprocessing
  - Imputation strategies
  - Scaling methods
  - Feature selection
  - Validation splits
  - NaN handling

- **`threading_config.yaml`** - Threading and resource management
  - Default thread counts
  - Thread policies (omp_heavy, cpu_blas_only, tf_gpu, etc.)
  - OpenMP and MKL settings
  - Per-family thread allocation

- **`safety_config.yaml`** - Safety and numerical stability
  - Feature clipping
  - Target capping
  - Numerical stability guards
  - Gradient clipping
  - Model output validation

- **`callbacks_config.yaml`** - Training callbacks
  - Early stopping configuration
  - Learning rate reduction
  - Model checkpointing
  - TensorBoard/CSV logging

- **`optimizer_config.yaml`** - Optimizer settings
  - Adam/AdamW/SGD/RMSprop defaults
  - Per-model learning rate overrides
  - Optimizer hyperparameters

- **`system_config.yaml`** - System-level settings
  - Paths and directories
  - Environment variables
  - Logging configuration
  - Isolation runner settings
  - Security and safety settings

### Existing Configs

- **`family_config.yaml`** - Family thread policies and runtime behavior (already exists)
- **`first_batch_specs.yaml`** - First batch specifications (already exists)
- **`sequential_config.yaml`** - Sequential model configuration (already exists)

## Usage

These configs are designed to be loaded by `CONFIG/config_loader.py`:

```python
from CONFIG.config_loader import load_training_config

# Load a training config
pipeline_config = load_training_config("pipeline_config")
gpu_config = load_training_config("gpu_config")
memory_config = load_training_config("memory_config")
```

## Migration Status

**Status:** Config files created, ready for code integration

These config files contain all settings identified in the configuration audit (`docs/internal/CONFIG_LOCATIONS_AUDIT.md`). The next step is to update the codebase to load and use these configs instead of hardcoded values.

## Priority Order for Integration

1. **High Priority** (User-facing, frequently changed):
   - Model hyperparameters (already partially implemented)
   - Training pipeline settings (`pipeline_config.yaml`)
   - GPU settings (`gpu_config.yaml`)
   - Data processing limits (`pipeline_config.yaml`)

2. **Medium Priority** (Occasionally changed):
   - Threading policies (`threading_config.yaml`)
   - Memory management (`memory_config.yaml`)
   - Preprocessing (`preprocessing_config.yaml`)
   - Callbacks (`callbacks_config.yaml`)

3. **Low Priority** (Rarely changed, system-level):
   - System paths (`system_config.yaml`)
   - Safety guards (`safety_config.yaml`)
   - Optimizer defaults (`optimizer_config.yaml`)

## Notes

- All configs use `null` for optional values that should use defaults
- Environment variable overrides will be supported during integration
- Configs are designed to be backward-compatible during migration
- Some settings (like family classifications) may remain code-based for type safety

