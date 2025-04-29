from typing import Dict, Any, Callable  
  
class Tool:  
    """Base class for all tools"""  
    def __init__(self, name: str, description: str, func: Callable):  
        self.name = name  
        self.description = description  
        self.func = func  
          
    def execute(self, **kwargs) -> Any:  
        """Execute the tool with the given arguments"""  
        return self.func(**kwargs)  
          
    def get_description(self) -> str:  
        """Get a formatted description of the tool"""  
        return f"{self.name}: {self.description}"