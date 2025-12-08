# Feature Selection Module Configs

This directory contains configuration files for the feature selection pipeline.

## Files

- `multi_model.yaml` - Multi-model feature selection configuration
  - Model families (lightgbm, xgboost, random_forest, etc.)
  - Aggregation strategies
  - Sampling settings
  - SHAP/permutation importance settings

## Usage

Feature selection configs are loaded by `CONFIG/config_builder.py` and merged with experiment configs.

## Migration

The legacy `CONFIG/multi_model_feature_selection.yaml` will be moved here during Phase 2 of the config refactor.

