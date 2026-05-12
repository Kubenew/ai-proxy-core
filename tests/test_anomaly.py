from ai_proxy_core.anomaly import ZScoreDetector


def test_zscore_detector():
    d = ZScoreDetector(window_size=20, threshold=2.0)
    for _ in range(15):
        assert d.add(100.0) is False
    assert d.add(500.0) is True
