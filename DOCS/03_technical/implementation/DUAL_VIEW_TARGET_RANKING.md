# Dual-View Target Ranking Implementation

## Overview

The target ranking system now supports **two evaluation views** per target, exactly like feature selection:

1. **CROSS_SECTIONAL view**: Pooled cross-sectional samples (existing implementation)
2. **SYMBOL_SPECIFIC view**: Evaluate the same target separately on each symbol's own time series
3. **LOSO view** (optional): Leave-One-Symbol-Out evaluation

This ensures **target ranking → feature ranking → training** stays consistent with the same view.

## Architecture

### Evaluation Matrix

For each `target`:

#### View A — Cross-sectional (always run)
- Dataset: `(timestamp, symbol)` stacked table
- Split: Time-based purged/embargo CV
- Output: `cs_metrics` (single score per target)

#### View B — Symbol-specific (enabled by default)
- Loop symbols `s in universe`:
  - Dataset: Only rows where `symbol == s`
  - Split: Time-based purged/embargo CV (same horizon-derived purge/embargo)
  - Output: `sym_metrics[s]` (score per symbol)

#### View C — LOSO (optional, high value)
- Train on all symbols except `s`, validate on `s` (time-aligned + purged)
- Answers: "Is this target learnable cross-sectionally but generalizes to unseen symbols?"

### Reproducibility Structure

Results are stored in a symmetric structure:

```
REPRODUCIBILITY/
  TARGET_RANKING/
    {target_name}/
      CROSS_SECTIONAL/
        cohort={cohort_id}/
          metrics.json
          metadata.json
      SYMBOL_SPECIFIC/
        symbol={symbol}/
          cohort={cohort_id}/
            metrics.json
            metadata.json
      routing_decisions.json  # Top-level routing decisions
```

### Routing Decisions

Each target gets a deterministic routing decision:

- **CROSS_SECTIONAL only**: `cs_auc >= T_cs` AND `frac_symbols_good >= T_frac`
- **SYMBOL_SPECIFIC only**: `cs_auc < T_cs` AND `exists symbol with auc >= T_sym`
- **BOTH**: `cs_auc >= T_cs` BUT performance is concentrated (high IQR / low frac_symbols_good)
- **BLOCKED**: `cs_auc >= 0.90` OR `any symbol auc >= 0.95` → require label/split sanity tests

## Usage

### Basic Usage (Backward Compatible)

```python
from TRAINING.ranking import rank_targets

# Default: Runs CROSS_SECTIONAL view only (backward compatible)
results = rank_targets(
    targets=targets_dict,
    symbols=['AAPL', 'MSFT', 'GOOGL'],
    data_dir=Path("data"),
    model_families=['lightgbm', 'random_forest'],
    output_dir=Path("results")
)
```

### Dual-View Usage

Dual-view is **enabled by default**. To disable:

```yaml
# CONFIG/target_ranking_config.yaml
target_ranking:
  enable_symbol_specific: true  # Default: true
  enable_loso: false  # Default: false (optional)
  routing:
    cs_auc_threshold: 0.65
    frac_symbols_good_threshold: 0.5
    symbol_auc_threshold: 0.60
    suspicious_cs_auc: 0.90
    suspicious_symbol_auc: 0.95
```

### Accessing Routing Decisions

```python
import json
from pathlib import Path

# Load routing decisions
routing_file = Path("results/REPRODUCIBILITY/TARGET_RANKING/routing_decisions.json")
with open(routing_file) as f:
    routing_data = json.load(f)

# Get routing for a specific target
target_route = routing_data['routing_decisions']['y_will_peak_60m_0.8']
print(f"Route: {target_route['route']}")  # 'CROSS_SECTIONAL', 'SYMBOL_SPECIFIC', 'BOTH', or 'BLOCKED'
print(f"Reason: {target_route['reason']}")
print(f"Winner symbols: {target_route['winner_symbols']}")  # For SYMBOL_SPECIFIC/BOTH
```

### Feature Selection with View Consistency

Feature selection **automatically respects** the view from target ranking:

```python
from TRAINING.ranking import select_features_for_target

# For cross-sectional training (uses CROSS_SECTIONAL view)
features_cs = select_features_for_target(
    target_column="y_will_peak_60m_0.8",
    symbols=['AAPL', 'MSFT', 'GOOGL'],
    data_dir=Path("data"),
    view="CROSS_SECTIONAL",  # Must match target ranking view
    symbol=None
)

# For symbol-specific training (uses SYMBOL_SPECIFIC view)
features_sym = select_features_for_target(
    target_column="y_will_peak_60m_0.8",
    symbols=['AAPL'],  # Single symbol
    data_dir=Path("data"),
    view="SYMBOL_SPECIFIC",
    symbol="AAPL"  # Required for SYMBOL_SPECIFIC
)
```

## Integration with Existing Reproducibility Suite

### ✅ Fully Compatible

The dual-view system integrates seamlessly with your existing reproducibility suite:

1. **RunContext** now includes `view` and `symbol` fields
2. **ReproducibilityTracker** automatically stores view/symbol metadata
3. **Cohort directories** are organized by view: `TARGET_RANKING/{view}/{target}/symbol={symbol}/cohort={cohort_id}/`
4. **Metadata.json** includes `view` field for TARGET_RANKING stage
5. **Index.parquet** tracks view/symbol for trend analysis

### Artifact Layout

