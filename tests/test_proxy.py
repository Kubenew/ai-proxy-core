from ai_proxy_core.proxy import _filter_headers, get_client, close_client


def test_filter_headers_removes_hop_by_hop():
    headers = {
        "host": "example.com",
        "connection": "keep-alive",
        "keep-alive": "timeout=5",
        "content-type": "application/json",
    }
    filtered = _filter_headers(headers)
    assert "host" in filtered
    assert "content-type" in filtered
    assert "connection" not in filtered
    assert "keep-alive" not in filtered


def test_filter_headers_case_insensitive():
    headers = {"Connection": "close", "X-Custom": "value"}
    filtered = _filter_headers(headers)
    assert "Connection" not in filtered
    assert "X-Custom" in filtered


def test_get_client_returns_singleton():
    client1 = get_client(timeout=30.0)
    client2 = get_client(timeout=60.0)
    assert client1 is client2


async def test_close_client_resets():
    get_client(30.0)
    import ai_proxy_core.proxy as proxy_mod
    assert proxy_mod._client is not None
    await close_client()
    assert proxy_mod._client is None
