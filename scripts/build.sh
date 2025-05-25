#!/bin/bash

# Agent API 构建脚本

set -e

echo "🚀 开始构建 Agent API..."

# 检查 Docker 是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装，请先安装 Docker"
    exit 1
fi

# 检查 docker-compose 是否安装
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose 未安装，请先安装 docker-compose"
    exit 1
fi

# 检查配置文件
if [ ! -f ".env" ]; then
    echo "⚠️ 未找到 .env 文件，正在创建..."
    cp env.example .env
    echo "✅ 已创建 .env 文件，请编辑填入真实配置"
    echo "📝 请编辑 .env 文件，填入您的 AGENT_APP_ID 和 AGENT_API_KEY"
    exit 1
fi

# 构建 Docker 镜像
echo "🔨 构建 Docker 镜像..."
docker-compose build

echo "✅ 构建完成！"
echo ""
echo "🚀 启动服务："
echo "   docker-compose up -d"
echo ""
echo "📊 查看状态："
echo "   docker-compose ps"
echo ""
echo "📝 查看日志："
echo "   docker-compose logs -f" 