```
REPRODUCIBILITY/
  TARGET_RANKING/
    y_will_peak_60m_0.8/
      CROSS_SECTIONAL/
        cohort=cs_..._f2849563/
          metadata.json  # Contains: view="CROSS_SECTIONAL", symbol=null
          metrics.json
      SYMBOL_SPECIFIC/
        symbol=AAPL/
          cohort=cs_..._a1b2c3d4/
            metadata.json  # Contains: view="SYMBOL_SPECIFIC", symbol="AAPL"
            metrics.json
      routing_decisions.json  # Top-level routing summary
```

## Gating Rules (Prevents Explosion)

Feature ranking is **gated** to prevent combinatorial explosion:

- **Cross-sectional**: Feature-rank only **top M** targets globally (e.g., 5–10)
- **Symbol-specific**: Feature-rank only **top K** targets per symbol (e.g., 2–5)

This prevents `23 targets × 5 symbols × 300 features × CV` from becoming unmanageable.

## Downstream Training Contract

Training planner receives:

```python
{
    'targets_cs': ['y_will_peak_60m_0.8', ...],  # Top M cross-sectional targets
    'targets_by_symbol': {
        'AAPL': ['y_will_valley_60m_0.8', ...],  # Top K per symbol
        'MSFT': [...]
    },
    'features_by_target_cs': {
        'y_will_peak_60m_0.8': ['feature1', 'feature2', ...]
    },
    'features_by_target_sym': {
        'AAPL': {
            'y_will_valley_60m_0.8': ['feature3', 'feature4', ...]
        }
    }
}
```

## Configuration

Add to `CONFIG/target_ranking_config.yaml`:

```yaml
target_ranking:
  # Enable/disable views
  enable_symbol_specific: true
  enable_loso: false  # Optional, high value
  
  # Routing thresholds
  routing:
    cs_auc_threshold: 0.65  # Minimum CS AUC for CROSS_SECTIONAL route
    frac_symbols_good_threshold: 0.5  # Minimum fraction of symbols with good performance
    symbol_auc_threshold: 0.60  # Minimum symbol AUC for SYMBOL_SPECIFIC route
    suspicious_cs_auc: 0.90  # CS AUC that triggers BLOCKED
    suspicious_symbol_auc: 0.95  # Symbol AUC that triggers BLOCKED
```

## Backward Compatibility

✅ **Fully backward compatible**:
- Default behavior: Runs CROSS_SECTIONAL view only (same as before)
- Existing code continues to work without changes
- New `view` and `symbol` parameters are optional (default to CROSS_SECTIONAL)
- Results structure extends existing structure (doesn't break existing tools)

## Next Steps

1. ✅ **Load routing decisions in intelligent_trainer**: Implemented - `intelligent_trainer` now loads routing decisions and passes appropriate `view`/`symbol` to feature selection
2. **Add placebo test per symbol**: Before trusting "symbol-specific strong" targets, run placebo test (shuffle labels) and assert AUC ~ 0.5
3. **Implement LOSO CV splitter**: Currently LOSO uses combined data; needs dedicated CV splitter that trains on all-but-one symbol, validates on one symbol

## Status

- ✅ Dual-view evaluation implemented
- ✅ Routing decision logic implemented
- ✅ Reproducibility integration complete (2025-12-12: Fixed `log_comparison()` signature, view/symbol metadata correctly passed through)
- ✅ Feature selection view consistency implemented
- ✅ Intelligent trainer integration complete
- ✅ ResolvedConfig integration (2025-12-12: Consistent logging and purge/embargo calculation)
- ⏳ Placebo test per symbol (future enhancement)
- ⏳ LOSO CV splitter (future enhancement)

## Example: Using Routing Decisions

```python
from TRAINING.ranking.target_routing import load_routing_decisions
from TRAINING.ranking import select_features_for_target

# Load routing decisions
routing = load_routing_decisions(output_dir / "REPRODUCIBILITY" / "TARGET_RANKING" / "routing_decisions.json")

# For each target, use appropriate view
for target_name, route_info in routing.items():
    route = route_info['route']
    
    if route == 'CROSS_SECTIONAL':
        # Use cross-sectional feature selection
        features = select_features_for_target(
            target_column=target_name,
            symbols=all_symbols,
            view="CROSS_SECTIONAL"
        )
    elif route == 'SYMBOL_SPECIFIC':
        # Use symbol-specific feature selection for winner symbols
        for symbol in route_info['winner_symbols']:
            features = select_features_for_target(
                target_column=target_name,
                symbols=[symbol],
                view="SYMBOL_SPECIFIC",
                symbol=symbol
            )
    elif route == 'BOTH':
        # Use both views
        # Cross-sectional features
        features_cs = select_features_for_target(
            target_column=target_name,
            symbols=all_symbols,
            view="CROSS_SECTIONAL"
        )
        # Symbol-specific features for winner symbols
        for symbol in route_info['winner_symbols']:
            features_sym = select_features_for_target(
                target_column=target_name,
                symbols=[symbol],
                view="SYMBOL_SPECIFIC",
                symbol=symbol
            )
    elif route == 'BLOCKED':
        # Skip or require manual review
        logger.warning(f"Target {target_name} is BLOCKED: {route_info['reason']}")
```

**Note**: The `intelligent_trainer` automatically handles routing decisions - you don't need to manually implement this logic unless you're building custom workflows.
