"""Show how multiple AlignedPlotItems have aligned AxisItems by using their parent's graphics layout."""
import sys
from textwrap import wrap
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph_extensions as pgx

if QtGui.QApplication.instance() is None:
    qapp=QtGui.QApplication(sys.argv)
else:
    # Presumably running in a GUI with event QApplication already created
    qapp=None

long_label = 'multiline<br>axis label<br>(e.g. complex units)'

# To hold AlignedPlotItems, need to use the extended version of GraphicsLayout/GraphicsLayoutWidget.
glwx=pgx.GraphicsLayoutWidget()
glwx.addLabel('<br>'.join(wrap("<em>pyqtgraph PlotItem</em> - since the label of the left axis of the first PlotItem is"
                               "two lines, the left axes of the PlotItems aren't aligned.", 40)))
glwx.addHorizontalSpacer(100)
glwx.addLabel('<br>'.join(wrap("<em>pyqtgraph_extensions AlignedPlotItem</em> - because they use their parent's layout"
                               "grid for their components (axes, title, ViewBox) these components are aligned.", 40)))
glwx.nextRow()

# Make left column showing pyqtgraph PlotItems.
glo=pg.GraphicsLayout()
glwx.addItem(glo)
plt1=glo.addPlot(labels={'left':long_label, 'bottom': 'x'},title='PlotItem 1')
glo.nextRow()
plt2=glo.addPlot(labels={'left':'y (units)','bottom':'x'},title='PlotItem 2')
glwx.nextColumn()
# Make right column showing pyqtgraph_extensions AlignedPlotItems.
glx=pgx.GraphicsLayout()
glwx.addItem(glx)
aplt1=glx.addAlignedPlot(labels={'left':long_label, 'bottom': 'x'},title='AlignedPlotItem 1')
# aplt1 takes up 4 rows (title, top axis, view box, and bottom axis).
glx.nextRows() # equivalent to 4 calls glx.nextRow()
aplt2=glx.addAlignedPlot(labels={'left':'y (units)','bottom':'x'},title='AlignedPlotItem 2')
glwx.resize(800,400)
glwx.show()

if qapp is not None:
    sys.exit(qapp.exec_())
