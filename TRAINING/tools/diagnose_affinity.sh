#!/usr/bin/env bash
# Diagnostic script to identify CPU affinity issues

echo "=== CPU Affinity Diagnostic ==="
echo

echo "1. Shell process affinity:"
python3 -c "
import os
try:
    aff = sorted(os.sched_getaffinity(0))
    print(f'   Allowed CPUs: {aff} ({len(aff)} cores)')
except AttributeError:
    print('   sched_getaffinity not available (non-Linux?)')
"
echo

echo "2. Total CPU count:"
python3 -c "import os; print(f'   {os.cpu_count()} CPUs detected')"
echo

echo "3. Cgroup restrictions:"
if [ -f /proc/self/cgroup ]; then
    cgroup_path=$(cat /proc/self/cgroup | head -1 | cut -d: -f3)
    echo "   Cgroup: $cgroup_path"
    
    if [ -f "/sys/fs/cgroup/cpuset${cgroup_path}/cpuset.cpus" ]; then
        cpuset=$(cat "/sys/fs/cgroup/cpuset${cgroup_path}/cpuset.cpus")
        echo "   cpuset.cpus: $cpuset"
    elif [ -f "/sys/fs/cgroup${cgroup_path}/cpuset.cpus" ]; then
        cpuset=$(cat "/sys/fs/cgroup${cgroup_path}/cpuset.cpus")
        echo "   cpuset.cpus: $cpuset"
    else
        echo "   No cpuset restrictions found"
    fi
else
    echo "   No cgroup info available"
fi
echo

echo "4. Parent process:"
ps -p $PPID -o pid,ppid,cmd | tail -n +2
echo

echo "5. Current task affinity (via taskset):"
if command -v taskset &> /dev/null; then
    taskset -cp $$ 2>&1 | head -1
else
    echo "   taskset not available"
fi
echo

echo "6. Environment variables:"
env | grep -E "^(OMP|MKL|OPENBLAS|BLIS|PYTORCH)_" | sort
echo

echo "7. Test child process affinity:"
python3 << 'PYEOF'
import os
import multiprocessing as mp

def child_check():
    try:
        aff = sorted(os.sched_getaffinity(0))
        print(f'   Child affinity: {aff} ({len(aff)} cores)')
    except Exception as e:
        print(f'   Error: {e}')

if __name__ == '__main__':
    mp.set_start_method('spawn', force=True)
    p = mp.Process(target=child_check)
    p.start()
    p.join()
PYEOF
echo

echo "=== Diagnosis Complete ==="
echo
echo "Expected: All checks show 12 cores (or your full CPU count)"
echo "If any show 2 cores: That's your problem!"

