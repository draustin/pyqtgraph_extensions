import numpy as np
import pyqtgraph as pg
import pyqtgraph_extensions as pge


##
def test_nans(qtbot):
    x = np.arange(100)
    y = np.arange(120)[:, None]
    f = np.exp(-((x - 50) ** 2 + (y - 60) ** 2) / 200)
    fp = f.copy()
    fp[0, 0] = float("nan")
    fp[f < 0.2] = float("nan")
    plt = pg.plot()
    im = pge.ImageItem(fp)
    im.setRect(pge.axes_to_rect(x, y))
    im.setLookupTable(pge.get_colormap_lut())
    im.setLevels((0, 1))
    plt.addItem(im)

# I wrote this to test pyqtgraph_extensions' handling of images with zero-sized arrays.
# But then I realized that pyqtgraph itself doesn't handle them.
# def test_zero_size_image(qtbot):
#     widget = pg.PlotWidget()
#     array = np.zeros((0, 0))
#     image = pg.ImageItem(array)
#     widget.addItem(image)
#     qtbot.addWidget(widget)


## Investigate how to make a mask e.g. to grey out undefined values. Belongs elsewhere.
# f3=pg.makeARGB(f,pg.get_colormap_lut(),levels=(0,1),useRGBA=True)[0]#[:,:,[1,2,3,0]]
# f3[f<0.1]=[128,128,128,128]
# plt=pg.plot()
# im=pg.ImageItem(f3)
# im.setRect(pg.axes_to_rect(x,y))
# #im.setLookupTable(pg.get_colormap_lut())
# plt.addItem(im)
