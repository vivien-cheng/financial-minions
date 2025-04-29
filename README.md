# Financial Analysis Multi-Agent System

A multi-agent system for financial analysis using LLMs, implementing a hybrid hardcoded/LLM approach for reliable financial calculations.

## Architecture

```
src/
├── agents/                  # Agent implementations
│   ├── data_retriever.py    # Extracts financial data from documents
│   ├── financial_concept_selector.py  # Identifies relevant financial concepts
│   ├── information_structurer.py      # Structures data for calculations
│   ├── calculator.py        # Performs financial calculations
│   ├── explainer_validator.py # Validates and explains results
│   └── __init__.py         # Agent package initialization
├── clients/                 # LLM client implementations
│   ├── base.py             # Base client interface
│   ├── openai.py           # OpenAI API implementation
│   ├── anthropic.py        # Anthropic API implementation
│   └── __init__.py         # Client package initialization
├── tools/                   # Tool implementations
│   ├── tool.py             # Base tool interface
│   ├── registry.py         # Tool registration and management
│   └── __init__.py         # Tool package initialization
├── utils/                   # Utility functions
│   ├── financial_data_validator.py # Validates financial data
│   └── logging.py          # Logging configuration
├── examples/                # Example implementations
│   ├── amcor_quick_ratio.py    # Quick ratio analysis
│   ├── aes_inventory_turnover.py # Inventory turnover analysis
│   ├── three_m_capital_intensity.py # Capital intensity analysis
│   ├── evaluate_all.py      # Evaluation script
│   ├── run_all.py          # Run all examples
│   └── raw_data.json       # Example financial data
├── agent.py                 # Base agent class
├── models.py                # Data models
├── evaluator.py             # Evaluation framework
└── financial_orchestrator.py # Workflow orchestration
```

## Core Components

### Agents
- **DataRetrieverAgent**: Extracts specific financial metrics from documents
- **FinancialConceptSelectorAgent**: Identifies relevant financial concepts
- **InformationStructurerAgent**: Structures data for calculations
- **CalculatorAgent**: Performs financial calculations
- **ExplainerValidatorAgent**: Validates explanations

### Tools
- Retrieval tool for financial data
- Summarization tool for explanations
- Chunking tool for data processing

### Orchestrator
- Manages workflow execution
- Coordinates agent interactions
- Handles task delegation

## Setup

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys
```

## Usage

Run all examples:
```bash
python src/examples/run_all.py
```

Run all examples + Evaluate results:
```bash
python src/examples/evaluate_all.py
```

## Development

- Python 3.8+
- OpenAI API key required
- Virtual environment recommended
