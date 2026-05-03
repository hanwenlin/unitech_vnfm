# L-VNFM (Lightweight Enterprise VNFM) 系统设计方案

## 1. 项目简介
L-VNFM 是一款借鉴 OpenStack Tacker 架构思想，基于 **FastAPI** 和 **TOSCA** 标准构建的轻量化网络功能虚拟化管理器（VNFM）。它通过异步任务编排和插件化驱动，实现了 VNF 从模板解析到云原生/虚拟化资源落地的全生命周期管理，旨在提供一个高性能、易扩展的电信级编排引擎。

## 2. 核心技术栈
- **后端**: FastAPI (基于 Python 3.10+ ASGI 架构)
- **解析引擎**: `tosca-parser` (解析标准 YAML 格式的 VNFD)
- **异步框架**: Asyncio + `aio-pika` (RabbitMQ 异步驱动)
- **插件系统**: `Pluggy` (支持驱动热插拔与钩子扩展)
- **持久化层**: PostgreSQL + `SQLModel` (异步 ORM，兼顾 Pydantic 模型验证)
- **前端**: Vue 3
- - **中间件**: RabbitMQ, PostgreSQL (可选)

---

## 3. 系统架构 (System Architecture)

系统采用“前台异步受理、中间消息削峰、后台分布式执行”的解耦架构。

### 3.1 后端三层模型
1. **API Server (Northbound)**: 
   - 职责：REST 接口暴露、JWT 鉴权、基于 `tosca-parser` 校验 VNFD、任务入队。
   - 特点：利用 FastAPI 异步特性实现秒级响应，即便底层部署任务耗时较长。
2. **Message Broker (RabbitMQ)**:
   - 职责：任务持久化（Task Persistence）、流量削峰、支撑 Worker 横向扩展。
3. **Conductor Worker (Execution Engine)**:
   - 职责：监听任务队列、维护 **FSM (有限状态机)**、调用 VIM 插件执行底层操作，完成VNFM生命周期。
   - 特点：无状态设计，支持多实例部署以应对大规模并发。

### 3.2 插件化设计 (Pluggy-based)
通过 `Pluggy` 模拟 Tacker 的 Driver 机制，实现对异构基础设施的兼容：
- **`VimDriverSpec`**: 定义标准生命周期 Hook 接口。
- **核心方法**: `create`, `instantiate`, `scale_in`, `scale_out`, `update_image`, `update`, `terminate`, `delete`, `status`。

---

## 4. 数据库模型 (Data Model & Objects)

借鉴 Tacker 设计，建立精细化的资源跟踪映射，支持授权记录与全生命周期审计。

### 4.1 核心实体表
* **VnfPackage / VNFD**: 存储 TOSCA 模板及解析后的节点映射、策略（如 Scaling 阈值）。
* **VnfInstance**: 记录 VNF 实例基础信息、`instantiation_state` 及当前的 `task_state`（如 `SPAWNING`）。
* **VnfResource**: **核心关联表**。记录逻辑节点（VDU）与物理资源（K8s Pod UUID / VM ID）的 **1:1 映射**。
* **VimAuth**: 存储加密后的 VIM 接入凭证（支持多租户隔离）。
* **LifecycleEvent**: 记录所有 LCM 操作的授权人、参数、时间戳及详细执行结果。
* 可能还有其它数据库表，参考tacker以及能完成vnfm完整功能添加数据库表

---

## 5. 前端设计方案 (Frontend Design)

### 5.1 核心页面
- **Dashboard**: 资源统计看板，展示 VNF 运行分布图及 VIM 健康状态。
- **Instance List**: VNF 实例管理列表。
  - **状态呼吸灯**：实现 `ACTIVE` (绿), `ERROR` (红), `PROCESSING` (蓝), `PENDING` (黄) 状态显示。
- **Topology View**: 渲染 VNF 内部 VDU、CP 与虚拟网络的逻辑拓扑。

### 5.2 异步状态更新机制
- **双向绑定**: 前端通过 **WebSocket** 监听后端状态变更推送。
- **即时反馈**: 用户提交操作后，前端立即展示“指令下发成功”，UI 自动进入加载状态，等待后台异步回调更新。

---

## 6. 核心代码结构参考

### 后端目录结构 (`vnfm/`)
```text
vnfm/
├── api/                # FastAPI 路由与中间件
│   ├── routes/         # 资源路由 (vnf_lcm, catalog)
│   ├── auth/           # 凭证加解密与 JWT
│   └── middleware/     # 租户隔离与审计中间件
├── parser/             # TOSCA 解析封装与校验逻辑
├── conductor/          # Worker 逻辑与状态机
│   ├── manager.py      # 消息监听与分发
│   └── fsm.py          # 异步状态机定义
├── drivers/            # 基于 Pluggy 的驱动插件
│   ├── specs.py        # 驱动钩子规范 (HookSpec)
│   ├── k8s/            # K8s 驱动插件实现
│   └── openstack/      # OpenStack 驱动插件实现
├── db/                 # SQLModel 数据库实体与迁移
└── common/             # 异步工具类、Schema 定义

### 前端目录结构 (`vnfm-ui/`)
vnfm-ui/
├── src/
│   ├── api/            # Axios 接口封装与 WebSocket 配置
│   ├── store/          # Pinia 状态管理
│   ├── views/          # 视图组件 (Instance, Package)
│   └── components/     # 拓扑图组件、状态指示灯
└── vite.config.ts