from app.core.rate_limit import SlidingWindowLimiter, client_key


class FakeClock:
    def __init__(self):
        self.now = 0.0

    def __call__(self):
        return self.now


def test_allows_up_to_the_limit_then_refuses():
    clock = FakeClock()
    limiter = SlidingWindowLimiter(limit=3, window_s=60, clock=clock)
    assert [limiter.allow("a") for _ in range(4)] == [True, True, True, False]


def test_window_slides():
    clock = FakeClock()
    limiter = SlidingWindowLimiter(limit=2, window_s=60, clock=clock)
    assert limiter.allow("a") and limiter.allow("a")
    assert not limiter.allow("a")
    clock.now = 60.0  # the first two hits have aged out
    assert limiter.allow("a")


def test_keys_are_independent():
    limiter = SlidingWindowLimiter(limit=1, window_s=60, clock=FakeClock())
    assert limiter.allow("a")
    assert limiter.allow("b")
    assert not limiter.allow("a")


def test_sweep_drops_idle_keys():
    clock = FakeClock()
    limiter = SlidingWindowLimiter(limit=1, window_s=10, clock=clock)
    for i in range(499):
        limiter.allow(f"k{i}")
    clock.now = 100.0  # all idle
    limiter.allow("fresh")  # 500th call triggers the sweep
    assert set(limiter._hits) == {"fresh"}


class _Req:
    def __init__(self, xff=None, host="10.0.0.9"):
        self.headers = {"x-forwarded-for": xff} if xff else {}
        self.client = type("C", (), {"host": host})()


def test_client_key_uses_the_proxy_appended_hop():
    assert client_key(_Req("6.6.6.6, 203.0.113.7")) == "203.0.113.7"
    assert client_key(_Req()) == "10.0.0.9"
