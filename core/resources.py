"""
Resource template handling implementation following MCP standards.
"""

from typing import Dict, Any, Optional, List, Union, Callable
import re
from dataclasses import dataclass
from .errors import InvalidInputError, ResourceNotFoundError, ProcessingError

@dataclass
class ResourceTemplate:
    """
    MCP Resource Template implementation.
    
    Handles URI template parsing and matching according to MCP specification.
    """
    template: str
    variables: Dict[str, str]
    constraints: Optional[Dict[str, Any]] = None
    description: Optional[str] = None

    def __post_init__(self):
        """Validate and process template after initialization"""
        self.pattern = self._compile_template()
        self._validate_constraints()

    def _compile_template(self) -> re.Pattern:
        """Compile template into regex pattern"""
        pattern = self.template
        
        # Replace template variables with named capture groups
        for var_name in self.variables:
            var_pattern = "{" + var_name + "}"
            if var_pattern in pattern:
                constraint = self.constraints.get(var_name) if self.constraints else None
                regex = self._get_constraint_pattern(constraint)
                pattern = pattern.replace(var_pattern, f"(?P<{var_name}>{regex})")
        
        return re.compile(f"^{pattern}$")

    def _get_constraint_pattern(self, constraint: Optional[Any]) -> str:
        """Convert constraint to regex pattern"""
        if not constraint:
            return "[^/]+"  # Default: match anything except path separator
            
        if isinstance(constraint, str):
            return re.escape(constraint)
        elif isinstance(constraint, list):
            return "|".join(map(re.escape, constraint))
        elif isinstance(constraint, dict):
            if "pattern" in constraint:
                return constraint["pattern"]
            elif "enum" in constraint:
                return "|".join(map(re.escape, constraint["enum"]))
            elif "type" in constraint:
                return {
                    "string": r"[^/]+",
                    "integer": r"-?\d+",
                    "number": r"-?\d*\.?\d+",
                    "boolean": r"true|false",
                    "path": r".+"
                }.get(constraint["type"], r"[^/]+")
        
        return "[^/]+"

    def _validate_constraints(self):
        """Validate constraint definitions"""
        if not self.constraints:
            return
            
        for var_name, constraint in self.constraints.items():
            if var_name not in self.variables:
                raise InvalidInputError(
                    f"Constraint defined for non-existent variable: {var_name}"
                )
            
            if isinstance(constraint, dict):
                valid_keys = {"type", "pattern", "enum", "min", "max", "format"}
                invalid_keys = set(constraint.keys()) - valid_keys
                if invalid_keys:
                    raise InvalidInputError(
                        f"Invalid constraint keys for {var_name}: {invalid_keys}"
                    )

    def match(self, uri: str) -> Optional[Dict[str, str]]:
        """
        Match URI against template pattern.
        
        Args:
            uri: URI to match
            
        Returns:
            Dict of matched variables or None if no match
            
        Raises:
            InvalidInputError: If URI is invalid
        """
        try:
            match = self.pattern.match(uri)
            if match:
                variables = match.groupdict()
                self._validate_variables(variables)
                return variables
            return None
        except Exception as e:
            raise InvalidInputError(f"Invalid URI format: {str(e)}")

    def _validate_variables(self, variables: Dict[str, str]):
        """Validate matched variables against constraints"""
        if not self.constraints:
            return
            
        for var_name, value in variables.items():
            constraint = self.constraints.get(var_name)
            if not constraint:
                continue
                
            if isinstance(constraint, dict):
                self._validate_against_constraint(var_name, value, constraint)

    def _validate_against_constraint(
        self,
        var_name: str,
        value: str,
        constraint: Dict[str, Any]
    ):
        """Validate value against specific constraint"""
        if "type" in constraint:
            self._validate_type(var_name, value, constraint["type"])
        
        if "min" in constraint and float(value) < constraint["min"]:
            raise InvalidInputError(
                f"Value {value} for {var_name} below minimum {constraint['min']}"
            )
        
        if "max" in constraint and float(value) > constraint["max"]:
            raise InvalidInputError(
                f"Value {value} for {var_name} above maximum {constraint['max']}"
            )
        
        if "enum" in constraint and value not in constraint["enum"]:
            raise InvalidInputError(
                f"Value {value} for {var_name} not in allowed values: {constraint['enum']}"
            )
        
        if "format" in constraint:
            format_pattern = {
                "date": r"^\d{4}-\d{2}-\d{2}$",
                "time": r"^\d{2}:\d{2}:\d{2}$",
                "datetime": r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z?$",
                "email": r"^[^@]+@[^@]+\.[^@]+$",
                "uuid": r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
            }.get(constraint["format"])
            
            if format_pattern and not re.match(format_pattern, value):
                raise InvalidInputError(
                    f"Value {value} for {var_name} does not match format {constraint['format']}"
                )

    def _validate_type(self, var_name: str, value: str, type_name: str):
        """Validate value against type constraint"""
        try:
            if type_name == "integer":
                int(value)
            elif type_name == "number":
                float(value)
            elif type_name == "boolean":
                if value.lower() not in ("true", "false"):
                    raise ValueError
        except ValueError:
            raise InvalidInputError(
                f"Value {value} for {var_name} is not of type {type_name}"
            )

    def to_dict(self) -> Dict[str, Any]:
        """Convert template to dictionary representation"""
        return {
            "template": self.template,
            "variables": self.variables,
            "constraints": self.constraints,
            "description": self.description
        }

class ResourceHandler:
    """
    Handler for MCP resources using templates.
    
    Maps URI templates to handler functions and manages resource access.
    """
    
    def __init__(self):
        self.templates: List[ResourceTemplate] = []
        self.handlers: Dict[str, Callable] = {}

    def register(
        self,
        template: str,
        variables: Dict[str, str],
        handler: Callable,
        constraints: Optional[Dict[str, Any]] = None,
        description: Optional[str] = None
    ):
        """Register a new resource template and handler"""
        resource_template = ResourceTemplate(
            template=template,
            variables=variables,
            constraints=constraints,
            description=description
        )
        self.templates.append(resource_template)
        self.handlers[template] = handler

    async def handle(self, uri: str) -> Any:
        """
        Handle resource request using registered templates.
        
        Args:
            uri: Resource URI to handle
            
        Returns:
            Handler result
            
        Raises:
            ResourceNotFoundError: If no matching template found
            InvalidInputError: If URI is invalid
        """
        for template in self.templates:
            variables = template.match(uri)
            if variables is not None:
                handler = self.handlers[template.template]
                try:
                    return await handler(**variables)
                except Exception as e:
                    raise ProcessingError(
                        f"Resource handler failed: {str(e)}",
                        {"uri": uri, "variables": variables}
                    )
        
        raise ResourceNotFoundError(
            f"No matching resource template for URI: {uri}"
        )

    def list_resources(self) -> List[Dict[str, Any]]:
        """List all registered resource templates"""
        return [template.to_dict() for template in self.templates]

    def get_template(self, template_str: str) -> Optional[ResourceTemplate]:
        """Get resource template by template string"""
        for template in self.templates:
            if template.template == template_str:
                return template
        return None

    def unregister(self, template_str: str):
        """Unregister a resource template"""
        template = self.get_template(template_str)
        if template:
            self.templates.remove(template)
            del self.handlers[template_str]
