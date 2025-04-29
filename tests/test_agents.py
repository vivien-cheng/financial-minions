import pytest  
import asyncio  
from unittest.mock import AsyncMock, MagicMock  
from src.agent import Agent  
from src.models import JobOutput  
from src.agents.data_retriever import DataRetrieverAgent  
from src.agents.financial_concept_selector import FinancialConceptSelectorAgent  
from src.agents.information_structurer import InformationStructurerAgent  
from src.agents.calculator import CalculatorAgent  
from src.agents.explainer_validator import ExplainerValidatorAgent  
  
class TestAgent:  
    @pytest.fixture  
    def mock_model(self):  
        model = MagicMock()  
        model.generate = AsyncMock(return_value="""```json  
{  
    "explanation": "Test explanation",  
    "citation": "Test citation",  
    "answer": "Test answer"  
}  
```""")  
        return model  
      
    @pytest.mark.asyncio  
    async def test_data_retriever_agent(self, mock_model):  
        agent = DataRetrieverAgent(mock_model, "data_retriever")  
        output = await agent.execute("Extract financial data", "Sample context")  
          
        assert isinstance(output, JobOutput)  
        assert output.explanation == "Test explanation"  
        assert output.citation == "Test citation"  
        assert output.answer == "Test answer"  
          
        mock_model.generate.assert_called_once()  
      
    @pytest.mark.asyncio  
    async def test_financial_concept_selector_agent(self, mock_model):  
        agent = FinancialConceptSelectorAgent(mock_model, "financial_concept_selector")  
        output = await agent.execute("Identify financial concept", "Sample context")  
          
        assert isinstance(output, JobOutput)  
        assert output.explanation == "Test explanation"  
        assert output.citation == "Test citation"  
        assert output.answer == "Test answer"  
          
        mock_model.generate.assert_called_once()  