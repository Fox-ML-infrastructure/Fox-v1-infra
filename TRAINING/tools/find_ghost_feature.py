#!/usr/bin/env python3
"""
Quick scanner to find the 24h/1440m ghost feature.

This script helps identify features that require 1440 minutes (24 hours) of lookback
but might not match standard naming patterns.
"""

import re
import sys
from pathlib import Path

# Add repo root to path
repo_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(repo_root))

def find_ghost_features(feature_list, interval_minutes=5.0):
    """
    Scan feature list for potential 1440m (24h) lookback features.
    
    Args:
        feature_list: List of feature names to scan
        interval_minutes: Data interval in minutes (default: 5m)
    
    Returns:
        List of (feature_name, detected_lookback_minutes, reason) tuples
    """
    ghost_features = []
    
    # Patterns that indicate 1440m lookback
    patterns = [
        (r'_1d$|_1D$', 'Ends in _1d'),
        (r'_24h$|_24H$', 'Ends in _24h'),
        (r'^daily_', 'Starts with daily_'),
        (r'_daily$', 'Ends with _daily'),
        (r'daily', 'Contains "daily"'),
        (r'day', 'Contains "day"'),
        (r'_1440m', 'Contains _1440m'),
        (r'1440(?!\d)', 'Contains 1440 (not followed by digit)'),
        (r'volatility.*day|vol.*day|volume.*day', 'Vol/day pattern'),
        (r'rolling.*daily', 'Rolling daily pattern'),
    ]
    
    for feat_name in feature_list:
        detected_lookback = None
        reason = None
        
        # Check each pattern
        for pattern, pattern_reason in patterns:
            if re.search(pattern, feat_name, re.IGNORECASE):
                # Calculate lookback
                if '1440' in pattern or '1d' in pattern.lower() or '24h' in pattern.lower() or 'daily' in pattern.lower() or 'day' in pattern.lower():
                    detected_lookback = 1440.0
                    reason = f"{pattern_reason} (assumed 1440m = 24h)"
                break
        
        # Also check for explicit minute patterns
        if detected_lookback is None:
            minutes_match = re.search(r'_(\d+)m$', feat_name, re.I)
            if minutes_match:
                minutes = int(minutes_match.group(1))
                if minutes >= 1440:  # 24 hours or more
                    detected_lookback = float(minutes)
                    reason = f"Explicit {minutes}m pattern"
        
        # Check for day patterns
        if detected_lookback is None:
            days_match = re.search(r'_(\d+)d', feat_name, re.I)
            if days_match:
                days = int(days_match.group(1))
                if days >= 1:
                    detected_lookback = float(days * 1440)
                    reason = f"{days} day(s) = {days * 1440}m"
        
        if detected_lookback is not None and detected_lookback >= 1440:
            ghost_features.append((feat_name, detected_lookback, reason))
    
    return ghost_features


def main():
    """Main entry point."""
    print("🔍 SCANNING FOR 24H/1440M GHOST FEATURES...")
    print("=" * 60)
    
    # Try to load features from feature registry or config
    feature_list = []
    
    # Option 1: Try to load from feature registry
    try:
        from TRAINING.common.feature_registry import get_registry
        registry = get_registry()
        # Get all registered features
        if hasattr(registry, 'get_all_features'):
            feature_list = registry.get_all_features()
        elif hasattr(registry, '_features'):
            feature_list = list(registry._features.keys())
    except Exception as e:
        print(f"⚠️  Could not load from feature registry: {e}")
    
    # Option 2: If no features loaded, prompt user
    if not feature_list:
        print("\n📝 Please provide feature names (one per line, or comma-separated):")
        print("   (Press Ctrl+D when done, or paste list and press Enter)")
        try:
            input_text = sys.stdin.read().strip()
            if ',' in input_text:
                feature_list = [f.strip() for f in input_text.split(',')]
            else:
                feature_list = [f.strip() for f in input_text.split('\n') if f.strip()]
        except EOFError:
            print("\n❌ No features provided. Exiting.")
            sys.exit(1)
    
    if not feature_list:
        print("❌ No features to scan. Exiting.")
        sys.exit(1)
    
    print(f"\n📊 Scanning {len(feature_list)} features...")
    print()
    
    # Find ghost features
    ghost_features = find_ghost_features(feature_list)
    
    if ghost_features:
        print(f"👻 FOUND {len(ghost_features)} POTENTIAL GHOST FEATURE(S):\n")
        for feat_name, lookback, reason in sorted(ghost_features, key=lambda x: x[1], reverse=True):
            print(f"   🚫 {feat_name}")
            print(f"      Lookback: {lookback:.0f}m ({lookback/60:.1f}h)")
            print(f"      Reason: {reason}")
            print()
        
        print("=" * 60)
        print("💡 RECOMMENDATION:")
        print("   Add these features to CONFIG/excluded_features.yaml or")
        print("   ensure they are caught by active sanitization patterns.")
    else:
        print("✅ No obvious 1440m features found in the provided list.")
        print()
        print("💡 If you're still seeing a 1440m lookback discrepancy:")
        print("   1. Check the actual feature names in your logs")
        print("   2. Verify the feature registry metadata")
        print("   3. Check if the feature has a non-standard name")


if __name__ == "__main__":
    main()
