from ai_proxy_core.backend import Backend
from ai_proxy_core.balancer import AdaptiveBalancer


def test_choose_returns_lowest_score():
    b1 = Backend(url="http://a:5000")
    b2 = Backend(url="http://b:5000")
    b1.last_latency_ms = 10.0
    b2.last_latency_ms = 100.0
    balancer = AdaptiveBalancer([b1, b2])
    chosen = balancer.choose()
    assert chosen is b1


def test_choose_returns_none_when_all_disabled():
    b = Backend(url="http://a:5000")
    b.healthy = False
    balancer = AdaptiveBalancer([b])
    assert balancer.choose() is None


def test_choose_skips_disabled_backend():
    import time
    b1 = Backend(url="http://a:5000")
    b2 = Backend(url="http://b:5000")
    b1.last_latency_ms = 10.0
    b2.last_latency_ms = 100.0
    b1.disabled_until = time.time() + 60
    balancer = AdaptiveBalancer([b1, b2])
    chosen = balancer.choose()
    assert chosen is b2


def test_choose_skips_unhealthy_backend():
    b1 = Backend(url="http://a:5000")
    b2 = Backend(url="http://b:5000")
    b1.healthy = False
    balancer = AdaptiveBalancer([b1, b2])
    chosen = balancer.choose()
    assert chosen is b2
