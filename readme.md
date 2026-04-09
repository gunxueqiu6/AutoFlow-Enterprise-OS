# 声明：本项目代码仅供技术展示，未经作者授权禁止用于任何商业或非商业用途，如需授权请通过GitHub lssues联系


# 制造业AI协同平台

基于AI原生的制造业数字化转型解决方案，提供智能采购、库存管理、RPA自动化等核心业务功能，助力企业实现降本增效。

## 项目概述

制造业AI协同平台是一个基于微服务架构的智能系统，通过AI技术和自动化手段，解决制造业数字化转型中的核心痛点：

- **智能采购**：通过AI Agent理解用户意图，自动创建采购申请并对接ERP系统
- **实时库存**：提供内部和外部库存查询接口，支持供应链协同
- **RPA自动化**：通过Playwright实现UI自动化，减少人工操作
- **多渠道接入**：支持企业微信等IM平台，实现便捷的消息交互
- **数据驱动**：集成监控系统，提供数据可视化和决策支持

## 技术架构

### 系统架构图

```plaintext
graph LR
    subgraph "交互层"
        A[企业微信] --> F
        B[钉钉] --> F
        C[飞书] --> F
        D[Web上传] --> F
        E[IMAP邮箱] --> F
    end

    subgraph "AI核心层"
        F[统一AI网关<br/>(FastAPI)] --> G[AI Agent调度中心<br/>(LangChain/LangGraph)]
        G --> H
        G --> I[OCR服务 PaddleOCR]
        G --> J[ASR服务 Whisper.cpp]
        G --> K[RPA/UI自动化执行器<br/>(Playwright)]
    end

    subgraph "业务服务层"
        K --> L
        G --> M[采购服务<br/>(FastAPI)]
        G --> N[库存服务<br/>(FastAPI)]
        G --> O[生产服务<br/>(FastAPI)]
        G --> P[自动化价值计量服务<br/>(FastAPI)]
    end

    subgraph "数据与支撑层"
        M & N & O & P --> Q
        M & N & O & P --> R
        S[安全API网关<br/>(FastAPI)] --> N
        T[Grafana] --> P
    end

    subgraph "外部协同"
        U[供应链合作伙伴] --> S
    end

    classDef gateway fill:#4CAF50,stroke:#388E3C;
    classDef ai fill:#2196F3,stroke:#0D47A1;
    classDef service fill:#FF9800,stroke:#E65100;
    classDef data fill:#9C27B0,stroke:#4A148C;
    class F,S gateway;
    class G,H,I,J,K ai;
    class M,N,O,P service;
    class Q,R,T,U data;
```

## 核心功能

### 1. 统一AI网关
- **多渠道接入**：支持企业微信、钉钉、飞书等IM平台
- **消息处理**：统一消息格式，进行协议转换和安全验证
- **Webhook管理**：处理外部系统的webhook请求
- **HTTPS支持**：配置SSL证书，确保通信安全

### 2. AI Agent调度中心
- **意图识别**：理解用户自然语言意图
- **对话管理**：基于LangGraph的有状态对话管理
- **工具调用**：集成采购、库存等业务工具
- **AI能力集成**：对接OCR、ASR等AI服务
- **会话存储**：将对话状态存储到Redis和PostgreSQL

### 3. 采购服务
- **采购申请**：创建和管理采购申请单
- **单号生成**：自动生成规范化的采购申请单号
- **ERP对接**：通过RPA执行器对接ERP系统
- **状态跟踪**：实时跟踪采购申请状态

### 4. 库存服务
- **内部接口**：提供完整的库存信息查询
- **外部接口**：提供脱敏的库存信息给供应商
- **数据管理**：库存数据的增删改查
- **实时同步**：确保库存数据的准确性

### 5. RPA执行器
- **UI自动化**：基于Playwright的浏览器自动化
- **任务调度**：执行采购订单创建等重复性任务
- **错误处理**：自动处理执行过程中的异常
- **执行日志**：记录执行过程和结果

