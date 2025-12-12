# Quick Start

Installation and basic usage.

## Prerequisites

- Python 3.11+
- 8GB+ RAM (16GB+ recommended)
- GPU optional (CUDA 11.8+ if using GPU)

## Installation

```bash
git clone <repository-url>
cd trader

# Create environment
conda env create -f environment.yml
conda activate trader

# Or use pip
pip install -r requirements.txt
```

## Verify Installation

```bash
python --version  # Should be 3.11+
python -c "import torch; print(torch.cuda.is_available())"  # GPU check
```

## Data Pipeline

```bash
# Verify data exists
ls data/data_labeled/interval=5m/

# Run feature engineering
python DATA_PROCESSING/features/comprehensive_builder.py \
    --config config/features.yaml \
    --output-dir DATA_PROCESSING/data/processed/

# Generate targets
python DATA_PROCESSING/pipeline/barrier_pipeline.py \
    --input-dir data/data_labeled/interval=5m/ \
    --output-dir DATA_PROCESSING/data/labeled/
```

## Model Training

### Intelligent Training Pipeline (Recommended)

The intelligent training pipeline automates the complete workflow: target ranking → feature selection → training plan generation → model training:

```bash
# One-command end-to-end pipeline
python -m TRAINING.orchestration.intelligent_trainer \
    --data-dir "data/data_labeled/interval=5m" \
    --symbols AAPL MSFT GOOGL \
    --auto-targets \
    --auto-features \
    --output-dir "my_training_run"
```

**What it does:**
1. Ranks all targets → selects top N
2. Selects features per target
3. Generates routing plan → training plan
4. Trains models using plan (2-stage: CPU → GPU)

**For testing - auto-detects test config when output-dir contains "test":**
```bash
python -m TRAINING.orchestration.intelligent_trainer \
    --data-dir "data/data_labeled/interval=5m" \
    --symbols AAPL MSFT GOOGL TSLA NVDA \
    --output-dir "test_e2e_run" \
    --auto-targets \
    --auto-features
```

**Configuration:**
- All settings come from `CONFIG/training_config/pipeline_config.yaml`
- Test config auto-detected when output-dir contains "test"
- Training plan automatically generated and used for filtering
- See [Intelligent Training Tutorial](../01_tutorials/training/INTELLIGENT_TRAINING_TUTORIAL.md) for details
- See [Training Routing Guide](../02_reference/training_routing/README.md) for routing system details

### Manual Training (Programmatic)

```python
from TRAINING.model_fun import LightGBMTrainer
from CONFIG.config_loader import load_model_config
import polars as pl
import numpy as np

# Load data
df = pl.read_parquet("DATA_PROCESSING/data/labeled/AAPL_labeled.parquet")

# Prepare features and targets
feature_cols = [col for col in df.columns 
                if not col.startswith('y_') and col not in ['ts', 'symbol']]
X = df[feature_cols].to_pandas()
y = df['y_will_peak'].to_pandas()

# Load config (all hyperparameters load from config - Single Source of Truth)
config = load_model_config("lightgbm", variant="conservative")

# Train (fully reproducible: same config → same results)
trainer = LightGBMTrainer(config)
trainer.train(X, y)

# Feature importance (returns numpy array)
importance = trainer.get_feature_importance()
if importance is not None:
    # Get top 20 features
    top_indices = np.argsort(importance)[-20:][::-1]
    print("Top 20 features:")
    for idx in top_indices:
        print(f"  Feature {idx}: {importance[idx]:.4f}")
```

## Troubleshooting

**Import errors**: Ensure conda environment is activated.

**GPU not detected**: Install CUDA toolkit and PyTorch with CUDA support.

**Out of memory**: Use streaming builder or reduce batch size.

## Related Documentation

- [Getting Started](GETTING_STARTED.md)
- [Architecture Overview](ARCHITECTURE_OVERVIEW.md)
- [Documentation Index](../INDEX.md)
