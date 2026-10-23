"""Free-kick flight: gravity + quadratic drag + Magnus lift, solved so the ball
enters the top-right corner. Writes traj.json (1 ms samples) for the renderer.
Coordinates: metres, y up, goal line z=0, goal centre x=0, pitch toward +z."""
import json, math, numpy as np

RHO, R, M = 1.2, 0.11, 0.43           # air density, ball radius, ball mass (FIFA size 5)
A = math.pi * R * R
CD = 0.25                              # past the drag crisis at ~30 m/s
G = 9.81
SPIN_RPS = 10.0
SPIN_AXIS = np.array([0.0, 1.0, 0.10]) # mostly vertical (sidespin) + a little topspin tilt
SPIN_AXIS /= np.linalg.norm(SPIN_AXIS)
BALL0 = np.array([4.0, 0.11, 35.0])    # about 35 m out, right of centre (1997, Lyon)
TARGET = np.array([3.56, 0.95, 0.0])   # clips the inside of the right post (inner edge 3.66)

def cl(s):
    return 1.0 * s           # linear in spin parameter, so curvature grows as the ball slows (the NJP 2010 spiral)

def fly(v0, dt=0.001, tmax=2.0, spin_decay=0.02):
    p = BALL0.copy(); v = v0.copy(); w = 2 * math.pi * SPIN_RPS
    out = [(0.0, *p, w)]
    t = 0.0
    while t < tmax:
        sp = np.linalg.norm(v)
        drag = -0.5 * RHO * CD * A * sp * v / M
        s = R * w / sp
        # Magnus force along w x v, magnitude 0.5 rho CL A v^2
        wxv = np.cross(SPIN_AXIS, v); wxv /= (np.linalg.norm(wxv) + 1e-9)
        lift = 0.5 * RHO * cl(s) * A * sp * sp * wxv / M
        a = drag + lift + np.array([0, -G, 0])
        v = v + a * dt; p = p + v * dt; w *= (1 - spin_decay * dt); t += dt
        out.append((t, *p, w))
        if p[2] < -0.6: break
    return np.array(out)

def at_goal(tr):
    i = np.argmax(tr[:, 3] <= 0)
    f = tr[i-1, 3] / (tr[i-1, 3] - tr[i, 3])
    return tr[i-1] + f * (tr[i] - tr[i-1])

def solve(speed=36.0):
    # unknowns: yaw (heading) and pitch; spin sign set so the ball bends to -x (right->left)
    yaw, pitch = 0.0, 0.2
    for _ in range(60):
        def hit(yw, pt):
            d = np.array([math.sin(yw) * math.cos(pt), math.sin(pt), -math.cos(yw) * math.cos(pt)])
            g = at_goal(fly(speed * d)); return np.array([g[1], g[2]])
        h = hit(yaw, pitch); e = TARGET[:2] - h
        if np.linalg.norm(e) < 1e-4: break
        J = np.zeros((2, 2)); eps = 1e-4
        J[:, 0] = (hit(yaw + eps, pitch) - h) / eps; J[:, 1] = (hit(yaw, pitch + eps) - h) / eps
        yaw, pitch = np.array([yaw, pitch]) + np.linalg.solve(J, e)
    return yaw, pitch, speed

if __name__ == '__main__':
    # spin axis +y with v toward -z: w x v = y x (-z) = -x  -> bends left as seen from behind (good)
    yaw, pitch, speed = solve()
    d = np.array([math.sin(yaw) * math.cos(pitch), math.sin(pitch), -math.cos(yaw) * math.cos(pitch)])
    tr = fly(speed * d)
    g = at_goal(tr)
    # where it was aimed: straight line along launch heading (horizontal) to the goal line
    aim_x = BALL0[0] + d[0] / -d[2] * BALL0[2]
    ball_dir = (TARGET - BALL0); ball_dir /= np.linalg.norm(ball_dir)
    # max sideways deviation of the real path from the launch line
    ln = np.array([d[0], 0, d[2]]); ln /= np.linalg.norm(ln)
    rel = tr[:, 1:4] - BALL0
    perp = np.abs(rel[:, 0] * ln[2] - rel[:, 2] * ln[0])
    info = dict(yaw_deg=math.degrees(yaw), pitch_deg=math.degrees(pitch), speed=speed,
                t_goal=float(g[0]), goal=[float(g[1]), float(g[2])], aim_x_at_goal_line=float(aim_x),
                bend_vs_launch_line_m=float(perp[np.argmax(tr[:, 3] <= 0)]),
                v_goal=float(np.linalg.norm((tr[np.argmax(tr[:,3]<=0)+1,1:4]-tr[np.argmax(tr[:,3]<=0),1:4])/0.001)))
    print(json.dumps(info, indent=1))
    keep = tr[::1]
    json.dump(dict(info=info, ball0=BALL0.tolist(), spin_axis=SPIN_AXIS.tolist(), dt=0.001,
                   t=keep[:, 0].round(4).tolist(), p=keep[:, 1:4].round(4).tolist(), w=keep[:, 4].round(3).tolist()),
              open('traj.json', 'w'))
