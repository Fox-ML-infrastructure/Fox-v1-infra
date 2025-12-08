# Experiment Configs

This directory contains experiment-level configuration files. Each experiment config defines:
- What data to use (symbols, data_dir, interval)
- What target to predict
- Which model families to use
- Overrides for specific modules

## Example

See `fwd_ret_60m_test.yaml` for an example experiment config.

## Usage

```python
from CONFIG.config_builder import load_experiment_config, build_feature_selection_config

exp_cfg = load_experiment_config("fwd_ret_60m_test")
fs_cfg = build_feature_selection_config(exp_cfg)
```

