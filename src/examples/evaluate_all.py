import asyncio
import json
from src.evaluator import PipelineEvaluator
from src.examples.amcor_quick_ratio import run_amcor_quick_ratio_example
from src.examples.aes_inventory_turnover import run_aes_inventory_turnover_example
from src.examples.three_m_capital_intensity import run_three_m_capital_intensity_example

async def evaluate_all():
    evaluator = PipelineEvaluator()
    
    print("\n=== Evaluating Amcor Quick Ratio Analysis ===")
    amcor_result = await run_amcor_quick_ratio_example()
    amcor_evaluation = await evaluator.evaluate("amcor", amcor_result)
    print(f"Amcor Evaluation: {json.dumps(amcor_evaluation, indent=2)}")
    
    print("\n=== Evaluating AES Inventory Turnover Analysis ===")
    aes_result = await run_aes_inventory_turnover_example()
    aes_evaluation = await evaluator.evaluate("aes", aes_result)
    print(f"AES Evaluation: {json.dumps(aes_evaluation, indent=2)}")
    
    print("\n=== Evaluating 3M Capital Intensity Analysis ===")
    three_m_result = await run_three_m_capital_intensity_example()
    three_m_evaluation = await evaluator.evaluate("3m", three_m_result)
    print(f"3M Evaluation: {json.dumps(three_m_evaluation, indent=2)}")

if __name__ == "__main__":
    asyncio.run(evaluate_all()) 