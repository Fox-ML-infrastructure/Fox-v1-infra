# Decision Engine

**What's needed for decision-making to work:**

## ✅ Already Working

1. **Post-run hook**: Decisions are evaluated and persisted after each run
2. **Policies**: 4 default policies are defined and will trigger when conditions are met
3. **Index integration**: Decision fields are stored in `index.parquet`

## 🔧 What's Needed (Minimal)

### 1. Segment ID in Index (Required)

The DecisionEngine needs `segment_id` to properly segment by identity breaks. Currently it's computed but not stored in index.

**Fix:** Add `segment_id` computation to `_update_index()` using `prepare_segments()`.

### 2. Minimum Data Requirements

Policies need at least **3 runs** in a cohort to evaluate:
- `feature_instability`: Needs 3+ runs with `jaccard_topK` data
- `route_instability`: Needs 3+ runs with `route_entropy` or `route_changed` data
- `feature_explosion_decline`: Needs 3+ runs with `cs_auc` and `n_features_selected`
- `class_balance_drift`: Needs 3+ runs with `pos_rate`

**Status:** Will work automatically once you have 3+ runs per cohort.

### 3. Optional: Regression Predictions

Policies work **without** regression predictions, but predictions improve decision quality.

**To enable predictions:**
- Run `analyze_cohort_trends()` periodically (or after each run)
- This populates `next_pred` in index.parquet
- DecisionEngine will use predictions if available

**Not required** - policies work on raw metrics alone.

## 📊 Current Status

**What works now:**
- ✅ Decision evaluation after each run
- ✅ Decision persistence to JSON
- ✅ Policy evaluation (once 3+ runs exist)
- ✅ Decision fields in index.parquet

**What needs fixing:**
- ⚠️ `segment_id` not in index (policies work but don't respect identity breaks)
- ⚠️ `jaccard_topK` may not be populated (feature selection stability tracking)

**What's optional:**
- 🔵 Regression predictions (`next_pred`) - nice to have but not required
- 🔵 Apply mode - only needed if you want decisions to auto-modify config

## 🚀 Quick Start

**Just run your pipeline normally.** After 3+ runs in the same cohort:
- Decisions will be evaluated automatically
- Check `REPRODUCIBILITY/decisions/{run_id}.json` for decision results
- Check logs for decision summaries: `📊 Decision: level=X, actions=[...], reasons=[...]`

**To enable apply mode:**
```python
trainer.train_with_intelligence(decision_apply_mode=True, ...)
```

## 📝 Next Steps (if needed)

1. **Add segment_id to index** (5 min fix)
2. **Populate jaccard_topK** (if you want feature instability detection)
3. **Run regression analysis** (optional, for predictions)
