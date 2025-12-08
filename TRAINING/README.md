# TRAINING Module

This directory contains the core training infrastructure for FoxML Core.

## Documentation

**All training documentation has been moved to the `docs/` folder for better organization.**

See the [Training Documentation](../../docs/INDEX.md#tier-b-tutorials--walkthroughs) for complete guides.

## Quick Links

- [Intelligent Training Tutorial](../../docs/01_tutorials/training/INTELLIGENT_TRAINING_TUTORIAL.md) - Automated target ranking and feature selection
- [Model Training Guide](../../docs/01_tutorials/training/MODEL_TRAINING_GUIDE.md) - Manual training workflow
- [Feature Selection Tutorial](../../docs/01_tutorials/training/FEATURE_SELECTION_TUTORIAL.md) - Feature selection workflow
- [Walk-Forward Validation](../../docs/01_tutorials/training/WALKFORWARD_VALIDATION.md) - Validation workflow
- [Experiments Workflow](../../docs/01_tutorials/training/EXPERIMENTS_WORKFLOW.md) - 3-phase training workflow
- [Training Optimization](../../docs/03_technical/implementation/TRAINING_OPTIMIZATION_GUIDE.md) - Optimization guide
- [Feature Selection Implementation](../../docs/03_technical/implementation/FEATURE_SELECTION_GUIDE.md) - Implementation details

## Directory Structure

```
TRAINING/
├── orchestration/          # Intelligent training pipeline
├── ranking/                # Target ranking system
├── model_fun/              # Model trainers (17 models)
├── strategies/             # Training strategies
├── utils/                  # Utilities (data loading, leakage filtering, etc.)
├── common/                 # Common utilities (safety, threading, etc.)
├── preprocessing/          # Data preprocessing
├── processing/             # Data processing
├── features/               # Feature engineering
├── datasets/               # Dataset classes
├── models/                 # Model wrappers and registry
├── EXPERIMENTS/            # 3-phase training workflow
└── train.py                # Main training entry point
```

For detailed documentation on each component, see the [Training Documentation](../../docs/INDEX.md#tier-b-tutorials--walkthroughs).

