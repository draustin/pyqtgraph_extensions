import pyqtgraph as pg
import pyqtgraph.functions as fn
import numpy as np
from . import AxisItem
from pyqtgraph import QtCore,QtGui

class ImageItem(pg.ImageItem):
    sigColorMapChanged = QtCore.Signal()
    def __init__(self, image=None, **kargs):
        pg.ImageItem.__init__(self,image,**kargs)
    def setLevels(self, levels, update=True):
        """
        Set image scaling levels. Can be one of:
        
        * [blackLevel, whiteLevel]
        * [[minRed, maxRed], [minGreen, maxGreen], [minBlue, maxBlue]]
            
        Only the first format is compatible with lookup tables. See :func:`makeARGB <pyqtgraph.makeARGB>`
        for more details on how levels are applied.
        """
        emit=self.levels!=levels
        pg.ImageItem.setLevels(self,levels,update)
        if emit:
            self.sigColorMapChanged.emit()
        
class LegendItem(pg.LegendItem):
    """
    Customisation subclass of pyqtgraph.LegendItem for:
        * control over background color - defaults to pyqtgraph's default
    """
    def __init__(self, size=None, offset=None,background_color=None):
        pg.LegendItem.__init__(self,size,offset)
        if background_color is None:
            background_color=pg.CONFIG_OPTIONS['background']
        self.background_color=background_color
    def paint(self, p, *args):
        p.setPen(fn.mkPen(255,255,255,100))
        p.setBrush(fn.mkBrush(self.background_color))
        p.drawRect(self.boundingRect())
        
class ColorBarItem(pg.GraphicsWidget):
    """A color bar for an ImageItem.
    
    Vertical, with AxisItem for scale on the right side (could be extended to
    other orientations and scale on other side). Doesn't respond to changes in 
    ImageItem lookup table or levels - will need appropriate signals from
    ImageItem for this.
    """
    def __init__(self,parent=None,image=None,label=None):
        pg.GraphicsWidget.__init__(self,parent)
        self.bar=pg.ImageItem()
        self.bar.setParentItem(self)
        self.bar.setImage(np.arange(256)[None,:])
        self.axis=pg.AxisItem(orientation='right',parent=self)        
        self.rect_width=10
        self.left_marg=5        
        self.setWidth()
        self.image=None
        self.setImage(image)
        if label is not None:
            self.setLabel(label)
    def resizeEvent(self,ev):
        y=0#max(-self.axis.boundingRect().y(),0)
        self.bar.setRect(QtCore.QRectF(self.left_marg,self.height(),self.rect_width,-self.height()))
        self.axis.setGeometry(self.left_marg+self.rect_width,y,self.width()-self.rect_width-self.left_marg,self.height()-y)
    def setLabel(self,label):
        self.axis.setLabel(label)
        self.setWidth()
    def setWidth(self):
        self.setMinimumWidth(self.left_marg+self.rect_width+self.axis.minimumWidth())
    def setImage(self,image):
        if self.image is not None:
            print('TODO disconnect')
        self.image=image
        if self.image is not None:
            self.update()
            self.image.sigColorMapChanged.connect(self.update)
    def update(self):
        self.bar.setLookupTable(self.image.lut)
        for _ in range(2):
            # Strange apparent bug in pyqtgraph.AxisItem - doesn't update
            # after only one call. TODO report
            self.axis.setRange(*self.image.levels)
        
class ViewBox(pg.ViewBox):
    """Convenience extension of ViewBox providing plot functions.
    
    This is necessary for seamless use of pyqtgraph.add_right_axis."""
    def __init__(self,**kwargs):
        pg.ViewBox.__init__(self,**kwargs)
    
    def plot(self, *args, **kargs):
        """
        Add and return a new plot.
        See :func:`PlotDataItem.__init__ <pyqtgraph.PlotDataItem.__init__>` for data arguments
        """
        item = pg.PlotDataItem(*args, **kargs)
        self.addItem(item)
        return item
        
        
class PlotWindow(pg.PlotWindow):
    """Adds some features to PlotWindow class."""
    def _repr_png_(self):
        """Generate png representation for ipython notebook.
        
        Thanks to
        https://groups.google.com/forum/#!msg/pyqtgraph/Nu921kIkeFk/tmvn-BR_BQ0J
        """
        # Need to keep a reference to the image, otherwise Qt segfaults
        self._repr_png_image = QtGui.QImage(self.size(),
                            QtGui.QImage.Format_RGB32)
        painter = QtGui.QPainter(self._repr_png_image)
        self.render(painter)

        byte_array = QtCore.QByteArray()
        buffer = QtCore.QBuffer(byte_array)
        buffer.open(QtCore.QIODevice.ReadWrite)
        self._repr_png_image.save(buffer, 'PNG')
        buffer.close()

        return bytes(byte_array)