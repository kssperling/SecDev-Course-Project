# tests/test_token_security.py
def test_token_hashing():
    """Test that tokens are properly hashed"""
    from app.token_security import TokenManager

    manager = TokenManager()

    # Токены не должны храниться в открытом виде
    token_data = manager._token_map
    for hashed_token in token_data.keys():
        assert "token-alice" not in hashed_token
        assert "token-bob" not in hashed_token


def test_token_validation_with_original_tokens(client):
    """Test that original tokens still work after hashing implementation"""
    response = client.get("/entries", headers={"Authorization": "Bearer token-alice"})
    assert response.status_code == 200
