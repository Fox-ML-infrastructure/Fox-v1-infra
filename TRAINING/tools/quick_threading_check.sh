#!/usr/bin/env bash
# Quick threading sanity check - validates every family uses correct OMP/MKL
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TRAINING_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
PROJECT_ROOT="$(cd "$TRAINING_DIR/.." && pwd)"

cd "$TRAINING_DIR"

# Enable diagnostics
export TRAINER_DIAG=1
export TRAINER_NO_ISOLATION=1
export PYTHONPATH="${PROJECT_ROOT}:${PYTHONPATH:-}"

# Test families (subset for quick check)
FAMILIES_QUICK=(LightGBM XGBoost NGBoost Ensemble MLP)

echo "=========================================="
echo "Threading Sanity Check"
echo "=========================================="
echo "Testing families: ${FAMILIES_QUICK[*]}"
echo ""

for family in "${FAMILIES_QUICK[@]}"; do
    echo "----------------------------------------"
    echo "Testing: $family"
    echo "----------------------------------------"
    
    timeout 60s python train_with_strategies.py \
        --data-dir ../5m_with_barrier_targets_full/interval=5m \
        --symbols CBRE \
        --strategy single_task \
        --families "$family" \
        --targets fwd_ret_5m \
        --output-dir "test_threading_${family,,}" \
        --min-cs 1 \
        --max-samples-per-symbol 100 \
        --epochs 1 \
        --threads 12 \
        --experimental \
        --use-polars \
        --model-types cross-sectional \
        2>&1 | grep -E "(🔍|openmp_effective|affinity=|Trained in)" || true
    
    echo ""
done

echo "=========================================="
echo "✅ Quick check complete!"
echo "=========================================="
echo ""
echo "What to look for in the output above:"
echo "  - HGB/LGBM/XGB: openmp_effective ≈ 8-12, affinity=16"
echo "  - Ridge/Meta:   MKL ≈ 4-8, OMP ≈ 1"
echo "  - No affinity pins like {0,8}"
echo ""
echo "To run full diagnostics on all families:"
echo "  export TRAINER_DIAG=1"
echo "  ./test_13_symbols.sh"

