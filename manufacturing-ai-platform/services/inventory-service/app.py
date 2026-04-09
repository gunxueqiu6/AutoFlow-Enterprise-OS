from fastapi import FastAPI, HTTPException
import psycopg2
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
        
        # 创建库存表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventory (
            material_id VARCHAR(255) PRIMARY KEY,
            material_name VARCHAR(255) NOT NULL,
            available_quantity INTEGER DEFAULT 0,
            total_quantity INTEGER DEFAULT 0,
            unit_price DECIMAL(10, 2),
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # 插入一些测试数据
        cursor.execute('''
        INSERT INTO inventory (material_id, material_name, available_quantity, total_quantity, unit_price)
        VALUES 
        ('A001', '螺丝', 150, 200, 0.5),
        ('A002', '螺母', 100, 150, 0.3),
        ('A003', '垫片', 200, 250, 0.1),
        ('B001', '电机', 10, 15, 500.0),
        ('B002', '轴承', 50, 80, 20.0)
        ON CONFLICT (material_id) DO NOTHING
        ''')
        
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"初始化数据库失败: {str(e)}")

# 初始化数据库
init_db()

@app.get("/internal/inventory/{material_id}")
async def get_internal_inventory(material_id: str):
    """内部接口：获取完整的库存信息"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT material_id, material_name, available_quantity, total_quantity, unit_price, last_updated
        FROM inventory WHERE material_id = %s
        ''', (material_id,))
        
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not result:
            raise HTTPException(status_code=404, detail="物料不存在")
        
        return {
            "material_id": result[0],
            "material_name": result[1],
            "available_quantity": result[2],
            "total_quantity": result[3],
            "unit_price": float(result[4]),
            "last_updated": result[5]
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"获取库存失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取库存失败")

@app.get("/api/v1/inventory/{material_id}")
async def get_external_inventory(material_id: str):
    """外部接口：获取过滤和脱敏后的库存信息"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT material_id, available_quantity
        FROM inventory WHERE material_id = %s
        ''', (material_id,))
        
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not result:
            raise HTTPException(status_code=404, detail="物料不存在")
        
        return {
            "material_id": result[0],
            "available_quantity": result[1]
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"获取库存失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取库存失败")

@app.get("/")
async def root():
    """健康检查"""
    return {"message": "库存服务运行正常", "environment": ENVIRONMENT}

@app.get("/health")
async def health_check():
    """健康检查接口"""
    try:
        # 检查数据库连接
        conn = get_db_connection()
        conn.close()
        
        return {"status": "healthy", "service": "inventory-service"}
    except Exception as e:
        return {"status": "unhealthy", "service": "inventory-service", "error": str(e)}
