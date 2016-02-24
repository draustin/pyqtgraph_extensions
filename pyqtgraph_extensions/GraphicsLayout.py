import pyqtgraph as pg
from pyqtgraph import QtCore,QtGui
from . import AlignedPlotItem,ColorBarItem

class GraphicsLayout(pg.GraphicsLayout):
    """Like pyqtgraph.GraphicsLayout except supports items which can
    span multiple rows & columns of the interal QtGui.QGraphicsGridLayout. Such
    items are (normal items are supported as well):
        pyqtgraph_ex.AlginedPlotItem
    """
    def __init__(self, parent=None, border=None):
        pg.GraphicsLayout.__init__(self,parent,border)
        self.setSpacing(0)
    def addAlignedPlot(self, row=None, col=None, **kwargs):
        """
        Create an AlignedPlotItem starting in the next available cell (or in the cell specified)
        All extra keyword arguments are passed to :func:`AlignedPlotItem.__init__ <pyqtgraph_ex.AlignedPlotItem.__init__>`
        Returns the created item.
        """
        if row is None:
            row = self.currentRow
        if col is None:
            col = self.currentCol
        
        plot = AlignedPlotItem(self,(row,col),**kwargs)
        
        self.currentCol=col+3
        return plot
    def addLayout(self, row=None, col=None, rowspan=1, colspan=1, **kargs):
        """
        Create an empty GraphicsLayout and place it in the next available cell (or in the cell specified)
        All extra keyword arguments are passed to :func:`GraphicsLayout.__init__ <pyqtgraph.GraphicsLayout.__init__>`
        Returns the created item.
        """
        layout = GraphicsLayout(**kargs)
        self.addItem(layout, row, col, rowspan, colspan)
        return layout
    def addColorBar(self,row=None,rel_row=None,col=None,rowspan=1,colspan=1,**kwargs):
        cbar=ColorBarItem(self,**kwargs)
        if rel_row is None:
            rel_row=0
        if row is None:
            row=self.currentRow
        self.addItem(cbar,row=row+rel_row,col=col,rowspan=rowspan,colspan=colspan)
    def nextRows(self,N=4):
        for n in range(N):
            self.nextRow()
    def nextCols(self,N=2):
        for n in range(N):
            self.nextCol()
    def addHorizontalSpacer(self,width=10,row=None,col=None):
        spacer=pg.GraphicsWidget()
        spacer.setFixedWidth(width)
        spacer.setFixedHeight(0)
        self.addItem(spacer,row,col)
    def addVerticalSpacer(self,height=10,row=None,col=None):
        spacer=pg.GraphicsWidget()
        spacer.setFixedWidth(0)
        spacer.setFixedHeight(height)
        self.addItem(spacer,row,col)
    def setRowStretchFactor(self,factor,row=None,rel_row=None):
        if rel_row is None:
            rel_row=0
        if row is None:
            row=self.currentRow
        self.layout.setRowStretchFactor(row+rel_row,factor)
    def setColumnStretchFactor(self,factor,col=None,rel_col=None):
        if rel_col is None:
            rel_col=0
        if col is None:
            col=self.currentCol
        self.layout.setColumnStretchFactor(col+rel_col,factor)
        
class GraphicsLayoutWidget(pg.GraphicsView):
    def __init__(self, parent=None, **kwargs):
        pg.GraphicsView.__init__(self, parent)
        self.ci = GraphicsLayout(**kwargs)
        for n in ['nextRow', 'nextCol', 'nextColumn', 'addPlot', 'addViewBox', 'addItem', 'getItem', 'addLayout', 'addLabel',
        'removeItem', 'itemIndex', 'addAlignedPlot', 'nextRows', 'nextCols', 'addColorBar', 'nextRows', 'addHorizontalSpacer', 'addVerticalSpacer', 'setRowStretchFactor', 'setColumnStretchFactor']:
            setattr(self, n, getattr(self.ci, n))
        self.setCentralItem(self.ci)
    def clear(self):
        self.ci.clear()
        # Remove additional top-level items in scene
        items=[item for item in self.scene().items() if item is not self.ci and item.parentItem() is None]
        for item in items:
            self.scene().removeItem(item)
            
    def _repr_png_(self):
        """Generate png representation for ipython notebook.
        
        Thanks to
        https://groups.google.com/forum/#!msg/pyqtgraph/Nu921kIkeFk/tmvn-BR_BQ0J
        """
        # put this in in the hope that it would apply the layout resizing
        # before converting to PNG. It still doesn't. So in notebook, have to
        # use separate cells
        QtGui.QApplication.processEvents()
        # Need to keep a reference to the image, otherwise Qt segfaults
        self._repr_png_image = QtGui.QImage(self.viewRect().size().toSize(),
                            QtGui.QImage.Format_RGB32)
        painter = QtGui.QPainter(self._repr_png_image)
        self.render(painter)

        byte_array = QtCore.QByteArray()
        buffer = QtCore.QBuffer(byte_array)
        buffer.open(QtCore.QIODevice.ReadWrite)
        self._repr_png_image.save(buffer, 'PNG')
        buffer.close()

        return bytes(byte_array)