# # tests/test_resource_limits.py
# def test_entries_quota_limit(client):
#     """Test that users cannot exceed entries quota"""
#     # Создаем максимальное количество записей
#     for i in range(1001):
#         response = client.post(
#             "/entries",
#             json={"title": f"Test Entry {i}", "kind": "book", "status": "todo"},
#             headers={"Authorization": "Bearer token-alice"},
#         )
#         if i >= 1000:
#             assert response.status_code == 429
#             assert "quota_exceeded" in response.json()["error"]["code"]
#         else:
#             assert response.status_code == 201
#
#
# def test_system_health_endpoint(client):
#     """Test system health endpoint returns proper metrics"""
#     response = client.get("/system/health")
#     assert response.status_code == 200
#     assert "memory" in response.json()["details"]
#     assert "limits" in response.json()["details"]
