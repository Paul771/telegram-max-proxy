import httpx
import json

print("Тестирование API endpoints...")
print("=" * 60)

base_url = "http://127.0.0.1:8000"

# Test 1: Root endpoint
print("\n[TEST 1] GET /")
try:
    response = httpx.get(f"{base_url}/", timeout=5.0)
    print(f"Статус: {response.status_code}")
    print(f"Ответ: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
except Exception as e:
    print(f"Ошибка: {e}")

# Test 2: Health check
print("\n[TEST 2] GET /health")
try:
    response = httpx.get(f"{base_url}/health", timeout=5.0)
    print(f"Статус: {response.status_code}")
    print(f"Ответ: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
except Exception as e:
    print(f"Ошибка: {e}")

# Test 3: OpenAPI docs
print("\n[TEST 3] GET /docs")
try:
    response = httpx.get(f"{base_url}/docs", timeout=5.0)
    print(f"Статус: {response.status_code}")
    print(f"Документация доступна: http://127.0.0.1:8000/docs")
except Exception as e:
    print(f"Ошибка: {e}")

print("\n" + "=" * 60)
print("Тестирование завершено!")
