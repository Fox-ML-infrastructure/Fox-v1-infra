# Decision Application Verification Checklist

## Quick Verification (After Running with Apply Mode)

After running with `--apply-decisions apply` or `apply_mode: "apply"`, verify:

### 1. Decision Selection Log

Look for this log line:
```
📊 Decision selection: cohort_id=..., segment_id=..., decision_level=X, actions=[...], reasons=[...]
```

**Check:**
- ✅ `cohort_id` matches your run's cohort
- ✅ `segment_id` is present (or None if first segment)
- ✅ `decision_level >= 2` (otherwise patch won't apply)

### 2. Patch Application Log

If patch was applied, you should see:
```
🔧 Applied decision patch: {...}
📄 Patch saved to: REPRODUCIBILITY/applied_configs/patch_applied_{run_id}.json
📄 Patched config saved to: REPRODUCIBILITY/applied_configs/patched_config_{run_id}.yaml
🔑 Config hash updated with patch_hash: {hash}
```

**Check:**
- ✅ Patch file exists
- ✅ Patched config file exists
- ✅ Patch hash is logged

### 3. Artifact Files

Check these files exist:
```
REPRODUCIBILITY/
  applied_configs/
    decision_used_{run_id}.json          # Decision file that was used
    patch_applied_{run_id}.json          # Patch that was applied (apply mode)
    patched_config_{run_id}.yaml         # Full patched config (apply mode)
    patch_dry_run_{run_id}.json          # Patch preview (dry_run mode)
```

**Check:**
- ✅ `decision_used_*.json` exists (shows which decision was selected)
- ✅ `patch_applied_*.json` exists (if apply mode)
- ✅ `patched_config_*.yaml` exists (if apply mode)

### 4. Config Hash Update

Check metadata.json for:
```json
{
  "decision_patch_hash": "abc12345",
  "cs_config_hash": "..."
}
```

**Check:**
- ✅ `decision_patch_hash` is present in metadata
- ✅ This hash will cause a new segment_id on next run (identity break)

## Common Issues

### "No decision found for cohort_id=..."

**Cause:** No previous runs in this cohort, or decision file doesn't exist.

**Fix:** Run 3+ times in the same cohort to generate decisions.

### "Decision level X < 2, skipping application"

**Cause:** Decision level too low (policies didn't trigger).

**Fix:** This is expected - policies only trigger when conditions are met.

### "Pre-run decision loading failed"

**Cause:** Exception during decision loading (check debug logs).

**Fix:** Check logs for full traceback. Usually non-critical.

## Dry-Run Mode

With `--apply-decisions dry_run` or `apply_mode: "dry_run"`:

- ✅ Shows patch that **would** be applied
- ✅ Saves patch to `patch_dry_run_*.json`
- ✅ Does **not** modify config
- ✅ Does **not** update config_hash

Use this to preview patches before enabling apply mode.
