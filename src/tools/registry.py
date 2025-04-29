from typing import Dict, List, Callable, Any, Optional  
from src.tools.tool import Tool  
import re  
from rank_bm25 import BM25Plus  
import numpy as np  
from sentence_transformers import SentenceTransformer  
from sklearn.metrics.pairwise import cosine_similarity  

def retrieve_from_context(context: str, query: str, max_results: int = 3) -> List[str]:  
    """Retrieve relevant passages from context using both keyword and semantic matching"""  
    # Split context into chunks  
    chunks = chunk_text(context)  
      
    # Get both keyword and semantic matches  
    keyword_matches = bm25_retrieve(chunks, query, max_results)  
    semantic_matches = semantic_retrieve(chunks, query, max_results)  
      
    # Combine and deduplicate results  
    combined = list(set(keyword_matches + semantic_matches))  
    return combined[:max_results]  

def summarize_text(text: str, max_length: int = 200) -> str:  
    """Summarize text (this would normally call an LLM)"""  
    # In a real implementation, this would call your summarization model  
    # For now, we'll use a simple extractive approach  
    sentences = re.split(r'(?<=[.!?])\s+', text)  
    if len(sentences) <= 3:  
        return text  
          
    # Just return first and last sentences for demo purposes  
    return " ".join([sentences[0]] + [sentences[-1]])  

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 100) -> List[str]:  
    """Split text into overlapping chunks"""  
    chunks = []  
    start = 0  
      
    while start < len(text):  
        end = min(start + chunk_size, len(text))  
          
        # Try to break at sentence boundary  
        if end < len(text):  
            boundary = text.rfind('.', start, end) + 1  
            if boundary > start:  
                end = boundary  
                  
        chunks.append(text[start:end])  
        start = end - overlap  
          
    return chunks  

def calculate(expression: str) -> float:  
    """Safely evaluate a mathematical expression"""  
    # Limited to basic operations for safety  
    allowed_chars = set("0123456789+-*/().e ")  
    if not all(c in allowed_chars for c in expression):  
        raise ValueError("Invalid characters in expression")  
          
    return eval(expression)  # In production, use a safer evaluation method  

def calculate_financial_ratio(numerator: float, denominator: float) -> float:  
    """Calculate a financial ratio with error handling for division by zero"""  
    if denominator == 0:  
        return float('inf')  # or handle this case differently  
    return numerator / denominator  

def bm25_retrieve(chunks: List[str], query: str, k: int) -> List[str]:  
    """Retrieve chunks using BM25 keyword matching"""  
    tokenized_chunks = [chunk.split() for chunk in chunks]  
    bm25 = BM25Plus(tokenized_chunks)  
      
    scores = bm25.get_scores(query.split())  
    top_k_indices = np.argsort(scores)[-k:][::-1]  
    return [chunks[i] for i in top_k_indices]  

def semantic_retrieve(chunks: List[str], query: str, k: int) -> List[str]:  
    """Retrieve chunks using semantic similarity"""  
    model = SentenceTransformer('all-MiniLM-L6-v2')  
      
    query_embedding = model.encode(query)  
    chunk_embeddings = model.encode(chunks)  
      
    similarities = cosine_similarity([query_embedding], chunk_embeddings)[0]  
    top_k_indices = np.argsort(similarities)[-k:][::-1]  
    return [chunks[i] for i in top_k_indices]  

def extract_financial_data(text: str, field_name: str) -> List[Dict[str, Any]]:  
    """Extract financial data points for a specific field with improved accuracy"""  
    results = []  
    lines = text.split('\n')  
      
    # Common financial data patterns  
    patterns = [  
        r'\$?\s*(\d+(?:,\d{3})*(?:\.\d+)?)\s*(?:million|billion|m|b|M|B)?',  # Standard format  
        r'\(?\$?\s*(\d+(?:,\d{3})*(?:\.\d+)?)\s*(?:million|billion|m|b|M|B)?\)?',  # With parentheses  
        r'(\d+(?:,\d{3})*(?:\.\d+)?)\s*\(\d+(?:,\d{3})*(?:\.\d+)?\)',  # With comparison  
    ]  
      
    for i, line in enumerate(lines):  
        if field_name.lower() in line.lower():  
            for pattern in patterns:  
                matches = re.finditer(pattern, line)  
                for match in matches:  
                    try:  
                        # Extract and clean the number  
                        amount_str = match.group(1).replace(',', '')  
                        amount = float(amount_str)  
                          
                        # Adjust for scale  
                        if any(scale in line for scale in ['billion', 'b', 'B']):  
                            amount *= 1_000_000_000  
                        elif any(scale in line for scale in ['million', 'm', 'M']):  
                            amount *= 1_000_000  
                          
                        # Extract year if present  
                        year = extract_year(line)  
                          
                        results.append({  
                            'line': i,  
                            'text': line.strip(),  
                            'value': amount,  
                            'year': year,  
                            'field': field_name  
                        })  
                    except (ValueError, IndexError):  
                        continue  
      
    return results  

def extract_year(text: str) -> Optional[int]:  
    """Extract year from text"""  
    year_patterns = [  
        r'FY(\d{4})',  # Fiscal year  
        r'(\d{4})',    # Regular year  
        r'(\d{2})',    # Two-digit year  
    ]  
      
    for pattern in year_patterns:  
        match = re.search(pattern, text)  
        if match:  
            year = int(match.group(1))  
            if year < 100:  # Handle two-digit years  
                year += 2000 if year < 50 else 1900  
            return year  
      
    return None

class ToolRegistry:  
    def __init__(self):  
        self.tools: Dict[str, Tool] = {}  
          
    def register_tool(self, name: str, description: str, func: Callable) -> None:  
        """Register a new tool"""  
        self.tools[name] = Tool(name, description, func)  
          
    def get_tool(self, name: str) -> Tool:  
        """Get a tool by name"""  
        if name not in self.tools:  
            raise ValueError(f"Tool {name} not found")  
        return self.tools[name]  
          
    def get_all_descriptions(self) -> str:  
        """Get formatted descriptions of all tools"""  
        return "\n".join([tool.get_description() for tool in self.tools.values()])  
          
    def execute_tool(self, name: str, **kwargs) -> Any:  
        """Execute a tool by name with the given arguments"""  
        tool = self.get_tool(name)  
        return tool.execute(**kwargs)  

def create_default_registry() -> ToolRegistry:  
    """Initialize with our basic tools"""  
    registry = ToolRegistry()  
      
    registry.register_tool(  
        "retrieve",   
        "Retrieve relevant information from context",   
        retrieve_from_context  
    )  
      
    registry.register_tool(  
        "summarize",   
        "Summarize text to a shorter length",   
        summarize_text  
    )  
      
    registry.register_tool(  
        "chunk",   
        "Split text into manageable chunks",   
        chunk_text  
    )  
      
    registry.register_tool(  
        "calculate",   
        "Safely evaluate a mathematical expression",   
        calculate  
    )  
      
    registry.register_tool(  
        "calculate_financial_ratio",   
        "Calculate a financial ratio with error handling",   
        calculate_financial_ratio  
    )  
      
    registry.register_tool(  
        "extract_financial_data",   
        "Extract financial data points from text",   
        extract_financial_data  
    )  
      
    return registry