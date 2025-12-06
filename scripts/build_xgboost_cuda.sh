#!/bin/bash
# Build XGBoost with CUDA support from source
# For RTX 3080 (compute capability 8.6)

set -e

echo "🔧 Building XGBoost with CUDA support..."

# Check if CUDA is available
if ! command -v nvcc &> /dev/null; then
    echo "❌ nvcc not found. CUDA toolkit may not be installed."
    exit 1
fi

# Get CUDA compute capability (RTX 3080 = 8.6)
CUDA_ARCH="86"

# Create temporary build directory
BUILD_DIR="/tmp/xgboost_build"
if [ -d "$BUILD_DIR" ]; then
    echo "📁 Removing existing build directory..."
    rm -rf "$BUILD_DIR"
fi

echo "📥 Cloning XGBoost repository..."
git clone --recursive --depth 1 https://github.com/dmlc/xgboost.git "$BUILD_DIR"
cd "$BUILD_DIR"

echo "🔨 Building XGBoost with CUDA support..."
mkdir -p build
cd build

# Find CUDA paths in conda environment
# Conda CUDA is typically in targets/x86_64-linux/
CUDA_TARGETS="$CONDA_PREFIX/targets/x86_64-linux"
CUDA_INCLUDE="$CUDA_TARGETS/include"
CUDA_LIB="$CUDA_TARGETS/lib"

# Check if targets directory exists, if not try root
if [ ! -d "$CUDA_INCLUDE" ] || [ ! -f "$CUDA_INCLUDE/cuda_runtime.h" ]; then
    CUDA_INCLUDE="$CONDA_PREFIX/include"
    CUDA_LIB="$CONDA_PREFIX/lib"
fi

# Verify CUDA headers exist
if [ ! -f "$CUDA_INCLUDE/cuda_runtime.h" ]; then
    echo "❌ ERROR: Could not find cuda_runtime.h"
    echo "   Searched in: $CUDA_INCLUDE"
    echo "   Please ensure CUDA toolkit is installed in conda environment"
    echo "   Try: conda install -c conda-forge cuda-toolkit"
    exit 1
fi

echo "📁 CUDA include: $CUDA_INCLUDE"
echo "📁 CUDA lib: $CUDA_LIB"
echo "📁 CUDA compiler: $CONDA_PREFIX/bin/nvcc"

# Set environment variables for CMake
export CUDA_TOOLKIT_ROOT_DIR="$CONDA_PREFIX"
export CUDA_PATH="$CONDA_PREFIX"
export CUDA_HOME="$CONDA_PREFIX"
export PATH="$CONDA_PREFIX/bin:$PATH"
export LD_LIBRARY_PATH="$CUDA_LIB:$LD_LIBRARY_PATH"

cmake .. \
    -DUSE_CUDA=ON \
    -DCUDA_ARCHITECTURES="$CUDA_ARCH" \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_INSTALL_PREFIX="$CONDA_PREFIX" \
    -DCUDA_TOOLKIT_ROOT_DIR="$CONDA_PREFIX" \
    -DCUDA_INCLUDE_DIRS="$CUDA_INCLUDE" \
    -DCUDA_CUDART_LIBRARY="$CUDA_LIB/libcudart.so" \
    -DCMAKE_CUDA_COMPILER="$CONDA_PREFIX/bin/nvcc" \
    -DCMAKE_CUDA_HOST_COMPILER="$(which g++)"

make -j$(nproc)

echo "📦 Installing XGBoost Python package..."
cd ../python-package
pip install -e . --no-deps

echo "✅ XGBoost with CUDA support installed!"
echo ""
echo "Testing installation..."
python3 << 'PYEOF'
import xgboost as xgb
import os
os.environ.setdefault("CUDA_VISIBLE_DEVICES", "0")

try:
    test_data = xgb.DMatrix([[1, 2, 3]], label=[1])
    xgb.train({"tree_method": "gpu_hist", "max_depth": 1}, test_data, num_boost_round=1)
    print("✅ SUCCESS! XGBoost GPU support is working!")
except Exception as e:
    print(f"❌ GPU support not working: {e}")
PYEOF

echo ""
echo "🎉 Done! XGBoost GPU support should now be available."

