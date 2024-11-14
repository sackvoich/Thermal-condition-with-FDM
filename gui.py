from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QComboBox, QSlider)
from PySide6.QtCore import Qt, QTimer
from params import HeatEquationParameters, generate_initial_conditions
from solver import solve
from analytical_solution import analytical_solution

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import sys

class HeatEquationApp(QWidget):
    def __init__(self):
        super().__init__()
        self.params = HeatEquationParameters()
        self.results = None
        self.errors = None
        self.current_frame = 0
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.update_animation)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Решение уравнения теплопроводности")
        main_layout = QVBoxLayout()

        # Создаем горизонтальный layout для разделения настроек и графика
        h_layout = QHBoxLayout()
        
        # Левая панель с настройками
        settings_layout = QVBoxLayout()
        
        self.entry_L = self.create_input_field("Длина отрезка (L):", settings_layout)
        self.entry_Nx = self.create_input_field("Количество узлов (Nx):", settings_layout)
        self.entry_dt = self.create_input_field("Шаг по времени (dt):", settings_layout)
        self.entry_Nt = self.create_input_field("Количество временных шагов (Nt):", settings_layout)
        self.entry_alpha = self.create_input_field("Коэффициент теплопроводности (alpha):", settings_layout)

        self.scheme_selector = QComboBox(self)
        self.scheme_selector.addItems(["Явная", "Неявная"])
        settings_layout.addWidget(QLabel("Численная схема:"))
        settings_layout.addWidget(self.scheme_selector)

        self.initial_conditions_selector = QComboBox(self)
        self.initial_conditions_selector.addItems(["sin(πx)", "x(L-x)", "constant", "zero", "manual"])
        self.initial_conditions_selector.currentTextChanged.connect(self.toggle_manual_input)
        settings_layout.addWidget(QLabel("Тип начальных условий:"))
        settings_layout.addWidget(self.initial_conditions_selector)

        self.initial_conditions_input = self.create_input_field("Начальные условия (через запятую):", settings_layout)
        self.initial_conditions_input.setEnabled(False)

        self.left_boundary_input = self.create_input_field("Левое граничное условие:", settings_layout)
        self.right_boundary_input = self.create_input_field("Правое граничное условие:", settings_layout)

        # Кнопки управления
        button_layout = QHBoxLayout()
        self.run_button = QPushButton("Запустить симуляцию")
        self.run_button.clicked.connect(self.run_simulation)
        
        self.play_button = QPushButton("▶ Воспроизвести")
        self.play_button.clicked.connect(self.toggle_animation)
        self.play_button.setEnabled(False)

        self.toggle_graph_button = QPushButton("Показать ошибки")
        self.toggle_graph_button.clicked.connect(self.toggle_graph)
        self.toggle_graph_button.setEnabled(False)
        
        button_layout.addWidget(self.run_button)
        button_layout.addWidget(self.play_button)
        button_layout.addWidget(self.toggle_graph_button)
        settings_layout.addLayout(button_layout)

        # Добавляем слайдер времени
        self.time_slider = QSlider(Qt.Horizontal)
        self.time_slider.setMinimum(0)
        self.time_slider.setMaximum(0)
        self.time_slider.valueChanged.connect(self.slider_changed)
        self.time_slider.setEnabled(False)
        settings_layout.addWidget(QLabel("Временной шаг:"))
        settings_layout.addWidget(self.time_slider)

        # Добавляем настройки в левую часть окна
        settings_widget = QWidget()
        settings_widget.setLayout(settings_layout)
        settings_widget.setMaximumWidth(400)
        h_layout.addWidget(settings_widget)

        # Правая часть с графиком
        self.figure = plt.Figure()
        self.canvas = FigureCanvas(self.figure)
        h_layout.addWidget(self.canvas)

        main_layout.addLayout(h_layout)
        self.setLayout(main_layout)

        self.showing_error = False  # Флаг для отслеживания текущего графика

    def create_input_field(self, label_text, layout):
        label = QLabel(label_text)
        layout.addWidget(label)
        entry = QLineEdit(self)
        layout.addWidget(entry)
        return entry

    def toggle_manual_input(self, text):
        """Включает или выключает поле для ручного ввода начальных условий."""
        self.initial_conditions_input.setEnabled(text == "manual")

    def run_simulation(self):
        try:
            # Получаем параметры из UI
            L = float(self.entry_L.text())
            Nx = int(self.entry_Nx.text())
            dt = float(self.entry_dt.text())
            Nt = int(self.entry_Nt.text())
            alpha = float(self.entry_alpha.text())
            condition_type = self.initial_conditions_selector.currentText()

            # Генерируем начальные условия
            if condition_type == "manual":
                initial_conditions = list(map(float, self.initial_conditions_input.text().split(',')))
                if len(initial_conditions) != Nx:
                    raise ValueError(f"Длина массива начальных условий должна быть {Nx}.")
            else:
                initial_conditions = generate_initial_conditions(L, Nx, condition_type)

            left_boundary = float(self.left_boundary_input.text())
            right_boundary = float(self.right_boundary_input.text())

            # Устанавливаем параметры
            self.params.set_parameters(L, Nx, dt, Nt, alpha)
            self.params.set_initial_conditions(initial_conditions.tolist())  # Передаем как список
            self.params.set_boundary_conditions(left_boundary, right_boundary)

            # Запускаем численное решение
            scheme = self.scheme_selector.currentText()
            self.results = solve(self.params, scheme)

            # Сравниваем с аналитическим решением
            self.errors = self.calculate_error()

            # Визуализируем численные результаты
            self.time_slider.setMaximum(self.params.Nt)
            self.time_slider.setValue(0)
            self.time_slider.setEnabled(True)
            self.play_button.setEnabled(True)
            self.toggle_graph_button.setEnabled(True)

            self.current_frame = 0
            self.showing_error = False
            self.plot_frame(0)

        except ValueError as e:
            print(f"Ошибка: {e}")

    def calculate_error(self):
        """Вычисляет отклонение численного решения от аналитического."""
        x = np.linspace(0, self.params.L, self.params.Nx)
        errors = []

        for t_index in range(self.params.Nt + 1):
            t = t_index * self.params.dt
            analytical = analytical_solution(x, t, self.params.alpha, self.params.L)
            numerical = self.results[t_index]
            error = np.sqrt(np.mean((numerical - analytical) ** 2))  # Среднеквадратичная ошибка
            errors.append(error)
        
        return errors

    def toggle_graph(self):
        """Переключение между графиком решения и графиком ошибки."""
        self.showing_error = not self.showing_error
        if self.showing_error:
            self.toggle_graph_button.setText("Показать решение")
            self.plot_error()
        else:
            self.toggle_graph_button.setText("Показать ошибки")
            self.plot_frame(self.current_frame)

    def plot_frame(self, frame):
        """Рисует график распределения температуры."""
        if self.showing_error:
            return  # Если показываются ошибки, не обновляем график решения
        
        x = np.linspace(0, self.params.L, self.params.Nx)
        self.figure.clf()
        ax = self.figure.add_subplot(111)

        ax.plot(x, self.results[frame])
        ax.set_xlabel('Расстояние (м)')
        ax.set_ylabel('Температура (°C)')
        ax.set_title(f'Распределение температуры (шаг {frame} из {self.params.Nt})')
        ax.grid(True)

        self.canvas.draw()

    def plot_error(self):
        """Рисует график ошибки."""
        self.figure.clf()
        ax = self.figure.add_subplot(111)

        ax.plot(range(len(self.errors)), self.errors, label="Среднеквадратичная ошибка")
        ax.set_xlabel('Шаг времени')
        ax.set_ylabel('Ошибка')
        ax.set_title('Отклонение численного решения от аналитического')
        ax.grid(True)
        ax.legend()

        self.canvas.draw()

    def toggle_animation(self):
        if self.animation_timer.isActive():
            self.animation_timer.stop()
            self.play_button.setText("▶ Воспроизвести")
        else:
            self.animation_timer.start(50)  # Обновление каждые 50 мс
            self.play_button.setText("⏸ Пауза")

    def update_animation(self):
        self.current_frame = (self.current_frame + 1) % (self.params.Nt + 1)
        self.time_slider.setValue(self.current_frame)
        if not self.showing_error:  # Обновляем только, если показывается график решения
            self.plot_frame(self.current_frame)

    def slider_changed(self, value):
        self.current_frame = value
        if not self.showing_error:  # Обновляем только, если показывается график решения
            self.plot_frame(value)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HeatEquationApp()
    window.show()
    sys.exit(app.exec())
