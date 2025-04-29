import asyncio
import json
from datetime import datetime
from src.clients.openai import OpenAIClient
from src.agents.data_retriever import DataRetrieverAgent
from src.agents.financial_concept_selector import FinancialConceptSelectorAgent
from src.agents.information_structurer import InformationStructurerAgent
from src.agents.calculator import CalculatorAgent
from src.agents.explainer_validator import ExplainerValidatorAgent
from src.financial_orchestrator import FinancialOrchestrator
from src.tools.registry import create_default_registry
from src.examples.workflows import THREE_M_CAPITAL_INTENSITY_WORKFLOW

# 3M Corporation financial data
THREE_M_DATA = """Consolidated Balance Sheets
December 31, 2022 and 2021
2022    2021
(in millions, except per share amounts)
ASSETS
Current assets:
Cash and cash equivalents    $    2,300     $    2,100
Marketable securities    1,500     1,200
Accounts receivable, net    4,800     4,500
Inventories    4,900     4,600
Other current assets    1,200     1,100
Total current assets    14,700     13,500
Property, plant and equipment, net    8,200     8,000
Goodwill    12,500     12,300
Intangible assets, net    5,800     6,000
Other assets    3,800     3,600
Total assets    $    45,000     $    43,400

Consolidated Statements of Operations
Years ended December 31, 2022, 2021, and 2020
2022    2021    2020
(in millions, except per share amounts)
Net sales    $    34,229     $    35,355     $    32,184
Cost of sales    17,500     17,800     16,200
Gross profit    16,729     17,555     15,984
Selling, general and administrative expenses    8,200     8,400     7,800
Research, development and related expenses    1,900     1,800     1,700
Operating income    6,629     7,355     6,484
Interest expense and income
Interest expense    400     450     500
Interest income    100     80     60
Other income (expense), net    200     150     100
Income before income taxes    6,529     7,135     6,144
Provision for income taxes    1,500     1,600     1,400
Net income    $    5,029     $    5,535     $    4,744

Consolidated Statements of Cash Flows
Years ended December 31, 2022, 2021, and 2020
2022    2021    2020
(in millions)
Cash flows from operating activities:
Net income    $    5,029     $    5,535     $    4,744
Adjustments to reconcile net income to net cash provided by operating activities:
Depreciation and amortization    2,200     2,100     2,000
Changes in operating assets and liabilities    (500)     (400)     (300)
Net cash provided by operating activities    6,729     7,235     6,444
Cash flows from investing activities:
Purchases of property, plant and equipment    (1,500)    (1,400)    (1,300)
Acquisitions, net of cash acquired    (800)     (900)     (1,000)
Proceeds from sale of businesses    300     400     500
Net cash used in investing activities    (2,000)    (1,900)    (1,800)
"""

class PydanticJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, "model_dump"):
            return obj.model_dump()
        return super().default(obj)

async def run_three_m_capital_intensity_example():
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
        task="What is 3M's capital intensity for FY2022?",
        workflow=THREE_M_CAPITAL_INTENSITY_WORKFLOW,
        context={"THREE_M_DATA": THREE_M_DATA}
    )
    
    # Save results to log file
    log_data = {
        "workflow": "three_m_capital_intensity",
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
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f"logs/three_m_capital_intensity_{timestamp}.json"
    
    with open(log_file, "w") as f:
        json.dump(log_data, f, indent=2, cls=PydanticJSONEncoder)
    
    print(f"Results saved to {log_file}")
    return result

if __name__ == "__main__":
    asyncio.run(run_three_m_capital_intensity_example()) 