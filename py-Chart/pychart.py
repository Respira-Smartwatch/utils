from PyQt5 import QtWidgets, QtCore, QtGui
import pyqtgraph as pg
from random import randint
import serial
import sys  # We need sys so that we can pass argv to QApplication
import os

S_BTN_WID = 75 # Setting up a global parameter for button width

class PyChart(QtWidgets.QMainWindow):

    def __init__(self, n_g=1, f_s=20, serial_dev="/dev/ttyUSB0", *args, **kwargs):
        """Standard init function. Sets some variables 
           Specify number of desired graphs with the n_g parameter"""

        super(PyChart, self).__init__(*args, **kwargs)
        self.title = "Py-Chart"
        self.width = 1280
        self.height = 960
        self.init_graphs_no = n_g
        self.num_graphs=0
        self.sample_rate_hz = f_s
        self.sample_T_ms = int(1000 / f_s)
        self.bus = serial.Serial(port=serial_dev, baudrate=9600, timeout=self.sample_T_ms/1000)

        # Setup for modifiable layouts
        self.chart_bottom_layouts = []
        self.graphWidgets = []
        self.fileLabels = []
        self.chooseFileButtons = []
        
        self.initUI()

    # TODO: Move live plotting to its own method
    def initUI(self):
        """Bulk of UI initialization and creation"""

        # UI SETUP --------------------------------------------------------
        
        # Setting Window title
        self.setWindowTitle(self.title)
        self.resize(self.width, self.height)

        # Create Static Layouts
        self.main_layout = QtWidgets.QHBoxLayout()
        self.graph_layout = QtWidgets.QVBoxLayout()
        self.sidebar_layout = QtWidgets.QVBoxLayout()

        # Initialize and connect Widgets ------------------------------------ 

        # Add Plot button
        self.addPltBtn = QtWidgets.QPushButton("Add Plot")
        self.addPltBtn.setMaximumWidth(S_BTN_WID)
        self.addPltBtn.clicked.connect(self.create_graph_view)

        # mock button
        self.mockButton = QtWidgets.QPushButton("Mock Live")
        self.mockButton.setMaximumWidth(S_BTN_WID)
        self.mockButton.clicked.connect(self.mock_button_pressed)

        # text boxes: TODO: Decide on necessity
        self.plotFileLoc = QtWidgets.QLineEdit("Enter File Location")
        self.saveFileLoc = QtWidgets.QLineEdit("Enter a Save File")

        # Layout population -------------------------------------------------
        # Populate Main Layout : Grid layout houses a vertical layout
        self.main_layout.addLayout(self.graph_layout)
        self.main_layout.addLayout(self.sidebar_layout)

        # Create Graph views for n_g number of graphs
        for _ in range(self.init_graphs_no):
            self.create_graph_view()

        # Sidebar layout stuff
        #sidebar_layout.addWidget(self.plotFileLoc)
        self.sidebar_layout.addWidget(self.addPltBtn)
        #sidebar_layout.addWidget(self.saveFileLoc)
        #self.sidebar_layout.addWidget(self.mockButton)

        # Dummy widget - layout application --------------------------------- 
        # Create and utilize dummy widget (have to apply layout to dummy)
        widget = QtWidgets.QWidget()
        widget.setLayout(self.main_layout)
        self.setCentralWidget(widget)

        # Plotting ----------------------------------------------------------
        # TODO - Relegate to its own method
        # PlaceHolder data types: not necessary here TODO: Remove?
        self.x = None
        self.y = None
        self.y2 = None
        self.setup_graph_data()

        # pen is the line creation method: decides plot colors
        self.red_pen = pg.mkPen(color=(255,0,0))    
        self.blue_pen = pg.mkPen(color=(0,0,255))

        # PLOTTING - TODO: Put this in its own method

        # For plot Streaming need to assign a dataline so we can update it 
        self.data_line = self.graphWidgets[0].plot(self.x,self.y, pen=self.red_pen)
        self.data_line2 = self.graphWidgets[0].plot(self.x, self.y2, pen=self.blue_pen)

        # Start a timer function - Need a timer to update graph at certain speed.
        self.timer = QtCore.QTimer()                        # Initialize a timer
        self.timer.setTimerType(QtCore.Qt.PreciseTimer)
        self.timer.setInterval(self.sample_T_ms)  # Set the timer interval
        self.timer.timeout.connect(self.live_plot_update)   # Set timeout behaviour
        self.timer.start()                                  # Start timer


    # TODO: Add error Dialogue
    def create_graph_view(self):
        """ A method that creates  graph view up to 10"""

        # Do not allow more than 10 graphs to be created
        if(self.num_graphs >= 10):
            print("Cannot create another graph!")
            return -1

        # Create required objects
        layout = QtWidgets.QHBoxLayout()   
        g = pg.PlotWidget()
        lbl = QtWidgets.QLabel("None")

        # Setup for required objects
        btn = QtWidgets.QPushButton("Browse")  
        btn.setMaximumWidth(S_BTN_WID)
        btn.clicked.connect(lambda ch, i=self.num_graphs: self.file_button_pressed(i))

        g.setTitle(f"Graph {self.num_graphs + 1}", color="b", size='20pt')        
        g.showGrid(x=True, y=True)
        #g.setBackground("w")

        # Layout configuration
        layout.addWidget(btn)
        layout.addWidget(lbl)

        # Adding this to class scope lists
        self.graphWidgets.append(g)
        self.fileLabels.append(lbl)
        self.chooseFileButtons.append(btn)
        self.chart_bottom_layouts.append(QtWidgets.QHBoxLayout())
        self.graph_layout.addWidget(g)
        self.graph_layout.addLayout(layout)
        self.num_graphs += 1


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
            lbl_str = ", ".join(filenames)
            print(fnames)
            self.rename_graph(self.graphWidgets[g_id], f"Graph {g_id+1} - {fnames[0]}") # TODO: FIX THIS (only uses first name)
            self.plot_static(g_id, filenames[0])
        else:
            print("No File Selected")
            lbl_str = "No File Selected"

        self.fileLabels[g_id].setText(lbl_str)
        print("choose file pressed")

        return filenames

    def setup_graph_data(self):
        """Function occurs - simply to setup x and y data for plotting 
           This is very temporary atm"""
        self.x = list(range(1000))
        self.y = [randint(0,100) for _ in range(1000)]
        self.y2 = [randint(0,100) for _ in range(1000)]
    

    def rename_graph(self, graph, name: str, col="b", sz="20pt"):
        """A function that renames the graph for easy renaming"""
        graph.setTitle(name, color=col, size=sz)

    # TODO: Make this read multiple filetypes
    # TODO: Make this accept files with two columns x and y
    # TODO: Create Error handling dialogues
    def read_file(self, file, add_x=True):
        """ A Function that reads a file, and returns x and y lists 
            Currently only supports files with numbers on newlines."""

        with open(file, 'r') as f:
            dat = f.read()
        
        y = [float(x) for x in dat.strip().split('\n')]
        
        if add_x:
            x = [i for i in range(0,len(y))]
        
        return x, y


    def plot_static(self, g_id:int, inFile:str, isolate=True):
        """ Plots static data - file formats described in read_file method"""
        # Clear given plot
        if isolate:
            self.graphWidgets[g_id].clear()
        # Pull Data from file (supported files?)
        x, y = self.read_file(inFile)
        # Plot the data
        self.graphWidgets[g_id].plot(x, y, pen=self.red_pen)


    # TODO: Mess with this and allow live plotting!
    def live_plot_update(self):
        """The main function for live drawing: At the moment utilizes random data"""

        data = int.from_bytes(self.bus.read(1), 'little')

        if data > 0:
            self.x = self.x[1:]
            self.x.append(self.x[-1] + 1)
            self.y = self.y[1:]
            self.y2 = self.y2[1:]
            print(data)
            data = int(data)
            self.y.append(data)
            self.y2.append(0)
            self.data_line.setData(self.x, self.y)
            self.data_line2.setData(self.x, self.y2)
        



def main():
    app = QtWidgets.QApplication(sys.argv)
    main = PyChart(f_s= 50, n_g=2)
    main.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
