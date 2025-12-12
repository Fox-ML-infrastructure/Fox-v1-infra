"""
Time Contract Enforcement

Enforces the minimal "time contract" for training pipeline:
- Features are known at bar close `t`
- Prediction happens at `t`
- Label starts at `t+1` (or later), never inside the same bar

This prevents accidental lookahead and same-bar contamination.
"""

from typing import Dict, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class TimeContract:
    """
    Metadata describing the time contract for a target/feature set.
    
    This ensures:
    - Features are computed only from data <= t (bar close)
    - Labels start at t+1 (never include bar t)
    - Decision time is clearly defined
    """
    decision_time: str = "bar_close"  # When prediction happens: "bar_close" or "bar_open"
    label_starts_at: str = "t+1"  # When label window starts: "t+1", "t+2", etc.
    interval_minutes: Optional[float] = None  # Bar interval in minutes
    prices: str = "unknown"  # Price adjustment: "unknown", "unadjusted", "adjusted"
    
    def to_dict(self) -> Dict[str, any]:
        """Convert to dictionary for serialization."""
        return {
            "decision_time": self.decision_time,
            "label_starts_at": self.label_starts_at,
            "interval_minutes": self.interval_minutes,
            "prices": self.prices
        }
    
    def validate_label_computation(self, current_bar_idx: int, label_start_idx: int) -> bool:
        """
        Validate that label computation respects the time contract.
        
        Args:
            current_bar_idx: Index of current bar (t)
            label_start_idx: Index where label computation starts
            
        Returns:
            True if contract is respected (label_start_idx > current_bar_idx)
        """
        if label_start_idx <= current_bar_idx:
            logger.error(
                f"⚠️  TIME CONTRACT VIOLATION: Label starts at bar {label_start_idx} "
                f"but current bar is {current_bar_idx}. Label must start at t+1 or later."
            )
            return False
        return True
    
    def log_contract(self, target_name: str) -> None:
        """Log the time contract for a target."""
        logger.info(
            f"⏱️  Time contract for {target_name}: "
            f"decision_time={self.decision_time}, "
            f"label_starts_at={self.label_starts_at}, "
            f"interval={self.interval_minutes}m, "
            f"prices={self.prices}"
        )


def enforce_t_plus_one_boundary(
    current_bar_idx: int,
    horizon_bars: int,
    label_start_offset: int = 1
) -> tuple[int, int]:
    """
    Enforce t+1 boundary for label computation.
    
    Ensures labels are computed from bars [t+label_start_offset, t+label_start_offset+horizon_bars),
    never including bar t.
    
    Args:
        current_bar_idx: Current bar index (t)
        horizon_bars: Number of bars in the horizon
        label_start_offset: Offset from current bar (default: 1 for t+1)
        
    Returns:
        (label_start_idx, label_end_idx) tuple
    """
    label_start_idx = current_bar_idx + label_start_offset
    label_end_idx = label_start_idx + horizon_bars
    
    if label_start_offset < 1:
        logger.warning(
            f"⚠️  Label start offset {label_start_offset} < 1. "
            f"Labels should start at t+1 or later to avoid same-bar contamination."
        )
    
    return label_start_idx, label_end_idx


def validate_feature_as_of_safety(
    feature_name: str,
    feature_data: any,
    current_bar_idx: int,
    max_lookback_bars: Optional[int] = None
) -> bool:
    """
    Validate that a feature is "as-of safe" (only uses data <= t).
    
    This is a basic check - full validation requires inspecting the feature computation.
    
    Args:
        feature_name: Name of the feature
        feature_data: Feature data (for length checking)
        current_bar_idx: Current bar index (t)
        max_lookback_bars: Maximum allowed lookback (if known)
        
    Returns:
        True if feature appears safe (basic check only)
    """
    # Basic check: feature should be available at current bar
    # Full validation requires inspecting rolling window computation
    if hasattr(feature_data, '__len__'):
        if len(feature_data) <= current_bar_idx + 1:
            # Feature data length suggests it might include future data
            logger.warning(
                f"⚠️  Potential as-of safety issue for {feature_name}: "
                f"feature length ({len(feature_data)}) <= current_bar+1 ({current_bar_idx+1})"
            )
            return False
    
    return True
