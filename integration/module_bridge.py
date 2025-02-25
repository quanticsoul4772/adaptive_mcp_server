"""
Module Bridge: Facilitates communication and coordination between different MCP server modules.
"""

from typing import Dict, Any, List, Optional
from enum import Enum, auto
from dataclasses import dataclass, field
import asyncio
import logging

class ModuleType(Enum):
    REASONING = auto()
    RESEARCH = auto()
    VALIDATION = auto()
    CREATIVE = auto()

@dataclass
class ModuleContext:
    """Represents the context and state of a module"""
    module_type: ModuleType
    capabilities: Dict[str, Any] = field(default_factory=dict)
    current_state: Dict[str, Any] = field(default_factory=dict)
    performance_metrics: Dict[str, float] = field(default_factory=dict)

class ModuleBridge:
    """
    Manages communication and coordination between different MCP server modules.
    """
    def __init__(self):
        """Initialize the module bridge with empty module registries"""
        self._registered_modules: Dict[ModuleType, List[Any]] = {
            ModuleType.REASONING: [],
            ModuleType.RESEARCH: [],
            ModuleType.VALIDATION: [],
            ModuleType.CREATIVE: []
        }
        self._module_contexts: Dict[ModuleType, ModuleContext] = {}
        self._logger = logging.getLogger('mcp.module_bridge')

    def register_module(self, module: Any, module_type: ModuleType):
        """
        Register a module with the bridge
        
        Args:
            module: Module instance to register
            module_type: Type of module being registered
        """
        self._registered_modules[module_type].append(module)
        
        # Create a context for the module
        context = ModuleContext(
            module_type=module_type,
            capabilities=self._extract_module_capabilities(module)
        )
        self._module_contexts[module_type] = context
        
        self._logger.info(f"Registered {module_type.name} module: {module.__class__.__name__}")

    def _extract_module_capabilities(self, module: Any) -> Dict[str, Any]:
        """
        Extract capabilities from a module
        
        Args:
            module: Module to analyze
        
        Returns:
            Dictionary of module capabilities
        """
        capabilities = {}
        for method_name in dir(module):
            if method_name.startswith('can_') or method_name.startswith('supports_'):
                method = getattr(module, method_name)
                if callable(method):
                    try:
                        capabilities[method_name] = method()
                    except Exception:
                        capabilities[method_name] = False
        return capabilities

    async def coordinate_modules(
        self, 
        primary_module_type: ModuleType, 
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Coordinate modules to process input data
        
        Args:
            primary_module_type: Module type initiating the coordination
            input_data: Input data to process
        
        Returns:
            Processed and integrated results
        """
        try:
            # Initialize results container
            coordinated_results = {
                'input': input_data,
                'module_outputs': {},
                'integrated_output': None
            }

            # Execute modules in a coordinated sequence
            for module_type in [
                ModuleType.RESEARCH,
                ModuleType.REASONING,
                ModuleType.CREATIVE,
                ModuleType.VALIDATION
            ]:
                if module_type == primary_module_type:
                    continue

                module_results = await self._execute_module_type(
                    module_type, 
                    input_data, 
                    coordinated_results
                )
                
                coordinated_results['module_outputs'][module_type.name] = module_results

            # Perform final integration
            coordinated_results['integrated_output'] = await self._integrate_results(
                coordinated_results['module_outputs']
            )

            return coordinated_results

        except Exception as e:
            self._logger.error(f"Module coordination error: {e}")
            raise

    async def _execute_module_type(
        self, 
        module_type: ModuleType, 
        input_data: Dict[str, Any],
        previous_results: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Execute all modules of a specific type
        
        Args:
            module_type: Type of modules to execute
            input_data: Input data for modules
            previous_results: Results from previous module executions
        
        Returns:
            List of results from modules of this type
        """
        module_results = []
        for module in self._registered_modules[module_type]:
            try:
                # Dynamically find an appropriate method for processing
                process_method = getattr(module, 'process', None) or \
                                 getattr(module, 'reason', None) or \
                                 getattr(module, 'validate', None)
                
                if process_method and callable(process_method):
                    result = await process_method(
                        input_data, 
                        context=previous_results
                    )
                    module_results.append(result)
            except Exception as e:
                self._logger.warning(f"Error in {module_type.name} module: {e}")
        
        return module_results

    async def _integrate_results(
        self, 
        module_outputs: Dict[str, List[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """
        Integrate results from different modules
        
        Args:
            module_outputs: Outputs from different module types
        
        Returns:
            Integrated result
        """
        # Basic integration strategy: combine confidences and aggregate insights
        integrated_result = {
            'confidences': {},
            'insights': [],
            'final_output': None
        }

        for module_type, results in module_outputs.items():
            for result in results:
                # Collect confidences
                if 'confidence' in result:
                    integrated_result['confidences'][module_type] = result['confidence']
                
                # Aggregate insights
                if 'insights' in result:
                    integrated_result['insights'].extend(result['insights'])

        # Compute weighted final output based on confidences
        if integrated_result['confidences']:
            total_confidence = sum(integrated_result['confidences'].values())
            integrated_result['final_output'] = {
                'weighted_confidence': total_confidence / len(integrated_result['confidences']),
                'module_contributions': integrated_result['confidences']
            }

        return integrated_result

    def get_module_performance(self, module_type: ModuleType) -> Dict[str, float]:
        """
        Retrieve performance metrics for a module type
        
        Args:
            module_type: Type of module to get metrics for
        
        Returns:
            Performance metrics
        """
        context = self._module_contexts.get(module_type)
        return context.performance_metrics if context else {}

# Singleton instance
module_bridge = ModuleBridge()
