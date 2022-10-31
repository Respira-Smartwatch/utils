from PyQt5 import QtWidgets, QtCore
import pyqtgraph as pg
from random import randint
import sys  # We need sys so that we can pass argv to QApplication
import os

class PyChart(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(PyChart, self).__init__(*args, **kwargs)
        self.title = "Py-Chart"
        self.width = 1280
        self.height = 960
        self.initUI()

    # TODO: Refactor this! 
    # TODO: Create Button Methods
    # TODO: Create File Dialogue
    # TODO: Implement Charting
    def initUI(self):

        # Setting Window title
        self.setWindowTitle(self.title)
        self.resize(self.width, self.height)

        # Create Layouts
        main_layout = QtWidgets.QGridLayout()
        v_layout = QtWidgets.QVBoxLayout()

        # Create a Graph widget
        self.graphWidget1 = pg.PlotWidget()

        self.plotButton = QtWidgets.QPushButton("Plot a File")
        self.plotButton.clicked.connect(self.plot_button_pressed)

        self.mockButton = QtWidgets.QPushButton("Mock Live")

        self.plotFileLoc = QtWidgets.QLineEdit("Enter File Location")
        self.saveFileLoc = QtWidgets.QLineEdit("Enter a Save File")

        main_layout.addWidget(self.graphWidget1, 0, 0)
        main_layout.addLayout(v_layout, 0,2)

        v_layout.addWidget(self.plotFileLoc)
        v_layout.addWidget(self.plotButton)
        v_layout.addWidget(self.saveFileLoc)
        v_layout.addWidget(self.mockButton)

        widget = QtWidgets.QWidget()
        widget.setLayout(main_layout)
        self.setCentralWidget(widget)
        

        self.x = None
        self.y = None
        self.y2 = None
        self.setup_graph_data()


        # pen is a line marker, color is red
        red_pen = pg.mkPen(color=(255,0,0))    
        blue_pen = pg.mkPen(color=(0,0,255))

        # Title
        self.graphWidget1.setTitle("Graph", color="b", size="30pt")
        
        # Show the grid
        self.graphWidget1.showGrid(x=True, y=True)

        # setting a whight background color
        self.graphWidget1.setBackground('w')

        # Plotting
        # For static plotting
        #self.graphWidget.plot(hour, temperature, pen=pen)

        # For plot Streaming
        self.data_line = self.graphWidget1.plot(self.x,self.y, pen=red_pen)
        self.data_line2 = self.graphWidget1.plot(self.x, self.y2, pen=blue_pen)

        # Start a timer function
        self.timer = QtCore.QTimer()                        # Initialize a timer
        self.timer.setInterval(50)                          # Set the timer interval
        self.timer.timeout.connect(self.update_plot_data)   # Set timeout behaviour
        self.timer.start()                                  # Start timer


    def plot_button_pressed(self):
        print("Pressed!")
        

    def setup_graph_data(self):
        self.x = list(range(100))
        self.y = [randint(0,100) for _ in range(100)]
        self.y2 = [randint(0,100) for _ in range(100)]
    

    def rename_graph(self, name: str, col="b", sz="30pt"):
        self.graphWidget1.setTitle(name, color=col, size=sz)


    def update_plot_data(self):

        self.x = self.x[1:]
        self.x.append(self.x[-1] + 1)

        self.y = self.y[1:]
        self.y2 = self.y2[1:]
        self.y.append(randint(0,100))
        self.y2.append(randint(0,100))

        self.data_line.setData(self.x, self.y)
        self.data_line2.setData(self.x, self.y2)



def main():
    app = QtWidgets.QApplication(sys.argv)
    main = PyChart()
    main.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()