import pytest  
from src.tools.implementations import (  
    retrieve_from_context,  
    summarize_text,  
    chunk_text,  
    calculate,  
    calculate_financial_ratio,  
    extract_financial_data,  
    extract_year  
)  
from src.tools.registry import ToolRegistry, create_default_registry  
from src.tools.tool import Tool  
  
class TestTools:  
    def test_retrieve_from_context(self):  
        context = "This is a test. It contains financial data. The quick ratio is 0.75."  
        query = "quick ratio"  
        results = retrieve_from_context(context, query)  
          
        assert len(results) > 0  
        assert "quick ratio" in results[0].lower()  
      
    def test_summarize_text(self):  
        text = "This is the first sentence. This is the second sentence. This is the third sentence."  
        summary = summarize_text(text)  
          
        assert len(summary) < len(text)  
        assert "first sentence" in summary  
      
    def test_chunk_text(self):  
        text = "A" * 2000  # 2000 characters  
        chunks = chunk_text(text, chunk_size=1000, overlap=100)  
          
        assert len(chunks) > 1  
        assert len(chunks[0]) <= 1000  
        assert chunks[0][-100:] == chunks[1][:100]  
      
    def test_calculate(self):  
        result = calculate("2 + 2 * 3")  
        assert result == 8  
          
        with pytest.raises(ValueError):  
            calculate("2 + 2; rm -rf /")  
      
    def test_calculate_financial_ratio(self):  
        result = calculate_financial_ratio(100, 50)  
        assert result == 2.0  
          
        result = calculate_financial_ratio(100, 0)  
        assert result == float('inf')  
      
    def test_tool_registry(self):  
        registry = ToolRegistry()  
        registry.register_tool("test", "Test tool", lambda x: x * 2)  
          
        assert "test" in registry.tools  
        assert registry.execute_tool("test", x=5) == 10  
          
        with pytest.raises(ValueError):  
            registry.get_tool("nonexistent")  
      
    def test_create_default_registry(self):  
        registry = create_default_registry()  
          
        assert "retrieve" in registry.tools  
        assert "summarize" in registry.tools  
        assert "chunk" in registry.tools  
        assert "calculate" in registry.tools  
        assert "calculate_ratio" in registry.tools  
        assert "extract_financial_data" in registry.tools