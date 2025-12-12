# Bayesian Decision Policy

## Overview

The Bayesian patch policy implements **Thompson sampling** over discrete patch templates to learn which config patches improve performance. It's a closed-loop controller that:

1. **Observes** past run outcomes (from `index.parquet`)
2. **Learns** which patches work best (per cohort+segment)
3. **Recommends** patches with confidence scores
4. **Updates** beliefs after each run

## Architecture

### Components

1. **PatchTemplate**: Discrete action templates (e.g., "cap_features_10pct", "tighten_routing_20pct")
2. **ArmStats**: Posterior statistics per template (mean, variance, sample count)
3. **BayesState**: Per-cohort+segment state (persisted to JSON)
4. **BayesianPatchPolicy**: Thompson sampling policy that selects best arm

### Integration

- Hooks into existing `DecisionEngine` (no framework rewrite)
- Works alongside rule-based policies (Bayesian takes precedence if high-confidence)
- State persisted to `REPRODUCIBILITY/bayes_state/{cohort_id}_seg{segment_id}.json`
- Receipts saved to `REPRODUCIBILITY/patches/` (same as rule-based decisions)

## How It Works

### 1. Patch Templates

Default templates (discrete action space):

- `cap_features_10pct`: Reduce max_features by 10%
- `cap_features_20pct`: Reduce max_features by 20% (max clamp)
- `tighten_routing_10pct`: Increase routing thresholds by 10%
- `tighten_routing_20pct`: Increase routing thresholds by 20% (max clamp)
- `freeze_features`: Freeze feature selection to cached

Each template maps to existing action codes (`cap_features`, `tighten_routing`, etc.).

### 2. Reward Computation

Reward = `current_metric - median(baseline_metrics)`

- Baseline = recent runs in same cohort+segment (without patches, or rolling median)
- Metric = `cs_auc` by default (configurable via `reward_metric`)

### 3. Thompson Sampling

For each template (arm):
- Sample reward: `reward_hat ~ Normal(mean, sqrt(var))`
- Select arm with highest sampled reward
- This balances exploration vs exploitation automatically

### 4. Decision Levels

- **Level 3** (auto-apply): `P(improve) >= 0.8` AND `expected_gain >= 0.01`
- **Level 2** (recommend): `P(improve) >= 0.6` AND `expected_gain >= 0.005`
- **Level 1** (warning): `P(improve) >= 0.4`
- **Level 0** (no action): Otherwise

### 5. State Update

After each run:
- Compute reward (current vs baseline)
- Update arm stats (exponential moving average with recency decay)
- Persist state to JSON

## Configuration

Enable in `intelligent_training_config.yaml`:

```yaml
decisions:
  use_bayesian: true
  bayesian:
    min_runs_for_learning: 5      # Need 5+ runs before recommending
    p_improve_threshold: 0.8       # 80% confidence to auto-apply
    min_expected_gain: 0.01        # 1% expected gain minimum
    reward_metric: "cs_auc"        # Optimize cross-sectional AUC
    recency_decay: 0.95            # 95% weight on recent runs
```

## Usage

### Dry-Run (Preview Only)

```bash
python -m TRAINING.orchestration.intelligent_trainer \
    --data-dir data/data_labeled_v2/interval=5m \
    --symbols AAPL MSFT GOOGL \
    --apply-decisions dry_run
```

Check `REPRODUCIBILITY/patches/applied_patch.json` to see what would be applied.

### Apply Mode (Auto-Apply)

```bash
python -m TRAINING.orchestration.intelligent_trainer \
    --data-dir data/data_labeled_v2/interval=5m \
    --symbols AAPL MSFT GOOGL \
    --apply-decisions apply
```

Only applies if `P(improve) >= 0.8` and `expected_gain >= 0.01`.

## Receipts

Every run saves (in `REPRODUCIBILITY/patches/`):

- `decision_used.json`: Decision that was selected (includes Bayesian metadata)
- `resolved_config.yaml`: Config that actually ran
- `applied_patch.json`: Patch applied (or `"none"`)

Bayesian metadata in `decision_used.json`:
```json
{
  "policy_results": {
    "bayesian_metadata": {
      "confidence": 0.85,
      "expected_gain": 0.012,
      "baseline_reward": 0.65,
      "bayes_stats": {
        "cap_features_10pct": {
          "sample": 0.015,
          "mean": 0.012,
          "n": 3,
          "p_improve": 0.85,
          "expected_gain": 0.012
        }
      }
    }
  }
}
```

## State Files

Bayesian state persisted to:
```
REPRODUCIBILITY/bayes_state/{cohort_id}_seg{segment_id}.json
```

Format:
```json
{
  "cohort_id": "abc123",
  "segment_id": 1,
  "arms": {
    "cap_features_10pct": {
      "n": 3,
      "mean_reward": 0.012,
      "var_reward": 0.001,
      "last_updated": "2025-12-12T12:00:00"
    }
  },
  "baseline_reward": 0.65,
  "last_run_id": "20251212_120000_run1"
}
```

## Safety Constraints

1. **Hard clamps**: All patches limited to ±20% (enforced in `apply_decision_patch`)
2. **One policy at a time**: Only first action applied (prevents conflicts)
3. **Identity breaks**: Never learns across different `segment_id` / data/config identities
4. **Minimum runs**: Requires `min_runs_for_learning` runs before recommending
5. **Confidence threshold**: Only auto-apply if `P(improve) >= 0.8`

## Difficulty Assessment

**MEDIUM** - Straightforward to hook in, but requires:

- State persistence (JSON files) ✅
- Reward computation from index.parquet ✅
- Thompson sampling implementation ✅
- Integration with existing policy system ✅

**Not required:**
- Gaussian Processes (too complex for this use case)
- Continuous hyperparameter optimization (discrete templates are sufficient)
- Dashboard/UI (backend only)

## Reproducibility

Every recommendation is reproducible from:
- Same `index.parquet` snapshot
- Same `bayes_state/{cohort_id}_seg{segment_id}.json` state file

Thompson sampling uses `np.random.normal()` - set seed for deterministic behavior if needed.

## Next Steps

1. **Run with `use_bayesian: true`** in config
2. **Collect 5+ runs** in same cohort+segment
3. **Check receipts** in `REPRODUCIBILITY/patches/`
4. **Monitor convergence**: After 10-20 runs, policy should converge to best patches

If it's thrashing (recommending different patches every run), increase `p_improve_threshold` or `min_expected_gain`.
