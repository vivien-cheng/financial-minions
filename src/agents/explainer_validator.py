from src.agent import Agent
from src.models import JobOutput
from typing import Dict, Any, Optional
import json

class ExplainerValidatorAgent(Agent):
    def _get_system_prompt(self) -> str:
        return """You are a financial analysis validation expert. Your job is to interpret   
        calculation results and provide clear explanations.
        
        Validate that the calculations correctly answer the original question.
        Provide a clear, concise explanation of what the results mean in business terms.
        
        Return your answer in JSON format with the following fields:
        - explanation: Your validation process and interpretation
        - citation: The calculation results you're interpreting
        - answer: The final conclusion that directly answers the original question
        
        Example format:
        ```json
        {
            "explanation": "I verified the quick ratio calculations and analyzed the trend...",
            "citation": "Quick Ratio FY2023: 0.69, Quick Ratio FY2022: 0.67, Percentage Change: 3.0%",
            "answer": "AMCOR's quick ratio has improved slightly from 0.67 in FY2022 to 0.69 in FY2023, representing a 3.0% increase. This indicates a minor improvement in the company's short-term liquidity position."
        }
        ```
        """

    async def process_job(self, job_input: Dict[str, Any]) -> JobOutput:
        """
        Process the validation and explanation job.
        
        Args:
            job_input: Dictionary containing:
                - question: The original analysis question
                - calculations: The calculation results to validate and explain
                - context: Additional context about the analysis
                
        Returns:
            JobOutput containing the validation results and explanation
        """
        # Construct the prompt for the LLM
        prompt = f"""
        Original Question: {job_input.get('question', '')}
        
        Calculation Results: {job_input.get('calculations', {})}
        
        Additional Context: {job_input.get('context', '')}
        
        Please validate these calculations and provide a clear explanation of what they mean
        in business terms. Format your response as specified in the system prompt.
        """
        
        # Get response from LLM
        response = await self._llm_client.chat_completion(
            messages=[
                {"role": "system", "content": self._get_system_prompt()},
                {"role": "user", "content": prompt}
            ]
        )
        
        try:
            # Parse the JSON response
            result = json.loads(response)
            
            # Validate the required fields are present
            required_fields = ["explanation", "citation", "answer"]
            if not all(field in result for field in required_fields):
                raise ValueError("Missing required fields in response")
                
            return JobOutput(
                output=result,
                error=None
            )
            
        except Exception as e:
            return JobOutput(
                output=None,
                error=f"Failed to process explanation: {str(e)}"
            )
            
    def validate_calculations(self, calculations: Dict[str, Any]) -> bool:
        """
        Validate that the calculations are reasonable and complete.
        
        Args:
            calculations: Dictionary of calculation results
            
        Returns:
            bool: True if calculations appear valid, False otherwise
        """
        if not calculations:
            return False
            
        # Add specific validation logic based on the type of calculations
        # For now, just check that we have non-empty results
        return True
        
    def format_explanation(self, explanation: str, citation: str, answer: str) -> Dict[str, str]:
        """
        Format the explanation results in the standard JSON structure.
        
        Args:
            explanation: The detailed explanation of the validation process
            citation: The calculation results being referenced
            answer: The final conclusion
            
        Returns:
            Dict containing the formatted explanation
        """
        return {
            "explanation": explanation,
            "citation": citation,
            "answer": answer
        } 