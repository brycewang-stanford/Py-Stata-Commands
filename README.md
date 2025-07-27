# Py-Stata-Commands

[![Python Version](https://img.shields.io/pypi/pyversions/py-stata-commands)](https://pypi.org/project/py-stata-commands/)
[![PyPI Version](https://img.shields.io/pypi/v/py-stata-commands)](https://pypi.org/project/py-stata-commands/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://img.shields.io/pypi/dm/py-stata-commands)](https://pypi.org/project/py-stata-commands/)

> **Comprehensive Python package providing Stata-equivalent commands for pandas DataFrames** 🐍

**Py-Stata-Commands** is a unified package that brings the familiar functionality of Stata's most essential data manipulation and statistical commands to Python. If you're a researcher transitioning from Stata to Python, this package makes the transition seamless by providing familiar syntax and functionality.

## 🎯 Core Modules

### 📊 **tabulate** - Cross-tabulation and Frequency Analysis
Python implementation of Stata's `tabulate` command for comprehensive cross-tabulation and frequency analysis.

### 🔧 **egen** - Extended Generate Functions  
Python implementation of Stata's `egen` command for advanced data generation and manipulation.

### 📈 **reghdfe** - High-Dimensional Fixed Effects Regression
Python implementation of Stata's `reghdfe` command for estimating linear regressions with multiple high-dimensional fixed effects.

### 🎛️ **winsor2** - Data Winsorizing and Trimming
Python implementation of Stata's `winsor2` command for winsorizing and trimming outliers.

## 🚀 Quick Installation

```bash
pip install py-stata-commands
```

## 📖 Quick Start Guide

### Cross-tabulation with `tabulate`

```python
import pandas as pd
from py_stata_commands import tabulate

# Create sample data
df = pd.DataFrame({
    'gender': ['M', 'F', 'M', 'F', 'M', 'F'],
    'education': ['High', 'Low', 'High', 'High', 'Low', 'Low']
})

# One-way tabulation
result = tabulate.tabulate(df['gender'])

# Two-way tabulation with statistics
result = tabulate.tabulate(df['gender'], df['education'], chi2=True)
```

### Data generation with `egen`

```python
from py_stata_commands import egen

# Create ranking variable
df['rank_var'] = egen.rank(df['income'])

# Row statistics
df['row_mean'] = egen.rowmean(df, ['var1', 'var2', 'var3'])
df['row_total'] = egen.rowtotal(df, ['var1', 'var2', 'var3'])

# Group statistics
df['group_mean'] = egen.mean(df, 'income', by='group')
df['group_tag'] = egen.tag(df, ['group'])
```

### High-dimensional fixed effects regression with `reghdfe`

```python
from py_stata_commands import reghdfe

# Multiple fixed effects regression
result = reghdfe.reghdfe(
    data=df,
    depvar='wage',
    regressors=['experience', 'education'],
    absorb=['firm_id', 'year'],
    cluster='firm_id'
)
```

### Data winsorizing with `winsor2`

```python
from py_stata_commands import winsor2

# Winsorize at 1% and 99% percentiles
result = winsor2.winsor2(df, ['income'], cuts=(1, 99))

# Winsorize by group
result = winsor2.winsor2(df, ['income'], by='industry')

# Trim outliers instead of winsorizing
result = winsor2.winsor2(df, ['income'], trim=True)
```

## 🏗️ Project Structure

```
py_stata_commands/
├── __init__.py              # Main package initialization
├── tabulate/               # Cross-tabulation module
│   ├── __init__.py
│   ├── core.py
│   ├── results.py
│   └── stats.py
├── egen/                   # Extended generation module
│   ├── __init__.py
│   └── core.py
├── reghdfe/               # High-dimensional FE regression
│   ├── __init__.py
│   ├── core.py
│   ├── estimation.py
│   └── utils.py
├── winsor2/               # Winsorizing module
│   ├── __init__.py
│   ├── core.py
│   └── utils.py
├── utils/                 # Shared utilities
│   ├── __init__.py
│   └── common.py
└── tests/                 # Test suite
    ├── test_tabulate.py
    ├── test_egen.py
    ├── test_reghdfe.py
    └── test_winsor2.py
```

## 🔧 Key Features

- **Familiar Syntax**: Stata-like command structure and parameters
- **Pandas Integration**: Seamless integration with pandas DataFrames
- **High Performance**: Optimized implementations using pandas and NumPy
- **Comprehensive Coverage**: Most commonly used Stata commands
- **Statistical Rigor**: Proper statistical tests and robust standard errors
- **Flexible Output**: Multiple output formats and customization options
- **Missing Value Handling**: Configurable treatment of missing data

## 📚 Documentation

Each module comes with comprehensive documentation and examples:

- [**tabulate Documentation**](docs/tabulate.md) - Cross-tabulation and frequency analysis
- [**egen Documentation**](docs/egen.md) - Extended data generation functions
- [**reghdfe Documentation**](docs/reghdfe.md) - High-dimensional fixed effects regression  
- [**winsor2 Documentation**](docs/winsor2.md) - Data winsorizing and trimming

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

This package builds upon the excellent work of:
- [pandas](https://pandas.pydata.org/) for data manipulation
- [numpy](https://numpy.org/) for numerical computing
- [scipy](https://scipy.org/) for statistical functions
- [pyhdfe](https://github.com/jeffgortmaker/pyhdfe) for high-dimensional fixed effects algorithms

## 📧 Contact

Created by [Bryce Wang](https://github.com/brycewang-stanford) - feel free to contact me!

---

⭐ **Star this repository if you find it useful!** ⭐
