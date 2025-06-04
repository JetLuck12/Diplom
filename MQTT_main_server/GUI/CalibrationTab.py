from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QTextEdit, QFileDialog, QComboBox, QHBoxLayout, QLineEdit
)

class CalibrationTab(QWidget):
    def __init__(self, calibrator):
        super().__init__()
        self.calibrator = calibrator

        # UI элементы
        self.calibrate_button = QPushButton("Калибровать")
        self.refresh_axes_button = QPushButton("Обновить оси")
        self.save_config_button = QPushButton("Сохранить конфигурацию")
        self.load_config_button = QPushButton("Загрузить конфигурацию")
        self.status_output = QTextEdit()
        self.status_output.setReadOnly(True)

        # Новые поля для ширины и высоты
        self.width_input = QLineEdit()
        self.width_input.setPlaceholderText("Ширина")
        self.height_input = QLineEdit()
        self.height_input.setPlaceholderText("Высота")

        # Выбор оси фотодиода
        self.photodiod_axis_label = QLabel("Ось фотодиода:")
        self.photodiod_axis_selector = QComboBox()

        # Компоновка
        layout = QVBoxLayout()

        # Линия выбора оси
        axis_layout = QHBoxLayout()
        axis_layout.addWidget(self.photodiod_axis_label)
        axis_layout.addWidget(self.photodiod_axis_selector)
        axis_layout.addWidget(self.refresh_axes_button)
        layout.addLayout(axis_layout)

        # Линия с кнопкой "Калибровать" и параметрами
        calibration_layout = QHBoxLayout()
        calibration_layout.addWidget(self.calibrate_button)
        calibration_layout.addWidget(self.width_input)
        calibration_layout.addWidget(self.height_input)
        layout.addLayout(calibration_layout)

        layout.addWidget(self.save_config_button)
        layout.addWidget(self.load_config_button)

        layout.addWidget(QLabel("Статус:"))
        layout.addWidget(self.status_output)

        self.setLayout(layout)

        # Подключение сигналов
        self.calibrate_button.clicked.connect(self.start_calibration)
        self.save_config_button.clicked.connect(self.save_configuration)
        self.load_config_button.clicked.connect(self.load_configuration)
        self.photodiod_axis_selector.currentIndexChanged.connect(self.on_axis_selected)
        self.refresh_axes_button.clicked.connect(self.update_axis_list)

    def start_calibration(self):
        self.status_output.append("Запуск калибровки...")
        self.calibrator.calibrate()
        self.status_output.append("Калибровка завершена.")

    def save_configuration(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Сохранить конфигурацию", "", "JSON Files (*.json)")
        if file_path:
            self.calibrator.save_configuration(file_path)
            self.status_output.append(f"Конфигурация сохранена: {file_path}")

    def load_configuration(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Загрузить конфигурацию", "", "JSON Files (*.json)")
        if file_path:
            self.calibrator.load_configuration(file_path)
            self.status_output.append(f"Конфигурация загружена: {file_path}")

    def calibrate_from_config(self):
        self.status_output.append("Запуск калибровки по сохраненной конфигурации...")
        self.calibrator.calibrate_from_config()
        self.status_output.append("Калибровка по конфигурации завершена.")

    def update_axis_list(self):
        """Обновляет список доступных осей фотодиода."""
        self.photodiod_axis_selector.clear()
        axis_int_list = self.calibrator.main.handlers["smc"].get_motors()
        axis_str_list = [str(n) for n in axis_int_list]
        self.photodiod_axis_selector.addItems(axis_str_list)

    def on_axis_selected(self):
        selected_axis = self.photodiod_axis_selector.currentText()
        self.calibrator.diod_axis = selected_axis
