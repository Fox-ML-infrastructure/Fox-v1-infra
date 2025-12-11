"""
Reproducibility Tracking Module

Tracks and compares run results across pipeline stages to verify deterministic behavior.
Supports target ranking, feature selection, and other pipeline stages.

Usage:
    from TRAINING.utils.reproducibility_tracker import ReproducibilityTracker
    
    tracker = ReproducibilityTracker(output_dir=Path("results"))
    tracker.log_comparison(
        stage="target_ranking",
        item_name="y_will_swing_low_15m_0.05",
        metrics={
            "mean_score": 0.751,
            "std_score": 0.029,
            "mean_importance": 0.23,
            "composite_score": 0.764,
            "metric_name": "ROC-AUC"
        }
    )
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class ReproducibilityTracker:
    """
    Tracks run results and compares them to previous runs for reproducibility verification.
    
    Stores run summaries in JSON format and provides comparison logging with tolerance-based
    verification. Helps verify deterministic behavior across pipeline stages.
    """
    
    def __init__(
        self,
        output_dir: Path,
        log_file_name: str = "reproducibility_log.json",
        max_runs_per_item: int = 10,
        score_tolerance: float = 0.001,  # 0.1% tolerance
        importance_tolerance: float = 0.01  # 1% tolerance
    ):
        """
        Initialize reproducibility tracker.
        
        Args:
            output_dir: Directory where reproducibility logs are stored
            log_file_name: Name of the JSON log file
            max_runs_per_item: Maximum number of runs to keep per item (prevents log bloat)
            score_tolerance: Tolerance for score differences (default: 0.1%)
            importance_tolerance: Tolerance for importance differences (default: 1%)
        """
        self.output_dir = Path(output_dir)
        self.log_file = self.output_dir / log_file_name
        self.max_runs_per_item = max_runs_per_item
        self.score_tolerance = score_tolerance
        self.importance_tolerance = importance_tolerance
    
    def load_previous_run(
        self,
        stage: str,
        item_name: str
    ) -> Optional[Dict[str, Any]]:
        """
        Load the previous run's summary for a stage/item combination.
        
        Args:
            stage: Pipeline stage name (e.g., "target_ranking", "feature_selection")
            item_name: Name of the item (e.g., target name, symbol name)
        
        Returns:
            Dictionary with previous run results, or None if no previous run exists
        """
        if not self.log_file.exists():
            return None
        
        try:
            with open(self.log_file, 'r') as f:
                all_runs = json.load(f)
            
            # Get the most recent run for this stage/item
            key = f"{stage}:{item_name}"
            item_runs = all_runs.get(key, [])
            if not item_runs:
                return None
            
            # Return the most recent (last) entry
            return item_runs[-1]
        except (json.JSONDecodeError, KeyError, IndexError, IOError) as e:
            logger.debug(f"Could not load previous run for {stage}:{item_name}: {e}")
            return None
    
    def save_run(
        self,
        stage: str,
        item_name: str,
        metrics: Dict[str, Any],
        additional_data: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Save the current run's summary to the reproducibility log.
        
        Args:
            stage: Pipeline stage name (e.g., "target_ranking", "feature_selection")
            item_name: Name of the item (e.g., target name, symbol name)
            metrics: Dictionary of metrics to track (must include at least mean_score, std_score)
            additional_data: Optional additional data to store with the run
        """
        # Load existing runs
        all_runs = {}
        if self.log_file.exists():
            try:
                with open(self.log_file, 'r') as f:
                    all_runs = json.load(f)
            except (json.JSONDecodeError, IOError):
                all_runs = {}
        
        # Create key for this stage/item combination
        key = f"{stage}:{item_name}"
        
        # Initialize entry if needed
        if key not in all_runs:
            all_runs[key] = []
        
        # Create summary entry
        summary = {
            "timestamp": datetime.now().isoformat(),
            "stage": stage,
            "item_name": item_name,
            **{k: float(v) if isinstance(v, (int, float)) else v 
               for k, v in metrics.items()}
        }
        
        if additional_data:
            summary["additional_data"] = additional_data
        
        # Append to item's run history (keep last N runs)
        all_runs[key].append(summary)
        if len(all_runs[key]) > self.max_runs_per_item:
            all_runs[key] = all_runs[key][-self.max_runs_per_item:]
        
        # Save back to file
        try:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            with open(self.log_file, 'w') as f:
                json.dump(all_runs, f, indent=2)
        except IOError as e:
            logger.warning(f"Could not save reproducibility log: {e}")
    
    def log_comparison(
        self,
        stage: str,
        item_name: str,
        metrics: Dict[str, Any],
        additional_data: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Compare current run to previous run and log the comparison for reproducibility verification.
        
        Args:
            stage: Pipeline stage name (e.g., "target_ranking", "feature_selection")
            item_name: Name of the item (e.g., target name, symbol name)
            metrics: Dictionary of metrics to track and compare
            additional_data: Optional additional data to store with the run
        """
        previous = self.load_previous_run(stage, item_name)
        
        if previous is None:
            logger.info(f"📊 Reproducibility: First run for {stage}:{item_name} (no previous run to compare)")
            # Save current run for next time
            self.save_run(stage, item_name, metrics, additional_data)
            return
        
        # Extract metrics for comparison
        metric_name = metrics.get("metric_name", "Score")
        current_mean = float(metrics.get("mean_score", 0.0))
        previous_mean = float(previous.get("mean_score", 0.0))
        mean_diff = current_mean - previous_mean
        
        current_std = float(metrics.get("std_score", 0.0))
        previous_std = float(previous.get("std_score", 0.0))
        std_diff = current_std - previous_std
        
        # Compare importance if present
        current_importance = float(metrics.get("mean_importance", 0.0))
        previous_importance = float(previous.get("mean_importance", 0.0))
        importance_diff = current_importance - previous_importance
        
        # Compare composite score if present
        current_composite = float(metrics.get("composite_score", current_mean))
        previous_composite = float(previous.get("composite_score", previous_mean))
        composite_diff = current_composite - previous_composite
        
        # Calculate relative differences (for percentage change)
        mean_pct = (mean_diff / abs(previous_mean)) * 100 if previous_mean != 0 else 0.0
        composite_pct = (composite_diff / abs(previous_composite)) * 100 if previous_composite != 0 else 0.0
        
        # Determine if results are reproducible (within tolerance)
        is_reproducible = (
            abs(mean_diff) < self.score_tolerance and
            abs(composite_diff) < self.score_tolerance and
            abs(importance_diff) < self.importance_tolerance
        )
        
        status_emoji = "✅" if is_reproducible else "⚠️"
        status_text = "REPRODUCIBLE" if is_reproducible else "DIFFERENT"
        
        # Build comparison log message
        logger.info(f"{status_emoji} Reproducibility ({status_text}):")
        logger.info(f"   Previous: {metric_name}={previous_mean:.3f}±{previous_std:.3f}, "
                   f"importance={previous_importance:.2f}, composite={previous_composite:.3f}")
        logger.info(f"   Current:  {metric_name}={current_mean:.3f}±{current_std:.3f}, "
                   f"importance={current_importance:.2f}, composite={current_composite:.3f}")
        logger.info(f"   Diff:     {metric_name}={mean_diff:+.4f} ({mean_pct:+.2f}%), "
                   f"composite={composite_diff:+.4f} ({composite_pct:+.2f}%), "
                   f"importance={importance_diff:+.2f}")
        
        if not is_reproducible:
            logger.warning(f"   ⚠️  Results differ from previous run - check for non-deterministic behavior")
        
        # Save current run for next time
        self.save_run(stage, item_name, metrics, additional_data)
