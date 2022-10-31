from PyQt5 import QtWidgets, QtCore, QtGui
import pyqtgraph as pg
from random import randint
import sys  # We need sys so that we can pass argv to QApplication
import os

class PyChart(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        """Standard init function. Sets some variables"""
        super(PyChart, self).__init__(*args, **kwargs)
        self.title = "Py-Chart"
        self.width = 1280
        self.height = 960
        self.initUI()

    # TODO: Refactor this! 
    # TODO: Create Button Methods
    # DONE: Create File Dialogue 
    # TODO: Implement Charting
    def initUI(self):
        """Bulk of UI initialization and creation"""
        # Setting Window title
        self.setWindowTitle(self.title)
        self.resize(self.width, self.height)

        # Create Layouts
        main_layout = QtWidgets.QGridLayout()
        v_layout = QtWidgets.QVBoxLayout()

        # Initialize and connect Widgets

        # graph
        self.graphWidget1 = pg.PlotWidget()

        # plot button
        self.plotButton = QtWidgets.QPushButton("Plot a File")
        self.plotButton.clicked.connect(self.plot_button_pressed)

        # mock button
        self.mockButton = QtWidgets.QPushButton("Mock Live")
        self.mockButton.clicked.connect(self.mock_button_pressed)

        # choose file button
        self.chooseFileButton = QtWidgets.QPushButton("Choose File")
        self.chooseFileButton.clicked.connect(self.file_button_pressed)

        # Label that keeps track of open file
        self.fileLabel = QtWidgets.QLabel("None")

        # text boxes: TODO: Decide on necessity
        self.plotFileLoc = QtWidgets.QLineEdit("Enter File Location")
        self.saveFileLoc = QtWidgets.QLineEdit("Enter a Save File")

        # Populate Grid Layout : Grid layout houses a vertical layout
        main_layout.addWidget(self.graphWidget1, 0, 0)
        main_layout.addLayout(v_layout, 0,2)

        #  Populate Vertical Layout
        v_layout.addWidget(self.fileLabel)
        v_layout.addWidget(self.chooseFileButton)
        v_layout.addWidget(self.plotFileLoc)
        v_layout.addWidget(self.plotButton)
        v_layout.addWidget(self.saveFileLoc)
        v_layout.addWidget(self.mockButton)

        # Create and utilize dummy widget (have to apply layout to dummy)
        widget = QtWidgets.QWidget()
        widget.setLayout(main_layout)
        self.setCentralWidget(widget)

        # PlaceHolder data types: not necessary here TODO: Remove?
        self.x = None
        self.y = None
        self.y2 = None
        self.setup_graph_data()


        # pen is the line creation method: decides plot colors
        red_pen = pg.mkPen(color=(255,0,0))    
        blue_pen = pg.mkPen(color=(0,0,255))


        # GRAPH SETTINGS ------------------------------------------- 

        # Graph Title Default
        self.graphWidget1.setTitle("Graph", color="b", size="30pt")
        
        # Show the grid
        self.graphWidget1.showGrid(x=True, y=True)

        # setting a white background color
        self.graphWidget1.setBackground('w')

        # PLOTTING - TODO: Put this in its own method

        # For static plotting simply assign an x and y
        #self.graphWidget.plot(hour, temperature, pen=pen)

        # For plot Streaming need to assign a dataline so we can update it 
        self.data_line = self.graphWidget1.plot(self.x,self.y, pen=red_pen)
        self.data_line2 = self.graphWidget1.plot(self.x, self.y2, pen=blue_pen)

        # Start a timer function - Need a timer to update graph at certain speed.
        self.timer = QtCore.QTimer()                        # Initialize a timer
        self.timer.setInterval(50)                          # Set the timer interval
        self.timer.timeout.connect(self.update_plot_data)   # Set timeout behaviour
        self.timer.start()                                  # Start timer


    def plot_button_pressed(self):
        """What happens when the plot button is pressed"""
        print("plot pressed")

    def mock_button_pressed(self):
        """What happens when the mock button is pressed"""
        print("mock pressed")
    

    # TODO: Store file somewhere 
    # TODO: Read file here or at other location
    # TODO: Setup File Protection!
    def file_button_pressed(self):
        """Occurs when the File button is pressed, opens a file dialogue, and gets
           path to desired file or files.
           Currently has no filters, and does no error checking!
           Also, does not modify file in any way (yet), just gets its name"""

        dlg = QtWidgets.QFileDialog()
        dlg.setFileMode(QtWidgets.QFileDialog.AnyFile)

        filenames = QtCore.QStringListModel()

        if dlg.exec_():
            filenames = dlg.selectedFiles()
            fnames = [x.split('/')[-1] for x in filenames]
            print(fnames)
            self.fileLabel.setText(", ".join(filenames))

            self.rename_graph(fnames[0]) # TODO: FIX THIS (only uses first name)

        print("choose file pressed")


    def setup_graph_data(self):
        """Function occurs - simply to setup x and y data for plotting 
           This is very temporary atm"""
        self.x = list(range(100))
        self.y = [randint(0,100) for _ in range(100)]
        self.y2 = [randint(0,100) for _ in range(100)]
    

    def rename_graph(self, name: str, col="b", sz="30pt"):
        """A function that renames the graph for easy renaming"""
        self.graphWidget1.setTitle(name, color=col, size=sz)


    def update_plot_data(self):
        """The main function for live drawing: At the moment utilizes random data"""

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