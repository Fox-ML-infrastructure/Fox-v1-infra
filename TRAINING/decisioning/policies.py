"""
Decision Policies

Define thresholds and heuristics for decision-making.
"""

from typing import Dict, Any, List, Optional, Tuple
import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)


class DecisionPolicy:
    """A decision policy that evaluates conditions and triggers actions."""
    
    def __init__(
        self,
        name: str,
        condition_fn,
        action: Optional[str] = None,
        reason: Optional[str] = None,
        level: int = 1  # 0=no action, 1=warning, 2=recommendation, 3=action
    ):
        """
        Initialize policy.
        
        Args:
            name: Policy name
            condition_fn: Function(cohort_data, latest_run) -> bool
            action: Action code if triggered (e.g., "freeze_features")
            reason: Reason code if triggered (e.g., "jaccard_collapse")
            level: Decision level (0-3)
        """
        self.name = name
        self.condition_fn = condition_fn
        self.action = action
        self.reason = reason
        self.level = level
    
    @staticmethod
    def get_default_policies() -> List['DecisionPolicy']:
        """Get default decision policies."""
        policies = []
        
        # Policy 1: Feature instability (jaccard collapse)
        def jaccard_collapse(cohort_data: pd.DataFrame, latest: pd.Series) -> bool:
            if len(cohort_data) < 3:
                return False
            if 'jaccard_topK' not in cohort_data.columns:
                return False
            recent = cohort_data['jaccard_topK'].tail(3).dropna()
            if len(recent) < 2:
                return False
            return recent.iloc[-1] < 0.5 and recent.iloc[-1] < recent.iloc[-2] * 0.8
        
        policies.append(DecisionPolicy(
            name="feature_instability",
            condition_fn=jaccard_collapse,
            action="freeze_features",
            reason="jaccard_collapse",
            level=2
        ))
        
        # Policy 2: Route instability (high entropy or frequent changes)
        def route_instability(cohort_data: pd.DataFrame, latest: pd.Series) -> bool:
            if len(cohort_data) < 3:
                return False
            if 'route_entropy' in cohort_data.columns:
                recent_entropy = cohort_data['route_entropy'].tail(3).dropna()
                if len(recent_entropy) > 0:
                    return recent_entropy.iloc[-1] > 1.5  # High entropy = unstable routing
            if 'route_changed' in cohort_data.columns:
                recent_changes = cohort_data['route_changed'].tail(5).sum()
                return recent_changes >= 3  # 3+ changes in last 5 runs
            return False
        
        policies.append(DecisionPolicy(
            name="route_instability",
            condition_fn=route_instability,
            action="tighten_routing",
            reason="route_instability",
            level=2
        ))
        
        # Policy 3: Performance decline with feature explosion
        def feature_explosion_decline(cohort_data: pd.DataFrame, latest: pd.Series) -> bool:
            if len(cohort_data) < 3:
                return False
            if 'cs_auc' not in cohort_data.columns or 'n_features_selected' not in cohort_data.columns:
                return False
            recent = cohort_data.tail(3)
            auc_trend = recent['cs_auc'].diff().tail(2)
            feature_trend = recent['n_features_selected'].diff().tail(2)
            # AUC declining while features increasing
            return (auc_trend.iloc[-1] < -0.01 and feature_trend.iloc[-1] > 10) if len(auc_trend) > 0 and len(feature_trend) > 0 else False
        
        policies.append(DecisionPolicy(
            name="feature_explosion_decline",
            condition_fn=feature_explosion_decline,
            action="cap_features",
            reason="feature_explosion_decline",
            level=2
        ))
        
        # Policy 4: Class balance drift
        def class_balance_drift(cohort_data: pd.DataFrame, latest: pd.Series) -> bool:
            if len(cohort_data) < 3:
                return False
            if 'pos_rate' not in cohort_data.columns:
                return False
            recent = cohort_data['pos_rate'].tail(3).dropna()
            if len(recent) < 2:
                return False
            drift = abs(recent.iloc[-1] - recent.iloc[0])
            return drift > 0.1  # 10% drift
        
        policies.append(DecisionPolicy(
            name="class_balance_drift",
            condition_fn=class_balance_drift,
            action="retune_class_weights",
            reason="pos_rate_drift",
            level=1  # Warning only
        ))
        
        return policies


def evaluate_policies(
    cohort_data: pd.DataFrame,
    latest_run: pd.Series,
    policies: List[DecisionPolicy]
) -> Dict[str, Dict[str, Any]]:
    """
    Evaluate all policies.
    
    Args:
        cohort_data: Historical data for cohort
        latest_run: Latest run data
        policies: List of policies to evaluate
    
    Returns:
        Dict mapping policy_name -> {triggered: bool, level: int, action: str, reason: str}
    """
    results = {}
    
    for policy in policies:
        try:
            triggered = policy.condition_fn(cohort_data, latest_run)
            results[policy.name] = {
                'triggered': triggered,
                'level': policy.level if triggered else 0,
                'action': policy.action if triggered else None,
                'reason': policy.reason if triggered else None
            }
        except Exception as e:
            logger.warning(f"Policy {policy.name} evaluation failed: {e}")
            results[policy.name] = {
                'triggered': False,
                'level': 0,
                'action': None,
                'reason': None
            }
    
    return results


def apply_decision_patch(
    resolved_config: Dict[str, Any],
    decision_result: Any  # DecisionResult (avoid circular import)
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Apply decision patch to resolved config.
    
    Args:
        resolved_config: Current resolved config
        decision_result: Decision result
    
    Returns:
        (new_config, patch_dict) - new config and patch that was applied
    """
    new_config = resolved_config.copy()
    patch = {}
    
    actions = decision_result.decision_action_mask or []
    
    # Action: freeze_features
    if "freeze_features" in actions:
        # Set feature selection to use cached/previous selection
        if 'feature_selection' not in new_config:
            new_config['feature_selection'] = {}
        new_config['feature_selection']['use_cached'] = True
        patch['feature_selection.use_cached'] = True
    
    # Action: tighten_routing
    if "tighten_routing" in actions:
        # Increase routing thresholds
        if 'target_routing' not in new_config:
            new_config['target_routing'] = {}
        if 'routing' not in new_config['target_routing']:
            new_config['target_routing']['routing'] = {}
        routing = new_config['target_routing']['routing']
        routing['cs_auc_threshold'] = routing.get('cs_auc_threshold', 0.65) * 1.1  # Increase by 10%
        routing['frac_symbols_good_threshold'] = routing.get('frac_symbols_good_threshold', 0.5) * 1.1
        patch['target_routing.routing.cs_auc_threshold'] = routing['cs_auc_threshold']
        patch['target_routing.routing.frac_symbols_good_threshold'] = routing['frac_symbols_good_threshold']
    
    # Action: cap_features
    if "cap_features" in actions:
        # Add feature cap
        if 'feature_selection' not in new_config:
            new_config['feature_selection'] = {}
        if 'max_features' not in new_config['feature_selection']:
            new_config['feature_selection']['max_features'] = 100  # Cap at 100
            patch['feature_selection.max_features'] = 100
    
    # Action: retune_class_weights
    if "retune_class_weights" in actions:
        # Flag for class weight retuning (doesn't auto-apply, just flags)
        if 'training' not in new_config:
            new_config['training'] = {}
        new_config['training']['retune_class_weights'] = True
        patch['training.retune_class_weights'] = True
    
    return new_config, patch
