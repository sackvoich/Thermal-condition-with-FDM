import numpy as np
from discretization import explicit_scheme, implicit_scheme
from analytical_solution import analytical_solution

def solve(params, scheme):
    dx = params.L / (params.Nx - 1)
    u = params.initial_conditions.copy()
    
    # Создаем массив для хранения всех временных шагов
    u_history = np.zeros((params.Nt + 1, params.Nx))
    u_history[0] = u  # Сохраняем начальное состояние
    
    for t in range(params.Nt):
        if scheme == "Явная":
            u = explicit_scheme(u, dx, params.dt, params.alpha,
                              params.left_boundary_condition,
                              params.right_boundary_condition)
        elif scheme == "Неявная":
            u = implicit_scheme(u, dx, params.dt, params.alpha,
                              params.left_boundary_condition,
                              params.right_boundary_condition)
        u_history[t + 1] = u  # Сохраняем текущее состояние
        
    return u_history

def calculate_error(params, numerical_solution):
    """Вычисляет отклонение между численным и аналитическим решениями."""
    x = np.linspace(0, params.L, params.Nx)
    errors = []

    for t_index in range(params.Nt + 1):
        t = t_index * params.dt
        analytical = analytical_solution(x, t, params.alpha, params.L)
        numerical = numerical_solution[t_index]
        error = np.sqrt(np.mean((numerical - analytical) ** 2))  # Среднеквадратичная ошибка
        errors.append(error)
    
    return errors
