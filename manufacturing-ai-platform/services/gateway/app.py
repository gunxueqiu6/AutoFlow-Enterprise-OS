from fastapi import FastAPI, Request, HTTPException
import requests
import xml.etree.ElementTree as ET
from Crypto.Cipher import AES
import base64
import hashlib
import time
import json
import os
from dotenv import load_dotenv

app = FastAPI()

# 加载环境变量
load_dotenv()

# 企业微信配置
CORP_ID = os.getenv('WECHAT_CORP_ID', 'your_corp_id')
ENCODING_AES_KEY = os.getenv('WECHAT_ENCODING_AES_KEY', 'your_encoding_aes_key')

# AI Agent调度中心地址
AGENT_DISPATCHER_URL = os.getenv('AGENT_DISPATCHER_URL', 'http://agent-dispatcher:8000/dispatch')

# 环境配置
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
DEBUG = os.getenv('DEBUG', 'true').lower() == 'true'

# 日志配置
LOG_LEVEL = os.getenv('LOG_LEVEL', 'info')

# 解密企业微信消息
def decrypt_msg(encrypted_msg, encoding_aes_key):
    """解密企业微信消息"""
    try:
        key = base64.b64decode(encoding_aes_key + '=')
        cipher = AES.new(key, AES.MODE_CBC, key[:16])
        decrypted = cipher.decrypt(base64.b64decode(encrypted_msg))
        padding = ord(decrypted[-1:])
        decrypted = decrypted[:-padding]
        xml_content = decrypted[20:]
        return xml_content.decode('utf-8')
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"解密失败: {str(e)}")

# 验证企业微信签名
def verify_signature(msg_signature, timestamp, nonce, echostr):
    """验证企业微信签名"""
    try:
        items = [ENCODING_AES_KEY, timestamp, nonce, echostr]
        items.sort()
        signature = hashlib.sha1(''.join(items).encode('utf-8')).hexdigest()
        return signature == msg_signature
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"签名验证失败: {str(e)}")

@app.post("/webhook/wechat")
async def wechat_webhook(request: Request):
    """处理企业微信webhook请求"""
    try:
        # 获取请求参数
        params = dict(request.query_params)
        msg_signature = params.get('msg_signature')
        timestamp = params.get('timestamp')
        nonce = params.get('nonce')
        
        # 获取请求体
        body = await request.body()
        xml_data = body.decode('utf-8')
        
        # 解析XML
        root = ET.fromstring(xml_data)
        encrypted_msg = root.find('.//Encrypt').text
        
        # 验证签名
        if not verify_signature(msg_signature, timestamp, nonce, encrypted_msg):
            raise HTTPException(status_code=401, detail="签名验证失败")
        
        # 解密消息
        decrypted_xml = decrypt_msg(encrypted_msg, ENCODING_AES_KEY)
        
        # 解析解密后的XML
        decrypted_root = ET.fromstring(decrypted_xml)
        msg_type = decrypted_root.find('.//MsgType').text
        
        if msg_type == 'text':
            content = decrypted_root.find('.//Content').text
            from_user = decrypted_root.find('.//FromUserName').text
            
            # 构建标准化消息
            standard_msg = {
                "employee_id": from_user,
                "content": content,
                "source": "wechat"
            }
            
            # 转发到AI Agent调度中心
            response = requests.post(AGENT_DISPATCHER_URL, json=standard_msg, timeout=30)
            response.raise_for_status()
        
        return "success"
    except HTTPException:
        raise
    except Exception as e:
        print(f"处理微信消息失败: {str(e)}")
        raise HTTPException(status_code=500, detail="处理消息失败")

@app.get("/")
async def root():
    """健康检查"""
    return {"message": "统一AI网关服务运行正常", "environment": ENVIRONMENT}

@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {"status": "healthy", "service": "gateway"}