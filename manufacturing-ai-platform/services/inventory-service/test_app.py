import pytest
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

# 测试健康检查接口
def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert response.json()["service"] == "inventory-service"

# 测试根路径
def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "库存服务运行正常" in response.json()["message"]

# 测试内部库存查询
def test_internal_inventory():
    response = client.get("/internal/inventory/A001")
    assert response.status_code == 200
    assert response.json()["material_id"] == "A001"
    assert "available_quantity" in response.json()
    assert "total_quantity" in response.json()
    assert "unit_price" in response.json()

# 测试外部库存查询
def test_external_inventory():
    response = client.get("/api/v1/inventory/A001")
    assert response.status_code == 200
    assert response.json()["material_id"] == "A001"
    assert "available_quantity" in response.json()
    assert "unit_price" not in response.json()  # 外部接口不返回价格信息

# 测试不存在的物料
def test_nonexistent_material():
    response = client.get("/internal/inventory/NONEXISTENT")
    assert response.status_code == 404
    assert "物料不存在" in response.json()["detail"]

    response = client.get("/api/v1/inventory/NONEXISTENT")
    assert response.status_code == 404
    assert "物料不存在" in response.json()["detail"]