from PyQt5 import QtWidgets, QtCore, QtGui
import pyqtgraph as pg
from random import randint
import sys  # We need sys so that we can pass argv to QApplication
import os

S_BTN_WID = 75

class PyChart(QtWidgets.QMainWindow):

    def __init__(self, n_g=4, f_s=20, *args, **kwargs):
        """Standard init function. Sets some variables 
           Specify number of desired graphs with the n_g parameter"""

        super(PyChart, self).__init__(*args, **kwargs)
        self.title = "Py-Chart"
        self.width = 1280
        self.height = 960
        self.num_graphs=n_g
        self.sample_rate_hz = f_s
        self.sample_T_ms = int(1000 / f_s)
        
        self.initUI()

    # TODO: Refactor this! 
    # TODO: Create Button Methods
    # DONE: Create File Dialogue 
    # DONE: Implement File Dialogue
    # TODO: Implement Charting
    def initUI(self):
        """Bulk of UI initialization and creation"""

        # UI SETUP --------------------------------------------------------
        
        # Setting Window title
        self.setWindowTitle(self.title)
        self.resize(self.width, self.height)

        # Create Layouts
        main_layout = QtWidgets.QHBoxLayout()
        graph_layout = QtWidgets.QVBoxLayout()
        sidebar_layout = QtWidgets.QVBoxLayout()
        p_layouts = [QtWidgets.QHBoxLayout() for _ in range(self.num_graphs)]


        # Initialize and connect Widgets ------------------------------------ 
        # graphs - as many as self.num_graphs - can be passed as a parameter
        self.graphWidgets = [pg.PlotWidget() for _ in range(self.num_graphs)]

        # plot button
        self.plotButton = QtWidgets.QPushButton("Plot a File")
        self.plotButton.setMaximumWidth(S_BTN_WID)
        self.plotButton.clicked.connect(self.plot_button_pressed)

        # mock button
        self.mockButton = QtWidgets.QPushButton("Mock Live")
        self.mockButton.setMaximumWidth(S_BTN_WID)
        self.mockButton.clicked.connect(self.mock_button_pressed)

        # choose file buttons
        self.chooseFileButtons = [QtWidgets.QPushButton("Browse") for _ in range(self.num_graphs)]
        for idx, btn in enumerate(self.chooseFileButtons): 
            btn.setMaximumWidth(S_BTN_WID)
            btn.clicked.connect(lambda ch, i=idx: self.file_button_pressed(i))

        # Label that keeps track of open file
        self.fileLabels = [QtWidgets.QLabel("None") for _ in range(self.num_graphs)]

        # text boxes: TODO: Decide on necessity
        self.plotFileLoc = QtWidgets.QLineEdit("Enter File Location")
        self.saveFileLoc = QtWidgets.QLineEdit("Enter a Save File")

        # Layout population -------------------------------------------
        # Populate Main Layout : Grid layout houses a vertical layout
        main_layout.addLayout(graph_layout)
        main_layout.addLayout(sidebar_layout)

        # Populate the graph layout (Graphs and file selection)
        for idx, graph in enumerate(self.graphWidgets):
            graph_layout.addWidget(graph)
            graph_layout.addLayout(p_layouts[idx])

        #  Populate Vertical Layout
        for idx, l in enumerate(p_layouts):
            l.addWidget(self.chooseFileButtons[idx])
            l.addWidget(self.fileLabels[idx])

        #sidebar_layout.addWidget(self.plotFileLoc)
        sidebar_layout.addWidget(self.plotButton)
        #sidebar_layout.addWidget(self.saveFileLoc)
        sidebar_layout.addWidget(self.mockButton)

        # Dummy widget - layout application --------------------------------- 
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
        for idx, graph in enumerate(self.graphWidgets):
            # Graph Title Default
            graph.setTitle(f"Graph {idx+1}", color="b", size="30pt")
        
            # Show the grid
            graph.showGrid(x=True, y=True)

            # setting a white background color
            graph.setBackground('w')



        # PLOTTING - TODO: Put this in its own method

        # For static plotting simply assign an x and y
        #self.graphWidget.plot(hour, temperature, pen=pen)

        # For plot Streaming need to assign a dataline so we can update it 
        self.data_line = self.graphWidgets[0].plot(self.x,self.y, pen=red_pen)
        self.data_line2 = self.graphWidgets[0].plot(self.x, self.y2, pen=blue_pen)

        # Start a timer function - Need a timer to update graph at certain speed.
        self.timer = QtCore.QTimer()                        # Initialize a timer
        self.timer.setTimerType(QtCore.Qt.PreciseTimer)
        self.timer.setInterval(self.sample_T_ms)  # Set the timer interval
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
    def file_button_pressed(self, g_id):
        """Occurs when the File button is pressed, opens a file dialogue, and gets
           path to desired file or files.
           Currently has no filters, and does no error checking!
           Also, does not modify file in any way (yet), just gets its name"""

        dlg = QtWidgets.QFileDialog()
        dlg.setFileMode(QtWidgets.QFileDialog.AnyFile)

        if dlg.exec_():
            filenames = dlg.selectedFiles()
            fnames = [x.split('/')[-1] for x in filenames]
            print(fnames)
            self.fileLabels[g_id].setText(", ".join(filenames))
            self.rename_graph(self.graphWidgets[g_id], fnames[0]) # TODO: FIX THIS (only uses first name)
        else:
            print("ERROR - FileDialogue did not execute")
            sys.exit(os.EX_UNAVAILABLE)
        print("choose file pressed")


    def setup_graph_data(self):
        """Function occurs - simply to setup x and y data for plotting 
           This is very temporary atm"""
        self.x = list(range(1000))
        self.y = [randint(0,100) for _ in range(1000)]
        self.y2 = [randint(0,100) for _ in range(1000)]
    

    def rename_graph(self, graph, name: str, col="b", sz="30pt"):
        """A function that renames the graph for easy renaming"""
        graph.setTitle(name, color=col, size=sz)


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
    main = PyChart(f_s= 50, n_g=4)
    main.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()