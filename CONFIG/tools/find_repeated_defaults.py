#!/usr/bin/env python
"""
Scan YAML configs and find repeated (key_path, value) pairs
that are good candidates for centralization into CONFIG/defaults.yaml.

This script helps identify Single Source of Truth (SST) opportunities by
finding settings that are duplicated across multiple config files.

Usage:
    python CONFIG/tools/find_repeated_defaults.py
    python CONFIG/tools/find_repeated_defaults.py --min-occurrences 5 --min-coverage 0.7
    python CONFIG/tools/find_repeated_defaults.py --group-by-family
"""

import argparse
import sys
from collections import defaultdict, Counter
from pathlib import Path
from typing import Any, Dict, List, Tuple, Set
import yaml

# Add CONFIG to path for imports
_CONFIG_DIR = Path(__file__).resolve().parent.parent
if str(_CONFIG_DIR) not in sys.path:
    sys.path.insert(0, str(_CONFIG_DIR))


def is_scalar(value: Any) -> bool:
    """Return True if value is a scalar we care about for defaults."""
    return isinstance(value, (int, float, bool, str)) and value is not None


def flatten_dict(d: Dict[str, Any], parent_key: str = "", max_depth: int = 10) -> Dict[str, Any]:
    """
    Flatten a nested dict to dotted keys.
    Example:
        {"a": {"b": 1}, "c": 2} -> {"a.b": 1, "c": 2}
    """
    if max_depth <= 0:
        return {}
    
    items: Dict[str, Any] = {}
    for k, v in d.items():
        if parent_key:
            new_key = f"{parent_key}.{k}"
        else:
            new_key = k

        if isinstance(v, dict):
            items.update(flatten_dict(v, new_key, max_depth - 1))
        elif isinstance(v, list):
            # Skip lists for now (could extend later)
            continue
        else:
            items[new_key] = v
    return items


def should_skip_key(key_path: str) -> bool:
    """
    Skip keys that obviously should not be global defaults.
    These are typically identifiers, paths, or content-specific values.
    """
    blacklist_substrings = [
        "name",
        "symbol",
        "ticker",
        "path",
        "file",
        "checkpoint",
        "output_dir",
        "save_dir",
        "experiment",
        "description",
        "model_family",
        "target",
        "data_dir",
        "joblib_temp",
        "note",
        "aliases",
        "variants",
    ]
    lower = key_path.lower()
    return any(substr in lower for substr in blacklist_substrings)


def should_skip_file(file_path: Path) -> bool:
    """Skip files that shouldn't be scanned for defaults."""
    skip_names = {
        "defaults.yaml",
        "logging_config.yaml",
        "feature_registry.yaml",
        "feature_groups.yaml",
        "excluded_features.yaml",
        "feature_target_schema.yaml",
    }
    return file_path.name in skip_names


def detect_model_family(file_path: Path, data: Dict[str, Any]) -> str:
    """
    Detect model family from file path or config content.
    Returns family name or 'other' if unknown.
    """
    # Check file path
    if "model_config" in str(file_path):
        # Extract from filename: model_config/lightgbm.yaml -> lightgbm
        name = file_path.stem.lower()
        return name
    
    # Check config content
    if "model_family" in data:
        family = str(data["model_family"]).lower()
        return family
    
    # Check for model families section
    if "model_families" in data:
        # This is a multi-model config, return 'multi_model'
        return "multi_model"
    
    # Check for common patterns
    if "hyperparameters" in data:
        # Likely a model config
        return file_path.stem.lower()
    
    return "other"


def load_yaml(path: Path) -> Dict[str, Any]:
    """Load YAML file safely."""
    try:
        with path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        if not isinstance(data, dict):
            return {}
        return data
    except Exception as e:
        print(f"Warning: Failed to load {path}: {e}", file=sys.stderr)
        return {}


