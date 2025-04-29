import pytest  
import asyncio  
from unittest.mock import AsyncMock, MagicMock  
from src.financial_orchestrator import FinancialOrchestrator  
from src.models import JobOutput, JobManifest, Job  
from src.agent import Agent  
  
class TestOrchestrator:  
    @pytest.fixture  
    def mock_supervisor_model(self):  
        model = MagicMock()  
        model.generate = AsyncMock(return_value="Final synthesized answer")  
        return model  
      
    @pytest.fixture  
    def mock_agent(self):  
        agent = MagicMock(spec=Agent)  
        agent.execute = AsyncMock(return_value=JobOutput(  
            explanation="Test explanation",  
            citation="Test citation",  
            answer="Test answer"  
        ))  
        return agent  
      
    @pytest.fixture  
    def mock_tool_registry(self):  
        registry = MagicMock()  
        registry.execute_tool = MagicMock(return_value="Tool result")  
        registry.get_all_descriptions = MagicMock(return_value="Tool descriptions")  
        return registry  
      
    @pytest.mark.asyncio  
    async def test_run_financial_analysis(self, mock_supervisor_model, mock_agent, mock_tool_registry):  
        # Create orchestrator with mock components  
        orchestrator = FinancialOrchestrator(  
            supervisor_model=mock_supervisor_model,  
            agents={"test_agent": mock_agent},  
            tool_registry=mock_tool_registry  
        )  
          
        # Define a simple workflow  
        workflow = [  
            {  
                "agent": "test_agent",  
                "task": "Test task",  
                "output_key": "test_output"  
            }  
        ]  
          
        # Run the analysis  
        result = await orchestrator.run_financial_analysis(  
            task="Test financial task",  
            context="Test context",  
            workflow=workflow  
        )  
          
        # Verify the result  
        assert "final_answer" in result  
        assert result["final_answer"] == "Final synthesized answer"  
        assert "steps" in result  
        assert len(result["steps"]) == 1  
          
        # Verify that the agent was called  
        mock_agent.execute.assert_called_once_with("Test task", "Test context")  
          
        # Verify that the supervisor model was called for synthesis  
        mock_supervisor_model.generate.assert_called_once()