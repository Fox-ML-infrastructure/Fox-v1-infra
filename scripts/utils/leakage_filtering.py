"""
Target-Aware Leakage Filtering Utilities

Provides reusable functions for filtering features based on target horizon
to prevent temporal overlap leakage.
"""

import re
from pathlib import Path
from typing import List, Set, Optional, Dict
import yaml
import logging

logger = logging.getLogger(__name__)

_REPO_ROOT = Path(__file__).resolve().parents[2]


def load_exclusion_config(config_path: Path = None) -> dict:
    """Load feature exclusion configuration"""
    if config_path is None:
        config_path = _REPO_ROOT / "CONFIG" / "excluded_features.yaml"
    
    if not config_path.exists():
        logger.warning(f"Exclusion config not found: {config_path}")
        return {}
    
    with open(config_path) as f:
        return yaml.safe_load(f)


def extract_target_horizon(target_name: str) -> Optional[Dict[str, any]]:
    """
    Extract horizon information from target name.
    
    Examples:
        fwd_ret_20d -> {'value': 20, 'unit': 'd', 'minutes': 20*1440}
        fwd_ret_60m -> {'value': 60, 'unit': 'm', 'minutes': 60}
        fwd_ret_oc_same_day -> {'value': 1, 'unit': 'd', 'minutes': 1440}
        peak_60m_0.8 -> {'value': 60, 'unit': 'm', 'minutes': 60}
        y_will_peak_60m_0.8 -> {'value': 60, 'unit': 'm', 'minutes': 60}
        y_will_peak_mfe_10m_0.001 -> {'value': 10, 'unit': 'm', 'minutes': 10}
    
    Returns:
        Dict with 'value', 'unit', 'minutes' or None if can't parse
    """
    # Special case: open-to-close same day (treat as 1 day)
    if target_name == 'fwd_ret_oc_same_day':
        return {'value': 1, 'unit': 'd', 'minutes': 1440}
    
    # Pattern for fwd_ret_XXd or fwd_ret_XXm
    fwd_ret_match = re.match(r'fwd_ret_(\d+)([dm])', target_name)
    if fwd_ret_match:
        value = int(fwd_ret_match.group(1))
        unit = fwd_ret_match.group(2)
        minutes = value * 1440 if unit == 'd' else value
        return {'value': value, 'unit': unit, 'minutes': minutes}
    
    # Pattern for XXm in target name (e.g., peak_60m, valley_30m, y_will_peak_mfe_10m_0.001)
    # This will match the first occurrence of XXm in the name
    minutes_match = re.search(r'(\d+)m', target_name)
    if minutes_match:
        value = int(minutes_match.group(1))
        return {'value': value, 'unit': 'm', 'minutes': value}
    
    # Pattern for XXd in target name
    days_match = re.search(r'(\d+)d', target_name)
    if days_match:
        value = int(days_match.group(1))
        return {'value': value, 'unit': 'd', 'minutes': value * 1440}
    
    return None


