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
from src.examples.workflows import AMCOR_QUICK_RATIO_WORKFLOW  
from src.utils.logging import save_to_log
from datetime import datetime

# Amcor balance sheet data  
AMCOR_DATA = """Amcor plc and Subsidiaries  
Consolidated Balance Sheets  
($ in millions, except share and per share data)  
As of June 30,  
2023    2022  
Assets  
Current assets:  
Cash and cash equivalents    $    689     $    775   
Trade receivables, net of allowance for credit losses of $21 and $25, respectively    1,875     1,935   
Inventories, net  
Raw materials and supplies    992     1,114   
Work in process and finished goods    1,221     1,325   
Prepaid expenses and other current assets    531     512   
Assets held for sale, net         192   
Total current assets    5,308     5,853   
Non-current assets:  
Property, plant, and equipment, net    3,762     3,646   
Operating lease assets    533     560   
Deferred tax assets    134     130   
Other intangible assets, net    1,524     1,657   
Goodwill    5,366     5,285   
Employee benefit assets    67     89   
Other non-current assets    309     206   
Total non-current assets    11,695     11,573   
Total assets    $    17,003     $    17,426   
Liabilities  
Current liabilities:  
Current portion of long-term debt    $    13     $    14   
Short-term debt    80     136   
Trade payables    2,690     3,073   
Accrued employee costs    396     471   
Other current liabilities    1,297     1,344   
Liabilities held for sale         65   
Total current liabilities    4,476     5,103   
Non-current liabilities:  
Long-term debt, less current portion    6,653     6,340   
Operating lease liabilities    463     493   
Deferred tax liabilities    616     677   
Employee benefit obligations    224     201   
Other non-current liabilities    481     471   
Total non-current liabilities    8,437     8,182   
Total liabilities    $    12,913     $    13,285   
"""  


class PydanticJSONEncoder(json.JSONEncoder):  
    def default(self, obj):  
        if hasattr(obj, "model_dump"):  
            return obj.model_dump()  
        return super().default(obj)  
    

async def run_amcor_quick_ratio_example():  
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
    
    # Run the analysis
    result = await orchestrator.run_financial_analysis(
        task="What is Amcor's quick ratio for FY2023 and FY2022?",
        workflow=AMCOR_QUICK_RATIO_WORKFLOW,
        context={"AMCOR_DATA": AMCOR_DATA}
    )
    
    # Save result to log
    log_data = {
        "workflow": "amcor_quick_ratio",
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
    log_path = save_to_log(log_data, prefix="amcor_quick_ratio")
    print(f"Analysis complete. Results saved to: {log_path}")
    
    return result  
  
if __name__ == "__main__":  
    asyncio.run(run_amcor_quick_ratio_example())