def analyze_configs(
    root: Path,
    min_occurrences: int = 3,
    min_coverage: float = 0.6,
    group_by_family: bool = False,
    include_patterns: List[str] = None,
) -> Dict[str, Any]:
    """
    Analyze config files and find repeated defaults.
    
    Returns:
        Dictionary with analysis results
    """
    # Gather YAML files
    if include_patterns:
        yaml_files = set()
        for pattern in include_patterns:
            yaml_files.update(root.glob(pattern))
    else:
        yaml_files = set(root.rglob("*.yaml"))
    
    # Filter out skipped files
    yaml_files = {p for p in yaml_files if not should_skip_file(p)}
    
    if not yaml_files:
        return {"error": "No YAML files found to scan."}
    
    # stats[key_path][value] -> count
    stats: Dict[str, Counter] = defaultdict(Counter)
    # Track which files have each key (for coverage calculation)
    key_file_counts: Counter = Counter()
    # Track which files use each (key, value) pair
    key_value_files: Dict[Tuple[str, Any], Set[Path]] = defaultdict(set)
    # Track model families
    file_families: Dict[Path, str] = {}
    
    print(f"Scanning {len(yaml_files)} YAML files under {root}...\n")
    
    for path in sorted(yaml_files):
        data = load_yaml(path)
        if not data:
            continue
        
        family = detect_model_family(path, data)
        file_families[path] = family
        
        flat = flatten_dict(data)
        keys_seen_in_file = set()
        
        for key_path, value in flat.items():
            if should_skip_key(key_path):
                continue
            if not is_scalar(value):
                continue
            
            keys_seen_in_file.add(key_path)
            stats[key_path][value] += 1
            key_value_files[(key_path, value)].add(path)
        
        for key_path in keys_seen_in_file:
            key_file_counts[key_path] += 1
    
    if not stats:
        return {"error": "No scalar config entries found (after filtering)."}
    
    # Build candidate list
    candidates: List[Tuple[str, Any, int, int, float, Set[Path]]] = []
    
    for key_path, counter in stats.items():
        total_for_key = key_file_counts[key_path]
        if total_for_key == 0:
            continue
        
        most_common_value, count = counter.most_common(1)[0]
        coverage = count / float(total_for_key)
        
        if count >= min_occurrences and coverage >= min_coverage:
            files_using_value = key_value_files.get((key_path, most_common_value), set())
            candidates.append(
                (key_path, most_common_value, count, total_for_key, coverage, files_using_value)
            )
    
    # Group by family if requested
    family_groups = defaultdict(list)
    if group_by_family:
        for key_path, value, count, total, coverage, files in candidates:
            # Determine which family this key belongs to
            families_using = {file_families.get(f, "other") for f in files}
            if len(families_using) == 1:
                family = list(families_using)[0]
            else:
                family = "mixed"
            family_groups[family].append((key_path, value, count, total, coverage, files))
    
    return {
        "total_files": len(yaml_files),
        "candidates": candidates,
        "family_groups": dict(family_groups) if group_by_family else None,
        "file_families": file_families,
    }


def format_file_list(files: Set[Path], root: Path, max_files: int = 5) -> str:
    """Format list of files, showing relative paths."""
    file_list = sorted(files)
    if len(file_list) <= max_files:
        return "\n".join(f"      - {f.relative_to(root)}" for f in file_list)
    else:
        shown = file_list[:max_files]
        remaining = len(file_list) - max_files
        lines = [f"      - {f.relative_to(root)}" for f in shown]
        lines.append(f"      ... and {remaining} more")
        return "\n".join(lines)


