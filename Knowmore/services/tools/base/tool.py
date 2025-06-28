from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

class BaseTool(ABC):
    """Base class for all tools"""
    
    def __init__(self):
        self.name = self.get_name()
        self.description = self.get_description()
        self.parameters = self.get_parameters()
    
    @abstractmethod
    def get_name(self) -> str:
        """Return the tool name"""
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """Return the tool description"""
        pass
    
    @abstractmethod
    def get_parameters(self) -> Dict[str, Any]:
        """Return the tool parameters schema"""
        pass
    
    @abstractmethod
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute the tool with given parameters"""
        pass
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """Validate parameters against schema"""
        # Basic validation - can be extended
        required_params = self.parameters.get('required', [])
        for param in required_params:
            if param not in parameters:
                return False
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert tool to dictionary format for API"""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters
            }
        }