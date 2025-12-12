# RESULTS Directory Organization Options

## Current Structure

```
RESULTS/
  {N_effective}/              # e.g., 943943
    {run_name}/               # e.g., test_e2e_ranking_unified_20251212_012021
      target_rankings/
      feature_selections/
      REPRODUCIBILITY/
      ...
```

**Pros:**
- Easy to find runs by sample size
- Groups comparable runs together

**Cons:**
- Many numeric directories at top level
- Hard to find recent runs
- No experiment type grouping

---

## Option 1: Date-Based (Recommended for Most Use Cases)

```
RESULTS/
  {YYYY-MM-DD}/               # e.g., 2025-12-12
    {run_name}/               # e.g., test_e2e_ranking_unified_20251212_012021
      target_rankings/
      REPRODUCIBILITY/
      metadata.json           # Contains N_effective for filtering
      ...
```

**Pros:**
- ✅ Easy to find recent runs
- ✅ Natural chronological organization
- ✅ Cleaner top-level structure
- ✅ N_effective still queryable via `index.parquet` or metadata

**Cons:**
- Runs with same N_effective but different dates are separated
- Need to query metadata/index to find by sample size

**Implementation:**
- Use `datetime.now().strftime("%Y-%m-%d")` for date folder
- Store N_effective in `metadata.json` (already done)
- Use `index.parquet` for filtering by N_effective

---

## Option 2: Flatter Structure with Queryable Index

```
RESULTS/
  {run_name}/                 # e.g., test_e2e_ranking_unified_20251212_012021
    target_rankings/
    REPRODUCIBILITY/
    metadata.json             # Contains N_effective, date, experiment_type
    ...
```

**Pros:**
- ✅ Simplest structure
- ✅ All metadata in one place
- ✅ Easy to query via `index.parquet`
- ✅ No arbitrary grouping

**Cons:**
- All runs at same level (can get cluttered)
- Need tooling to filter/find runs

**Implementation:**
- Store all metadata in `metadata.json`
- Use `index.parquet` for all filtering
- Add CLI tool: `python tools/list_runs.py --by-sample-size 943943`

---

## Option 3: Hybrid (Date + Sample Size)

```
RESULTS/
  {YYYY-MM-DD}/               # e.g., 2025-12-12
    {run_name}/               # e.g., test_e2e_ranking_unified_20251212_012021
      ...
```

But also maintain symlinks or tags:
```
RESULTS/
  by_sample_size/
    {N_effective}/            # e.g., 943943 -> symlink to actual run
      {run_name} -> ../../2025-12-12/{run_name}
```

**Pros:**
- ✅ Best of both worlds
- ✅ Find by date OR by sample size

**Cons:**
- More complex to maintain
- Symlinks can break

---

## Option 4: Experiment Type + Date

```
RESULTS/
  {experiment_type}/          # e.g., test, production, experiment
    {YYYY-MM-DD}/            # e.g., 2025-12-12
      {run_name}/
        ...
```

**Pros:**
- ✅ Separates test vs production runs
- ✅ Date-based within each type
- ✅ Clear organization

**Cons:**
- Need to detect experiment type (already done via "test" in output-dir)
- More nesting

**Implementation:**
- Detect from `output_dir` name (already checks for "test")
- Structure: `RESULTS/{experiment_type}/{date}/{run_name}/`

---

## Option 5: Sample Size Ranges (Binned)

```
RESULTS/
  sample_900k-1M/            # Binned ranges
    {run_name}/
      ...
  sample_500k-600k/
    {run_name}/
      ...
```

**Pros:**
- ✅ Groups similar sample sizes
- ✅ Fewer top-level directories

**Cons:**
- Arbitrary binning
- Less precise than exact N_effective

---

## Recommendation

**Option 1 (Date-Based)** is recommended because:

1. **Most common use case**: "Show me runs from today/last week"
2. **Clean structure**: Only ~365 top-level directories max (one per day)
3. **Metadata preserved**: N_effective still in `metadata.json` and `index.parquet`
4. **Queryable**: Can still filter by sample size using the index
5. **Simple**: No symlinks or complex logic

**Alternative**: If you frequently filter by sample size, use **Option 2 (Flatter)** with a good CLI tool for querying.

---

## Migration Strategy

If changing organization:

1. Keep old structure for existing runs (no migration needed)
2. New runs use new structure
3. Update `index.parquet` to include full path for both old and new
4. Add CLI tool to query/find runs regardless of structure

---

## Implementation Example (Date-Based)

```python
# In IntelligentTrainer.__init__
from datetime import datetime

# Determine experiment type
experiment_type = "test" if "test" in output_dir_name.lower() else "production"

# Get date
run_date = datetime.now().strftime("%Y-%m-%d")

# Create structure: RESULTS/{experiment_type}/{date}/{run_name}/
self.output_dir = results_dir / experiment_type / run_date / output_dir_name
```

Or simpler (just date):
```python
run_date = datetime.now().strftime("%Y-%m-%d")
self.output_dir = results_dir / run_date / output_dir_name
```