### 6. 监控系统
- **Prometheus**：收集服务指标和监控数据
- **Grafana**：可视化监控面板
- **健康检查**：实时监控服务状态
- **告警机制**：异常情况自动告警

## 技术栈

| 类别 | 技术 | 版本 | 用途 |
|------|------|------|------|
| 后端框架 | FastAPI | 0.104.1 | 微服务开发 |
| 数据库 | PostgreSQL | 15 | 数据存储 |
| 向量数据库 | Qdrant | 1.11.4 | 向量存储和检索 |
| 缓存 | Redis | 7.0 | 会话存储和缓存 |
| AI能力 | PaddleOCR | latest | 光学字符识别 |
| AI能力 | Whisper.cpp | main | 语音识别 |
| RPA | Playwright | latest | UI自动化 |
| 容器化 | Docker | 20.10+ | 容器运行环境 |
| 容器编排 | Docker Compose | 1.29+ | 服务编排 |
| 监控 | Prometheus | latest | 指标收集 |
| 监控 | Grafana | latest | 数据可视化 |
| CI/CD | GitHub Actions | - | 自动化构建部署 |

## 项目结构

```
manufacturing-ai-platform/
├── docker-compose.yml          # 开发环境编排文件
├── docker-compose.prod.yml     # 生产环境编排文件
├── .env                        # 开发环境变量
├── .env.production             # 生产环境变量
├── setup.sh                    # 一键初始化脚本
├── prometheus.yml              # Prometheus配置
├── services/
│   ├── gateway/                # 统一AI网关
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── app.py
│   ├── agent-dispatcher/       # AI Agent调度中心
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── app.py
│   ├── procurement-service/    # 采购服务
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── app.py
│   │   └── test_app.py
│   ├── inventory-service/      # 库存服务
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── app.py
│   │   └── test_app.py
│   └── rpa-executor/           # RPA/UI自动化执行器
│       ├── Dockerfile
│       ├── requirements.txt
│       └── executor.py
├── data/
│   ├── postgres-data/          # PostgreSQL数据卷
│   └── qdrant-data/            # Qdrant数据卷
└── .github/
    └── workflows/
        └── ci-cd.yml           # CI/CD配置
```

## 快速开始

### 1. 环境准备

- Docker 19.03+ 
- Docker Compose 1.25+ 
- Git

### 2. 克隆项目

```bash
git clone <repository-url>
cd manufacturing-ai-platform
```

### 3. 开发环境部署

```bash
# 运行初始化脚本
./setup.sh

# 或手动启动
docker-compose up -d --build
```

### 4. 生产环境部署

```bash
# 复制生产环境配置
cp .env.production .env

# 修改配置文件中的敏感信息
# vim .env

# 启动生产环境
docker-compose -f docker-compose.prod.yml up -d --build
```

## 服务访问

| 服务 | 地址 | 说明 |
|------|------|------|
| 统一AI网关 | http://localhost:8000 | 主服务入口 |
| AI Agent调度中心 | http://localhost:8001 | Agent服务 |
| 采购服务 | http://localhost:8002 | 采购API |
| 库存服务 | http://localhost:8003 | 库存API |
| RPA执行器 | http://localhost:8004 | RPA服务 |
| Qdrant控制台 | http://localhost:6333/dashboard | 向量数据库管理 |
| PaddleOCR服务 | http://localhost:8081 | OCR服务 |
| Whisper服务 | http://localhost:8082 | 语音识别服务 |
| Prometheus | http://localhost:9090 | 监控指标 |
| Grafana | http://localhost:3000 | 监控面板 |

## API文档

每个服务都提供了自动生成的API文档：

- 统一AI网关：http://localhost:8000/docs
- 采购服务：http://localhost:8002/docs
- 库存服务：http://localhost:8003/docs
- RPA执行器：http://localhost:8004/docs

## 部署指南

### 开发环境

1. **环境准备**：安装Docker和Docker Compose
2. **配置修改**：根据需要修改`.env`文件中的配置
3. **启动服务**：运行`docker-compose up -d --build`
4. **开发测试**：使用`uvicorn app:app --reload`启动开发服务器

### 生产环境

