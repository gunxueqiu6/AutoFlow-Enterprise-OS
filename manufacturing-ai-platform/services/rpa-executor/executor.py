from fastapi import FastAPI, HTTPException
from playwright.sync_api import sync_playwright
import time
import os
from dotenv import load_dotenv

app = FastAPI()

# 加载环境变量
load_dotenv()

# 环境配置
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
DEBUG = os.getenv('DEBUG', 'true').lower() == 'true'

# 模拟RPA执行任务
def execute_task(task_type: str, request_id: str):
    """执行RPA任务"""
    try:
        # 这里应该根据任务类型执行不同的RPA操作
        # 暂时模拟执行过程
        print(f"开始执行RPA任务: {task_type}")
        print(f"采购申请ID: {request_id}")
        
        # 模拟浏览器操作
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=not DEBUG)
            page = browser.new_page()
            
            # 模拟访问ERP系统
            page.goto("https://example.com/erp")
            time.sleep(2)
            
            # 模拟登录（实际项目中应该使用环境变量或配置文件）
            page.fill("#username", "admin")
            page.fill("#password", "password")
            page.click("#login-button")
            time.sleep(2)
            
            # 模拟创建采购订单
            page.goto("https://example.com/erp/purchase-orders")
            time.sleep(1)
            page.click("#create-order-button")
            time.sleep(1)
            page.fill("#request-id", request_id)
            page.click("#submit-button")
            time.sleep(2)
            
            browser.close()
        
        print(f"RPA任务执行完成: {task_type}")
        return True
    except Exception as e:
        print(f"RPA任务执行失败: {str(e)}")
        return False

@app.post("/execute")
async def execute(task_type: str, request_id: str):
    """执行RPA任务"""
    try:
        if not task_type or not request_id:
            raise HTTPException(status_code=400, detail="参数无效")
        
        # 执行任务
        success = execute_task(task_type, request_id)
        
        if success:
            return {"status": "success", "message": "RPA任务执行成功"}
        else:
            raise HTTPException(status_code=500, detail="RPA任务执行失败")
    except HTTPException:
        raise
    except Exception as e:
        print(f"执行RPA任务失败: {str(e)}")
        raise HTTPException(status_code=500, detail="执行RPA任务失败")

@app.get("/")
async def root():
    """健康检查"""
    return {"message": "RPA执行器服务运行正常", "environment": ENVIRONMENT}

@app.get("/health")
async def health_check():
    """健康检查接口"""
    try:
        # 测试Playwright是否可用
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            browser.close()
        
        return {"status": "healthy", "service": "rpa-executor"}
    except Exception as e:
        return {"status": "unhealthy", "service": "rpa-executor", "error": str(e)}
