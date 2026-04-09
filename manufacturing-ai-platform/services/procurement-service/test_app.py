import pytest
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

# 测试健康检查接口
def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert response.json()["service"] == "procurement-service"

# 测试根路径
def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "采购服务运行正常" in response.json()["message"]

# 测试创建采购申请
def test_create_purchase_request():
    response = client.post("/api/v1/purchase-requests", params={
        "material_id": "A001",
        "quantity": 10,
        "purpose": "测试采购",
        "employee_id": "U123"
    })
    assert response.status_code == 200
    assert "request_id" in response.json()
    assert response.json()["status"] == "submitted"

# 测试获取采购申请
def test_get_purchase_request():
    # 先创建一个采购申请
    create_response = client.post("/api/v1/purchase-requests", params={
        "material_id": "A001",
        "quantity": 5,
        "purpose": "测试查询",
        "employee_id": "U123"
    })
    request_id = create_response.json()["request_id"]
    
    # 然后查询该申请
    get_response = client.get(f"/api/v1/purchase-requests/{request_id}")
    assert get_response.status_code == 200
    assert get_response.json()["request_id"] == request_id
    assert get_response.json()["material_id"] == "A001"

# 测试无效参数
def test_invalid_parameters():
    response = client.post("/api/v1/purchase-requests", params={
        "material_id": "",
        "quantity": -1,
        "purpose": "",
        "employee_id": ""
    })
    assert response.status_code == 400
    assert "参数无效" in response.json()["detail"]