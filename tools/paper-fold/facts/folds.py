"""Fold-by-fold fact table for a 0.1 mm A4 page (297 x 210 mm).
thickness = t * 2^n
footprint: each fold halves the longer side (alternating directions, the normal way to fold a page)
paper length needed if every fold goes the same way (Gallivan 2002 limit): L = pi*t/6 * (2^n + 4) * (2^n - 1)
"""
import math, csv, sys
t = 0.1e-3            # m
L0, W0 = 0.297, 0.210 # m
LY = 9.4607e15
def fmt_len(m):
    a = abs(m)
    if a < 1e-9: return f"{m*1e12:.3g} pm"
    if a < 1e-6: return f"{m*1e9:.3g} nm"
    if a < 1e-3: return f"{m*1e6:.3g} µm"
    if a < 1e-2: return f"{m*1e3:.3g} mm"
    if a < 1: return f"{m*100:.3g} cm"
    if a < 1e3: return f"{m:.3g} m"
    if a < 0.1*LY: return f"{m/1e3:,.4g} km"
    return f"{m/LY:,.4g} light-years"
rows = []
l, w = L0, W0
for n in range(0, 104):
    if n > 0:
        if l >= w: l /= 2
        else: w /= 2
    th = t * 2**n
    gal = math.pi * t / 6 * (2**n + 4) * (2**n - 1)
    rows.append((n, th, l, w, gal))
out = csv.writer(sys.stdout)
out.writerow(['fold', 'layers', 'thickness_m', 'thickness', 'page_long_side', 'page_short_side', 'paper_length_one_direction'])
for n, th, l, w, gal in rows:
    out.writerow([n, f"{2**n:.4g}" if n > 40 else 2**n, f"{th:.6g}", fmt_len(th), fmt_len(l), fmt_len(w), fmt_len(gal)])
