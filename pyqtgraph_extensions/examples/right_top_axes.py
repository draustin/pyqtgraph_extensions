"""Demo add_right_axis, allowing a right-hand y-axis with the same x-axis."""
import sys
import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph_extensions as pgx

if QtGui.QApplication.instance() is None:
    qapp=QtGui.QApplication(sys.argv)
else:
    # Presumably running in a GUI with event QApplication already created
    qapp=None

## Demo add_right_axis.
plt=pg.PlotWindow(labels={'left':'left-hand y-axis','bottom':'x axis'})
# Make left y-axis blue ...
plt.getAxis('left').setPen('b')
# ... and color its data the same
plt.plot([0,1],[0,1],pen='b')
# Make a right y-axis, with linked x-axis.
right_plot=pgx.add_right_axis(plt,pen='r',label='right-hand y axis')
right_plot.plot([0,1],[1,0],pen='r')

## Same as above, but with top axis.
plt=pg.PlotWindow(labels={'left':'y-axis','bottom':'bottom x axis'})
plt.getAxis('bottom').setPen('b')
plt.plot([0,1],[0,1],pen='b')
right_plot=pgx.add_top_axis(plt,pen='r',label='top x axis')
right_plot.plot([0,1],[1,0],pen='r')

if qapp is not None:
    sys.exit(qapp.exec_())