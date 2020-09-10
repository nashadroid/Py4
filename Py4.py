from numpy import loadtxt
from numpy.fft import fft, fftfreq
import numpy as np
from matplotlib import pyplot as plt
import warnings

import sys
import matplotlib
matplotlib.use('Qt5Agg')

from PyQt5 import QtCore, QtGui, QtWidgets

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure


class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=4, height=3, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):

        self.probeNums = []
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setWindowTitle("Py4")

        self.sc = MplCanvas(self, width=4, height=3, dpi=100)
        self.sc.axes.plot([0,1,2,3,4], [10,1,20,3,40])
        self.sc.setMinimumSize(500,400)

        # Create toolbar, passing canvas as first parameter, parent (self, the MainWindow) as second.
        toolbar = NavigationToolbar(self.sc, self)

        # Probe Select
        self.listWidget = QtWidgets.QListWidget()
        self.listWidget.setSelectionMode(
        QtWidgets.QAbstractItemView.ExtendedSelection
        )
        self.listWidget.setGeometry(QtCore.QRect(10, 10, 211, 291))
        for probe in probes:
                item = QtWidgets.QListWidgetItem(probe)
                self.listWidget.addItem(item)
        self.listWidget.itemClicked.connect(self.update_plot)
        self.listWidget.setMinimumSize(100,200)
        
        # Options
        self.fft = QtWidgets.QCheckBox("fft")
        self.logx = QtWidgets.QCheckBox("Log-X")
        self.logy = QtWidgets.QCheckBox("Log-Y")

        self.fft.stateChanged.connect(self.update_plot)
        self.logx.stateChanged.connect(self.update_plot)
        self.logy.stateChanged.connect(self.update_plot)

        self.options = QtWidgets.QHBoxLayout()

        self.options.addWidget(self.fft)
        self.options.addWidget(self.logx)
        self.options.addWidget(self.logy)

        self.optionsWidget = QtWidgets.QWidget()
        self.optionsWidget.setLayout(self.options)
        
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.listWidget)
        layout.addWidget(self.optionsWidget)
        layout.addWidget(toolbar)
        layout.addWidget(self.sc)

        # Create a placeholder widget to hold our toolbar and canvas.
        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        self.show()

    def update_plot(self):

        selectedItemText = [item.text() for item in self.listWidget.selectedItems()]
        self.probeNums = [i for i, probe in enumerate(probes) if probe in selectedItemText]

        self.sc.axes.cla()  # Clear the canvas.

        units = []

        for probeNum in self.probeNums:
            # Extract the label and unit of each probe
            [_ , label , unit] = probes[probeNum].split(": ")
            units.append(unit)
        
            #plot
            if self.fft.isChecked():
                #npArray = np.array([probeData[: , probeNum+1]])
                fftArray = fft(probeData[: , probeNum+1])
                fftFreqArray = fftfreq(len(probeData[: , probeNum+1]), d=(probeData[1,1]*1e-9))
                fftArray = np.fft.fftshift(fftArray)
                fftFreqArray = np.fft.fftshift(fftFreqArray)
                self.sc.axes.plot(fftFreqArray, abs(fftArray), label=label)
                self.sc.axes.set_xlabel("Frequency (s-1)")
            else:
                self.sc.axes.plot(probeData[: , 1], probeData[: , probeNum+1], label=label)
                self.sc.axes.set_xlabel("Time (ns)")

        # Reduce list of units to remove repeats
        units = list(dict.fromkeys(units))

        # Warn if there are more than one units used
        if len(units) > 1:
            warnings.warn("WARNING: Multiple units plotted")

        # Check and do log options
        if self.logx.isChecked():
            self.sc.axes.set_xscale('log')

        if self.logy.isChecked():
            self.sc.axes.set_yscale('log')

        self.sc.axes.set_ylabel(units[0])

        if len(self.probeNums) > 1 :
            self.sc.axes.legend()

        # Trigger the canvas to update and redraw.
        self.sc.draw()

print("Welcome to Py4")
file = "history.p4"
probes = []

# Load in probe labels
with open(file, 'r') as f:

    # Get a list of lines
    lines = f.readlines()

    # Check if correct file type
    try:
        if "#File type: probes" not in lines[2]:
            warnings.warn("WARNING: File may not be probe format")
    except:
        print("Cannot Read File")
        exit(1)

    # Make a list with all the probe names
    for line in lines[4:]:
        if line[0] == '#':
            probes.append(str(line[1:-1]))

# Load in the actual data, yes I know it's inefficient to open the file twice
print("Loading history.p4...")
probeData = loadtxt(file, comments="#", delimiter=" ", unpack=False)

print("Launching GUI")
app = QtWidgets.QApplication(sys.argv)
w = MainWindow()
app.exec_()


