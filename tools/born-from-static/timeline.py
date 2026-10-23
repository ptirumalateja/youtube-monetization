"""Beat times shared by picture, text and sound (seconds, 30 fps)."""
import numpy as np

FPS = 30
DUR = 15.0
N_FRAMES = int(DUR * FPS)

STEPS = 50
STEP_START = 2.0          # step 1 lands here
STEP_FRAMES = 4           # each denoising step is held for 4 frames
STEP_END = STEP_START + (STEPS - 1) * STEP_FRAMES / FPS   # step 50 would land here...
REVEAL = 9.0              # ...but step 50 is held back to the hit
BREATH = (STEP_END, REVEAL)
FORWARD = (11.6, 14.8)    # noise is added back (the training direction)

S0 = 0.035                # signal left in the static on frame 0 (a faint hint)


def step_at(t):
    """Denoising step shown at time t (0 = pure static, 50 = clean)."""
    if t < STEP_START:
        return 0
    if t >= REVEAL:
        return STEPS
    return min(STEPS - 1, 1 + int((t - STEP_START) * FPS / STEP_FRAMES))


def step_times():
    return [STEP_START + (k - 1) * STEP_FRAMES / FPS for k in range(1, STEPS)] + [REVEAL]


def signal_for_step(k):
    """Signal fraction s (noise is sqrt(1 - s^2)) after step k.

    Log-SNR rises with the step (slightly front-loaded so something changes early),
    so the picture appears coarse-first and the last steps only refine detail.
    """
    if k <= 0:
        return S0
    if k >= STEPS:
        return 1.0
    lo, hi = np.log(S0 ** 2 / (1 - S0 ** 2)), 4.2   # log-SNR from frame 0 up to ~98.5% signal
    lsnr = lo + (hi - lo) * (k / (STEPS - 1)) ** 0.7
    snr = np.exp(lsnr)
    return float(np.sqrt(snr / (1 + snr)))


def signal_at(t):
    if FORWARD[0] <= t:
        u = min(1.0, (t - FORWARD[0]) / (FORWARD[1] - FORWARD[0]))
        # forward process: log-SNR falls smoothly back to frame 0's value
        lo, hi = np.log(S0 ** 2 / (1 - S0 ** 2)), 7.0
        u = u * u * (3 - 2 * u)
        lsnr = hi + (lo - hi) * u
        snr = np.exp(lsnr)
        return float(np.sqrt(snr / (1 + snr)))
    return signal_for_step(step_at(t))
