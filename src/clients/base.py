from typing import List, Dict, Any, Tuple  
import asyncio  
  
class ModelClient:  
    """Base class for all model clients"""  
      
    async def generate(self, messages: List[Dict[str, str]]) -> str:  
        """Generate a response from the model"""  
        raise NotImplementedError("Subclasses must implement this")