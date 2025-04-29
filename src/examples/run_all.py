import asyncio
from src.examples.amcor_quick_ratio import run_amcor_quick_ratio_example
from src.examples.aes_inventory_turnover import run_aes_inventory_turnover_example
from src.examples.three_m_capital_intensity import run_three_m_capital_intensity_example

async def run_all_examples():
    print("Running all financial analysis examples...")
    print("\n=== Running Amcor Quick Ratio Analysis ===")
    await run_amcor_quick_ratio_example()
    
    print("\n=== Running AES Inventory Turnover Analysis ===")
    await run_aes_inventory_turnover_example()
    
    print("\n=== Running 3M Capital Intensity Analysis ===")
    await run_three_m_capital_intensity_example()
    
    print("\nAll examples completed!")

if __name__ == "__main__":
    asyncio.run(run_all_examples()) 