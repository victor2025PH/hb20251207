#!/bin/bash
# 测试后端 API 端点

echo "=========================================="
echo "  测试后端 API 端点"
echo "=========================================="
echo

BASE_URL="http://127.0.0.1:8080/api/v1/admin"

# 测试健康检查
echo "1. 测试健康检查端点..."
curl -s "$BASE_URL/health" | head -3
echo
echo

# 测试红包列表端点（需要认证，这里只测试端点是否存在）
echo "2. 测试红包列表端点（需要认证）..."
response=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/redpackets/")
if [ "$response" = "401" ] || [ "$response" = "200" ]; then
    echo "✅ 端点存在 (HTTP $response)"
else
    echo "❌ 端点可能不存在 (HTTP $response)"
fi
echo

# 测试邀请配置端点
echo "3. 测试邀请配置端点（需要认证）..."
response=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/invite/config")
if [ "$response" = "401" ] || [ "$response" = "200" ]; then
    echo "✅ 端点存在 (HTTP $response)"
else
    echo "❌ 端点可能不存在 (HTTP $response)"
fi
echo

# 测试红包雨调度端点
echo "4. 测试红包雨调度端点（需要认证）..."
response=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$BASE_URL/redpackets/schedule-rain")
if [ "$response" = "401" ] || [ "$response" = "422" ] || [ "$response" = "200" ]; then
    echo "✅ 端点存在 (HTTP $response)"
else
    echo "❌ 端点可能不存在 (HTTP $response)"
fi
echo

echo "=========================================="
echo "  测试完成"
echo "=========================================="
echo "注意: 401 状态码表示需要认证，这是正常的"
echo "      200 或 422 状态码表示端点存在"

