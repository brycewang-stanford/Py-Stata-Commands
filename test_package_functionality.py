#!/usr/bin/env python3
"""
PyStataR 包功能验证测试

这个脚本测试 pystatar 包的基本功能，确保所有模块都能正常工作。
"""

import pandas as pd
import numpy as np
from pystatar import tabulate, egen, reghdfe, winsor2
from pystatar import rank, rowmean

def test_package_imports():
    """测试包导入功能"""
    print("✅ 测试包导入功能...")
    
    # 测试直接函数导入
    from pystatar import tabulate as tab_func
    from pystatar import rank, rowmean
    from pystatar import reghdfe as reg_func
    from pystatar import winsor2 as wins_func
    
    # 测试模块导入
    from pystatar import tabulate_module, egen_module, reghdfe_module, winsor2_module
    
    print("   ✅ 所有导入测试通过")

def test_basic_functionality():
    """测试基本功能"""
    print("✅ 测试基本功能...")
    
    # 创建测试数据
    np.random.seed(42)
    df = pd.DataFrame({
        'x1': np.random.normal(0, 1, 100),
        'x2': np.random.normal(0, 1, 100),
        'group': np.random.choice(['A', 'B', 'C'], 100),
        'id': np.arange(100),
        'category': np.random.choice([1, 2, 3], 100)
    })
    df['y'] = 2 * df['x1'] + 1.5 * df['x2'] + np.random.normal(0, 0.5, 100)
    
    try:
        # 测试 tabulate
        print("   📊 测试 tabulate 模块...")
        tab_result = tabulate(df['group'])
        print(f"      - 单变量制表: {type(tab_result)}")
        
        tab_result_2way = tabulate(df['group'], df['category'])
        print(f"      - 双变量制表: {type(tab_result_2way)}")
        
    except Exception as e:
        print(f"   ❌ tabulate 测试失败: {e}")
    
    try:
        # 测试 egen
        print("   🔧 测试 egen 模块...")
        ranked = rank(df['x1'])
        print(f"      - rank 函数: 生成了 {len(ranked)} 个排名值")
        
        row_means = rowmean(df, ['x1', 'x2'])
        print(f"      - rowmean 函数: 计算了 {len(row_means)} 个行均值")
        
    except Exception as e:
        print(f"   ❌ egen 测试失败: {e}")
    
    try:
        # 测试 reghdfe
        print("   📈 测试 reghdfe 模块...")
        reg_result = reghdfe(df, 'y', ['x1', 'x2'])
        print(f"      - 基础回归: {type(reg_result)}")
        
    except Exception as e:
        print(f"   ❌ reghdfe 测试失败: {e}")
    
    try:
        # 测试 winsor2
        print("   ✂️ 测试 winsor2 模块...")
        winsorized = winsor2(df, ['x1'], cuts=(5, 95))
        print(f"      - winsor2 函数: 处理了 {winsorized.shape[0]} 行数据")
        
    except Exception as e:
        print(f"   ❌ winsor2 测试失败: {e}")

def main():
    """主测试函数"""
    print("🚀 开始 PyStataR 包功能验证测试")
    print("=" * 50)
    
    test_package_imports()
    print()
    test_basic_functionality()
    
    print()
    print("=" * 50)
    print("✨ 测试完成！")

if __name__ == "__main__":
    main()
