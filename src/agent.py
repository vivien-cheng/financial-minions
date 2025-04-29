from typing import List, Dict, Any, Optional
from src.models import JobOutput
import json
import re

class Agent:
    """Base class for all agents"""
    def __init__(self, model, role_name: str):
        self.model = model  # LLM client
        self.role_name = role_name
        self.system_prompt = self._get_system_prompt()
        
    def _get_system_prompt(self) -> str:
        """Get the system prompt for this agent role"""
        raise NotImplementedError("Subclasses must implement this")
        
    async def execute(self, task: str, context: str) -> JobOutput:
        """Execute a task with the given context"""
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"Task: {task}\n\nContext: {context}"}
        ]
        response = await self.model.generate(messages)
        return self._parse_output(response)
        
    def _parse_output(self, response: str) -> JobOutput:
        """Parse the model output into a structured JobOutput"""
        def preprocess_json_string(json_str: str) -> str:
            # Remove comments
            json_str = re.sub(r'//.*?$', '', json_str, flags=re.MULTILINE)
            
            # Fix trailing commas in arrays and objects
            json_str = re.sub(r',\s*}', '}', json_str)
            json_str = re.sub(r',\s*]', ']', json_str)
            
            # Fix unescaped quotes in a simpler way
            # First, find all string values
            string_pattern = r'"([^"\\]*(?:\\.[^"\\]*)*)"'
            matches = re.finditer(string_pattern, json_str)
            
            # Process each string value
            for match in matches:
                original = match.group(0)
                content = match.group(1)
                # Escape any unescaped quotes in the content
                fixed_content = content.replace('"', '\\"')
                if fixed_content != content:
                    json_str = json_str.replace(original, f'"{fixed_content}"')
            
            return json_str

        def extract_json(text: str) -> Optional[str]:
            # Try to extract from code blocks first
            block_matches = list(re.finditer(r"```(?:json)?\s*(.*?)```", text, re.DOTALL))
            if block_matches:
                return block_matches[-1].group(1).strip()
            
            # Try to find the outermost JSON object
            try:
                start = text.find('{')
                end = text.rfind('}')
                if start != -1 and end != -1 and end > start:
                    return text[start:end+1]
            except:
                pass
            
            # Try a more aggressive approach
            potential_jsons = re.findall(r'\{[^{}]*\}', text)
            if potential_jsons:
                return potential_jsons[-1]
            
            return None

        # Extract and preprocess JSON
        json_str = extract_json(response)
        if not json_str:
            return JobOutput(
                explanation="Failed to extract JSON from response",
                citation=None,
                answer=response
            )

        try:
            # Preprocess and parse
            json_str = preprocess_json_string(json_str)
            data = json.loads(json_str)
            
            # Validate required fields
            if not isinstance(data, dict):
                raise ValueError("JSON must be an object")
            
            required_fields = ["explanation", "answer"]
            for field in required_fields:
                if field not in data:
                    raise ValueError(f"Missing required field: {field}")
            
            # Convert answer to string if it's a dictionary
            if isinstance(data.get("answer"), dict):
                data["answer"] = json.dumps(data["answer"])
            
            return JobOutput(
                explanation=data.get("explanation", ""),
                citation=data.get("citation"),
                answer=data.get("answer")
            )
            
        except (json.JSONDecodeError, ValueError) as e:
            return JobOutput(
                explanation=f"Failed to parse JSON: {str(e)}",
                citation=None,
                answer=response
            ) 