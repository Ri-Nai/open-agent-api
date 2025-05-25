# Docker 部署指南

这个文档说明如何使用 Docker 部署 Agent API 服务。

## 快速开始

### 1. 准备配置文件

复制环境变量示例文件：
```bash
cp env.example .env
```

编辑 `.env` 文件，填入您的真实配置：
```bash
# 必需配置
AGENT_APP_ID=your_real_app_id
AGENT_API_KEY=your_real_api_key

# 可选配置
SERVER_PORT=8000
LOG_LEVEL=INFO
```

### 2. 使用 Docker Compose（推荐）

```bash
# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 3. 使用 Docker 命令

```bash
# 构建镜像
docker build -t agent-api .

# 运行容器
docker run -d \
  --name agent-api \
  -p 8000:8000 \
  --env-file .env \
  agent-api

# 查看日志
docker logs -f agent-api

# 停止容器
docker stop agent-api
docker rm agent-api
```

## 配置方式

### 方式一：环境变量（推荐）

在 `.env` 文件中设置：
```bash
AGENT_APP_ID=your_app_id
AGENT_API_KEY=your_api_key
SERVER_PORT=8000
```

### 方式二：配置文件

创建 `config.local.yaml` 文件：
```yaml
agent:
  app_id: "your_app_id"
  api_key: "your_api_key"
server:
  port: 8000
```

然后挂载到容器：
```bash
docker run -d \
  --name agent-api \
  -p 8000:8000 \
  -v ./config.local.yaml:/app/config.local.yaml:ro \
  agent-api
```

## 健康检查

容器包含内置的健康检查：
```bash
# 检查容器健康状态
docker ps

# 手动健康检查
curl http://localhost:8000/health
```

## 日志管理

```bash
# 查看实时日志
docker-compose logs -f agent-api

# 查看最近的日志
docker-compose logs --tail=100 agent-api

# 查看特定时间的日志
docker-compose logs --since="2024-01-01T00:00:00" agent-api
```

## 故障排除

### 1. 容器无法启动

检查配置：
```bash
# 查看容器日志
docker-compose logs agent-api

# 检查环境变量
docker-compose exec agent-api env | grep AGENT
```

### 2. 端口冲突

修改 `docker-compose.yml` 中的端口映射：
```yaml
ports:
  - "8001:8000"  # 使用 8001 端口
```

### 3. 配置问题

验证配置文件：
```bash
# 进入容器检查配置
docker-compose exec agent-api cat config.yaml

# 检查挂载的配置文件
docker-compose exec agent-api cat config.local.yaml
```

## 生产部署建议

### 1. 使用外部配置

```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  agent-api:
    image: agent-api:latest
    ports:
      - "8000:8000"
    environment:
      - AGENT_APP_ID=${AGENT_APP_ID}
      - AGENT_API_KEY=${AGENT_API_KEY}
      - LOG_LEVEL=WARNING
    restart: always
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '0.5'
```

### 2. 使用反向代理

配合 Nginx 使用：
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 3. 数据持久化

如果需要持久化日志：
```yaml
volumes:
  - ./logs:/app/logs
```

## 镜像信息

- **基础镜像**: python:3.11-slim
- **工作目录**: /app
- **暴露端口**: 8000
- **运行用户**: appuser (非 root)
- **健康检查**: 每 30 秒检查 /health 端点

## 安全注意事项

1. **不要在镜像中包含敏感信息**
2. **使用环境变量或挂载的配置文件**
3. **定期更新基础镜像**
4. **使用非 root 用户运行**
5. **限制容器资源使用**

## 更新部署

```bash
# 拉取最新代码
git pull

# 重新构建并启动
docker-compose up -d --build

# 或者分步执行
docker-compose build
docker-compose up -d
``` 
