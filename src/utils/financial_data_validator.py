import json
from typing import Dict, Any, List, Tuple, Optional
import re
from dataclasses import dataclass
from enum import Enum

class ValidationStatus(Enum):
    VALID = "valid"
    WARNING = "warning"
    ERROR = "error"
    UNVERIFIED = "unverified"

@dataclass
class ValidationResult:
    status: ValidationStatus
    message: str
    expected_value: Optional[float] = None
    actual_value: Optional[float] = None
    error_percentage: Optional[float] = None

class FinancialDataValidator:
    """
    Utility class for validating financial data extraction results.
    Provides comprehensive validation including range checks, mathematical consistency,
    and ground truth comparison.
    """
    
    def __init__(self, ground_truth_path: Optional[str] = None):
        """
        Initialize the validator with optional ground truth data.
        
        Args:
            ground_truth_path: Path to JSON file containing ground truth data
        """
        self.ground_truth = {}
        if ground_truth_path:
            self.load_ground_truth(ground_truth_path)
            
        # Define expected value ranges for common financial metrics (in millions)
        self.expected_ranges = {
            "current_assets": (100, 100000),    # $100M to $100B
            "current_liabilities": (100, 100000),
            "inventory": (10, 50000),
            "revenue": (100, 500000),
            "capex": (10, 50000),
            "net_income": (-10000, 50000),      # Can be negative
            "total_assets": (1000, 1000000),
        }
        
        # Define common mathematical relationships that should hold
        self.math_relationships = [
            # (condition_name, lambda function that should return True)
            ("current_assets_gt_inventory", 
             lambda d: self._get_value(d, "current_assets") > self._get_value(d, "inventory")),
            
            ("quick_ratio_components", 
             lambda d: abs(self._get_value(d, "current_assets") - 
                        self._get_value(d, "inventory") - 
                        self._get_value(d, "quick_assets")) < 1),  # Allow small rounding differences
                        
            ("assets_gt_liabilities",
             lambda d: self._get_value(d, "total_assets") > self._get_value(d, "total_liabilities")),
        ]
        
        # Common synonyms for financial terms
        self.term_synonyms = {
            "current assets": ["current assets", "total current assets"],
            "current liabilities": ["current liabilities", "total current liabilities"],
            "inventory": ["inventory", "inventories", "total inventory", "total inventories"],
            "raw materials": ["raw materials", "raw materials and supplies", "materials and supplies"],
            "work in process": ["work in process", "work in progress", "wip"],
            "finished goods": ["finished goods", "finished products"],
            "cost of goods sold": ["cost of goods sold", "cost of sales", "cogs", "cos"],
            "revenue": ["revenue", "net sales", "total revenue", "net revenue"],
            "capital expenditures": ["capital expenditures", "purchases of property, plant and equipment", "capex", "ppe purchases"],
            "fixed assets": ["fixed assets", "property, plant and equipment", "ppe", "net property and equipment"],
            "net income": ["net income", "profit", "net earnings", "net profit"],
        }
    
    def load_ground_truth(self, file_path: str) -> None:
        """
        Load ground truth data from a JSON file.
        
        Args:
            file_path: Path to the JSON file
        """
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                
            # Process the ground truth data into a more usable format
            for item in data:
                company = item.get("company", "").lower()
                if company:
                    # Extract values from justification field
                    justification = item.get("justification", "")
                    values = self._extract_values_from_justification(justification)
                    
                    if values:
                        self.ground_truth[company] = values
        except Exception as e:
            print(f"Error loading ground truth data: {e}")
    
    def _extract_values_from_justification(self, justification: str) -> Dict[str, float]:
        """
        Extract numerical values from the justification text.
        
        Args:
            justification: Justification text from ground truth data
            
        Returns:
            Dictionary of extracted values
        """
        values = {}
        
        # Look for patterns like "5308-992-1221" or similar
        numbers = re.findall(r'\b\d+\b', justification)
        numbers = [float(n) for n in numbers]
        
        # Try to interpret based on known patterns
        if "Quick Ratio" in justification:
            if len(numbers) >= 6:
                values["Current Assets FY2023"] = numbers[0]
                values["Raw Materials FY2023"] = numbers[1]
                values["Work in Process and Finished Goods FY2023"] = numbers[2]
                values["Current Liabilities FY2023"] = numbers[3]
                values["Current Assets FY2022"] = numbers[4]
                values["Raw Materials FY2022"] = numbers[5]
                values["Work in Process and Finished Goods FY2022"] = numbers[6] if len(numbers) > 6 else None
                values["Current Liabilities FY2022"] = numbers[7] if len(numbers) > 7 else None
        
        elif "Cost of sales/Inventory" in justification:
            if len(numbers) >= 2:
                values["Cost of Sales FY2022"] = numbers[0]
                values["Inventory FY2022"] = numbers[1]
        
        elif "CAPEX/Revenue" in justification:
            pass  # Add pattern matching for CAPEX metrics
            
        return values
    
    def _get_value(self, data: Dict[str, Any], key_pattern: str) -> Optional[float]:
        """
        Find a value in the data dict by matching the key pattern.
        
        Args:
            data: Dictionary of financial data
            key_pattern: Pattern to match in the keys
            
        Returns:
            Matched value or None if not found
        """
        for key, value in data.items():
            if key_pattern.lower() in key.lower() and isinstance(value, (int, float)):
                return value
        return None
    
    def validate_range(self, data: Dict[str, Any]) -> Dict[str, ValidationResult]:
        """
        Validate that extracted values are within expected ranges.
        
        Args:
            data: Dictionary of extracted financial data
            
        Returns:
            Dictionary of validation results
        """
        results = {}
        
        for key, value in data.items():
            if not isinstance(value, (int, float)):
                results[key] = ValidationResult(
                    status=ValidationStatus.ERROR,
                    message="Non-numeric value"
                )
                continue
                
            # Find applicable validation range
            range_key = None
            for check_key in self.expected_ranges:
                if check_key in key.lower():
                    range_key = check_key
                    break
            
            if range_key:
                min_val, max_val = self.expected_ranges[range_key]
                if min_val <= value <= max_val:
                    results[key] = ValidationResult(
                        status=ValidationStatus.VALID,
                        message="Value within expected range"
                    )
                else:
                    results[key] = ValidationResult(
                        status=ValidationStatus.WARNING,
                        message=f"Value {value} outside expected range ({min_val}, {max_val})",
                        actual_value=value
                    )
            else:
                results[key] = ValidationResult(
                    status=ValidationStatus.UNVERIFIED,
                    message="No validation rule available"
                )
                
        return results
    
    def validate_math(self, data: Dict[str, Any]) -> Dict[str, ValidationResult]:
        """
        Validate mathematical relationships between values.
        
        Args:
            data: Dictionary of extracted financial data
            
        Returns:
            Dictionary of validation results
        """
        results = {}
        
        for name, check_func in self.math_relationships:
            try:
                if check_func(data):
                    results[name] = ValidationResult(
                        status=ValidationStatus.VALID,
                        message="Mathematical relationship holds"
                    )
                else:
                    results[name] = ValidationResult(
                        status=ValidationStatus.WARNING,
                        message="Mathematical relationship violated"
                    )
            except Exception as e:
                results[name] = ValidationResult(
                    status=ValidationStatus.ERROR,
                    message=f"Validation failed: {str(e)}"
                )
                
        return results
    
    def compare_with_ground_truth(self, company: str, data: Dict[str, Any]) -> Dict[str, ValidationResult]:
        """
        Compare extracted values with ground truth data.
        
        Args:
            company: Company name to look up in ground truth
            data: Dictionary of extracted financial data
            
        Returns:
            Dictionary of comparison results
        """
        results = {}
        company = company.lower()
        
        if company not in self.ground_truth:
            return {
                "ground_truth": ValidationResult(
                    status=ValidationStatus.ERROR,
                    message="No ground truth data available for this company"
                )
            }
            
        truth = self.ground_truth[company]
        
        for key, true_value in truth.items():
            if not true_value:
                continue
                
            # Find matching key in extracted data
            for data_key, extracted_value in data.items():
                if not isinstance(extracted_value, (int, float)):
                    continue
                    
                # Match keys regardless of case and spacing
                if self._normalize_key(key) == self._normalize_key(data_key):
                    error_pct = abs(extracted_value - true_value) / max(abs(true_value), 1) * 100
                    
                    if error_pct < 1:
                        results[key] = ValidationResult(
                            status=ValidationStatus.VALID,
                            message="Exact match with ground truth",
                            expected_value=true_value,
                            actual_value=extracted_value
                        )
                    elif error_pct < 5:
                        results[key] = ValidationResult(
                            status=ValidationStatus.WARNING,
                            message=f"Within 5% of ground truth (error: {error_pct:.1f}%)",
                            expected_value=true_value,
                            actual_value=extracted_value,
                            error_percentage=error_pct
                        )
                    else:
                        results[key] = ValidationResult(
                            status=ValidationStatus.ERROR,
                            message=f"Differs from ground truth by {error_pct:.1f}%",
                            expected_value=true_value,
                            actual_value=extracted_value,
                            error_percentage=error_pct
                        )
                        
        for key in truth:
            if key not in results:
                results[key] = ValidationResult(
                    status=ValidationStatus.ERROR,
                    message="Value not found in extracted data",
                    expected_value=truth[key]
                )
                
        return results
    
    def _normalize_key(self, key: str) -> str:
        """
        Normalize a key for comparison by removing spaces, punctuation, and converting to lowercase.
        
        Args:
            key: Key to normalize
            
        Returns:
            Normalized key
        """
        return re.sub(r'[^a-z0-9]', '', key.lower())
    
    def comprehensive_validation(self, company: str, data: Dict[str, Any]) -> Dict[str, Dict[str, ValidationResult]]:
        """
        Perform comprehensive validation of extracted financial data.
        
        Args:
            company: Company name
            data: Dictionary of extracted financial data
            
        Returns:
            Dictionary of validation results by category
        """
        return {
            "range_validation": self.validate_range(data),
            "math_validation": self.validate_math(data),
            "ground_truth": self.compare_with_ground_truth(company, data)
        } 