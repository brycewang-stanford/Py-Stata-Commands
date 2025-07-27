# PyStataR 发布指南

## 📋 前置准备

### 1. 注册 PyPI 账户
- **PyPI (正式)**: https://pypi.org/account/register/
- **TestPyPI (测试)**: https://test.pypi.org/account/register/

### 2. 生成 API Tokens
- **PyPI Token**: https://pypi.org/manage/account/token/
- **TestPyPI Token**: https://test.pypi.org/manage/account/token/

保存好这些 tokens，后面会用到。

## 🚀 发布步骤

### 方法 1: 使用提供的发布脚本（推荐）

```bash
# 运行发布脚本，它会构建包并提供发布命令
./publish_to_pypi.sh
```

### 方法 2: 手动发布

```bash
# 1. 激活虚拟环境
source .venv_pystatar/bin/activate

# 2. 清理并构建
rm -rf dist/ build/ *.egg-info
python -m build

# 3. 检查包质量
python -m twine check dist/*

# 4. 先发布到 TestPyPI 测试
python -m twine upload --repository testpypi dist/* --username __token__ --password <your-testpypi-token>

# 5. 测试安装
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ pystatar

# 6. 测试成功后，发布到正式 PyPI
python -m twine upload dist/* --username __token__ --password <your-pypi-token>
```

## ✅ 验证发布

### 测试安装
```bash
# 从 TestPyPI 安装测试
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ pystatar

# 从正式 PyPI 安装
pip install pystatar
```

### 测试功能
```python
# 测试基本导入
from pystatar import tabulate, egen, reghdfe, winsor2
print("✅ PyStataR 安装成功！")

# 测试基本功能
import pandas as pd
df = pd.DataFrame({'a': [1, 2, 1, 2], 'b': [1, 1, 2, 2]})
result = tabulate.tabulate(df['a'], df['b'])
print("✅ 基本功能正常！")
```

## 📈 发布后步骤

1. **更新 README badges**: 确保 PyPI links 正确
2. **创建 GitHub Release**: 为这个版本创建 release tag
3. **宣传发布**: 在社交媒体、学术论坛等地方分享
4. **更新文档**: 确保所有文档链接都是最新的

## 🔗 有用链接

- **PyPI 项目页面**: https://pypi.org/project/pystatar/
- **TestPyPI 项目页面**: https://test.pypi.org/project/pystatar/
- **GitHub 仓库**: https://github.com/brycewang-stanford/PyStataR
- **使用统计**: https://pypistats.org/packages/pystatar

## 🆘 故障排除

### 常见错误
1. **403 Forbidden**: API token 错误或账户权限问题
2. **400 Bad Request**: 包名冲突或版本号问题
3. **构建失败**: 检查 pyproject.toml 格式

### 解决方案
- 确保 token 复制完整（包括 `pypi-` 前缀）
- 检查包名是否已被占用
- 验证版本号格式（遵循 PEP 440）
