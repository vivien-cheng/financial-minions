import asyncio  
import os  
import json  
from src.clients.openai import OpenAIClient  
from src.clients.anthropic import AnthropicClient  
from src.agents.data_retriever import DataRetrieverAgent  
from src.agents.financial_concept_selector import FinancialConceptSelectorAgent  
from src.agents.information_structurer import InformationStructurerAgent  
from src.agents.calculator import CalculatorAgent  
from src.agents.explainer_validator import ExplainerValidatorAgent  
from src.financial_orchestrator import FinancialOrchestrator  
from src.tools.registry import create_default_registry  
from src.examples.workflows import AES_INVENTORY_TURNOVER_WORKFLOW  
from src.utils.logging import save_to_log
from datetime import datetime

# AES Corporation financial data  
AES_DATA = """Consolidated Balance Sheets  
December 31, 2022 and 2021  
2022    2021  
(in millions, except share and per share data)  
ASSETS  
CURRENT ASSETS  
Cash and cash equivalents    $    1,374     $    943   
Restricted cash    536     304   
Short-term investments    730     232   
Accounts receivable, net of allowance for doubtful accounts of $5 and $5, respectively    1,799     1,418   
Inventory    1,055     604  
  
Consolidated Statements of Operations  
Years ended December 31, 2022, 2021, and 2020  
2022    2021    2020  
(in millions, except per share amounts)  
Revenue:  
Regulated    $    3,538     $    2,868     $    2,661   
Non-Regulated    9,079     8,273     6,999   
Total revenue    12,617     11,141     9,660   
Cost of Sales:  
Regulated    (3,162)    (2,448)    (2,235)  
Non-Regulated    (6,907)    (5,982)    (4,732)  
Total cost of sales    (10,069)    (8,430)    (6,967)  
"""  
  
class PydanticJSONEncoder(json.JSONEncoder):  
    def default(self, obj):  
        if hasattr(obj, "model_dump"):  
            return obj.model_dump()  
        return super().default(obj)  
    

async def run_aes_inventory_turnover_example():  
    # Initialize clients  
    openai_client = OpenAIClient()  
    
    # Create agents  
    data_retriever = DataRetrieverAgent(openai_client)
    concept_selector = FinancialConceptSelectorAgent(openai_client, "concept_selector")
    info_structurer = InformationStructurerAgent(openai_client, "info_structurer")
    calculator = CalculatorAgent(openai_client, "calculator")
    explanation_validator = ExplainerValidatorAgent(openai_client, "explanation_validator")
      
    # Create orchestrator  
    orchestrator = FinancialOrchestrator(  
        supervisor_model=openai_client,  
        agents={  
            "data_retriever": data_retriever,  
            "financial_concept_selector": concept_selector,  
            "information_structurer": info_structurer,  
            "calculator": calculator,  
            "explainer_validator": explanation_validator  
        },  
        tool_registry=create_default_registry()  
    )  
      
    # Run analysis  
    result = await orchestrator.run_financial_analysis(  
        task="What is AES Corporation's inventory turnover for FY2022?",  
        workflow=AES_INVENTORY_TURNOVER_WORKFLOW,  
        context={"AES_DATA": AES_DATA}
    )  
      
    # Save result to log  
    log_data = {  
        "workflow": "aes_inventory_turnover",  
        "timestamp": datetime.now().isoformat(),  
        "result": {  
            "task": result["task"],  
            "steps": [  
                {  
                    "agent": step["agent"],  
                    "task": step["task"],  
                    "output": {  
                        "explanation": step["output"].explanation,  
                        "citation": step["output"].citation,  
                        "answer": step["output"].answer  
                    }  
                }  
                for step in result["steps"]  
            ],  
            "final_answer": result["final_answer"]  
        }  
    }  
    log_path = save_to_log(log_data, prefix="aes_inventory_turnover")  
    print(f"Analysis complete. Results saved to: {log_path}")  
      
    return result  
  
if __name__ == "__main__":  
    asyncio.run(run_aes_inventory_turnover_example())