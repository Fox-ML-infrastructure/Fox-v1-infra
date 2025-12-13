"""
Copyright (c) 2025-2026 Fox ML Infrastructure LLC

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

"""
Safe Subprocess Utilities

Helper functions for subprocess calls that avoid readline library conflicts.
These utilities set safe environment variables to prevent deadlocks from
Conda/system readline library mismatches.
"""

import os
import subprocess
import logging
from typing import List, Optional, Dict, Any

logger = logging.getLogger(__name__)


def get_safe_subprocess_env() -> Dict[str, str]:
    """
    Get a safe environment dictionary for subprocess calls.
    
    This prevents readline library conflicts that can cause:
    - "sh: symbol lookup error: sh: undefined symbol: rl_print_keybinding"
    - Process deadlocks/hangs when subprocess calls fail and retry indefinitely
    
    Returns:
        Environment dictionary with safe settings for subprocess calls
    """
    env = os.environ.copy()
    
    # Disable readline features to avoid library conflicts
    env.setdefault('TERM', 'dumb')  # Disable readline features
    env.setdefault('SHELL', '/usr/bin/bash')  # Use bash instead of sh if available
    env.setdefault('INPUTRC', '/dev/null')  # Disable readline config
    
    return env


def safe_subprocess_run(
    cmd: List[str],
    *,
    timeout: Optional[float] = None,
    cwd: Optional[str] = None,
    check: bool = False,
    capture_output: bool = True,
    text: bool = True,
    **kwargs
) -> subprocess.CompletedProcess:
    """
    Run a subprocess command with safe environment variables to avoid readline conflicts.
    
    This wrapper around subprocess.run() automatically sets TERM=dumb, SHELL=/usr/bin/bash,
    and INPUTRC=/dev/null to prevent readline library conflicts that can cause process deadlocks.
    
    Args:
        cmd: Command to run (list of strings)
        timeout: Timeout in seconds (default: None)
        cwd: Working directory (default: None)
        check: If True, raise CalledProcessError on non-zero exit (default: False)
        capture_output: If True, capture stdout and stderr (default: True)
        text: If True, decode output as text (default: True)
        **kwargs: Additional arguments passed to subprocess.run()
    
    Returns:
        CompletedProcess object with returncode, stdout, stderr
    
    Raises:
        FileNotFoundError: If command not found
        subprocess.TimeoutExpired: If timeout exceeded
        subprocess.CalledProcessError: If check=True and returncode != 0
        OSError: Can occur with readline library conflicts (symbol lookup errors)
    
    Example:
        >>> result = safe_subprocess_run(['git', 'rev-parse', '--short', 'HEAD'], timeout=2)
        >>> if result.returncode == 0:
        ...     print(result.stdout.strip())
    """
    env = get_safe_subprocess_env()
    
    try:
        return subprocess.run(
            cmd,
            env=env,
            timeout=timeout,
            cwd=cwd,
            check=check,
            capture_output=capture_output,
            text=text,
            **kwargs
        )
    except (FileNotFoundError, subprocess.TimeoutExpired) as e:
        # Re-raise these as-is (expected errors)
        raise
    except OSError as e:
        # OSError can occur with readline library conflicts (symbol lookup errors)
        # Log and re-raise with helpful message
        error_msg = str(e)
        if 'symbol lookup error' in error_msg or 'rl_print_keybinding' in error_msg:
            logger.warning(
                f"Subprocess failed due to readline library conflict: {e}\n"
                f"Command: {' '.join(cmd)}\n"
                f"Fix: Run 'conda install -c conda-forge readline=8.2' or 'conda update readline'"
            )
        raise
    except Exception as e:
        # Catch-all for other unexpected errors
        logger.debug(f"Subprocess call failed: {e} (command: {' '.join(cmd)})")
        raise
