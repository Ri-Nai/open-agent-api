#!/bin/bash

# Agent API 部署脚本

set -e

echo "🚀 开始部署 Agent API..."

# 检查配置文件
if [ ! -f ".env" ]; then
    echo "❌ 未找到 .env 文件，请先运行 ./scripts/build.sh"
    exit 1
fi

# 检查必需的环境变量
source .env
if [ -z "$AGENT_APP_ID" ] || [ -z "$AGENT_API_KEY" ]; then
    echo "❌ 请在 .env 文件中设置 AGENT_APP_ID 和 AGENT_API_KEY"
    exit 1
fi

# 停止现有服务
echo "🛑 停止现有服务..."
docker-compose down

# 启动服务
echo "🚀 启动服务..."
docker-compose up -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 10

# 检查服务状态
echo "🔍 检查服务状态..."
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ 服务启动成功！"
    echo ""
    echo "🌐 服务地址: http://localhost:8000"
    echo "📚 API 文档: http://localhost:8000/docs"
    echo "🔍 健康检查: http://localhost:8000/health"
    echo ""
    echo "📊 查看状态: docker-compose ps"
    echo "📝 查看日志: docker-compose logs -f"
else
    echo "❌ 服务启动失败，请检查日志："
    echo "   docker-compose logs"
    exit 1
fi 
