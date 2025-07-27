#!/bin/bash

# PyStataR 发布到 PyPI 的脚本
# 使用说明：
# 1. 确保您已经在 PyPI 和 TestPyPI 注册账户
# 2. 获取 API tokens:
#    - PyPI: https://pypi.org/manage/account/token/
#    - TestPyPI: https://test.pypi.org/manage/account/token/
# 3. 运行脚本时会提示输入 tokens

set -e  # 遇到错误时退出

echo "🚀 PyStataR 发布脚本"
echo "=================="

# 激活虚拟环境
echo "📦 激活虚拟环境..."
source .venv_pystatar/bin/activate

# 清理旧的构建文件
echo "🧹 清理旧的构建文件..."
rm -rf dist/ build/ *.egg-info

# 构建包
echo "🔨 构建发布包..."
python -m build

# 检查包质量
echo "✅ 检查包质量..."
python -m twine check dist/*

# 确认不包含开发记录
echo "🔍 确认不包含开发记录文件..."
if tar -tf dist/pystatar-*.tar.gz | grep -E "(开发记录|kaifajilu|INTEGRATION)"; then
    echo "❌ 错误：发布包中包含开发记录文件！"
    exit 1
else
    echo "✅ 确认：开发记录文件已排除"
fi

echo ""
echo "📋 发布包内容预览："
echo "Wheel 文件："
unzip -l dist/pystatar-*-py3-none-any.whl | head -20

echo ""
echo "📦 包已准备就绪！"
echo ""
echo "下一步：发布到 PyPI"
echo "==================="
echo ""
echo "🧪 先发布到 TestPyPI 进行测试："
echo "python -m twine upload --repository testpypi dist/* --username __token__ --password <your-testpypi-token>"
echo ""
echo "✅ 测试成功后，发布到正式 PyPI："
echo "python -m twine upload dist/* --username __token__ --password <your-pypi-token>"
echo ""
echo "🔗 获取 API tokens："
echo "- TestPyPI: https://test.pypi.org/manage/account/token/"
echo "- PyPI: https://pypi.org/manage/account/token/"
echo ""
echo "📊 发布后验证："
echo "pip install --index-url https://test.pypi.org/simple/ pystatar  # TestPyPI"
echo "pip install pystatar  # 正式 PyPI"
