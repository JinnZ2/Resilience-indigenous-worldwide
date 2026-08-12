#!/usr/bin/env python3
# warning_time_audit.py -- CC0, stdlib-only
# Generalizes Keuth/Fritz/Zurell 2026: a clean measurement proxy can lag
# true-state collapse when the proxy<->truth relationship is nonlinear.
# Feed it a proxy trajectory and a truth trajectory over time. It returns:
#   - the signed proxy<->truth curvature (under/over-estimation direction)
#   - the warning-time gap at each risk threshold
#   - a falsifiable field per verdict.
# Refutation protocol: outputs are recomputed from the trajectory every
# call (no stored verdicts). If field data refutes a verdict, update the
# input trajectory, never retune this module.

# ---------------------------------------------------------------
# DEFAULT THRESHOLDS: fractional LOSS of true state that defines each
# risk tier. Defaults mirror IUCN Red List criterion A3 loss levels.
# theta = fraction lost (0.30 = 30% of true state gone).
# ---------------------------------------------------------------
DEFAULT_TIERS = {"VU": 0.30, "EN": 0.50, "CR": 0.80}

# ---------------------------------------------------------------
# LAYER 1: first threshold crossing (linear-interpolated in time)
# loss_series and times are equal-length, times strictly increasing.
# Returns interpolated time of first crossing, or None if never crossed.
# ---------------------------------------------------------------
def first_crossing(times, loss_series, theta):
    for i in range(len(loss_series)):
        if loss_series[i] >= theta:
            if i == 0:
                return times[0]
            x0, x1 = loss_series[i-1], loss_series[i]
            t0, t1 = times[i-1], times[i]
            if x1 == x0:
                return t1
            frac = (theta - x0) / (x1 - x0)      # linear interp
            return t0 + frac * (t1 - t0)
    return None

# ---------------------------------------------------------------
# LAYER 2: extinction / total-collapse time
# first time true loss reaches (near) 1.0. Falls back to last time.
# ---------------------------------------------------------------
def collapse_time(times, truth_loss, eps=0.999):
    t = first_crossing(times, truth_loss, eps)
    return t if t is not None else times[-1]

# ---------------------------------------------------------------
# LAYER 3: signed proxy<->truth curvature
# Pair truth_loss (y) against proxy_loss (x), sort by x, integrate
# (y - x) over x by trapezoid. Diagonal y=x is the linear assumption.
#   D > 0  truth loss EXCEEDS proxy loss  -> proxy UNDERESTIMATES risk
#          (concave-danger: real state crashes while proxy looks ok)
#   D < 0  truth loss BELOW proxy loss    -> proxy OVERESTIMATES risk
#          (convex-conservative: proxy flags early, longer warning)
#   D ~ 0  faithful / linear
# ---------------------------------------------------------------
def curve_deviation(proxy_loss, truth_loss, tol=0.02):
    pts = sorted(zip(proxy_loss, truth_loss), key=lambda p: p[0])
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    area = 0.0
    span = 0.0
    for i in range(1, len(xs)):
        dx = xs[i] - xs[i-1]
        if dx <= 0:
            continue
        g0 = ys[i-1] - xs[i-1]      # vertical gap from diagonal
        g1 = ys[i] - xs[i]
        area += 0.5 * (g0 + g1) * dx
        span += dx
    D = area / span if span > 0 else 0.0
    if D > tol:
        shape = "CONCAVE  -> proxy UNDERESTIMATES loss (short warning)"
    elif D < -tol:
        shape = "CONVEX   -> proxy OVERESTIMATES loss early (conservative)"
    else:
        shape = "~LINEAR  -> proxy faithful to true loss"
    return {"signed_deviation": round(D, 4), "shape": shape}

# ---------------------------------------------------------------
# LAYER 4: warning-time gap per tier
# gap = t_proxy - t_truth  (positive = proxy lags = warning lost)
# warning_truth = collapse - t_truth ; warning_proxy = collapse - t_proxy
# ---------------------------------------------------------------
def warning_gap(times, truth_loss, proxy_loss, tiers, t_collapse):
    out = {}
    for name, theta in tiers.items():
        tt = first_crossing(times, truth_loss, theta)
        tp = first_crossing(times, proxy_loss, theta)
        if tt is None:
            out[name] = {"note": "truth never crosses in window"}
            continue
        wt_truth = t_collapse - tt
        wt_proxy = (t_collapse - tp) if tp is not None else 0.0
        gap = (tp - tt) if tp is not None else float("inf")
        lost_frac = (1.0 - wt_proxy / wt_truth) if wt_truth > 0 else 0.0
        out[name] = {
            "theta_loss": theta,
            "t_truth": round(tt, 2),
            "t_proxy": (round(tp, 2) if tp is not None else "never"),
            "warning_truth_yr": round(wt_truth, 2),
            "warning_proxy_yr": round(wt_proxy, 2),
            "gap_yr": (round(gap, 2) if tp is not None else "inf"),
            "warning_lost_frac": round(lost_frac, 3),
        }
    return out

# ---------------------------------------------------------------
# LAYER 5: verdict on the MOST-PRECAUTIONARY tier (lowest theta)
# that is where early action is still possible; blindness there is worst.
# ---------------------------------------------------------------
def verdict(gap_table, tiers):
    early = min(tiers, key=lambda k: tiers[k])
    row = gap_table.get(early, {})
    lost = row.get("warning_lost_frac", 0.0)
    if isinstance(lost, str):
        lost = 0.0
    if lost > 0.5:
        flag = "RED"
    elif lost > 0.2:
        flag = "YELLOW"
    else:
        flag = "GREEN"
    return {
        "tier": early, "warning_lost_frac": lost, "flag": flag,
        "falsify": ("co-observe true state against the proxy across one "
                    "full decline; at tier " + early + " the proxy should "
                    "lag the true crossing by ~" + str(row.get("gap_yr"))
                    + " time units if this verdict holds"),
    }

# ---------------------------------------------------------------
# AUDIT DRIVER
# times:        list of time points (yr)
# truth_loss:   fractional loss of TRUE state at each time (0..1)
# proxy_loss:   fractional loss the PROXY reports at each time (0..1)
# ---------------------------------------------------------------
def audit(times, truth_loss, proxy_loss, tiers=None):
    tiers = tiers or DEFAULT_TIERS
    tc = collapse_time(times, truth_loss)
    curve = curve_deviation(proxy_loss, truth_loss)
    gaps = warning_gap(times, truth_loss, proxy_loss, tiers, tc)
    v = verdict(gaps, tiers)
    return {"collapse_time": round(tc, 2), "curve": curve,
            "tiers": gaps, "verdict": v}

if __name__ == "__main__":
    import json
    # Demo: concave range-shifting case. Proxy loss rises linearly in time;
    # true loss = proxy_loss ** 0.6 (truth crashes early, proxy lags).
    T = list(range(0, 91))
    px = [t / 90.0 for t in T]
    ty = [round(p ** 0.6, 4) for p in px]
    result = audit(T, ty, px)
    print(json.dumps(result, indent=1))
