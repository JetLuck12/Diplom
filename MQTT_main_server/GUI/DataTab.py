import pyqtgraph as pg
from datetime import datetime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, QCheckBox
)

class DataTab(QWidget):
    def __init__(self, mqtt_handler=None):
        super().__init__()
        self.mqtt_handler = mqtt_handler

        self.delete_old_flag = False
        self.delete_old_label = QLabel("Удалять старые данные", self)
        self.delete_old = QCheckBox("Включить", self)
        self.delete_old.stateChanged.connect(self.on_checkbox_changed)

        self.top_layout = QHBoxLayout()

        self.top_layout.addWidget(self.delete_old_label)
        self.top_layout.addWidget(self.delete_old)

        # Последнее значение
        self.last_value_label = QLabel("Последнее значение: N/A")
        self.graph_widget = pg.PlotWidget()
        self.data = []  # Хранит данные [(time, value)]

        layout = QVBoxLayout()
        layout.addLayout(self.top_layout)
        layout.addWidget(self.last_value_label)
        layout.addWidget(self.graph_widget)

        self.setLayout(layout)

    def on_checkbox_changed(self, state):
        if state == 2:
            self.delete_old_flag = True
        else:
            self.delete_old_flag = False

    def update_data(self, timestamp, value):
        # Преобразуем timestamp в "час:минута:секунда"
        #readable_time = timestamp
        readable_time = datetime.fromtimestamp(timestamp/1000).strftime("%H:%M:%S.%f")[:-3]
        if len(self.data) != 0 and self.data[-1][0] == readable_time:
            print(f"cal: {self.data[-1]}")
            return
        if len(self.data) > 100 and self.delete_old_flag:
            self.data.pop(0)
        self.data.append((readable_time, value))
        self.last_value_label.setText(f"Последнее значение: {value} (время: {readable_time})")

        # Обновление графика
        x = list(range(len(self.data)))
        y = [d[1] for d in self.data]

        self.graph_widget.clear()
        self.graph_widget.plot(x, y, pen="b")  # Используем индекс вместо времени для оси X

        # Уменьшение количества меток в зависимости от объема данных
        max_labels = 10
        step = max(1, len(self.data) // max_labels)
        displayed_ticks = [(i, str(self.data[i][0])) for i in range(0, len(self.data), step)]

        axis = self.graph_widget.getAxis("bottom")
        axis.setTicks([displayed_ticks])
