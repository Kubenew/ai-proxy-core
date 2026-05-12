import time
from ai_proxy_core.backend import Backend


def test_backend_defaults():
    b = Backend(url="http://localhost:5000")
    assert b.url == "http://localhost:5000"
    assert b.healthy is True
    assert b.active_requests == 0
    assert b.error_count == 0


def test_backend_score():
    b = Backend(url="http://localhost:5000")
    assert b.score() == 9999.0  # last_latency_ms defaults to 9999

    b.last_latency_ms = 100.0
    b.active_requests = 5
    b.error_count = 2
    expected = 100.0 + (5 * 10.0) + (2 * 200.0)
    assert b.score() == expected


def test_backend_disabled():
    b = Backend(url="http://localhost:5000")
    assert b.disabled() is False

    b.disabled_until = time.time() + 60
    assert b.disabled() is True
