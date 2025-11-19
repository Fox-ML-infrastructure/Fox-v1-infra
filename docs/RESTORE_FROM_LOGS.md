# Restore Checkpoint from Log File

If you ran a comprehensive ranking and saved the output to a log file (like `scripts/ranking.md`), you can restore those results into a checkpoint to avoid re-running everything.

## Quick Restore

```bash
conda activate trader_env
cd /home/Jennifer/trader

# Restore from your saved log file
python scripts/restore_checkpoint_from_logs.py \
  --log-file scripts/ranking.md \
  --output-dir results/target_rankings
```

This will:
1. Parse `scripts/ranking.md` to extract all completed target evaluations
2. Reconstruct the results from the log output
3. Save them to `results/target_rankings/checkpoint.json`
4. Create a CSV summary at `results/target_rankings/restored_rankings.csv`

## Then Resume

After restoring, you can resume the script to:
- Skip all completed targets
- Only process remaining targets
- Merge restored results with new results

```bash
# Resume - will skip all restored targets
python scripts/rank_target_predictability.py \
  --discover-all \
  --symbols AAPL,MSFT,GOOGL,TSLA,JPM \
  --output-dir results/target_rankings \
  --resume
```

## What Gets Restored

The script extracts:
- Target name and column
- R² scores (mean and std)
- Importance scores
- Composite scores
- Model scores (per-model R²)
- Leakage flags (recalculated from R²)

## Verify Restoration

```bash
# Check how many targets were restored
python -c "
import json
with open('results/target_rankings/checkpoint.json') as f:
    data = json.load(f)
    print(f'Restored {len(data[\"completed_items\"])} targets')
    print('Top 5 targets:')
    items = list(data['completed_items'].items())
    items.sort(key=lambda x: x[1].get('composite_score', 0), reverse=True)
    for name, result in items[:5]:
        print(f'  {name}: composite={result.get(\"composite_score\", 0):.3f}, R²={result.get(\"mean_r2\", 0):.3f}')
"

# Or view the CSV
head -20 results/target_rankings/restored_rankings.csv
```

## Example Output

```
2025-11-18 12:00:00 - INFO - Parsing log file: scripts/ranking.md
2025-11-18 12:00:01 - INFO - Extracted: peak_60m_0.8 (R²=0.219, composite=0.555)
2025-11-18 12:00:01 - INFO - Extracted: valle60m_0.8 (R²=0.244, composite=0.583)
...
2025-11-18 12:00:05 - INFO - Extracted 25 completed targets from log
2025-11-18 12:00:05 - INFO - Checkpoint restored to: results/target_rankings/checkpoint.json
2025-11-18 12:00:05 - INFO - Completed targets: 25
2025-11-18 12:00:05 - INFO - You can now resume with:
2025-11-18 12:00:05 - INFO -   python scripts/rank_target_predictability.py --resume --output-dir results/target_rankings
```

## Limitations

The restore script extracts what it can from the log:
- ✅ Target names and columns
- ✅ Summary statistics (R², importance, composite)
- ✅ Model scores (if present in log)
- ⚠️ Per-symbol breakdowns (not available in summary logs)
- ⚠️ Full model importances (only summary available)

For best results, the log should contain:
- "Evaluating: <target_name> (<target_column>)" lines
- "Summary: R²=..." lines with final statistics
- "Scores: model1=..., model2=..." lines (optional, for per-model breakdown)

## Troubleshooting

### No results extracted

If the script finds 0 targets:
1. Check the log file format matches expected patterns
2. Look for "Evaluating:" and "Summary:" lines in the log
3. The log format may have changed - check the actual log content

### Partial results

If only some targets are extracted:
- The log may be incomplete
- Some targets may not have summary lines
- Check the log for missing "Summary:" lines

### Resume doesn't work

If resume doesn't skip restored targets:
1. Make sure you're using the same `--output-dir` as restore
2. Check that checkpoint.json exists and has data
3. Verify target names match between log and script

## Full Workflow

```bash
# Step 1: Restore from your saved log
python scripts/restore_checkpoint_from_logs.py \
  --log-file scripts/ranking.md \
  --output-dir results/target_rankings

# Step 2: Verify restoration
python -c "
import json
with open('results/target_rankings/checkpoint.json') as f:
    data = json.load(f)
    print(f'Restored: {len(data[\"completed_items\"])} targets')
"

# Step 3: Resume to complete remaining targets
python scripts/rank_target_predictability.py \
  --discover-all \
  --symbols AAPL,MSFT,GOOGL,TSLA,JPM \
  --output-dir results/target_rankings \
  --resume

# Step 4: Final results will include both restored and newly computed targets
```

This way you don't lose your 4 days of work!