def get_temporal_overlap_features(horizon_minutes: int, config: dict = None) -> Set[str]:
    """
    Get features that would create temporal overlap with target horizon.
    
    For a target with horizon H minutes, exclude features with windows:
    - Exactly H minutes (direct overlap)
    - H/2 to H*1.5 minutes (strong autocorrelation)
    - For daily targets: exclude features with matching day windows
    
    Args:
        horizon_minutes: Target prediction horizon in minutes
        config: Exclusion config (loads from file if None)
    
    Returns:
        Set of feature names to exclude
    """
    if config is None:
        config = load_exclusion_config()
    
    excluded = set()
    
    # Get all temporal overlap patterns from config
    temporal_patterns = config.get('temporal_overlap_30m_plus', [])
    
    # For minute-based horizons, exclude features with matching windows
    if horizon_minutes <= 1440:  # <= 1 day
        # Exclude features with windows in range [horizon/2, horizon*1.5]
        min_window = max(1, horizon_minutes // 2)
        max_window = int(horizon_minutes * 1.5)
        
        # Pattern to match: ret_XXm, vol_XXm, etc.
        for pattern in temporal_patterns:
            # Extract window size if it's a minute-based feature
            match = re.search(r'(\d+)m', pattern)
            if match:
                window_minutes = int(match.group(1))
                if min_window <= window_minutes <= max_window:
                    excluded.add(pattern)
    
    # For day-based horizons, exclude features with matching day windows
    elif horizon_minutes > 1440:  # > 1 day
        horizon_days = horizon_minutes / 1440
        
        # Exclude features with windows in range [horizon/2, horizon*1.5] days
        min_window_days = max(1, horizon_days / 2)
        max_window_days = horizon_days * 1.5
        
        # Pattern to match: ret_XXd, vol_XXd, returns_XXd, etc.
        for pattern in temporal_patterns:
            # Extract window size if it's a day-based feature
            match = re.search(r'(\d+)d', pattern)
            if match:
                window_days = int(match.group(1))
                if min_window_days <= window_days <= max_window_days:
                    excluded.add(pattern)
        
        # Also check for minute-based features that overlap
        for pattern in temporal_patterns:
            match = re.search(r'(\d+)m', pattern)
            if match:
                window_minutes = int(match.group(1))
                window_days = window_minutes / 1440
                if min_window_days <= window_days <= max_window_days:
                    excluded.add(pattern)
    
    return excluded


def get_excluded_features_for_target(
    target_name: str,
    config: dict = None,
    exclude_definite_leaks: bool = True,
    exclude_temporal_overlap: bool = True
) -> Set[str]:
    """
    Get set of features to exclude for a specific target.
    
    This is target-aware filtering that:
    1. Always excludes definite leaks
    2. Excludes temporal overlap features based on target horizon
    3. Excludes metadata and target columns
    
    Args:
        target_name: Name of the target (e.g., 'fwd_ret_20d', 'peak_60m_0.8')
        config: Exclusion config (loads from file if None)
        exclude_definite_leaks: Whether to exclude definite leaks
        exclude_temporal_overlap: Whether to exclude temporal overlap features
    
    Returns:
        Set of feature names to exclude
    """
    if config is None:
        config = load_exclusion_config()
    
    excluded = set()
    
    # Always exclude definite leaks
    if exclude_definite_leaks and config.get('exclude_definite_leaks', True):
        excluded.update(config.get('definite_leaks', []))
    
    # Exclude temporal overlap features based on target horizon
    if exclude_temporal_overlap:
        horizon_info = extract_target_horizon(target_name)
        if horizon_info:
            temporal_overlap = get_temporal_overlap_features(
                horizon_info['minutes'], config
            )
            excluded.update(temporal_overlap)
            logger.debug(
                f"Target {target_name} (horizon: {horizon_info['value']}{horizon_info['unit']}): "
                f"Excluding {len(temporal_overlap)} temporal overlap features"
            )
        else:
            # Fallback: use default temporal overlap (30m+ for 60m targets)
            if config.get('exclude_temporal_overlap', True):
                excluded.update(config.get('temporal_overlap_30m_plus', []))
    
    # Exclude metadata columns
    if config.get('exclude_metadata', True):
        excluded.update(config.get('metadata_columns', []))
    
    # Exclude target columns (patterns)
    if config.get('exclude_targets', True):
        target_patterns = config.get('target_patterns', [])
        # Don't exclude the current target itself (it's needed)
        for pattern in target_patterns:
            if not re.match(pattern, target_name):
                # This pattern doesn't match our target, so exclude features matching it
                # (We'll handle target exclusion separately in filter_features)
                pass
    
    return excluded


def filter_features_for_target(
    all_columns: List[str],
    target_name: str,
    config: dict = None,
    verbose: bool = True
) -> List[str]:
    """
    Filter feature list for a specific target, excluding:
    1. Definite leaks
    2. Temporal overlap features (target-aware)
    3. Metadata columns
    4. Target columns (except the current target)
    
    Args:
        all_columns: List of all column names in dataset
        target_name: Name of the target being predicted
        config: Exclusion config (loads from file if None)
        verbose: Whether to log filtering stats
    
    Returns:
        List of safe feature columns for this target
    """
    if config is None:
        config = load_exclusion_config()
    
    # Get excluded features for this target
    excluded_set = get_excluded_features_for_target(target_name, config)
    
    # Get target patterns (to exclude other targets)
    target_patterns = config.get('target_patterns', []) if config.get('exclude_targets', True) else []
    
    # Filter columns
    safe_features = []
    excluded_by_name = []
    excluded_by_pattern = []
    
    for col in all_columns:
        # Skip the target itself (it's not a feature)
        if col == target_name:
            continue
        
        # Check if in exclusion set
        if col in excluded_set:
            excluded_by_name.append(col)
            continue
        
        # Check if matches target pattern (but not the current target)
        if matches_target_pattern(col, target_patterns):
            excluded_by_pattern.append(col)
            continue
        
        # Safe feature
        safe_features.append(col)
    
    # Log stats
    if verbose:
        horizon_info = extract_target_horizon(target_name)
        horizon_str = f" (horizon: {horizon_info['value']}{horizon_info['unit']})" if horizon_info else ""
        logger.info(f"Feature filtering for {target_name}{horizon_str}:")
        logger.info(f"  Total columns: {len(all_columns)}")
        logger.info(f"  Safe features: {len(safe_features)}")
        logger.info(f"  Excluded by name: {len(excluded_by_name)}")
        logger.info(f"  Excluded by pattern: {len(excluded_by_pattern)}")
    
    return safe_features


def matches_target_pattern(column_name: str, patterns: List[str]) -> bool:
    """Check if column matches any target pattern (regex)"""
    for pattern in patterns:
        if re.match(pattern, column_name):
            return True
    return False


# Backward compatibility: re-export functions from filter_leaking_features
def get_excluded_features(config: dict = None) -> Set[str]:
    """Backward compatibility wrapper"""
    return get_excluded_features_for_target("", config, exclude_temporal_overlap=False)


def filter_features(
    all_columns: List[str],
    config: dict = None,
    verbose: bool = True
) -> List[str]:
    """Backward compatibility wrapper (target-agnostic filtering)"""
    if config is None:
        config = load_exclusion_config()
    
    excluded_set = get_excluded_features(config)
    target_patterns = config.get('target_patterns', []) if config.get('exclude_targets', True) else []
    
    safe_features = []
    for col in all_columns:
        if col in excluded_set:
            continue
        if matches_target_pattern(col, target_patterns):
            continue
        safe_features.append(col)
    
    if verbose:
        logger.info(f"Feature filtering (target-agnostic):")
        logger.info(f"  Total columns: {len(all_columns)}")
        logger.info(f"  Safe features: {len(safe_features)}")
    
    return safe_features

