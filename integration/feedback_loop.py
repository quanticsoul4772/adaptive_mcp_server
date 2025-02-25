"""
Feedback Loop: Implements intelligent feedback mechanism between MCP server modules.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
import asyncio
import logging
import statistics

@dataclass
class FeedbackMetric:
    """Represents a specific feedback metric"""
    name: str
    value: float
    weight: float = 1.0

@dataclass
class ModuleFeedback:
    """Captures feedback for a specific module"""
    module_name: str
    metrics: List[FeedbackMetric] = field(default_factory=list)
    timestamp: float = field(default_factory=asyncio.get_event_loop().time)

class FeedbackLoop:
    """
    Manages intelligent feedback and learning between different MCP server modules.
    """
    def __init__(self, learning_rate: float = 0.1):
        """
        Initialize the feedback loop
        
        Args:
            learning_rate: Rate at which feedback influences module behavior
        """
        self._module_feedbacks: Dict[str, List[ModuleFeedback]] = {}
        self._learning_rate = learning_rate
        self._logger = logging.getLogger('mcp.feedback_loop')

    def record_module_feedback(
        self, 
        module_name: str, 
        metrics: List[FeedbackMetric]
    ):
        """
        Record feedback metrics for a module
        
        Args:
            module_name: Name of the module
            metrics: List of feedback metrics
        """
        if module_name not in self._module_feedbacks:
            self._module_feedbacks[module_name] = []
        
        module_feedback = ModuleFeedback(
            module_name=module_name,
            metrics=metrics
        )
        
        self._module_feedbacks[module_name].append(module_feedback)
        
        # Limit historical feedbacks
        if len(self._module_feedbacks[module_name]) > 100:
            self._module_feedbacks[module_name] = self._module_feedbacks[module_name][-100:]
        
        self._logger.info(f"Recorded feedback for {module_name}")

    def analyze_module_performance(
        self, 
        module_name: str, 
        metric_filter: Optional[List[str]] = None
    ) -> Dict[str, float]:
        """
        Analyze performance of a module based on recorded feedback
        
        Args:
            module_name: Name of the module to analyze
            metric_filter: Optional list of metrics to focus on
        
        Returns:
            Performance analysis results
        """
        if module_name not in self._module_feedbacks:
            return {}
        
        module_feedbacks = self._module_feedbacks[module_name]
        
        # Compute weighted performance metrics
        performance_metrics = {}
        
        # Group metrics by name
        metric_groups = {}
        for feedback in module_feedbacks:
            for metric in feedback.metrics:
                if metric_filter and metric.name not in metric_filter:
                    continue
                
                if metric.name not in metric_groups:
                    metric_groups[metric.name] = []
                metric_groups[metric.name].append(metric.value)
        
        # Compute statistics for each metric group
        for metric_name, values in metric_groups.items():
            performance_metrics[metric_name] = {
                'mean': statistics.mean(values),
                'median': statistics.median(values),
                'std_dev': statistics.stdev(values) if len(values) > 1 else 0,
                'min': min(values),
                'max': max(values)
            }
        
        return performance_metrics

    async def generate_adaptive_configuration(
        self, 
        module_name: str
    ) -> Dict[str, Any]:
        """
        Generate adaptive configuration based on historical performance
        
        Args:
            module_name: Name of the module
        
        Returns:
            Adaptive configuration suggestions
        """
        performance = self.analyze_module_performance(module_name)
        
        # Basic adaptive configuration generation
        adaptive_config = {
            'performance_basis': performance,
            'suggested_adjustments': {}
        }
        
        # Example adaptation logic
        for metric_name, metric_stats in performance.items():
            if metric_stats['mean'] < 0.5:
                # If performance is low, suggest parameter relaxation
                adaptive_config['suggested_adjustments'][metric_name] = {
                    'strategy': 'relaxation',
                    'recommendation': f"Consider relaxing constraints for {metric_name}"
                }
            elif metric_stats['mean'] > 0.8:
                # If performance is high, suggest optimization
                adaptive_config['suggested_adjustments'][metric_name] = {
                    'strategy': 'optimization',
                    'recommendation': f"Potential for further optimization in {metric_name}"
                }
        
        return adaptive_config

    def reset_module_feedback(self, module_name: Optional[str] = None):
        """
        Reset feedback history for a module or all modules
        
        Args:
            module_name: Optional specific module to reset. If None, reset all.
        """
        if module_name:
            if module_name in self._module_feedbacks:
                del self._module_feedbacks[module_name]
        else:
            self._module_feedbacks.clear()
        
        self._logger.info(f"Reset feedback {'for ' + module_name if module_name else 'for all modules'}")

# Singleton instance
feedback_loop = FeedbackLoop()
