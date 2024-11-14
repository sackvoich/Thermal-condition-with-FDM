import numpy as np

def generate_initial_conditions(L, Nx, condition_type):
    """Создает массив начальных условий в зависимости от выбранного типа."""
    x = np.linspace(0, L, Nx)
    if condition_type == "sin(πx)":
        return np.sin(np.pi * x)
    elif condition_type == "x(L-x)":
        return x * (L - x)
    elif condition_type == "constant":
        return np.ones_like(x) * 10  # Постоянная температура 10°C
    elif condition_type == "zero":
        return np.zeros_like(x)  # Нулевая температура
    else:
        raise ValueError(f"Неизвестный тип начальных условий: {condition_type}")


class HeatEquationParameters:
    def __init__(self):
        self.L = 1.0
        self.Nx = 50
        self.dt = 0.01
        self.Nt = 100
        self.alpha = 0.01
        self.initial_conditions = np.zeros(self.Nx)
        self.left_boundary_condition = 0.0
        self.right_boundary_condition = 0.0

    def set_parameters(self, L, Nx, dt, Nt, alpha):
        self.L = L
        self.Nx = Nx
        self.dt = dt
        self.Nt = Nt
        self.alpha = alpha
        self.initial_conditions = np.zeros(self.Nx)

    def set_initial_conditions(self, initial_conditions):
        if len(initial_conditions) != self.Nx:
            raise ValueError(f"Length of initial conditions must be {self.Nx}.")
        self.initial_conditions = np.array(initial_conditions)

    def set_boundary_conditions(self, left, right):
        self.left_boundary_condition = left
        self.right_boundary_condition = right

    def display_parameters(self):
        print(f"Length: {self.L}, Nodes: {self.Nx}, dt: {self.dt}, Nt: {self.Nt}, alpha: {self.alpha}")
