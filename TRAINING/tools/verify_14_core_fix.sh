#!/usr/bin/env bash
# Verify the 14-core fix is working correctly
set -euo pipefail

cd "$(dirname "$0")/.."

echo "=== 14-Core Fix Verification ==="
echo

echo "1. Testing plan_for_family() output..."
python3 -c "
import sys
sys.path.insert(0, '.')
from common.threads import plan_for_family

families = ['LightGBM', 'QuantileLightGBM', 'XGBoost', 'RewardBased', 'Ensemble']
for f in families:
    plan = plan_for_family(f, 14)
    print(f'{f:20s} → OMP={plan[\"OMP\"]:2d} MKL={plan[\"MKL\"]}')
"
echo

echo "2. Testing allowed_cpus()..."
python3 -c "
import sys
sys.path.insert(0, '.')
from common.threads import allowed_cpus
cpus = allowed_cpus()
print(f'Allowed CPUs: {len(cpus)} cores → {cpus}')
"
echo

echo "3. Testing effective_threads()..."
python3 -c "
import sys
sys.path.insert(0, '.')
from common.threads import effective_threads
result = effective_threads(14)
print(f'effective_threads(14) → {result}')
"
echo

echo "4. Shell affinity check..."
if command -v taskset &> /dev/null; then
    taskset -pc $$ | head -1
else
    echo "taskset not available"
fi
python3 -c "
import os
if hasattr(os, 'sched_getaffinity'):
    aff = sorted(os.sched_getaffinity(0))
    print(f'Python sched_getaffinity: {len(aff)} cores → {aff}')
else:
    print('sched_getaffinity not available (Windows/macOS)')
"
echo

echo "5. Environment check..."
echo "OMP_NUM_THREADS    = ${OMP_NUM_THREADS:-<unset>}"
echo "MKL_NUM_THREADS    = ${MKL_NUM_THREADS:-<unset>}"
echo "OPENBLAS_NUM_THREADS = ${OPENBLAS_NUM_THREADS:-<unset>}"
echo "OMP_PLACES         = ${OMP_PLACES:-<unset>}"
echo "KMP_AFFINITY       = ${KMP_AFFINITY:-<unset>}"
echo

echo "✅ Verification complete!"
echo
echo "Expected for OMP-heavy families (LGBM/XGB/QuantileLGBM):"
echo "  OMP=14 (or your THREADS count)"
echo
echo "Expected for BLAS-only families (RewardBased):"
echo "  OMP=1 MKL=1"

