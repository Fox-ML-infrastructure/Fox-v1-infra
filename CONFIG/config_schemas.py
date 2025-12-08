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
Typed Configuration Schemas

Defines dataclasses for all pipeline configuration types to ensure
type safety and prevent config "crossing" between modules.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Any, Optional


@dataclass
class ExperimentConfig:
    """Experiment-level configuration (what are we running?)"""
    name: str
    data_dir: Path
    symbols: List[str]
    target: str
    interval: str = "5m"
    max_samples_per_symbol: int = 5000
    description: Optional[str] = None
    
    # Optional overrides for specific modules
    feature_selection_overrides: Dict[str, Any] = field(default_factory=dict)
    target_ranking_overrides: Dict[str, Any] = field(default_factory=dict)
    training_overrides: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Convert string paths to Path objects"""
        if isinstance(self.data_dir, str):
            self.data_dir = Path(self.data_dir)


@dataclass
class FeatureSelectionConfig:
    """Feature selection module configuration"""
    top_n: int
    model_families: Dict[str, Dict[str, Any]]
    aggregation: Dict[str, Any]
    sampling: Dict[str, Any] = field(default_factory=dict)
    shap: Dict[str, Any] = field(default_factory=dict)
    permutation: Dict[str, Any] = field(default_factory=dict)
    cross_validation: Dict[str, Any] = field(default_factory=dict)
    output: Dict[str, Any] = field(default_factory=dict)
    compute: Dict[str, Any] = field(default_factory=dict)
    
    # Target info (from experiment config)
    target: Optional[str] = None
    data_dir: Optional[Path] = None
    symbols: Optional[List[str]] = None
    max_samples_per_symbol: Optional[int] = None


@dataclass
class TargetRankingConfig:
    """Target ranking module configuration"""
    model_families: Dict[str, Dict[str, Any]]
    ranking: Dict[str, Any] = field(default_factory=dict)
    sampling: Dict[str, Any] = field(default_factory=dict)
    cross_validation: Dict[str, Any] = field(default_factory=dict)
    
    # Target discovery settings
    min_samples: int = 100
    min_class_samples: int = 10
    
    # Data info (from experiment config)
    data_dir: Optional[Path] = None
    symbols: Optional[List[str]] = None
    max_samples_per_symbol: Optional[int] = None


@dataclass
class TrainingConfig:
    """Training module configuration"""
    model_families: Dict[str, Dict[str, Any]]
    cv_folds: int = 5
    pipeline: Dict[str, Any] = field(default_factory=dict)
    gpu: Dict[str, Any] = field(default_factory=dict)
    memory: Dict[str, Any] = field(default_factory=dict)
    preprocessing: Dict[str, Any] = field(default_factory=dict)
    threading: Dict[str, Any] = field(default_factory=dict)
    callbacks: Dict[str, Any] = field(default_factory=dict)
    optimizer: Dict[str, Any] = field(default_factory=dict)
    
    # Data info (from experiment config)
    target: Optional[str] = None
    data_dir: Optional[Path] = None
    symbols: Optional[List[str]] = None
    max_samples_per_symbol: Optional[int] = None


@dataclass
class LeakageConfig:
    """Leakage detection and auto-fix configuration"""
    safety: Dict[str, Any] = field(default_factory=dict)
    auto_fix: Dict[str, Any] = field(default_factory=dict)
    auto_rerun: Dict[str, Any] = field(default_factory=dict)
    pre_scan: Dict[str, Any] = field(default_factory=dict)
    warning_thresholds: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SystemConfig:
    """System-level configuration (paths, logging, etc.)"""
    paths: Dict[str, Any] = field(default_factory=dict)
    logging: Dict[str, Any] = field(default_factory=dict)
    defaults: Dict[str, Any] = field(default_factory=dict)
    backup: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DataConfig:
    """Data loading configuration"""
    timestamp_column: str = "ts"
    interval: str = "5m"
    max_samples_per_symbol: int = 50000
    validation_split: float = 0.2
    random_state: int = 42

