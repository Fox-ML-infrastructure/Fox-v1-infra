# Testing Quick Reference

Quick reference for running test commands with the new config-driven approach.

## Your Test Command

Based on your requirements, here's the new command:

```bash
python -m TRAINING.orchestration.intelligent_trainer \
    --data-dir "data/data_labeled/interval=5m" \
    --symbols AAPL MSFT GOOGL TSLA NVDA \
    --output-dir "test_e2e_ranking_unified" \
    --families lightgbm xgboost random_forest catboost neural_network lasso mutual_information univariate_selection
```

## What Happens Automatically

When you use `--output-dir "test_e2e_ranking_unified"`, the system:

1. **Detects "test" in output-dir** → automatically uses `test.intelligent_training` config
2. **Applies test settings** from `CONFIG/pipeline/pipeline.yaml` (or `CONFIG/training_config/pipeline_config.yaml` for backward compatibility):
   - `top_n_targets: 23`
   - `max_targets_to_evaluate: 23`
   - `top_m_features: 50`
   - `min_cs: 3`
   - `max_rows_per_symbol: 5000`
   - `max_rows_train: 10000`

**No CLI arguments needed for these!** All from config.

## Customizing Test Settings

Edit `CONFIG/pipeline/pipeline.yaml` (or `CONFIG/training_config/pipeline_config.yaml` for backward compatibility):

```yaml
test:
  intelligent_training:
    top_n_targets: 23          # Change this
    max_targets_to_evaluate: 23  # Change this
    top_m_features: 50          # Change this
    min_cs: 3                   # Change this
    max_rows_per_symbol: 5000   # Change this
    max_rows_train: 10000       # Change this
```

Then run the same command - it will use your updated settings.

## Production Command (No Test Config)

For production runs, use an output-dir without "test":

```bash
python -m TRAINING.orchestration.intelligent_trainer \
    --data-dir "data/data_labeled/interval=5m" \
    --symbols AAPL MSFT GOOGL TSLA NVDA \
    --output-dir "production_run_2025" \
    --families lightgbm xgboost random_forest catboost neural_network lasso mutual_information univariate_selection
```

This uses default `intelligent_training` config (top_n_targets=5, top_m_features=100, etc.).

## Quick Comparison

| Setting | Old CLI | New Config Location |
|---------|---------|---------------------|
| `top_n_targets` | `--top-n-targets 23` | `test.intelligent_training.top_n_targets` |
| `top_m_features` | `--top-m-features 50` | `test.intelligent_training.top_m_features` |
| `min_cs` | `--min-cs 3` | `test.intelligent_training.min_cs` |
| `max_rows_per_symbol` | `--max-rows-per-symbol 5000` | `test.intelligent_training.max_rows_per_symbol` |
| `max_rows_train` | `--max-rows-train 10000` | `test.intelligent_training.max_rows_train` |
| `families` | `--families ...` | Still in CLI (manual override allowed) |

## See Also

- [Intelligent Training Tutorial](INTELLIGENT_TRAINING_TUTORIAL.md) - Complete guide
- [CLI vs Config Separation](../../03_technical/design/CLI_CONFIG_SEPARATION.md) - Policy document
- [Config Examples](../configuration/CONFIG_EXAMPLES.md) - More examples
