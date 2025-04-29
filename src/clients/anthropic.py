from typing import List, Dict, Any, Tuple  
from src.clients.base import ModelClient  
import os  
import anthropic  
import asyncio  
  
class AnthropicClient(ModelClient):  
    """Client for Anthropic models"""  
      
    def __init__(  
        self,  
        model_name: str = "claude-3-haiku-20240307",  
        api_key: str = None,  
        temperature: float = 0.0,  
        max_tokens: int = 4096  
    ):  
        self.model_name = model_name  
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")  
        if not self.api_key:  
            raise ValueError("Anthropic API key is required")  
          
        self.client = anthropic.Anthropic(api_key=self.api_key)  
        self.temperature = temperature  
        self.max_tokens = max_tokens  
      
    async def generate(self, messages: List[Dict[str, str]]) -> str:  
        """Generate a response from the Anthropic model"""  
        try:  
            # Convert messages to Anthropic format if needed  
            anthropic_messages = messages  
              
            response = await asyncio.to_thread(  
                self.client.messages.create,  
                model=self.model_name,  
                messages=anthropic_messages,  
                temperature=self.temperature,  
                max_tokens=self.max_tokens  
            )  
            return response.content[0].text  
        except Exception as e:  
            print(f"Error generating response from Anthropic: {e}")  
            return f"Error: {str(e)}"
