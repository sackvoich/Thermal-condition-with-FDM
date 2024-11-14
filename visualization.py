import matplotlib.pyplot as plt
import numpy as np

def plot_results(params, u):
    x = np.linspace(0, params.L, params.Nx)
    plt.plot(x, u)
    plt.xlabel('Дистанция (m)')
    plt.ylabel('Температура (°C)')
    plt.title('Результаты решения уравнения теплопроводности')
    plt.grid()
    plt.show()
