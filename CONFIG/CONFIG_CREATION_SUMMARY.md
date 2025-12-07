# Configuration Files Creation Summary

**Branch:** `feature/centralized-configs`  
**Date:** 2025-01-06  
**Status:** ✅ All config files created and validated

## Overview

Created comprehensive configuration files based on the configuration audit (`docs/internal/CONFIG_LOCATIONS_AUDIT.md`). These configs centralize all hardcoded settings found throughout the TRAINING directory.

## Files Created

### Training Configuration Files (9 new files)

1. **`training_config/pipeline_config.yaml`**
   - Main training pipeline settings
   - Timeouts (7200s isolation timeout)
   - Data processing limits (max_samples_per_symbol, cross-sectional limits)
   - Sequential model settings (lookback, backend)
   - Test/production defaults
   - Paths and determinism settings
   - Model family lists

2. **`training_config/gpu_config.yaml`**
   - GPU device selection and visibility
   - TensorFlow GPU settings (allocator, allow_growth, threads)
   - VRAM caps per family (4096MB default)
   - Mixed precision settings
   - XGBoost and PyTorch GPU configuration
   - CUDA library paths

3. **`training_config/memory_config.yaml`**
   - Memory thresholds (80% warning, 90% high warning)
   - Chunking settings (1M rows per chunk)
   - Memory caps for child processes
   - Cleanup and monitoring settings

4. **`training_config/preprocessing_config.yaml`**
   - Imputation strategies (median default)
   - Scaling methods (StandardScaler default)
   - Feature selection (50 features, 0.001 min importance)
   - Validation splits (20% test, 15% val/test for sequential)
   - NaN handling (10% threshold)
   - Data validation checks

5. **`training_config/threading_config.yaml`**
   - Default thread counts (calculated from CPU count)
   - Thread policies (omp_heavy, cpu_blas_only, tf_gpu, torch_gpu, tf_cpu)
   - OpenMP and MKL settings
   - Per-family thread allocation (ChangePoint, QuantileLightGBM, Ensemble)
   - Thread planning settings

6. **`training_config/safety_config.yaml`**
   - Feature clipping ([-1000, 1000])
   - Target capping (15 MAD)
   - Numerical stability (safe exp bounds: -40 to 40)
   - Gradient clipping (clipnorm=1.0, max_norm=1.0)
   - Model output validation
   - Safety guards (min_history_bars=120, max_na_fraction=0.05)

7. **`training_config/callbacks_config.yaml`**
   - Early stopping (patience=10 default, LSTM=5)
   - Learning rate reduction (patience=5, factor=0.5, min_lr=1e-6)
   - Model checkpointing (disabled by default)
   - TensorBoard/CSV logging (disabled by default)
   - Progress bar settings

8. **`training_config/optimizer_config.yaml`**
   - Adam optimizer defaults (lr=1e-3, clipnorm=1.0)
   - AdamW optimizer defaults (lr=1e-3, weight_decay=0.0)
   - SGD and RMSprop defaults
   - Per-model learning rate overrides (MultiTask=3e-4)

9. **`training_config/system_config.yaml`**
   - System paths (data_dir, output_dir, temp_dir, joblib_temp)
   - Environment variables (shell, term, inputrc, pythonpath)
   - Logging configuration (level, component-specific levels)
   - Isolation runner settings (timeout, memory caps)
   - Security settings (readline suppression, MKL guard)
   - Performance settings (Polars, cross-sectional alignment)

### Documentation

- **`training_config/README.md`** - Documentation for all training config files

## Existing Configs (Not Modified)

- `model_config/*.yaml` - 17 model config files (already exist)
- `training_config/family_config.yaml` - Family thread policies (already exists)
- `training_config/first_batch_specs.yaml` - First batch specs (already exists)
- `training_config/sequential_config.yaml` - Sequential config (already exists)

## Configuration Coverage

### ✅ High Priority (User-Facing)
- [x] Model hyperparameters (existing model configs)
- [x] Training pipeline settings
- [x] GPU settings
- [x] Data processing limits

### ✅ Medium Priority (Occasionally Changed)
- [x] Threading policies
- [x] Memory management
- [x] Preprocessing
- [x] Callbacks

### ✅ Low Priority (System-Level)
- [x] System paths
- [x] Safety guards
- [x] Optimizer defaults

## Next Steps

1. **Update `config_loader.py`** to support loading these new training configs
2. **Update codebase** to load configs instead of hardcoded values:
   - `train_with_strategies.py` - Main training script
   - `common/threads.py` - Threading configuration
   - `common/runtime_policy.py` - Runtime policies
   - `memory/memory_manager.py` - Memory settings
   - `utils/data_preprocessor.py` - Preprocessing
   - All `model_fun/*_trainer.py` files - Model defaults
3. **Add environment variable overrides** for runtime configuration
4. **Add validation** for config values
5. **Update documentation** with usage examples

## Validation

All YAML files have been validated and are syntactically correct.

## Notes

- Configs use `null` for optional values that should use defaults
- Environment variable overrides will be supported during integration
- Configs are designed to be backward-compatible during migration
- Some settings (like family classifications) may remain code-based for type safety
- TabCNN, TabLSTM, TabTransformer use CNN1D, LSTM, Transformer configs respectively (handled via aliases in config_loader)

