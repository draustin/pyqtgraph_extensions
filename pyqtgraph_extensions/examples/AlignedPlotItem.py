"""Illustrate AlignedPlotItem, which uses its parent graphics layout for its
internal elements. This allows them to be aligned with other items in the
layout."""
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph_extensions as pgx

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


## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()