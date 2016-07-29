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

# 2D Gaussian
x=np.linspace(-20,20,100)
y=np.linspace(-30,30,150)[:,None]
z=np.exp(-(x**2+y**2)/10)

# Setting window title and size at creation...
gl=pgx.GraphicsLayoutWidget(window_title='window title',size=(300,600))
# Make the PlotItem span 3 columns to match the AlignedPlotItem below
plt1=gl.addPlot(colspan=3)
# Add text in anchored to the corner of a plot - useful for publications
pgx.cornertext('(a)',plt1,(1,0))
# Easy access to the tableau10 and tableau20 color palette
plt1.plot([0,1],[0,1],pen=pgx.tableau10[4])
gl.nextRow()
plt2=gl.addAlignedPlot()
pgx.cornertext('(b)',plt2,(0,0),color='r')
# Add image easily, can use axes_to_rect to easily generate the required QRect
im=plt2.image(z,rect=pgx.axes_to_rect(x,y))
# add color bar - we want it in the same row as the viewbox, which is the current
# row plus 2
gl.addColorBar(image=im,rel_row=2)
gl.show()

if qapp is not None:
    sys.exit(qapp.exec_())