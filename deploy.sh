#!/bin/bash
# Safe Deploy Script - 本地构建和提交（不推送）

set -e  # 遇到错误立即退出

echo "🔍 Step 1: 本地构建验证..."
npm run build

if [ $? -eq 0 ]; then
    echo "✅ 构建成功!"
    
    echo ""
    echo "📝 Step 2: Git 提交..."
    git add .
    
    # 如果有 commit message 参数，使用它；否则使用默认
    if [ -z "$1" ]; then
        git commit -m "Update content"
    else
        git commit -m "$1"
    fi
    
    echo ""
    echo "✅ 已提交到本地 Git (未推送)"
    echo "💡 如需推送，请运行: git push"
else
    echo "❌ 构建失败! 请修复错误后再推送。"
    exit 1
fi
