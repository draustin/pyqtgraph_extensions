import numpy as np
import pyqtgraph as pg
from PyQt5.QtWidgets import QApplication

import pyqtgraph_extensions as pgx

##
app = QApplication([])

glw = pg.GraphicsLayoutWidget()
plt = glw.addPlot(title='Testing colormaps', labels={'left': 'y', 'bottom': 'x'})
im = pgx.ImageItem()
im.setLookupTable(pgx.get_colormap_lut())
x = np.arange(10)
y = np.arange(11)[:, None]
z = x + 1.1 * y
z[3, :] = np.nan
im.setImage(z)
plt.addItem(im)
cb = pgx.ColorBarItem(image=im)
# cb.setManual(lut=im.lut, levels=im.levels)
# cb.setLabel('intensity')
glw.addItem(cb)
glw.show()

app.exec()
