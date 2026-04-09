from fastapi import FastAPI, HTTPException
import psycopg2
import requests
import os
from dotenv import load_dotenv
from datetime import datetime

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

# RPA执行器地址
RPA_EXECUTOR_URL = os.getenv('RPA_EXECUTOR_URL', 'http://rpa-executor:8000/execute')

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
        
        # 创建采购申请表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS purchase_requests (
            request_id VARCHAR(255) PRIMARY KEY,
            material_id VARCHAR(255) NOT NULL,
            quantity INTEGER NOT NULL,
            purpose TEXT NOT NULL,
            employee_id VARCHAR(255) NOT NULL,
            status VARCHAR(50) DEFAULT 'submitted',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"初始化数据库失败: {str(e)}")

# 初始化数据库
init_db()

# 生成采购申请单号
def generate_request_id():
    """生成采购申请单号，格式：PR-日期-序号"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 获取今天的日期
        today = datetime.now().strftime('%Y%m%d')
        
        # 查询今天的最大序号
        cursor.execute('''
        SELECT MAX(request_id) FROM purchase_requests 
        WHERE request_id LIKE %s
        ''', (f'PR-{today}-%',))
        
        result = cursor.fetchone()
        if result[0]:
            # 提取序号并加1
            last_id = result[0]
            serial = int(last_id.split('-')[-1]) + 1
        else:
            serial = 1
        
        # 生成新的申请单号
        request_id = f'PR-{today}-{serial:03d}'
        
        cursor.close()
        conn.close()
        return request_id
    except Exception as e:
        print(f"生成申请单号失败: {str(e)}")
        # 生成一个基于时间戳的临时单号
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        return f'PR-{timestamp}'

# 调用RPA执行器
def call_rpa_executor(request_id):
    """调用RPA执行器创建正式单据"""
    try:
        payload = {
            "task_type": "create_purchase_order",
            "request_id": request_id
        }
        response = requests.post(RPA_EXECUTOR_URL, json=payload, timeout=60)
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"调用RPA执行器失败: {str(e)}")
        return False

@app.post("/api/v1/purchase-requests")
async def create_purchase_request(material_id: str, quantity: int, purpose: str, employee_id: str):
    """创建采购申请"""
    try:
        # 验证参数
        if not all([material_id, quantity > 0, purpose, employee_id]):
            raise HTTPException(status_code=400, detail="参数无效")
        
        # 生成申请单号
        request_id = generate_request_id()
        
        # 保存到数据库
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO purchase_requests (request_id, material_id, quantity, purpose, employee_id)
        VALUES (%s, %s, %s, %s, %s)
        ''', (request_id, material_id, quantity, purpose, employee_id))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        # 调用RPA执行器创建正式单据
        call_rpa_executor(request_id)
        
        return {"request_id": request_id, "status": "submitted"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"创建采购申请失败: {str(e)}")
        raise HTTPException(status_code=500, detail="创建采购申请失败")

@app.get("/api/v1/purchase-requests/{request_id}")
async def get_purchase_request(request_id: str):
    """获取采购申请详情"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT request_id, material_id, quantity, purpose, employee_id, status, created_at
        FROM purchase_requests WHERE request_id = %s
        ''', (request_id,))
        
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not result:
            raise HTTPException(status_code=404, detail="采购申请不存在")
        
        return {
            "request_id": result[0],
            "material_id": result[1],
            "quantity": result[2],
            "purpose": result[3],
            "employee_id": result[4],
            "status": result[5],
            "created_at": result[6]
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"获取采购申请失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取采购申请失败")

@app.get("/")
async def root():
    """健康检查"""
    return {"message": "采购服务运行正常", "environment": ENVIRONMENT}

@app.get("/health")
async def health_check():
    """健康检查接口"""
    try:
        # 检查数据库连接
        conn = get_db_connection()
        conn.close()
        
        return {"status": "healthy", "service": "procurement-service"}
    except Exception as e:
        return {"status": "unhealthy", "service": "procurement-service", "error": str(e)}
