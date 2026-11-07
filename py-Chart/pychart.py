from PyQt5 import QtWidgets, QtCore, QtGui
from enum import Enum
import numpy as np
import pyqtgraph as pg
from random import randint
import serial
import sys  # We need sys so that we can pass argv to QApplication
import os

S_BTN_WID = 75 # Setting up a global parameter for button width

class Pens(Enum):
    RED = pg.mkPen(color=(255,0,0))    
    BLUE = pg.mkPen(color=(0,0,255))
    GREEN = pg.mkPen(color=(0,255,0))
    PURPLE = pg.mkPen(color=(255,0,255))
    CYAN = pg.mkPen(color=(0,255, 255))

    def list():
       return [p.value for p in Pens]

class gSerial(serial.Serial):
    def __init__(self, port="/dev/ttyACM0", baudrate=115200, timeout=10, *args, **kwargs):
        self.accepted_bauds = [9600, 115200]
        try:
            super().__init__(port=port, baudrate=baudrate, timeout=timeout, *args, **kwargs)
        except serial.SerialException:
            print(f"Error: Serial Bus {port} Not Present")
            self.bus = 0
            self.connect_serial_cli()

       
    def connect_serial_cli(self)->serial.Serial:
        print("No serial bus present\n\nWould you like to connect to a bus?")
        while True:
            ans = input("y/n:")
            if ans.lower() not in ["y", "n"]:
                print("Please enter 'y' or 'n'")
                continue
            elif ans.lower() == "n":
                self.bus = 0
                return 0
            else:
                ser = input("Enter path to serial bus:")
                baud = int(input("Enter baud rage:"))
                if int(baud) not in self.accepted_bauds:
                    print(f"{baud} is not a value in {accepted_bauds} - using {accepted_bauds[0]}")
                    baud = self.accepted_bauds[0]
            try:
                super().__init__(port=ser, baudrate=baud, timeout=self.timeout)
                break
            except serial.SerialException:
                print(f"bus: '{ser}' is not a valid serial bus.")
                ans = input("Try again? (y/n):").lower().strip()
                if ans != "y":
                    print("Continuing without a serial bus")
                    self.bus = 0
                    return 0
                continue
        return self
    
