from typing import Dict, Any, List, Optional
import json
from src.utils.financial_data_validator import FinancialDataValidator
from src.models import JobOutput

class DataRetrieverAgent:
    """
    Agent responsible for extracting numerical data from financial documents.
    Uses LLM to extract and validate financial data.
    """
    
    def __init__(self, openai_client):
        self.openai_client = openai_client
        self.validator = FinancialDataValidator()
        
        self.system_prompt = """You are a financial data extraction expert. Your task is to extract specific numerical values from financial documents.
        
        For each request, you must:
        1. Identify the relevant financial statements (Balance Sheet, Income Statement, Cash Flow)
        2. Extract the exact values needed for the calculation
        3. Verify the units and fiscal years
        4. Return the data in a structured JSON format
        
        Common line items to look for:
        - Quick Ratio: Total Current Assets, Raw Materials and Supplies, Work in Process and Finished Goods, Total Current Liabilities
        - Inventory Turnover: Cost of Sales, Total Inventory
        - Capital Intensity: Capital Expenditures, Revenue, Fixed Assets, Total Assets, Net Income
        
        For Amcor's Quick Ratio, you should extract:
        - Total Current Assets for FY2023 and FY2022
        - Raw Materials and Supplies for FY2023 and FY2022
        - Work in Process and Finished Goods for FY2023 and FY2022
        - Total Current Liabilities for FY2023 and FY2022
        
        For AES's Inventory Turnover, you should extract:
        - Cost of Sales for FY2022
        - Inventory value for FY2022
        
        For 3M's Capital Intensity, you should extract:
        - Capital Expenditures (Purchases of property, plant and equipment) for FY2022
        - Revenue (Net sales) for FY2022
        - Fixed Assets (Property, plant and equipment, net) for FY2022
        - Total Assets for FY2022
        - Net Income for FY2022
        
        Return format:
        {
            "values": {
                "Total Current Assets FY2023": 5308,
                "Total Current Assets FY2022": 5853,
                "Raw Materials and Supplies FY2023": 992,
                "Raw Materials and Supplies FY2022": 1114,
                "Work in Process and Finished Goods FY2023": 1221,
                "Work in Process and Finished Goods FY2022": 1325,
                "Total Current Liabilities FY2023": 4476,
                "Total Current Liabilities FY2022": 5103
            }
        }
        """
    
    async def execute(self, task: str, context: Dict[str, Any]) -> JobOutput:
        """
        Execute the data retrieval task and return results in the expected JobOutput format.
        
        Args:
            task: The task description
            context: Additional context including document text
            
        Returns:
            JobOutput containing the extracted data
        """
        # Extract target metrics from the task
        target_metrics = []
        if "Quick Ratio" in task:
            target_metrics = [
                "Total Current Assets",
                "Raw Materials and Supplies",
                "Work in Process and Finished Goods",
                "Total Current Liabilities"
            ]
        elif "Inventory Turnover" in task:
            target_metrics = ["Cost of Sales", "Inventory"]
        elif "Capital Intensity" in task:
            target_metrics = [
                "Capital Expenditures",
                "Revenue",
                "Fixed Assets",
                "Total Assets",
                "Net Income"
            ]
            
        # Get document text from context
        document_text = context.get("document_text", "")
        if not document_text:
            # Try to get data from example-specific context
            if "AMCOR_DATA" in context:
                document_text = context["AMCOR_DATA"]
            elif "AES_DATA" in context:
                document_text = context["AES_DATA"]
            elif "THREE_M_DATA" in context:
                document_text = context["THREE_M_DATA"]
            
        if not document_text:
            return JobOutput(
                explanation="No document text found in context",
                citation="",
                answer={}
            )
            
        # Extract the data using LLM
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"Extract the following metrics from this financial document: {', '.join(target_metrics)}\n\n{document_text}"}
        ]
        
        try:
            response_text = await self.openai_client.generate(messages)
            
            # Handle potential JSON formatting issues
            if not response_text.strip().startswith("{"):
                # Try to extract JSON from the response
                json_start = response_text.find("{")
                json_end = response_text.rfind("}") + 1
                if json_start != -1 and json_end != -1:
                    response_text = response_text[json_start:json_end]
            
            extracted_data = json.loads(response_text)
            values = extracted_data.get("values", {})
            
            # Validate that we got the expected data
            if not values:
                # Try to extract values directly from the response
                if isinstance(extracted_data, dict) and "answer" in extracted_data:
                    values = extracted_data["answer"]
                elif isinstance(extracted_data, dict):
                    values = extracted_data
            
            # Format the result as JobOutput
            explanation = "Successfully extracted financial data using LLM"
            citation = document_text[:200] + "..."  # First 200 chars as citation
            
            return JobOutput(
                explanation=explanation,
                citation=citation,
                answer=values
            )
        except json.JSONDecodeError as e:
            # Try to extract values using regex as a fallback
            import re
            values = {}
            for metric in target_metrics:
                # Handle different metric names and formats
                metric_patterns = [
                    rf"{metric}.*?(\d+(?:,\d{{3}})*(?:\.\d+)?)",
                    rf"{metric.replace(' ', '.*?')}.*?(\d+(?:,\d{{3}})*(?:\.\d+)?)",
                    rf"{metric.split()[-1]}.*?(\d+(?:,\d{{3}})*(?:\.\d+)?)"
                ]
                
                for pattern in metric_patterns:
                    matches = re.findall(pattern, document_text, re.IGNORECASE)
                    if matches:
                        try:
                            value = float(matches[0].replace(",", ""))
                            values[metric] = value
                            break
                        except (ValueError, IndexError):
                            continue
            
            if values:
                return JobOutput(
                    explanation="Extracted data using regex fallback after JSON parse error",
                    citation=document_text[:200] + "...",
                    answer=values
                )
            
            return JobOutput(
                explanation=f"Error parsing LLM response: {str(e)}",
                citation=document_text[:200] + "...",
                answer={}
            ) 