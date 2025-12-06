# Validation Methodology

Methods for validating models and preventing overfitting.

## Overview

Proper validation is critical for realistic performance estimation. This document describes validation methods used in the system.

## Walk-Forward Validation

### Purpose

Simulate real trading conditions by:
1. Training on historical data
2. Testing on future data
3. Rolling forward in time

### Configuration

> **Note**: Walk-forward validation is currently planned but not yet implemented. The `TRAINING.walkforward` module does not exist. Configuration is available in `ALPACA_trading/config/base.yaml`.

For temporal validation, use `PurgedTimeSeriesSplit`:

```python
from scripts.utils.purged_time_series_split import PurgedTimeSeriesSplit
from sklearn.model_selection import cross_val_score

# Use purged time-series split to prevent temporal leakage
purged_cv = PurgedTimeSeriesSplit(n_splits=5, purge_overlap=17)
cv_scores = cross_val_score(trainer, X, y, cv=purged_cv)
```

### Benefits

- Prevents look-ahead bias
- Realistic performance estimates
- Tests temporal stability

## Early Stopping

### Purpose

Stop training when validation performance stops improving.

### Implementation

```python
config = {
    "early_stopping_rounds": 50,
    "n_estimators": 1000
}
```

### Benefits

- Prevents overfitting
- Reduces training time
- Improves generalization

## Regularization

### L1/L2 Regularization

```python
config = {
    "reg_alpha": 0.1,   # L1 (Lasso)
    "reg_lambda": 0.1   # L2 (Ridge)
}
```

### Dropout (Neural Networks)

```python
config = {
    "dropout": 0.3  # 30% dropout
}
```

## Best Practices

1. **Always Use Walk-Forward**: Never use random train/test splits for time series
2. **Enable Early Stopping**: Always use early stopping
3. **Regularize**: Use conservative variants for production
4. **Monitor**: Track train vs validation performance

## See Also

- [Walk-Forward Validation](../../01_tutorials/training/WALKFORWARD_VALIDATION.md) - Tutorial
- [Training Optimization Guide](../../../TRAINING/TRAINING_OPTIMIZATION_GUIDE.md) - Optimization tips

