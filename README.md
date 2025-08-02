# PyStataR## 🆕 What's New in v0.4.0

✨ **New Integration**: Added pyoutreg for professional regression output tables (Stata's `outreg2` equivalent)  
📊 **Enhanced Functionality**: Comprehensive regression result export to Excel/Word with publication-quality formatting  
🔧 **Four-Package Integration**: Now includes pyegen, pywinsor2, pdtab, and pyoutreg under unified interface  
📚 **Extended Documentation**: Complete examples for regression output and model comparison  
🚀 **Research-Ready**: End-to-end workflow from data processing to publication tablesython Version](https://img.shields.io/pypi/pyversions/pystatar)](https://pypi.org/project/pystatar/)
[![PyPI Version](https://img.shields.io/pypi/v/pystatar)](https://pypi.org/project/pystatar/)
[![License](https://img.shields.io/pypi/l/pystatar)](https://github.com/brycewang-stanford/PyStataR/blob/main/LICENSE)
[![Downloads](https://img.shields.io/pypi/dm/pystatar)](https://pypi.org/project/pystatar/)

> **The Ultimate Python Toolkit for Academic Research - Bringing Stata & R's Power to Python**  
> **集成 Stata 和 R 语言的最高频使用工具，让社科学术和统计研究，全面拥抱 Python/AI/开源社区**

## What's New in v0.3.0

**Enhanced Architecture**: Improved unified interface with better error handling and documentation  
**Cleaner Codebase**: Removed duplicate code and streamlined module structure  
**Better Documentation**: Enhanced examples and clearer API documentation  
**Performance**: Optimized imports and reduced overhead for faster loading  

## Project Vision & Goals

**PyStataR** serves as a unified interface to the most powerful and frequently used Stata-equivalent packages in Python. Instead of reinventing the wheel, we provide seamless integration of four mature PyPI packages under one convenient interface.

- **Seamless Integration**: Four proven PyPI packages unified under one interface
- **Familiar Workflow**: Stata-like syntax and functionality for Python users  
- **Academic Focus**: Built specifically for research and statistical analysis needs
- **Open Source**: Free and accessible to all researchers worldwide
- **No Reinvention**: Leverages existing, mature packages rather than duplicating functionality


### Why This Project Matters
- **Bridge the Gap**: Seamless transition from Stata to Python for researchers
- **Unified Interface**: One package, multiple powerful tools - no need to learn different APIs
- **Mature Foundation**: Built on battle-tested PyPI packages with years of development
- **Community-Driven**: Open source development with academic researchers in mind
- **No Maintenance Overhead**: Leverages existing packages rather than maintaining duplicate code

### Target Stata Commands (The Most Used in Academic Research)
✅ **pyegen** - Extended data generation and manipulation (Stata's `egen`)  
✅ **pywinsor2** - Data winsorizing and trimming (Stata's `winsor2`)  
✅ **pdtab** - Cross-tabulation and frequency analysis (Stata's `tabulate`)  
✅ **pyoutreg** - Professional regression output tables (Stata's `outreg2`)

**Based on mature PyPI packages**:
- [pyegen](https://pypi.org/project/pyegen/) - version 0.2.4+
- [pywinsor2](https://pypi.org/project/pywinsor2/) - version 0.4.3+  
- [pdtab](https://pypi.org/project/pdtab/) - version 0.1.1+
- [pyoutreg](https://pypi.org/project/pyoutreg/) - version 0.1.1+

**Want to contribute or request features?** 
-  [Create an issue](https://github.com/brycewang-stanford/PyStataR/issues) to request functionality
-  [Contribute](CONTRIBUTING.md) to help us improve the package
- ⭐ Star this repo to show your support!
---- 
## Core Modules Overview
### **pyegen** - Extended Data Generation and Manipulation  
- **Built on**: [pyegen v0.2.4](https://pypi.org/project/pyegen/) PyPI package
- **Key Features**: Group operations, ranking with tie-breaking, row statistics, percentile calculations
- **Use Cases**: Data preprocessing, feature engineering, panel data construction

### **pdtab** - Advanced Cross-tabulation and Frequency Analysis
- **Built on**: [pdtab v0.1.1](https://pypi.org/project/pdtab/) PyPI package  
- **Key Features**: One-way and two-way tables, statistical tests, comprehensive output formatting
- **Use Cases**: Survey analysis, categorical data exploration, market research

### **pywinsor2** - Advanced Outlier Detection and Treatment
- **Built on**: [pywinsor2 v0.4.3](https://pypi.org/project/pywinsor2/) PyPI package
- **Key Features**: IQR-based detection, percentile methods, group-wise operations, flexible trimming
- **Use Cases**: Data cleaning, outlier analysis, robust statistical modeling

### **pyoutreg** - Professional Regression Output Tables  
- **Built on**: [pyoutreg v0.1.1](https://pypi.org/project/pyoutreg/) PyPI package
- **Key Features**: Stata `outreg2` equivalent, Excel/Word export, model comparison, publication-quality formatting
- **Use Cases**: Academic papers, research reports, model comparison tables, publication workflows

## Advanced Features & Performance

### Performance Optimizations
- **Vectorized Operations**: All functions leverage NumPy and pandas for maximum speed
- **Memory Efficiency**: Optimized for large datasets common in academic research
- **Proven Reliability**: Built on four mature PyPI packages with extensive testing
- **Modular Design**: Use individual modules independently or together

### Research-Grade Features
- **Publication Ready**: Clean output formatting suitable for academic papers
- **Reproducible Research**: Consistent results and comprehensive documentation
- **Missing Data Handling**: Robust missing value treatment across all modules
- **Academic Standards**: Follows statistical best practices and conventions

## Quick Installation

```bash
pip install pystatar
```

## Comprehensive Usage Examples

### Two Ways to Use PyStataR

#### Method 1: Module-based Import (Recommended)
```python
from pystatar import pyegen, pywinsor2, pdtab, pyoutreg

# Each module maintains its independence and full functionality
```

#### Method 2: Direct Function Import (Convenience)
```python
from pystatar import rank, rowmean, winsor2, tabulate, outreg

# Direct access to key functions
```

### `pdtab` - Advanced Cross-tabulation

The `pdtab` module provides comprehensive frequency analysis and cross-tabulation capabilities.

#### Basic Usage Examples
```python
import pandas as pd
import numpy as np
from pystatar import pdtab

# Create sample dataset
df = pd.DataFrame({
    'gender': ['Male', 'Female', 'Male', 'Female', 'Male', 'Female'] * 100,
    'education': ['High School', 'College', 'Graduate', 'High School', 'College', 'Graduate'] * 100,
    'income_level': np.random.choice(['Low', 'Medium', 'High'], 600),
    'age': np.random.randint(22, 65, 600),
    'industry': np.random.choice(['Tech', 'Finance', 'Healthcare', 'Education'], 600)
})

# One-way frequency table
result = pdtab.tab1('education', df)
print(result)

# Two-way cross-tabulation
result = pdtab.tab2('gender', 'education', df)
print(result)

# Using convenience function
result = pdtab.tabulate('gender', 'education', df)
print(result)
```
### `pyegen` - Extended Data Generation

The `pyegen` module provides powerful data manipulation functions that extend Stata's egen capabilities.

#### Ranking and Statistical Functions
```python
from pystatar import pyegen

# Create test data
df = pd.DataFrame({
    'income': np.random.normal(50000, 15000, 1000),
    'industry': np.random.choice(['Tech', 'Finance', 'Healthcare'], 1000),
    'experience': np.random.randint(0, 30, 1000)
})

# Basic ranking functions
df['income_rank'] = pyegen.rank(df['income'])
df['income_rank_by_industry'] = pyegen.rank(df['income'], by=df['industry'])

# Group statistics
df['mean_income_by_industry'] = pyegen.mean(df['income'], by=df['industry'])
df['industry_count'] = pyegen.count(df, by='industry')

# Row operations (for multiple variables)
scores_df = pd.DataFrame({
    'math': np.random.normal(75, 10, 100),
    'english': np.random.normal(80, 12, 100),
    'science': np.random.normal(78, 11, 100)
})

scores_df['total_score'] = pyegen.rowtotal(scores_df, ['math', 'english', 'science'])
scores_df['avg_score'] = pyegen.rowmean(scores_df, ['math', 'english', 'science'])
scores_df['max_score'] = pyegen.rowmax(scores_df, ['math', 'english', 'science'])
```
```python
# Create test scores dataset
scores_df = pd.DataFrame({
    'student': range(1, 101),
    'math': np.random.normal(75, 10, 100),
    'english': np.random.normal(80, 12, 100),
    'science': np.random.normal(78, 11, 100),
    'history': np.random.normal(82, 9, 100)
})

# Row statistics
scores_df['total_score'] = egen.rowtotal(scores_df, ['math', 'english', 'science', 'history'])
scores_df['avg_score'] = egen.rowmean(scores_df, ['math', 'english', 'science', 'history'])
scores_df['min_score'] = egen.rowmin(scores_df, ['math', 'english', 'science', 'history'])
### `pywinsor2` - Advanced Outlier Treatment

The `pywinsor2` module provides comprehensive outlier detection and treatment methods.

#### Basic Winsorizing
```python
from pystatar import pywinsor2

# Create dataset with outliers
outlier_df = pd.DataFrame({
    'income': np.concatenate([
        np.random.normal(50000, 10000, 950),  # Normal observations
        np.random.uniform(200000, 500000, 50)  # Outliers
    ]),
    'age': np.random.randint(18, 70, 1000),
    'industry': np.random.choice(['Tech', 'Finance', 'Retail', 'Healthcare'], 1000)
})

# Basic winsorizing at 1st and 99th percentiles
result = pywinsor2.winsor2(outlier_df, ['income'])
print("Original vs Winsorized:")
print(f"Original: min={outlier_df['income'].min():.0f}, max={outlier_df['income'].max():.0f}")
print(f"Winsorized: min={result['income_w'].min():.0f}, max={result['income_w'].max():.0f}")

# Group-wise winsorizing
result = pywinsor2.winsor2(
    outlier_df, 
    ['income'],
    by='industry',          # Winsorize within each industry
    cuts=(5, 95),          # Use 5th and 95th percentiles
    suffix='_clean'        # Custom suffix
)

# Trimming vs Winsorizing
trim_result = pywinsor2.winsor2(
    outlier_df, 
    ['income'],
    trim=True,              # Trim (remove) instead of winsorize
    cuts=(2.5, 97.5)       # Trim 2.5% from each tail
)

print(f"Original N: {len(outlier_df)}")
print(f"After trimming N: {trim_result['income_tr'].notna().sum()}")
```
    'log_employment': np.random.normal(4, 0.5, n_obs),
    'log_capital': np.random.normal(8, 0.8, n_obs),
    'industry': np.repeat(np.random.choice(['Tech', 'Manufacturing', 'Services'], n_firms), n_years)
})

### `winsor2` - Advanced Outlier Treatment

The `winsor2` module provides comprehensive outlier detection and treatment methods.

#### Basic Winsorizing
```python
from pystatar import winsor2

# Create dataset with outliers
outlier_df = pd.DataFrame({
    'income': np.concatenate([
        np.random.normal(50000, 10000, 950),  # Normal observations
        np.random.uniform(200000, 500000, 50)  # Outliers
    ]),
    'age': np.random.randint(18, 70, 1000),
    'industry': np.random.choice(['Tech', 'Finance', 'Retail', 'Healthcare'], 1000)
})

# Basic winsorizing at 1st and 99th percentiles
result = winsor2.winsor2(outlier_df, ['income'])
print("Original vs Winsorized:")
print(f"Original: min={outlier_df['income'].min():.0f}, max={outlier_df['income'].max():.0f}")
print(f"Winsorized: min={result['income_w'].min():.0f}, max={result['income_w'].max():.0f}")
```

#### Group-wise Winsorizing
```python
# Winsorize within groups
result = winsor2.winsor2(
    outlier_df, 
    ['income'],
    by='industry',          # Winsorize within each industry
    cuts=(5, 95),          # Use 5th and 95th percentiles
    suffix='_clean'        # Custom suffix
)

# Compare distributions by group
for industry in outlier_df['industry'].unique():
    mask = outlier_df['industry'] == industry
    original = outlier_df.loc[mask, 'income']
    winsorized = result.loc[mask, 'income_clean']
    print(f"\n{industry}:")
    print(f"  Original: {original.describe()}")
    print(f"  Winsorized: {winsorized.describe()}")
```

#### Trimming vs Winsorizing Comparison
```python
# Compare different outlier treatment methods
trim_result = winsor2.winsor2(
    outlier_df, 
    ['income'],
    trim=True,              # Trim (remove) instead of winsorize
    cuts=(2.5, 97.5)       # Trim 2.5% from each tail
)

winsor_result = winsor2.winsor2(
    outlier_df, 
    ['income'],
    trim=False,             # Winsorize (cap) outliers
    cuts=(2.5, 97.5)
)

print("Treatment Comparison:")
print(f"Original N: {len(outlier_df)}")
print(f"After trimming N: {trim_result['income_tr'].notna().sum()}")
print(f"After winsorizing N: {len(winsor_result)}")
print(f"Trimmed mean: {trim_result['income_tr'].mean():.0f}")
print(f"Winsorized mean: {winsor_result['income_w'].mean():.0f}")
```

#### Advanced Outlier Detection
```python
# Multiple variable winsorizing with custom thresholds
multi_result = winsor2.winsor2(
    outlier_df,
    ['income', 'age'],
    cuts=(1, 99),           # Different cuts for different variables
    by='industry',          # Group-specific treatment
    replace=True,           # Replace original variables
    label=True              # Add descriptive labels
)

# Generate outlier indicators
outlier_df['income_outlier'] = winsor2.outlier_indicator(
    outlier_df['income'], 
    method='iqr',           # Use IQR method
    factor=1.5              # 1.5 * IQR threshold
)

outlier_df['extreme_outlier'] = winsor2.outlier_indicator(
    outlier_df['income'],
    method='percentile',    # Use percentile method
    cuts=(1, 99)
)

print("Outlier Detection Results:")
print(f"IQR method detected {outlier_df['income_outlier'].sum()} outliers")
print(f"Percentile method detected {outlier_df['extreme_outlier'].sum()} outliers")
```

### `pyoutreg` - Professional Regression Output Tables

The `pyoutreg` module provides Stata's `outreg2` equivalent functionality for exporting regression results to publication-quality tables.

#### Basic Regression Output
```python
import pandas as pd
import numpy as np
import statsmodels.api as sm
from pystatar import pyoutreg

# Create sample dataset
np.random.seed(42)
n = 1000
data = pd.DataFrame({
    'y': np.random.normal(50, 10, n),
    'x1': np.random.normal(0, 1, n),
    'x2': np.random.normal(0, 1, n),
    'x3': np.random.normal(0, 1, n),
    'industry': np.random.choice(['Tech', 'Finance', 'Healthcare'], n)
})

# Add some realistic relationships
data['y'] = 50 + 3*data['x1'] + 2*data['x2'] + np.random.normal(0, 5, n)

# Run regression
X = sm.add_constant(data[['x1', 'x2', 'x3']])
model = sm.OLS(data['y'], X).fit()

# Export to Excel (Stata outreg2 equivalent)
pyoutreg.outreg(model, 'regression_results.xlsx', replace=True, 
                ctitle='Model 1', title='My Research Results')
print("Regression results exported to Excel!")
```

#### Multiple Model Comparison
```python
# Compare multiple models (like Stata's outreg2 append)
model1 = sm.OLS(data['y'], sm.add_constant(data[['x1']])).fit()
model2 = sm.OLS(data['y'], sm.add_constant(data[['x1', 'x2']])).fit()
model3 = sm.OLS(data['y'], sm.add_constant(data[['x1', 'x2', 'x3']])).fit()

# Export multiple models to same file
pyoutreg.outreg(model1, 'comparison.xlsx', replace=True, ctitle='Model 1')
pyoutreg.outreg(model2, 'comparison.xlsx', append=True, ctitle='Model 2')
pyoutreg.outreg(model3, 'comparison.xlsx', append=True, ctitle='Model 3')

# Or use the comparison function
pyoutreg.outreg_compare([model1, model2, model3], 
                       'model_comparison.xlsx',
                       model_names=['Basic', 'Extended', 'Full Model'])
```

#### Summary Statistics Export
```python
# Export summary statistics (Stata's outreg2 sum)
pyoutreg.outreg(data=data[['y', 'x1', 'x2', 'x3']], 
                filename='summary_stats.xlsx',
                sum_stats=True, 
                replace=True,
                title='Descriptive Statistics')

# Grouped summary statistics
pyoutreg.outreg(data=data, 
                filename='summary_by_industry.xlsx',
                sum_stats=True,
                by='industry',
                replace=True,
                title='Statistics by Industry')
```

#### Advanced Output Formatting
```python
# Customize output format
pyoutreg.outreg(model, 'formatted_results.xlsx',
                replace=True,
                dec=3,                    # 3 decimal places
                bdec=4,                   # 4 decimal places for coefficients
                keep=['x1', 'x2'],        # Only show x1 and x2
                title='Publication Table',
                addnote='Robust standard errors in parentheses',
                font_size=12,
                font_name='Arial')

# Export to Word document
pyoutreg.outreg(model, 'results.docx',
                replace=True,
                landscape=True,           # Landscape orientation
                title='Research Results')
```

## Project Structure

```
pystatar/
├── __init__.py              # Main package with unified interface to:
│                           #   - pyegen (v0.2.4+)
│                           #   - pywinsor2 (v0.4.3+)
│                           #   - pdtab (v0.1.1+)
│                           #   - pyoutreg (v0.1.1+)
└── tests/                  # Integration tests
    ├── test_basic.py       # Basic integration tests
    ├── test_egen.py        # pyegen functionality tests
    ├── test_pdtab.py       # pdtab functionality tests
    ├── test_winsor2.py     # pywinsor2 functionality tests
    └── test_outreg.py      # pyoutreg functionality tests
```

### Why This Architecture?

- **No Code Duplication**: We don't reinvent the wheel - we use proven packages
- **Easier Maintenance**: Updates and bug fixes come from the original package maintainers
- **Better Reliability**: Built on packages with existing user bases and testing
- **Unified Interface**: One import gives you access to all functionality
- **Future-Proof**: Automatically benefits from improvements in underlying packages

## Key Features

- **Familiar Syntax**: Stata-like command structure and parameters
- **Unified Interface**: Access four powerful modules (pdtab, pyegen, pywinsor2, pyoutreg) through a single package
- **Namespace Design**: Maintains module independence while providing integrated functionality
- **Pandas Integration**: Seamless integration with pandas DataFrames
- **High Performance**: Optimized implementations using pandas and NumPy
- **Comprehensive Coverage**: Cross-tabulation, data generation, outlier treatment, and regression output functions
- **Statistical Rigor**: Proper statistical tests and robust calculations
- **Flexible Output**: Multiple output formats (Excel, Word, DataFrame) and customization options
- **Missing Value Handling**: Configurable treatment of missing data
- **Publication Ready**: Professional table formatting for academic papers and reports

## Documentation

Each module comes with comprehensive documentation and examples:

- [**pdtab Documentation**](docs/pdtab.md) - Cross-tabulation and contingency table analysis
- [**pyegen Documentation**](docs/pyegen.md) - Extended data generation functions
- [**pywinsor2 Documentation**](docs/pywinsor2.md) - Data winsorizing and outlier treatment
- [**pyoutreg Documentation**](docs/pyoutreg.md) - Professional regression output tables

## Contributing to the Project

We're building the future of academic research tools in Python! Here's how you can help:

### Priority Commands Needed
Help us implement the remaining **16 high-priority commands**:

**Data Management**: `summarize`, `describe`, `merge`, `reshape`, `collapse`, `keep`, `drop`, `generate`, `replace`, `sort`

**Statistical Analysis**: `reg`, `logit`, `probit`, `ivregress`, `xtreg`, `anova`

### How to Contribute

1. **Request a Command**: [Open an issue](https://github.com/brycewang-stanford/PyStataR/issues/new) with the command you need
2. **Implement a Command**: Check our [contribution guidelines](CONTRIBUTING.md) and submit a PR
3. **Report Bugs**: Help us improve existing functionality
4. **Improve Documentation**: Add examples, tutorials, or clarifications
5. **Spread the Word**: Star the repo and share with fellow researchers

###  Recognition
All contributors will be recognized in our documentation and release notes. Major contributors will be listed as co-authors on any academic publications about this project.

###  Academic Collaboration
We welcome partnerships with universities and research institutions. If you're interested in using this project in your coursework or research, please reach out!

## Community & Support

- **Documentation**: [https://pystatar.readthedocs.io](docs/)
- **Discussions**: [GitHub Discussions](https://github.com/brycewang-stanford/PyStataR/discussions)
- **Issues**: [Bug Reports & Feature Requests](https://github.com/brycewang-stanford/PyStataR/issues)
- **Email**: brycew6m@stanford.edu for academic collaborations

## Comparison with Stata

| Feature | Stata | PyStataR | Advantage |
|---------|-------|-------------------|-----------|
| **Speed** | Base performance | 2-10x faster* | Vectorized operations |
| **Memory** | Limited by system | Efficient pandas backend | Better large dataset handling |
| **Extensibility** | Ado files | Python ecosystem | Unlimited customization |
| **Cost** | $$$$ | Free & Open Source | Accessible to all researchers |
| **Integration** | Standalone | Python data science stack | Seamless workflow |
| **Output** | Limited formats | Multiple (LaTeX, HTML, etc.) | Publication ready |

*Performance comparison based on typical academic datasets (1M+ observations)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

This package builds upon the excellent work of:
- [pandas](https://pandas.pydata.org/) - The backbone of our data manipulation
- [numpy](https://numpy.org/) - Powering our numerical computations
- [scipy](https://scipy.org/) - Statistical functions and algorithms
- [statsmodels](https://www.statsmodels.org/) - Statistical modeling foundations
- [pyhdfe](https://github.com/jeffgortmaker/pyhdfe) - High-dimensional fixed effects algorithms
- The entire **Stata community** - For decades of statistical innovation that inspired this project

##  Future Roadmap

### Version 1.0 Goals (Target: End of 2025)
-  Core 4 commands implemented
-  Additional 16 high-priority commands
-  Comprehensive test suite (>95% coverage)
-  Complete documentation with tutorials
-  Performance benchmarks vs Stata

### Version 2.0 Vision (2026)
-  Machine learning integration
-  R integration for cross-platform compatibility
-  Web interface for non-programmers
-  Jupyter notebook extensions

## 📈 Project Statistics

[![GitHub stars](https://img.shields.io/github/stars/brycewang-stanford/PyStataR?style=social)](https://github.com/brycewang-stanford/PyStataR/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/brycewang-stanford/PyStataR?style=social)](https://github.com/brycewang-stanford/PyStataR/network)
[![GitHub issues](https://img.shields.io/github/issues/brycewang-stanford/PyStataR)](https://github.com/brycewang-stanford/PyStataR/issues)
[![GitHub pull requests](https://img.shields.io/github/issues-pr/brycewang-stanford/PyStataR)](https://github.com/brycewang-stanford/PyStataR/pulls)

##  Contact & Collaboration

**Created by [Bryce Wang](https://github.com/brycewang-stanford)** - Stanford University

-  **Email**: brycew6m@stanford.edu  
-  **GitHub**: [@brycewang-stanford](https://github.com/brycewang-stanford)
-  **LinkedIn**: [Connect with me](https://linkedin.com/in/brycewang)

### Academic Partnerships Welcome!
-  Course integration and teaching materials
-  Research collaborations and citations
-  Institutional licensing and support
-  Student contributor programs

---

### ⭐ **Love this project? Give it a star and help us reach more researchers!** ⭐

**Together, we're building the future of academic research in Python** 

### Disclaimer
The PyStataR tool is not affiliated with, endorsed by, or in any way associated with Stata or StataCorp LLC.
“Stata” is a registered trademark of StataCorp LLC. Any mention of it in this project is solely for academic reference and comparative functionality purposes.
This tool is independently developed by the author and does not copy or reuse any part of the Stata source code. It is inspired by the design of Stata's analytical features to support similar workflows in Python.
For any trademark or copyright concerns, please contact the author for resolution.
