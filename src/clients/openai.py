from typing import List, Dict, Any, Tuple  
from src.clients.base import ModelClient  
import os  
import openai  
import asyncio  
  
class OpenAIClient(ModelClient):  
    """Client for OpenAI models"""  
      
    def __init__(  
        self,  
        model_name: str = "gpt-4o",  
        api_key: str = None,  
        temperature: float = 0.0,  
        max_tokens: int = 4096  
    ):  
        self.model_name = model_name  
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")  
        if not self.api_key:  
            raise ValueError("OpenAI API key is required")  
          
        self.client = openai.OpenAI(api_key=self.api_key)  
        self.temperature = temperature  
        self.max_tokens = max_tokens  
      
    async def generate(self, messages: List[Dict[str, str]]) -> str:  
        """Generate a response from the OpenAI model"""  
        try:  
            response = await asyncio.to_thread(  
                self.client.chat.completions.create,  
                model=self.model_name,  
                messages=messages,  
                temperature=self.temperature,  
                max_tokens=self.max_tokens  
            )  
            return response.choices[0].message.content  
        except Exception as e:  
            print(f"Error generating response from OpenAI: {e}")  
            return f"Error: {str(e)}"