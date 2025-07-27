"""
Py-Stata-Commands Examples

This file demonstrates the basic usage of all four modules in the Py-Stata-Commands package.
"""

import pandas as pd
import numpy as np
from py_stata_commands import tabulate, egen, reghdfe, winsor2

# Create sample dataset
np.random.seed(42)
n = 1000

data = pd.DataFrame({
    'id': range(1, n+1),
    'firm_id': np.random.randint(1, 51, n),  # 50 firms
    'year': np.random.choice([2018, 2019, 2020, 2021, 2022], n),
    'gender': np.random.choice(['Male', 'Female'], n),
    'education': np.random.choice(['High School', 'College', 'Graduate'], n, p=[0.4, 0.4, 0.2]),
    'experience': np.random.normal(10, 5, n).clip(0, 40),
    'wage': np.random.lognormal(3, 0.5, n),
    'sales': np.random.exponential(1000, n),
    'industry': np.random.choice(['Tech', 'Finance', 'Retail', 'Manufacturing'], n)
})

# Add some structure to the data
data['wage'] = data['wage'] + data['experience'] * 500 + np.where(data['education'] == 'Graduate', 20000, 0)
data['sales'] = data['sales'] + data['firm_id'] * 100

print("=== Py-Stata-Commands Examples ===\n")

# ==========================================
# 1. TABULATE Examples
# ==========================================
print("1. TABULATE - Cross-tabulation Examples")
print("-" * 40)

# One-way tabulation
print("One-way tabulation of education:")
result = tabulate.tabulate(data['education'])
print(result)
print()

# Two-way tabulation
print("Two-way tabulation of gender by education:")
result = tabulate.tabulate(data['gender'], data['education'])
print(result)
print()

# Two-way tabulation with chi-square test
print("Two-way tabulation with chi-square test:")
result = tabulate.tabulate(data['gender'], data['education'], chi2=True)
print(result)
print()

# ==========================================
# 2. EGEN Examples  
# ==========================================
print("2. EGEN - Extended Generate Examples")
print("-" * 40)

# Create rankings
data['wage_rank'] = egen.rank(data['wage'])
print("Created wage ranking variable")

# Row statistics
data['row_mean'] = egen.rowmean(data, ['wage', 'sales'])
print("Created row mean of wage and sales")

# Group statistics
data['firm_mean_wage'] = egen.mean(data, 'wage', by='firm_id')
data['firm_count'] = egen.count(data, by='firm_id')
data['firm_tag'] = egen.tag(data, ['firm_id'])

print("Created firm-level statistics:")
print("- Average wage by firm")
print("- Count of employees by firm") 
print("- Tag for unique firms")
print()

# Show some results
firm_stats = data[data['firm_tag'] == 1][['firm_id', 'firm_mean_wage', 'firm_count']].head()
print("Sample firm statistics:")
print(firm_stats)
print()

# ==========================================
# 3. REGHDFE Examples
# ==========================================
print("3. REGHDFE - Fixed Effects Regression Examples")
print("-" * 40)

# Simple fixed effects regression
print("Wage regression with firm and year fixed effects:")
try:
    result = reghdfe.reghdfe(
        data=data,
        depvar='wage', 
        regressors=['experience'],
        absorb=['firm_id', 'year']
    )
    print(result.summary())
except Exception as e:
    print(f"Note: Full reghdfe implementation in progress: {e}")
    print("This would run: wage = experience + firm_FE + year_FE")
print()

# ==========================================
# 4. WINSOR2 Examples
# ==========================================
print("4. WINSOR2 - Winsorizing Examples")
print("-" * 40)

# Winsorize at 1% and 99% percentiles
print("Original wage statistics:")
print(data['wage'].describe())
print()

winsorized_data = winsor2.winsor2(data, ['wage'], cuts=(1, 99))
print("Wage statistics after winsorizing at 1% and 99%:")
print(winsorized_data['wage'].describe())
print()

# Winsorize by group
print("Winsorizing wage by industry:")
winsorized_by_group = winsor2.winsor2(data, ['wage'], by='industry', cuts=(5, 95))
print("Sample results by industry:")
comparison = pd.DataFrame({
    'Original': data.groupby('industry')['wage'].mean(),
    'Winsorized': winsorized_by_group.groupby('industry')['wage'].mean()
})
print(comparison)
print()

# Trimming instead of winsorizing
print("Trimming extreme values (setting to NaN):")
trimmed_data = winsor2.winsor2(data, ['wage'], trim=True, cuts=(2, 98))
print(f"Original observations: {len(data)}")
print(f"After trimming: {len(trimmed_data.dropna())}")
print()

# ==========================================
# 5. Combined Workflow Example
# ==========================================
print("5. COMBINED WORKFLOW - Typical Research Pipeline")
print("-" * 40)

# Step 1: Clean and winsorize data
clean_data = winsor2.winsor2(data.copy(), ['wage', 'sales'], cuts=(1, 99))

# Step 2: Generate additional variables
clean_data['log_wage'] = np.log(clean_data['wage'])
clean_data['experience_sq'] = clean_data['experience'] ** 2
clean_data['high_performer'] = (clean_data['wage'] > clean_data['wage'].quantile(0.75)).astype(int)

# Step 3: Create group-level variables
clean_data['industry_avg_wage'] = egen.mean(clean_data, 'wage', by='industry')
clean_data['firm_size_cat'] = pd.cut(
    egen.count(clean_data, by='firm_id'), 
    bins=[0, 10, 20, 50], 
    labels=['Small', 'Medium', 'Large']
)

# Step 4: Descriptive analysis
print("Cross-tabulation of high performers by education:")
tab_result = tabulate.tabulate(clean_data['high_performer'], clean_data['education'])
print(tab_result)
print()

# Step 5: Regression analysis (conceptual)
print("Research-ready dataset created with:")
print(f"- {len(clean_data)} observations")
print(f"- {len(clean_data.columns)} variables")
print("- Winsorized wage and sales data")
print("- Firm and industry-level aggregates")
print("- Ready for fixed effects regression")

print("\n=== Examples Complete ===")
print("For more detailed examples, see the documentation for each module.")
