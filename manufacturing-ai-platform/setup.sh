#!/bin/bash
# 制造业AI协同平台 - 一键初始化脚本

echo "🚀 开始初始化制造业AI协同平台..."

# 1. 创建必要的目录
mkdir -p models
mkdir -p data/postgres-data data/qdrant-data

# 2. 下载Whisper模型 (英文base模型作为示例)
if [ ! -f "models/ggml-base.en.bin" ]; then
    echo "📥 正在下载Whisper模型..."
    docker run --rm -v $(pwd)/models:/models ghcr.io/ggerganov/whisper.cpp:main \
        ./models/download-ggml-model.sh base.en /models
fi

# 3. 构建并启动所有服务
echo "🐳 正在构建并启动Docker服务..."
docker-compose up -d --build

# 4. 等待服务启动
echo "⏳ 等待服务启动中..."
sleep 30

# 5. 输出访问信息
echo ""
echo "✅ 平台已成功启动!"
echo "   - 统一AI网关: http://localhost:8000"
echo "   - Qdrant控制台: http://localhost:6333/dashboard"
echo "   - PaddleOCR服务: http://localhost:8081"
echo "   - Whisper服务: http://localhost:8082"
echo ""
echo "💡 接下来，请开始开发各个服务的具体业务逻辑代码。"