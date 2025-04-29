# Example workflows for financial analysis tasks  
  
# Example 1: Amcor (Quick Ratio)  
AMCOR_QUICK_RATIO_WORKFLOW = [  
    {  
        "agent": "data_retriever",  
        "task": "Extract the following financial data from the Amcor 10-K report for both FY2023 and FY2022: Total current assets, Raw materials and supplies, Work in process and finished goods, and Total current liabilities.",  
        "output_key": "extracted_data"  
    },  
    {  
        "agent": "financial_concept_selector",  
        "task": "Identify the formula and components needed to calculate the Quick Ratio for Amcor.",  
        "output_key": "financial_concept"  
    },  
    {  
        "agent": "information_structurer",  
        "task": "Using the extracted data: {extracted_data}, prepare the structured inputs needed to calculate the Quick Ratio for both FY2023 and FY2022. Specifically, calculate Quick Assets (Current Assets - Inventories) for both years.",  
        "output_key": "structured_data"  
    },  
    {  
        "agent": "calculator",  
        "task": "Using the structured data: {structured_data}, calculate the Quick Ratio for FY2023 and FY2022, and determine the percentage change between the two years.",  
        "output_key": "calculations"  
    },  
    {  
        "agent": "explainer_validator",  
        "task": "Based on the calculations: {calculations}, determine whether Amcor's quick ratio improved or declined between FY2023 and FY2022. Provide a clear explanation with the percentage change.",  
        "output_key": "final_answer"  
    }  
]  
  
# Example 2: AES Corporation (Inventory Turnover)  
AES_INVENTORY_TURNOVER_WORKFLOW = [  
    {  
        "agent": "data_retriever",  
        "task": "Extract the following financial data from the AES Corporation 10-K report for FY2022: Total cost of sales and Inventory value.",  
        "output_key": "extracted_data"  
    },  
    {  
        "agent": "financial_concept_selector",  
        "task": "Identify the formula and components needed to calculate the Inventory Turnover Ratio for AES Corporation.",  
        "output_key": "financial_concept"  
    },  
    {  
        "agent": "information_structurer",  
        "task": "Using the extracted data: {extracted_data}, prepare the structured inputs needed to calculate the Inventory Turnover Ratio for FY2022.",  
        "output_key": "structured_data"  
    },  
    {  
        "agent": "calculator",  
        "task": "Using the structured data: {structured_data}, calculate the Inventory Turnover Ratio for AES Corporation for FY2022.",  
        "output_key": "calculations"  
    },  
    {  
        "agent": "explainer_validator",  
        "task": "Based on the calculations: {calculations}, explain how many times AES Corporation sold its inventory in FY2022. Provide a clear and concise explanation.",  
        "output_key": "final_answer"  
    }  
]  
  
# Example 3: 3M (Capital Intensity Analysis)  
THREE_M_CAPITAL_INTENSITY_WORKFLOW = [  
    {  
        "agent": "data_retriever",  
        "task": "Extract the following financial data from the 3M 10-K report for FY2022: CAPEX (Purchases of property, plant and equipment), Net sales/Revenue, Property plant and equipment net (Fixed assets), Total assets, and Net income.",  
        "output_key": "extracted_data"  
    },  
    {  
        "agent": "financial_concept_selector",  
        "task": "Identify the formulas and components needed to assess whether 3M is a capital-intensive business, including CAPEX/Revenue ratio, Fixed assets/Total Assets ratio, and Return on Assets (ROA).",  
        "output_key": "financial_concept"  
    },  
    {  
        "agent": "information_structurer",  
        "task": "Using the extracted data: {extracted_data}, prepare the structured inputs needed to calculate CAPEX/Revenue ratio, Fixed assets/Total Assets ratio, and Return on Assets (ROA) for FY2022.",  
        "output_key": "structured_data"  
    },  
    {  
        "agent": "calculator",  
        "task": "Using the structured data: {structured_data}, calculate the CAPEX/Revenue ratio, Fixed assets/Total Assets ratio, and Return on Assets (ROA) for 3M for FY2022.",  
        "output_key": "calculations"  
    },  
    {  
        "agent": "explainer_validator",  
        "task": "Based on the calculations: {calculations}, determine whether 3M is a capital-intensive business. Provide a clear explanation referencing the calculated metrics.",  
        "output_key": "final_answer"  
    }  
]