class GraphWidget(QtWidgets.QWidget):
    """ A class that creates graph view"""
    def __init__(self, name="none", live_freq_hz = 1, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Create required objects ====
        # QT Info
        self.main_layout = QtWidgets.QVBoxLayout()
        self.bar_layout = QtWidgets.QHBoxLayout()   
        self.graph = pg.PlotWidget()
        self.pens = Pens.list()

        # Data Info
        self.sample_rate_hz = live_freq_hz
        self.sample_T_ms = int(1000 / live_freq_hz) 
        self.bus = gSerial()
        self.x = list(range(3000))
        self.y = [randint(0,100) for _ in range(3000)]

        # Setup for required objects ====
        # Browse Button
        self.browse_btn = QtWidgets.QPushButton("Browse")  
        self.browse_btn.setMaximumWidth(S_BTN_WID)
        self.browse_btn.clicked.connect(self.file_button_pressed)
        self.browse_lbl = QtWidgets.QLabel("File: None")

        # TODO: Mock Button
        #self.mockButton = QtWidgets.QPushButton("Mock Live")
        #self.mockButton.setMaximumWidth(S_BTN_WID)
        #self.mockButton.clicked.connect(self.mock_button_pressed)

        # Y Range setup 
        self.y_min = QtWidgets.QLineEdit()
        self.y_min.setFixedWidth(120)
        self.y_min.editingFinished.connect(lambda: self.set_y_range(self.y_min.text(), y_max=False))
        self.y_max = QtWidgets.QLineEdit()
        self.y_max.setFixedWidth(120)
        self.y_max.editingFinished.connect(lambda: self.set_y_range(self.y_max.text(), y_max=True))
        self.data_line = self.graph.plot(self.x,self.y, pen=Pens.RED.value)

        self.y_range = self.graph.getViewBox().viewRange()[0]

        self.graph.setTitle(f"Graph {name}", color="b", size='20pt')        
        self.graph.showGrid(x=True, y=True)
        #g.setBackground("w")

        # Layout configuration
        self.bar_layout.addWidget(self.browse_btn)
        self.bar_layout.addWidget(self.browse_lbl)
        self.bar_layout.addSpacing(40)
        self.bar_layout.addWidget(QtWidgets.QLabel("y_min"))
        self.bar_layout.addWidget(self.y_min)
        self.bar_layout.addWidget(QtWidgets.QLabel("y_max"))
        self.bar_layout.addWidget(self.y_max)
        self.bar_layout.addStretch(2)
        self.main_layout.addWidget(self.graph)
        self.main_layout.addLayout(self.bar_layout)

        # Start a timer function - Need a timer to update graph at certain speed.
        self.timer = QtCore.QTimer()                        # Initialize a timer
        self.timer.setTimerType(QtCore.Qt.PreciseTimer)
        self.timer.setInterval(self.sample_T_ms)  # Set the timer interval
        if self.bus:
            self.timer.timeout.connect(self.live_plot_update)   # Set timeout behaviour
            self.timer.start()                                  # Start timer

    def set_y_range(self, value, y_max=False):
        """Set the y_range of the graph object.
            value: value to set:
            y_max: set y_max if true, else set y_min
        """
        if not value.isdigit():
            return
        
        # Debug print for testing
        #print(f"setting {"y_max" if y_max else "y_min"} to {value}")
        old_y_range = self.graph.getViewBox().viewRange()[1]
        if y_max:
            self.y_range = (old_y_range[0], int(value))
        else:
            self.y_range = (int(value), old_y_range[1])
        
        self.graph.setYRange(*self.y_range)

    def file_button_pressed(self):
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
            self.rename_graph(self.graph, f"Graph of {fnames[0]}") # TODO: FIX THIS (only uses first name)
            self.plot_static(g_id, filenames[0])
        else:
            print("No File Selected")
            lbl_str = "No File Selected"
            filenames = "None"

        self.browse_lbl.setText(f"File: {lbl_str}")
        print("choose file pressed")

        return filenames

    def plot_button_pressed(self):
        """What happens when the plot button is pressed"""
        print("plot pressed")

    def mock_button_pressed(self):
        """What happens when the mock button is pressed"""
        print("mock pressed")
    
    def yrange(self):
        return


    def rename_graph(self, graph, name: str, col="b", sz="20pt"):
        """A function that renames the graph for easy renaming"""
        graph.setTitle(name, color=col, size=sz)

    def plot_static(self, inFile:str, isolate=True):
        """ Plots static data - file formats described in read_file method"""
        # Clear given plot
        if isolate:
            self.graph.clear()
        # Pull Data from file (supported files?)
        x, data = self.read_file(inFile)
        # Plot the data
        for idx, source in enumerate(data):
            self.graph.plot(x, source, pen=self.pens[idx])

    # TODO: Make this read multiple filetypes
    # TODO: Create Error handling dialogues
    # DONE: Make this accept files with two (NOW FIVE)  columns x and y
    # DONE: Allow first column to be X values
    def read_file(self, file, add_x=True):
        """ A Function that reads a file, and returns x and y lists 
            Currently only supports files with numbers on newlines."""

        with open(file, 'r') as f:
            dat = f.read()
        
        data = [[float(g) for g in x.split(',')] for x in dat.strip().split('\n')]
        
        if len(data[0]) >= 5:
            print("Currently PyChart Cannot handle more than 5 input columns")
            print("Only the first five data columns will be seen!!")

        if add_x:
            x = [i for i in range(0,len(data))]
        else:
            x = [line[0] for line in data]
            data = [line[1:] for line in data]

        out_data = np.array(data)
        out_data = out_data.transpose()

        return x, out_data.tolist()

    # DONE: Mess with this and allow live plotting!
    # TODO: Generalize this and allow multiple plotting streams!
    def live_plot_update(self):
        """The main function for live drawing: At the moment utilizes random data"""
        if not self.bus:
            print("No Live Plotting Available (No Serial Present)")
            return
                
        #data = int.from_bytes(self.bus.read(1), 'little')
        #data = str(self.bus.readline().decode()).strip().split(',')
        raw_data = str(self.bus.read_all().decode()).strip().replace("\r", "")

        data = []

        for line in raw_data.split("\n"):
            if "DMA" in line or "SOMETHING" in line or line.strip() == "":
                continue
            data.extend([int(x) for x in line.strip().split(",") if x != ""])

        if len(data) == 0:
            return 

        #print(data)
        #print(len(data))

        self.x = self.x[len(data):]
        self.y = self.y[len(data):]
        #print(len(self.x), len(self.y))

        last_x_val = self.x[-1] + 1

        self.x.extend(list(range(last_x_val, last_x_val + len(data))))
        self.y.extend(data)

        #print(len(self.x), len(self.y))
        self.data_line.setData(self.x, self.y)

class PyChart(QtWidgets.QMainWindow):
    def __init__(self, n_g=1, f_s=20, *args, **kwargs):
        """Standard init function. Sets some variables 
           Specify number of desired graphs with the n_g parameter"""

        super(PyChart, self).__init__(*args, **kwargs)
        self.title = "Py-Chart"
        self.width = 1280
        self.height = 960
        self.init_graphs_no = n_g
        self.num_graphs=0

        # Setup for modifiable layouts
        self.graphWidgets = []
        
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

    # TODO: Add error Dialogue
    def create_graph_view(self):
        """ A method that creates  graph view up to 10"""
        # Do not allow more than 10 graphs to be created
        if(self.num_graphs >= 10):
            print("Cannot create another graph!")
            return -1

        name = f"/tty/ACM0" 

        new_graph_widget = GraphWidget(name=name)
        self.graphWidgets.append(new_graph_widget)
        self.graph_layout.addLayout(new_graph_widget.main_layout)
        self.num_graphs += 1

    
def main():
    app = QtWidgets.QApplication(sys.argv)
    main = PyChart(f_s= 50, n_g=1)
    main.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
