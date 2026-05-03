# L-VNFM (Lightweight Enterprise VNFM)

基于 FastAPI 和 TOSCA 标准构建的轻量化网络功能虚拟化管理器（VNFM）。

## 快速开始

### 1. 环境准备

```bash
# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 启动基础设施

```bash
docker-compose up -d postgres rabbitmq redis
```

### 3. 启动后端服务

```bash
# API Server
uvicorn vnfm.main:app --reload --port 8000

# Worker (单独终端)
python -m vnfm.conductor.worker
```

### 4. 启动前端

```bash
cd vnfm-ui
npm install
npm run dev
```

### 5. 访问

- API 文档: http://localhost:8000/docs
- 前端: http://localhost:3000
- RabbitMQ 管理: http://localhost:15672

## 项目结构

```
vnfm/
  api/          # FastAPI 路由与中间件
  parser/       # TOSCA 解析封装
  conductor/    # Worker 与状态机
  drivers/      # 基于 Pluggy 的驱动插件
  db/           # SQLModel 数据库模型
  common/       # 工具类与配置
vnfm-ui/
  src/
    api/        # Axios 与 WebSocket
    store/      # Pinia 状态管理
    views/      # 页面视图
    components/ # 公共组件
```

## 默认账号

- `admin` / `admin`
- `user` / `user`

## 核心功能

- VNF 包管理（TOSCA 模板解析与校验）
- VNF 生命周期管理（实例化、扩缩容、终止、删除）
- 插件化 VIM 驱动（K8s / OpenStack）
- 异步任务编排（RabbitMQ + Worker）
- 状态机驱动的生命周期控制
- WebSocket 实时状态推送
- 拓扑可视化
