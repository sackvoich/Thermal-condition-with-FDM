import numpy as np

def explicit_scheme(u, dx, dt, alpha, left_boundary, right_boundary):
    u_new = np.copy(u)
    for i in range(1, len(u) - 1):
        u_new[i] = u[i] + alpha * dt / dx**2 * (u[i + 1] - 2 * u[i] + u[i - 1])
    u_new[0] = left_boundary
    u_new[-1] = right_boundary
    return u_new

def implicit_scheme(u, dx, dt, alpha, left_boundary, right_boundary):
    r = alpha * dt / dx**2
    N = len(u)
    A = np.diag((1 + 2 * r) * np.ones(N - 2)) + np.diag(-r * np.ones(N - 3), -1) + np.diag(-r * np.ones(N - 3), 1)
    u_new = np.zeros(N)
    u_new[1:-1] = np.linalg.solve(A, u[1:-1])
    u_new[0] = left_boundary
    u_new[-1] = right_boundary
    return u_new
