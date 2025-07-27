"""
Results classes for pandas-tabulate.

This module defines classes to hold and display tabulation results.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional


class TabulationResult:
    """
    Container for tabulation results and statistics.
    
    This class holds the results of tabulation operations and provides
    methods for displaying and accessing the data.
    """
    
    def __init__(self, table_type: str, data: Dict[str, Any], 
                 options: Dict[str, Any]):
        """
        Initialize TabulationResult.
        
        Parameters:
        -----------
        table_type : str
            Type of tabulation ("oneway" or "twoway")
        data : dict
            Dictionary containing tables and statistics
        options : dict
            Options used for the tabulation
        """
        self.table_type = table_type
        self.data = data
        self.options = options
    
    def __repr__(self) -> str:
        """String representation of the result."""
        return f"TabulationResult(type='{self.table_type}')"
    
    def __str__(self) -> str:
        """Formatted string output similar to Stata."""
        return self.display()
    
    def display(self, show_stats: bool = True) -> str:
        """
        Display formatted tabulation results.
        
        Parameters:
        -----------
        show_stats : bool, default True
            Whether to show statistical test results
            
        Returns:
        --------
        str
            Formatted output string
        """
        if self.table_type == "oneway":
            return self._display_oneway()
        else:
            return self._display_twoway(show_stats)
    
    def _display_oneway(self) -> str:
        """Display one-way tabulation results."""
        lines = []
        lines.append("One-way Tabulation")
        lines.append("=" * 50)
        
        freq_table = self.data['frequencies']
        total = self.data['total']
        
        # Create display table
        display_data = []
        for value in freq_table.index:
            row = [str(value), str(freq_table[value])]
            
            if 'percentages' in self.data:
                pct = self.data['percentages'][value]
                row.append(f"{pct:.2f}")
            
            if 'cumulative_freq' in self.data:
                cum_freq = self.data['cumulative_freq'][value]
                row.append(str(cum_freq))
            
            if 'cumulative_pct' in self.data:
                cum_pct = self.data['cumulative_pct'][value]
                row.append(f"{cum_pct:.2f}")
            
            display_data.append(row)
        
        # Headers
        headers = ["Value", "Freq."]
        if 'percentages' in self.data:
            headers.append("Percent")
        if 'cumulative_freq' in self.data:
            headers.append("Cum.")
        if 'cumulative_pct' in self.data:
            headers.append("Cum. %")
        
        # Format table
        lines.append(self._format_table(headers, display_data))
        lines.append(f"\nTotal: {total}")
        
        return "\n".join(lines)
    
    def _display_twoway(self, show_stats: bool = True) -> str:
        """Display two-way tabulation results."""
        lines = []
        lines.append("Two-way Tabulation")
        lines.append("=" * 50)
        
        # Main cross-tabulation
        crosstab = self.data['crosstab']
        lines.append("\nFrequencies:")
        lines.append(str(crosstab))
        
        # Percentages if requested
        if 'row_percentages' in self.data:
            lines.append("\nRow Percentages:")
            lines.append(str(self.data['row_percentages']))
        
        if 'col_percentages' in self.data:
            lines.append("\nColumn Percentages:")
            lines.append(str(self.data['col_percentages']))
        
        if 'cell_percentages' in self.data:
            lines.append("\nCell Percentages:")
            lines.append(str(self.data['cell_percentages']))
        
        # Statistical tests
        if show_stats and 'statistics' in self.data:
            lines.append("\nStatistical Tests:")
            lines.append("-" * 30)
            
            stats = self.data['statistics']
            
            if 'chi2' in stats:
                chi2_data = stats['chi2']
                lines.append(f"Chi-square test:")
                lines.append(f"  Chi2({chi2_data['df']}) = {chi2_data['statistic']:.4f}")
                lines.append(f"  p-value = {chi2_data['p_value']:.4f}")
                
                if chi2_data['p_value'] < 0.05:
                    lines.append("  Result: Reject null hypothesis (variables are associated)")
                else:
                    lines.append("  Result: Fail to reject null hypothesis (variables may be independent)")
            
            if 'exact' in stats:
                exact_data = stats['exact']
                lines.append(f"\nFisher exact test:")
                lines.append(f"  p-value = {exact_data['p_value']:.4f}")
                lines.append(f"  Odds ratio = {exact_data['odds_ratio']:.4f}")
            
            if 'cramers_v' in stats:
                cramers_data = stats['cramers_v']
                lines.append(f"\nCramér's V = {cramers_data['value']:.4f}")
                lines.append(f"Association strength: {cramers_data['interpretation']}")
        
        return "\n".join(lines)
    
    def _format_table(self, headers: list, data: list) -> str:
        """Format a table with headers and data."""
        # Calculate column widths
        col_widths = [len(h) for h in headers]
        
        for row in data:
            for i, cell in enumerate(row):
                col_widths[i] = max(col_widths[i], len(str(cell)))
        
        # Create format string
        fmt = "  ".join([f"{{:>{w}}}" for w in col_widths])
        
        # Format table
        lines = []
        lines.append(fmt.format(*headers))
        lines.append("-" * sum(col_widths) + "-" * (len(headers) - 1) * 2)
        
        for row in data:
            lines.append(fmt.format(*row))
        
        return "\n".join(lines)
    
    @property
    def frequencies(self) -> pd.DataFrame:
        """Get frequency table."""
        if self.table_type == "oneway":
            return pd.DataFrame(self.data['frequencies'])
        else:
            return self.data['crosstab']
    
    @property
    def statistics(self) -> Optional[Dict[str, Any]]:
        """Get statistical test results."""
        return self.data.get('statistics', None)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            'table_type': self.table_type,
            'data': self.data,
            'options': self.options
        }
    
    def save_csv(self, filename: str) -> None:
        """Save main table to CSV file."""
        if self.table_type == "oneway":
            df = pd.DataFrame(self.data['frequencies'])
            df.to_csv(filename)
        else:
            self.data['crosstab'].to_csv(filename)
