from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QApplication, QSlider
from PyQt6.QtCore import Qt
import pyfirmata2
import sys

board = pyfirmata2.Arduino('COM3')
pin9 = board.get_pin('d:5:s')
pin10 = board.get_pin('d:6:s')
pin11 = board.get_pin('d:9:s')
pin12 = board.get_pin('d:10:s')
pin13 = board.get_pin('d:11:s')

class Example(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()

        self.initUI()
        self.resize(500, 350)

    def initUI(self):
        self.sliders = []
        self.labels = []
        for i in range(5):
            slider = QSlider(Qt.Orientation.Vertical, self)
            slider.setFixedHeight(slider.height() * 10)
            slider.setRange(0, 180)
            slider.setTickPosition(QSlider.TickPosition.TicksBelow)
            slider.setTickInterval(20)
            slider.valueChanged.connect(self.update_value)
            self.sliders.append(slider)

            label = QtWidgets.QLabel(str(slider.value()))
            self.labels.append(label)

        layout = QtWidgets.QHBoxLayout()
        for i in range(5):
            layout.addWidget(self.sliders[i])
            layout.addWidget(self.labels[i])

        self.setLayout(layout)

    def update_value(self):
        values = []
        for i in range(5):
            self.labels[i].setText(str(self.sliders[i].value()))
            values.append(str(self.sliders[i].value()))
        print(values)
        pin9.write(values[0])
        pin10.write(values[1])
        pin11.write(values[2])
        pin12.write(values[3])
        pin13.write(values[4])




app = QApplication(sys.argv)
app.setStyle("QtCurve")
window = Example()
window.show()
sys.exit(app.exec())
