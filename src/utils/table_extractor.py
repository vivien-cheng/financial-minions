from typing import List, Dict, Any, Optional, Tuple
import re
import pandas as pd
from dataclasses import dataclass

@dataclass
class TableExtractionResult:
    table_name: str
    fiscal_years: List[str]
    data: pd.DataFrame
    confidence: float
    page_number: Optional[int] = None

class FinancialTableExtractor:
    """
    Utility class for extracting and processing tables from financial documents.
    Provides methods to identify, extract, and validate financial tables.
    """
    
    def __init__(self):
        # Common financial statement headers
        self.statement_headers = {
            "balance_sheet": [
                "Consolidated Balance Sheets",
                "Balance Sheets",
                "Statement of Financial Position"
            ],
            "income_statement": [
                "Consolidated Statements of Operations",
                "Consolidated Statements of Income",
                "Statements of Operations",
                "Statements of Income"
            ],
            "cash_flow": [
                "Consolidated Statements of Cash Flows",
                "Statements of Cash Flows"
            ]
        }
        
        # Common fiscal year patterns
        self.year_patterns = [
            r"\d{4}",                    # 2023
            r"December\s+\d{1,2},\s+\d{4}",  # December 31, 2023
            r"June\s+\d{1,2},\s+\d{4}",      # June 30, 2023
            r"FY\s+\d{4}",                   # FY 2023
            r"Fiscal\s+Year\s+\d{4}"         # Fiscal Year 2023
        ]
        
        # Common unit indicators
        self.unit_indicators = [
            r"\$ in millions",
            r"\$ in thousands",
            r"\$ in billions",
            r"\(in millions\)",
            r"\(in thousands\)",
            r"\(in billions\)"
        ]
    
    def identify_statement_type(self, text: str) -> Optional[str]:
        """
        Identify the type of financial statement from the text.
        
        Args:
            text: Text containing potential financial statement headers
            
        Returns:
            Statement type if identified, None otherwise
        """
        text = text.lower()
        for stmt_type, headers in self.statement_headers.items():
            for header in headers:
                if header.lower() in text:
                    return stmt_type
        return None
    
    def extract_fiscal_years(self, text: str) -> List[str]:
        """
        Extract fiscal years from the text.
        
        Args:
            text: Text containing fiscal year information
            
        Returns:
            List of fiscal years found
        """
        years = []
        for pattern in self.year_patterns:
            matches = re.findall(pattern, text)
            years.extend(matches)
        return years
    
    def extract_units(self, text: str) -> Optional[str]:
        """
        Extract the unit of measurement from the text.
        
        Args:
            text: Text containing unit information
            
        Returns:
            Unit if found, None otherwise
        """
        for pattern in self.unit_indicators:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)
        return None
    
    def normalize_table_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize table data by:
        1. Converting string numbers to floats
        2. Handling negative numbers in parentheses
        3. Removing currency symbols and commas
        4. Converting to consistent units
        
        Args:
            df: Input DataFrame with raw table data
            
        Returns:
            Normalized DataFrame
        """
        # Create a copy to avoid modifying the original
        normalized = df.copy()
        
        # Function to clean and convert a single value
        def clean_value(x):
            if not isinstance(x, str):
                return x
                
            # Remove currency symbols and commas
            x = re.sub(r'[^\d.-]', '', x)
            
            # Handle negative numbers in parentheses
            if '(' in str(x) and ')' in str(x):
                x = '-' + re.sub(r'[()]', '', x)
            
            try:
                return float(x)
            except ValueError:
                return x
        
        # Apply cleaning to all columns
        for col in normalized.columns:
            normalized[col] = normalized[col].apply(clean_value)
        
        return normalized
    
    def extract_table(self, text: str, page_number: Optional[int] = None) -> Optional[TableExtractionResult]:
        """
        Extract a financial table from the text.
        
        Args:
            text: Text containing the table
            page_number: Optional page number where the table was found
            
        Returns:
            TableExtractionResult if successful, None otherwise
        """
        # Identify statement type
        stmt_type = self.identify_statement_type(text)
        if not stmt_type:
            return None
            
        # Extract fiscal years
        years = self.extract_fiscal_years(text)
        if not years:
            return None
            
        # Extract units
        units = self.extract_units(text)
        
        try:
            # Split into lines and find the table boundaries
            lines = text.split('\n')
            table_start = None
            table_end = None
            
            for i, line in enumerate(lines):
                if any(header.lower() in line.lower() for header in self.statement_headers[stmt_type]):
                    table_start = i
                elif table_start is not None and len(line.strip()) == 0:
                    table_end = i
                    break
            
            if table_start is None or table_end is None:
                return None
                
            # Extract the table content
            table_lines = lines[table_start:table_end]
            
            # Convert to DataFrame
            data = []
            max_cols = 0
            
            # First pass to determine max columns
            for line in table_lines:
                if line.strip():
                    cols = len(line.split())
                    max_cols = max(max_cols, cols)
            
            # Second pass to pad rows with NaN values
            for line in table_lines:
                if line.strip():
                    row = line.split()
                    # Pad with NaN if needed
                    row.extend(['NaN'] * (max_cols - len(row)))
                    data.append(row)
                    
            if not data:
                return None
                
            df = pd.DataFrame(data[1:], columns=data[0])
            df = self.normalize_table_data(df)
            
            return TableExtractionResult(
                table_name=stmt_type,
                fiscal_years=years,
                data=df,
                confidence=0.8,  # Simplified confidence score
                page_number=page_number
            )
            
        except Exception as e:
            print(f"Error extracting table: {e}")
            return None
    
    def find_relevant_tables(self, text: str, target_metrics: List[str]) -> List[TableExtractionResult]:
        """
        Find tables relevant to the target metrics.
        
        Args:
            text: Text containing multiple tables
            target_metrics: List of metrics to look for
            
        Returns:
            List of relevant table extraction results
        """
        results = []
        
        # Split text into potential table sections
        sections = re.split(r'\n\s*\n', text)
        
        for section in sections:
            result = self.extract_table(section)
            if result:
                # Check if the table contains any target metrics
                for metric in target_metrics:
                    if any(metric.lower() in col.lower() for col in result.data.columns):
                        results.append(result)
                        break
                        
        return results 