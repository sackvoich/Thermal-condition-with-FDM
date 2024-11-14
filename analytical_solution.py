import numpy as np

def analytical_solution(x, t, alpha, L):
    """Вычисляет аналитическое решение задачи теплопроводности."""
    return np.sin(np.pi * x / L) * np.exp(-alpha * (np.pi / L) ** 2 * t)