1. **服务器准备**：
   - 推荐使用Ubuntu 20.04+或CentOS 7+
   - 至少4GB内存，2核CPU
   - 开放必要的端口（80, 443, 6333等）

2. **SSL证书配置**：
   - 获取SSL证书（推荐使用Let's Encrypt）
   - 将证书文件放置在`certs`目录
   - 配置`.env`文件中的证书路径

3. **环境配置**：
   - 修改`.env.production`文件，设置强密码和密钥
   - 配置数据库连接和服务地址

4. **启动服务**：
   ```bash
   docker-compose -f docker-compose.prod.yml up -d --build
   ```

5. **监控配置**：
   - 访问Grafana：http://服务器IP:3000
   - 登录用户名：admin，密码：在`.env`中配置
   - 导入Prometheus数据源，配置监控面板

### CI/CD部署

1. **GitHub配置**：
   - 在GitHub仓库中设置以下secrets：
     - `DOCKER_HUB_USERNAME`：Docker Hub用户名
     - `DOCKER_HUB_TOKEN`：Docker Hub访问令牌
     - `SERVER_HOST`：服务器IP地址
     - `SERVER_USER`：服务器用户名
     - `SERVER_PASSWORD`：服务器密码
     - `SERVER_PORT`：SSH端口

2. **自动部署**：
   - 推送代码到`main`或`master`分支
   - GitHub Actions会自动构建镜像并部署到服务器

## 安全配置

1. **环境变量**：
   - 使用强密码和密钥
   - 避免在代码中硬编码敏感信息
   - 定期更新密码和密钥

2. **网络安全**：
   - 配置防火墙，只开放必要的端口
   - 使用HTTPS加密通信
   - 配置网络隔离，限制服务间访问

3. **认证授权**：
   - 为外部接口配置OAuth2认证
   - 实现基于角色的访问控制
   - 定期审计API访问日志

## 测试指南

### 单元测试

```bash
# 进入服务目录
cd services/procurement-service

# 安装依赖
pip install -r requirements.txt

# 运行测试
pytest test_app.py -v
```

### API测试

```bash
# 测试库存服务
curl http://localhost:8003/api/v1/inventory/A001

# 测试采购服务
curl -X POST "http://localhost:8002/api/v1/purchase-requests?material_id=A001&quantity=10&purpose=设备维修&employee_id=U123"

# 测试健康检查
curl http://localhost:8000/health
```

### 性能测试

使用Apache Bench或JMeter进行性能测试：

```bash
# 安装Apache Bench
sudo apt install apache2-utils

# 测试API性能
ab -n 1000 -c 100 http://localhost:8003/api/v1/inventory/A001
```

## 维护指南

### 日志管理

```bash
# 查看服务日志
docker logs -f gateway

# 查看所有服务日志
docker-compose logs -f
```

### 数据备份

```bash
# 备份PostgreSQL数据
docker exec -t postgres pg_dump -U ai_platform manufacturing_ai > backup.sql

# 恢复数据
docker exec -i postgres psql -U ai_platform manufacturing_ai < backup.sql
```

### 服务更新

```bash
# 拉取最新代码
git pull

# 重新构建并启动
docker-compose up -d --build
```

### 常见问题

1. **服务启动失败**：
   - 检查Docker服务是否运行
   - 查看服务日志，分析错误原因
   - 确保端口未被占用

2. **数据库连接失败**：
   - 检查PostgreSQL服务是否正常运行
   - 验证数据库连接参数是否正确
   - 检查网络连接是否正常

3. **RPA执行失败**：
   - 检查Playwright是否正确安装
   - 验证目标系统是否可访问
   - 查看RPA执行日志

## 许可证

本项目基于MIT许可证开源。

## 贡献指南

1. Fork本仓库
2. 创建功能分支
3. 提交代码
4. 发起Pull Request

## 联系方式

- 项目维护者：[滚雪球@gunxueqiu6]
- 邮箱：[lichengfei7@gmail.com]
- 问题反馈：在GitHub Issues中提交

---

**制造业AI协同平台** - 让制造更智能，让管理更高效！