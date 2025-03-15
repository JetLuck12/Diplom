import pyqtgraph as pg
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel,
)

class DataTab(QWidget):
    def __init__(self, mqtt_handler=None):
        super().__init__()
        self.mqtt_handler = mqtt_handler

        # Последнее значение
        self.last_value_label = QLabel("Последнее значение: N/A")
        self.graph_widget = pg.PlotWidget()
        self.data = []  # Хранит данные [(time, value)]

        layout = QVBoxLayout()
        layout.addWidget(self.last_value_label)
        layout.addWidget(self.graph_widget)

        self.setLayout(layout)

    def update_data(self, timestamp, value):
        # Преобразуем timestamp в "час:минута:секунда"
        #readable_time = datetime.fromtimestamp(timestamp).strftime("%M:%S.%f")
        readable_time = timestamp % 10000
        if len(self.data) != 0 and self.data[-1][0] == readable_time:
            print(f"cal: {self.data[-1]}")
            return
        if len(self.data) > 100:
            self.data.pop(0)
        self.data.append((readable_time, value))
        self.last_value_label.setText(f"Последнее значение: {value} (время: {readable_time})")

        # Обновление графика
        x = [d[0] for d in self.data]
        y = [d[1] for d in self.data]

        self.graph_widget.clear()
        self.graph_widget.plot(range(len(x)), y, pen="b")  # Используем индекс вместо времени для оси X

        # Уменьшение количества меток в зависимости от объема данных
        max_labels = 10  # Максимальное количество меток на оси
        step = max(1, len(x) // max_labels)
        displayed_ticks = [(i, x[i]) for i in range(0, len(x), step)]

        axis = self.graph_widget.getAxis("bottom")
        axis.setTicks([displayed_ticks])
