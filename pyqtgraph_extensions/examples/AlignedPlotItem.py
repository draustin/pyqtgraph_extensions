"""Illustrate AlignedPlotItem, which uses its parent graphics layout for its
internal elements. This allows them to be aligned with other items in the
layout."""
import sys
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph_extensions as pgx

if QtGui.QApplication.instance() is None:
    qapp=QtGui.QApplication(sys.argv)
else:
    # Presumably running in a GUI with event QApplication already created
    qapp=None

# Original GraphicsLayoutWidget with PlotItems. The label of the left axis
# of the first PlotItem is two lines, the left axes of the PlotItems aren't 
# aligned.
gl=pg.GraphicsLayoutWidget()
plt1=gl.addPlot(labels={'left':'long axis name<br>(some units)','bottom':'x'},title='PlotItem 1')
gl.nextRow()
plt2=gl.addPlot(labels={'left':'y (units)','bottom':'x'},title='PlotItem 2')
gl.show()
##
# Same thing with AlignedPlotItems. An extended GraphicsLayoutWidget is needed
# for these. Because they use their parent's layout grid for
# their components (axes, title, ViewBox) these components are aligned.
glx=pgx.GraphicsLayoutWidget()
aplt1=glx.addAlignedPlot(labels={'left':'long axis name<br>(some units)','bottom':'x'},title='AlignedPlotItem 1')
# aplt1 takes up 4 rows (title, top axis, view box, and bottom axis). 
glx.nextRows() # defaults to 4x glx.nextRow()
aplt2=glx.addAlignedPlot(labels={'left':'y (units)','bottom':'x'},title='AlignedPlotItem 2')
glx.show()

if qapp is not None:
    sys.exit(qapp.exec_())
