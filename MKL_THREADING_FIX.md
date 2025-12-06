# MKL Threading Layer Fix

## Problem

Intel MKL uses Intel OpenMP (libiomp5) by default, which can conflict with GNU OpenMP (libgomp) used by LightGBM and XGBoost. This can cause:
- Segfaults during training
- Threading conflicts
- Performance degradation
- Unpredictable behavior

## Solution

Set `MKL_THREADING_LAYER=GNU` to force MKL to use GNU OpenMP (libgomp) instead of Intel OpenMP (libiomp5).

## Implementation

### Automatic (Recommended)
The fix is now automatically applied in `TRAINING/common/determinism.py` via `set_global_determinism()`, which sets `MKL_THREADING_LAYER=GNU` globally.

### Manual (For Shell Sessions)
Add to your shell profile (`~/.bashrc` or `~/.zshrc`):
```bash
export MKL_THREADING_LAYER=GNU
```

Or set per-session:
```bash
export MKL_THREADING_LAYER=GNU
conda activate trader_env
```

## What This Does

- **Before**: MKL uses Intel OpenMP (libiomp5) → conflicts with libgomp → potential segfaults
- **After**: MKL uses GNU OpenMP (libgomp) → same runtime as LightGBM/XGBoost → no conflicts

## Verification

Check if it's set:
```bash
echo $MKL_THREADING_LAYER
# Should output: GNU
```

Or in Python:
```python
import os
print(os.getenv("MKL_THREADING_LAYER"))  # Should print: GNU
```

## Impact

- ✅ Eliminates OpenMP runtime conflicts
- ✅ Prevents segfaults in scipy.linalg.solve (Ridge models)
- ✅ Stable threading for LightGBM/XGBoost
- ✅ No performance penalty (MKL still uses all cores via libgomp)
