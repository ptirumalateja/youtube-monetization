"""Shared timing for the PHP2Shell reel (picture, text and sound all read this)."""
FPS = 30
DUR = 15.0
W, H = 1080, 1920

# key beats (s)
HOOK = 0.0          # frame-0 hit, first ping
SPREAD = 2.2        # snap pull-back, spread begins
PHP = 2.4           # "THE BUG IS IN PHP." + 69.3% counter
HOSTS = 5.2         # 1,886,612 counter
BREATH = 8.5        # held breath (near silence, freeze)
HIT = 9.0           # "NO PASSWORD." biggest hit
HIT2 = 9.65         # "ONE REQUEST."
SINCE = 11.2        # "HIDDEN IN PHP SINCE 2012." + fixed versions
WHO = 13.0          # "SO WHO KNEW?" + fly back to the seed
END = 15.0


def smooth(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def ease_out(x):
    x = min(max(x, 0.0), 1.0)
    return 1 - (1 - x) ** 3


def spread_level(t):
    """Fraction of hosts lit at time t (0..1). Monotonic up to WHO, then drains to 0 for the loop."""
    if t < 1.2:
        return 0.0
    if t < WHO:
        x = (t - 1.2) / (BREATH - 1.2)
        # slow start, explosive middle, saturating at 1 by the breath
        return min(1.0, x ** 2.2) if x < 1 else 1.0
    return 1.0
