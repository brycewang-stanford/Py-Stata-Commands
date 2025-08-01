#!/usr/bin/env python3
"""
PyStataR 包功能验证测试

这个脚本测试 pystatar 包的基本功能，确保所有模块都能正常工作。
包含三个核心模块：pyegen、pywinsor2、pdtab
"""

import pandas as pd
import numpy as np
from pystatar import pyegen, pywinsor2, pdtab
from pystatar import rank, rowmean

def test_package_imports():
    """测试包导入功能"""
    print("✅ 测试包导入功能...")
    
    # 测试直接函数导入
    from pystatar import tabulate as tab_func
    from pystatar import rank, rowmean
    from pystatar import winsor2 as wins_func
    
    # 测试模块导入
    from pystatar import pyegen, pywinsor2, pdtab
    
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
        # 测试 pdtab
        print("   📊 测试 pdtab 模块...")
        tab_result = pdtab.oneway(df, 'group')
        print(f"      - 单变量制表: {type(tab_result)}")
        
        tab_result_2way = pdtab.twoway(df, 'group', 'category')
        print(f"      - 双变量制表: {type(tab_result_2way)}")
        
    except Exception as e:
        print(f"   ❌ pdtab 测试失败: {e}")
    
    try:
        # 测试 pyegen
        print("   🔧 测试 pyegen 模块...")
        ranked = pyegen.rank(df['x1'])
        print(f"      - rank 函数: 生成了 {len(ranked)} 个排名值")
        
        row_means = pyegen.rowmean(df, ['x1', 'x2'])
        print(f"      - rowmean 函数: 计算了 {len(row_means)} 个行均值")
        
    except Exception as e:
        print(f"   ❌ pyegen 测试失败: {e}")
    
    try:
        # 测试 pywinsor2
        print("   ✂️ 测试 pywinsor2 模块...")
        winsorized = pywinsor2.winsor2(df, ['x1'], cuts=(5, 95))
        print(f"      - winsor2 函数: 处理了 {winsorized.shape[0]} 行数据")
        
    except Exception as e:
        print(f"   ❌ pywinsor2 测试失败: {e}")

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
