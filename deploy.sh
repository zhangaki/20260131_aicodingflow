#!/bin/bash
# Safe Deploy Script - 确保构建成功后才推送

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
    echo "🚀 Step 3: 推送到 GitHub..."
    git push
    
    echo ""
    echo "🎉 部署成功! Vercel 将在 60 秒内自动部署。"
    echo "📊 查看部署状态: https://vercel.com/zhangaki/ai-coding-flow"
else
    echo "❌ 构建失败! 请修复错误后再推送。"
    exit 1
fi
