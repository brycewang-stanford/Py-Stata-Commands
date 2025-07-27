#!/usr/bin/env python3
"""
PyStataR 包详细功能演示

这个脚本展示了 pystatar 包的详细功能，等价于 Stata 的核心命令。
"""

import pandas as pd
import numpy as np
from pystatar import tabulate, egen, reghdfe, winsor2
from pystatar import rank, rowmean, count

def create_sample_data():
    """创建示例数据集"""
    np.random.seed(42)
    n = 1000
    
    # 创建面板数据
    firms = ['A', 'B', 'C', 'D', 'E'] * (n // 5)
    years = sorted([2018, 2019, 2020, 2021, 2022] * (n // 5))
    
    df = pd.DataFrame({
        'firm_id': firms,
        'year': years,
        'sales': np.random.lognormal(mean=10, sigma=1, size=n),
        'employees': np.random.randint(10, 1000, n),
        'industry': np.random.choice(['Tech', 'Finance', 'Manufacturing'], n),
        'country': np.random.choice(['US', 'EU', 'Asia'], n),
        'age': np.random.randint(1, 50, n),
        'rd_spending': np.random.exponential(scale=100, size=n),
    })
    
    # 创建因变量
    df['productivity'] = (
        2.5 * np.log(df['sales']) + 
        0.8 * np.log(df['employees']) + 
        0.3 * df['rd_spending'] / 100 + 
        np.random.normal(0, 2, n)
    )
    
    # 添加一些异常值
    outlier_indices = np.random.choice(n, size=int(n * 0.05), replace=False)
    df.loc[outlier_indices, 'productivity'] *= 3
    
    return df

def demonstrate_tabulate(df):
    """演示 tabulate 功能 (等价于 Stata 的 tabulate)"""
    print("🔸 tabulate 模块演示")
    print("=" * 40)
    
    # 单变量频率表
    print("1. 单变量频率表 (tabulate industry)")
    result1 = tabulate(df['industry'])
    print(result1)
    print()
    
    # 双变量交叉制表
    print("2. 双变量交叉制表 (tabulate industry country)")
    result2 = tabulate(df['industry'], df['country'])
    print(result2)
    print()
    
    # 带统计检验的交叉制表
    print("3. 带卡方检验的交叉制表")
    result3 = tabulate(df['industry'], df['country'], chi2=True)
    print(f"交叉制表结果: {type(result3)}")
    # 如果有统计检验结果，打印它们
    if hasattr(result3, 'chi2_stat'):
        print(f"卡方统计量: {result3.chi2_stat:.4f}")
        print(f"p值: {result3.p_value:.4f}")
    else:
        print("统计检验结果已包含在输出中")
    print()

def demonstrate_egen(df):
    """演示 egen 功能 (等价于 Stata 的 egen)"""
    print("🔸 egen 模块演示")
    print("=" * 40)
    
    # 排名
    print("1. 排名函数 (egen rank_sales = rank(sales))")
    df['rank_sales'] = rank(df['sales'])
    print(f"销售额排名: 最小值={df['rank_sales'].min()}, 最大值={df['rank_sales'].max()}")
    print()
    
    # 行统计
    print("2. 行均值 (egen mean_metrics = rowmean(sales employees))")
    df['mean_metrics'] = rowmean(df, ['sales', 'employees'])
    print(f"行均值: 前5行 = {df['mean_metrics'].head().values}")
    print()
    
    # 分组统计
    print("3. 分组计数 (egen count_by_industry = count(sales), by(industry))")
    df['count_by_industry'] = count(df['sales'], by=df['industry'])
    print("各行业的观测数量:")
    print(df[['industry', 'count_by_industry']].drop_duplicates().sort_values('industry'))
    print()

def demonstrate_reghdfe(df):
    """演示 reghdfe 功能 (等价于 Stata 的 reghdfe)"""
    print("🔸 reghdfe 模块演示")
    print("=" * 40)
    
    # 基础回归
    print("1. 基础回归 (reghdfe productivity sales employees)")
    result1 = reghdfe(df, 'productivity', ['sales', 'employees'])
    print(result1.summary())
    print()
    
    # 固定效应回归
    print("2. 固定效应回归 (reghdfe productivity sales employees, absorb(firm_id))")
    result2 = reghdfe(df, 'productivity', ['sales', 'employees'], fe=['firm_id'])
    print(result2.summary())
    print()
    
    # 多重固定效应
    print("3. 多重固定效应 (reghdfe productivity sales employees, absorb(firm_id year))")
    result3 = reghdfe(df, 'productivity', ['sales', 'employees'], fe=['firm_id', 'year'])
    print(result3.summary())
    print()

def demonstrate_winsor2(df):
    """演示 winsor2 功能 (等价于 Stata 的 winsor2)"""
    print("🔸 winsor2 模块演示")
    print("=" * 40)
    
    # 原始数据统计
    print("1. 原始数据统计")
    print(f"生产力 - 均值: {df['productivity'].mean():.2f}, 标准差: {df['productivity'].std():.2f}")
    print(f"生产力 - 最小值: {df['productivity'].min():.2f}, 最大值: {df['productivity'].max():.2f}")
    print()
    
    # Winsorizing (1% 和 99% 分位数)
    print("2. Winsorizing at 1% and 99% (winsor2 productivity, cuts(1 99))")
    df_winsor = winsor2(df.copy(), ['productivity'], cuts=(1, 99))
    print(f"处理后生产力 - 均值: {df_winsor['productivity'].mean():.2f}, 标准差: {df_winsor['productivity'].std():.2f}")
    print(f"处理后生产力 - 最小值: {df_winsor['productivity'].min():.2f}, 最大值: {df_winsor['productivity'].max():.2f}")
    print()
    
    # 分组 Winsorizing
    print("3. 分组 Winsorizing (winsor2 productivity, cuts(5 95) by(industry))")
    df_winsor_by = winsor2(df.copy(), ['productivity'], cuts=(5, 95), by='industry')
    print("按行业分组的 Winsorizing 结果:")
    for industry in df['industry'].unique():
        industry_data = df_winsor_by[df_winsor_by['industry'] == industry]['productivity']
        print(f"  {industry}: 均值={industry_data.mean():.2f}, 标准差={industry_data.std():.2f}")
    print()

def main():
    """主演示函数"""
    print("🚀 PyStataR 包详细功能演示")
    print("Stata 命令的 Python 等价实现")
    print("=" * 60)
    print()
    
    # 创建示例数据
    print("📊 创建示例数据集...")
    df = create_sample_data()
    print(f"数据集大小: {df.shape[0]} 行, {df.shape[1]} 列")
    print(f"变量: {list(df.columns)}")
    print()
    
    # 演示各个模块
    demonstrate_tabulate(df)
    print("\n" + "=" * 60 + "\n")
    
    demonstrate_egen(df)
    print("\n" + "=" * 60 + "\n")
    
    demonstrate_reghdfe(df)
    print("\n" + "=" * 60 + "\n")
    
    demonstrate_winsor2(df)
    
    print("=" * 60)
    print("✨ 演示完成！")
    print()
    print("📖 使用说明:")
    print("   pip install pystatar")
    print("   from pystatar import tabulate, egen, reghdfe, winsor2")
    print()
    print("🔗 更多信息:")
    print("   GitHub: https://github.com/brycewang-stanford/PyStataR")
    print("   PyPI: https://pypi.org/project/pystatar/")

if __name__ == "__main__":
    main()
