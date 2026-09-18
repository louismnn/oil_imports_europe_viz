import numpy as np

def curved_line(A, B, curvature=0.2, n=100):
    A = np.array(A)
    B = np.array(B)

    M = (A + B) / 2
    d = B - A

    perp = np.array([-d[1], d[0]])
    perp = perp / np.linalg.norm(perp)

    C = M + curvature * np.linalg.norm(d) * perp

    t = np.linspace(0, 1, n)

    points = (
        (1-t[:, None])**2 * A
        + 2*(1-t[:, None])*t[:, None] * C
        + t[:, None]**2 * B
    )

    return points.tolist()




