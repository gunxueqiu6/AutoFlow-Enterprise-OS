from fastapi import FastAPI, Request
import redis
import psycopg2
import requests
import json
import os
from dotenv import load_dotenv

app = FastAPI()

# 加载环境变量
load_dotenv()

# 环境配置
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
DEBUG = os.getenv('DEBUG', 'true').lower() == 'true'

# 数据库连接
DB_HOST = os.getenv('DB_HOST', 'postgres')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_USER = os.getenv('POSTGRES_USER', 'ai_platform')
DB_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'secure_password_123!')
DB_NAME = os.getenv('POSTGRES_DB', 'manufacturing_ai')

# Redis连接
REDIS_HOST = os.getenv('REDIS_HOST', 'redis')
REDIS_PORT = os.getenv('REDIS_PORT', '6379')
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', '')

# 服务地址
PROCUREMENT_SERVICE_URL = os.getenv('PROCUREMENT_SERVICE_URL', 'http://procurement-service:8000/api/v1/purchase-requests')
INVENTORY_SERVICE_URL = os.getenv('INVENTORY_SERVICE_URL', 'http://inventory-service:8000/internal/inventory')

# 初始化Redis
redis_client = redis.Redis(
    host=REDIS_HOST, 
    port=REDIS_PORT, 
    db=0,
    password=REDIS_PASSWORD
)

# 初始化数据库连接
def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )

# 初始化数据库表
def init_db():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 创建会话表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            session_id VARCHAR(255) PRIMARY KEY,
            employee_id VARCHAR(255) NOT NULL,
            context TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # 创建采购申请草稿表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS purchase_drafts (
            draft_id SERIAL PRIMARY KEY,
            session_id VARCHAR(255) REFERENCES sessions(session_id),
            material_id VARCHAR(255),
            quantity INTEGER,
            purpose TEXT,
            employee_id VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"初始化数据库失败: {str(e)}")

# 初始化数据库
init_db()

# 工具函数：创建采购申请
def create_purchase_request(material_id: str, quantity: int, purpose: str, employee_id: str) -> str:
    """调用采购服务创建采购申请"""
    try:
        payload = {
            "material_id": material_id,
            "quantity": quantity,
            "purpose": purpose,
            "employee_id": employee_id
        }
        response = requests.post(PROCUREMENT_SERVICE_URL, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        return result.get("request_id", "")
    except Exception as e:
        print(f"创建采购申请失败: {str(e)}")
        return ""

# 工具函数：查询库存
def query_inventory(material_id: str) -> dict:
    """调用库存服务查询库存"""
    try:
        response = requests.get(f"{INVENTORY_SERVICE_URL}/{material_id}", timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"查询库存失败: {str(e)}")
        return {"available_quantity": 0}

# 处理用户消息
def process_message(employee_id: str, content: str, source: str):
    """处理用户消息并生成回复"""
    # 简单的意图识别
    content = content.lower()
    
    if "采购" in content or "申请" in content:
        # 处理采购申请
        return "请提供物料ID、数量和用途，我将帮您创建采购申请。"
    elif "库存" in content or "查询" in content:
        # 处理库存查询
        return "请提供物料ID，我将帮您查询库存情况。"
    else:
        return "您好！我是制造业AI协同平台的助手，请问有什么可以帮助您的？"

@app.post("/dispatch")
async def dispatch_message(request: Request):
    """接收并处理来自统一AI网关的消息"""
    try:
        data = await request.json()
        employee_id = data.get("employee_id")
        content = data.get("content")
        source = data.get("source")
        
        if not all([employee_id, content, source]):
            return {"error": "缺少必要参数"}
        
        # 处理消息
        response = process_message(employee_id, content, source)
        
        # 这里应该有发送回复的逻辑
        # 暂时只返回处理结果
        return {"response": response}
    except Exception as e:
        print(f"处理消息失败: {str(e)}")
        return {"error": "处理消息失败"}

@app.get("/")
async def root():
    """健康检查"""
    return {"message": "AI Agent调度中心服务运行正常", "environment": ENVIRONMENT}

@app.get("/health")
async def health_check():
    """健康检查接口"""
    try:
        # 检查数据库连接
        conn = get_db_connection()
        conn.close()
        
        # 检查Redis连接
        redis_client.ping()
        
        return {"status": "healthy", "service": "agent-dispatcher"}
    except Exception as e:
        return {"status": "unhealthy", "service": "agent-dispatcher", "error": str(e)}