def print_report(results: Dict[str, Any], root: Path, min_occurrences: int, min_coverage: float):
    """Print formatted report of candidates."""
    if "error" in results:
        print(f"Error: {results['error']}")
        return
    
    total_files = results["total_files"]
    candidates = results["candidates"]
    family_groups = results.get("family_groups")
    
    print(f"Total configs scanned: {total_files}")
    print(f"min_occurrences={min_occurrences}, min_coverage={min_coverage:.2f}\n")
    
    if not candidates:
        print("No candidate defaults found with the current thresholds.")
        print("\nTry lowering --min-occurrences or --min-coverage to see more candidates.")
        return
    
    # Sort by count (descending), then by key_path
    candidates.sort(key=lambda x: (-x[2], x[0]))
    
    if family_groups:
        print("=== Candidate defaults (grouped by model family) ===\n")
        for family in sorted(family_groups.keys()):
            print(f"\n--- {family.upper()} ---")
            for key_path, value, count, total, coverage, files in sorted(
                family_groups[family], key=lambda x: (-x[2], x[0])
            ):
                print(f"\n{key_path}")
                print(f"  value       : {repr(value)}")
                print(f"  used in     : {count} / {total} configs ({coverage*100:.1f}%)")
                print(f"  files:")
                print(format_file_list(files, root))
    else:
        print("=== Candidate defaults ===\n")
        for key_path, value, count, total, coverage, files in candidates:
            print(f"{key_path}")
            print(f"  value       : {repr(value)}")
            print(f"  used in     : {count} / {total} configs ({coverage*100:.1f}%)")
            print(f"  files:")
            print(format_file_list(files, root))
            print()
    
    print(f"\n=== Summary ===")
    print(f"Found {len(candidates)} candidate defaults to centralize")
    print(f"\nNext steps:")
    print(f"1. Review the candidates above")
    print(f"2. Add them to CONFIG/defaults.yaml in appropriate sections")
    print(f"3. Remove explicit values from individual config files (optional, gradual)")


def main():
    parser = argparse.ArgumentParser(
        description="Find repeated config values that should be centralized into defaults.yaml",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic scan with default thresholds
  python CONFIG/tools/find_repeated_defaults.py

  # Stricter thresholds (must appear in 5+ files and 70%+ coverage)
  python CONFIG/tools/find_repeated_defaults.py --min-occurrences 5 --min-coverage 0.7

  # Group results by model family
  python CONFIG/tools/find_repeated_defaults.py --group-by-family

  # Scan only specific directories
  python CONFIG/tools/find_repeated_defaults.py --include 'model_config/*.yaml' 'training_config/*.yaml'
        """
    )
    parser.add_argument(
        "--root",
        type=str,
        default="CONFIG",
        help="Root directory to scan for YAML configs (default: CONFIG)",
    )
    parser.add_argument(
        "--min-occurrences",
        type=int,
        default=3,
        help="Minimum number of configs a (key,value) pair must appear in "
             "to be considered a candidate (default: 3)",
    )
    parser.add_argument(
        "--min-coverage",
        type=float,
        default=0.6,
        help="Minimum fraction of configs that share the same value for a key "
             "to treat it as a default (0.0–1.0, default: 0.6)",
    )
    parser.add_argument(
        "--include",
        nargs="*",
        default=None,
        help="Optional glob pattern(s) relative to root to restrict which YAMLs to scan. "
             "Example: --include 'model_config/*.yaml' 'training_config/*.yaml'",
    )
    parser.add_argument(
        "--group-by-family",
        action="store_true",
        help="Group candidates by model family (tree models, neural networks, etc.)",
    )
    
    args = parser.parse_args()
    
    root = Path(args.root).resolve()
    if not root.exists():
        print(f"Error: Root directory not found: {root}", file=sys.stderr)
        sys.exit(1)
    
    # If running from repo root, adjust path
    if not root.exists() and Path("CONFIG").exists():
        root = Path("CONFIG").resolve()
    
    results = analyze_configs(
        root=root,
        min_occurrences=args.min_occurrences,
        min_coverage=args.min_coverage,
        group_by_family=args.group_by_family,
        include_patterns=args.include,
    )
    
    print_report(results, root, args.min_occurrences, args.min_coverage)


if __name__ == "__main__":
    main()
