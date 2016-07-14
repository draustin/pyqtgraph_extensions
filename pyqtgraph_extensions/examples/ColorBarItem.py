"""Illustrate ColorBarItem, a MATLAB-like color bar suited for non-interactive
publication plots."""
import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph_extensions as pgx

# import logging
# logging.basicConfig(level=logging.DEBUG)
# logging.getLogger(pgx.__name__).setLevel(level=logging.DEBUG)

# Generate 2D Gaussian distribution
x=np.arange(100)-50
y=np.arange(110)[:,None]-55
z_0=np.exp(-(x**2+y**2)/100.0)

glw=pg.GraphicsLayoutWidget()
plt=glw.addPlot(title='ColorBarItem demo',labels={'left':'y','bottom':'x'})
im=pgx.ImageItem()
im.setLookupTable(pgx.get_colormap_lut())
plt.addItem(im)
# Add a color bar, linked to the image. It can go anywhere but we place it in
# the next column.
cb=pgx.ColorBarItem(image=im,label='intensity')
glw.addItem(cb)

def update():
    t=pg.time()
    # Create amplitude-modulated noisy Gaussian
    z=np.sin(t)**2*z_0+np.random.random(z_0.shape)*0.1
    levels=im.levels
    im.setImage(z,autoLevels=False)
update()
# The first setImage disables autorange...
cb.vb.enableAutoRange(1)
glw.show()


timer = QtCore.QTimer()
timer.timeout.connect(update)
timer.start(50)

## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()