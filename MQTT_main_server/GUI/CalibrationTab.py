from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QTextEdit, QFileDialog, QComboBox, QHBoxLayout
)

class CalibrationTab(QWidget):
    def __init__(self, calibrator):
        super().__init__()
        self.calibrator = calibrator

        # UI элементы
        self.calibrate_button = QPushButton("Калибровать")
        self.save_config_button = QPushButton("Сохранить конфигурацию")
        self.load_config_button = QPushButton("Загрузить конфигурацию")
        self.calibrate_from_config_button = QPushButton("Калибровать из конфигурации")
        self.status_output = QTextEdit()
        self.status_output.setReadOnly(True)

        # Выбор оси фотодиода
        self.photodiod_axis_label = QLabel("Ось фотодиода:")
        self.photodiod_axis_selector = QComboBox()

        # Компоновка
        layout = QVBoxLayout()
        axis_layout = QHBoxLayout()
        axis_layout.addWidget(self.photodiod_axis_label)
        axis_layout.addWidget(self.photodiod_axis_selector)

        layout.addLayout(axis_layout)
        layout.addWidget(self.calibrate_button)
        layout.addWidget(self.save_config_button)
        layout.addWidget(self.load_config_button)
        layout.addWidget(self.calibrate_from_config_button)
        layout.addWidget(QLabel("Статус:"))
        layout.addWidget(self.status_output)
        self.setLayout(layout)

        # Подключение сигналов
        self.calibrate_button.clicked.connect(self.start_calibration)
        self.save_config_button.clicked.connect(self.save_configuration)
        self.load_config_button.clicked.connect(self.load_configuration)
        self.calibrate_from_config_button.clicked.connect(self.calibrate_from_config)
        self.photodiod_axis_selector.currentIndexChanged.connect(self.on_axis_selected)

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
        self.photodiod_axis_selector.addItems(self.calibrator.main.handlers["smc"].axes)

    def showEvent(self, event):
        """Обновляет список осей при переходе на вкладку."""
        self.update_axis_list()
        super().showEvent(event)

    def on_axis_selected(self):
        selected_axis = self.photodiod_axis_selector.currentText()
        self.calibrator.diod_axis = selected_axis
