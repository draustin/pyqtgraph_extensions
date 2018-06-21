import logging,math
import pyqtgraph as pg
import pyqtgraph.functions as fn
import numpy as np
from . import AxisItem
from pyqtgraph import QtCore,QtGui

logger=logging.getLogger(__name__)

class IPythonPNGRepr:
    """Class which can represent itself as a PNG in an IPython notebook.

    Subclasses need to define method get_repr_png_image() which returns a
    QImage.    
    """
    def _repr_png_(self):
        """Generate png representation for ipython notebook.
        
        Thanks to
        https://groups.google.com/forum/#!msg/pyqtgraph/Nu921kIkeFk/tmvn-BR_BQ0J
        """
        # Need to keep a reference to the image, otherwise Qt segfaults
        self._repr_png_image=self.get_repr_png_image()
        byte_array = QtCore.QByteArray()
        buffer = QtCore.QBuffer(byte_array)
        buffer.open(QtCore.QIODevice.ReadWrite)
        self._repr_png_image.save(buffer, 'PNG')
        buffer.close()
        
        return bytes(byte_array)
        
class ImageItem(pg.ImageItem):
    sigLevelsChanged = QtCore.Signal()
    sigLookupTableChanged = QtCore.Signal()
    
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
        emit=self.levels is None or not np.allclose(self.levels,levels)
        pg.ImageItem.setLevels(self, levels, update)
        if emit:
            self.sigLevelsChanged.emit()
            
    def setLookupTable(self, lut, update=True, emit=True):
        """
        Set the lookup table (numpy array) to use for this image. (see 
        :func:`makeARGB <pyqtgraph.makeARGB>` for more information on how this is used).
        Optionally, lut can be a callable that accepts the current image as an 
        argument and returns the lookup table to use.
        
        Ordinarily, this table is supplied by a :class:`HistogramLUTItem <pyqtgraph.HistogramLUTItem>`
        or :class:`GradientEditorItem <pyqtgraph.GradientEditorItem>`.
        """
        pg.ImageItem.setLookupTable(self, lut, update)
        if emit:
            self.sigLookupTableChanged.emit()
    
    def setImage(self,image=None,autoLevels=True,levels=None,**kwargs):
        """Add behaviour that if autoLevels is False and levels is None, levels
        is set to current (if that is not None). (In original, this causes an error.)"""
        if levels is None and not autoLevels:
            if self.levels is not None:
                logger.debug('setImage retaining levels')
                levels=self.levels
            else:
                autoLevels=True
        pg.ImageItem.setImage(self,image=image,autoLevels=autoLevels,levels=levels,**kwargs)
        
class LegendItem(pg.LegendItem):
    """
    Customisation subclass of pyqtgraph.LegendItem for:
        * control over background and border color - defaults to pyqtgraph's default
        * control over spacing of items
    """
    def __init__(self, size=None, offset=None,background_color=None,border_color=None,margins=None,vertical_spacing=None):
        """
        Args:
            margins (left,top,right,bottom): if not None, set layout margins. 
                (0,0,0,0) is usually a good choice. If None, uses pyqtgraph
                defaults
            vertical_spacing (int): if not None, set vertical spacing between items.
                0 is a good choice. If None, use pyqtgraph default.
        """
        pg.LegendItem.__init__(self,size,offset)
        if background_color is None:
            background_color=pg.CONFIG_OPTIONS['background']
        if border_color is None:
            border_color=pg.CONFIG_OPTIONS['foreground']
        self.background_color=background_color
        self.border_color=border_color
        if margins is None:
            margins=0,0,0,0
        self.margins=margins
        #if margins is not None:
        #    self.layout.setContentsMargins(*margins)
        if vertical_spacing is not None:
            self.layout.setVerticalSpacing(vertical_spacing)
        
    def paint(self, p, *args):
        p.setPen(fn.mkPen(self.border_color))
        p.setBrush(fn.mkBrush(self.background_color))
        p.drawRect(self.boundingRect())
        
    def setTextStyle(self,*args,**kwargs):
        """Arguments passed on to setText of every LabelItem."""
        for sample,label in self.items:
            label.setText(label.text,*args,**kwargs)
            
    # def updateSize(self):
    #     if self.size is not None:
    #         return
    #         
    #     height = 0
    #     width = 0
    #     #print("-------")
    #     for sample, label in self.items:
    #         height += max(sample.height(), label.height()) + 3
    #         width = max(width, (sample.sizeHint(QtCore.Qt.MinimumSize, sample.size()).width() +
    #                             label.sizeHint(QtCore.Qt.MinimumSize, label.size()).width()))
    #         #print(width, height)
    #     #print width, height
    #     self.setGeometry(0, 0, width+25, height)
            
    def updateSize(self):
        # Modified from pyqtgraph's original to use minimumWidth() rather than
        # width() on items (likewise for height), to prevent runaway growth of 
        # legend with repeated calling of updateSize. Then original pyqtgraph fixed the bug. But
        # still want margin and verticalSpacing feature.
        if self.size is not None:
            return
        margins=self.margins#layout.getContentsMargins()
        height = margins[1]
        width = margins[0]
        for sample, label in self.items:
            height += max(sample.height(), label.height()) + self.layout.verticalSpacing()
            width = max(width, (sample.sizeHint(QtCore.Qt.MinimumSize, sample.size()).width() +
                                label.sizeHint(QtCore.Qt.MinimumSize, label.size()).width()))
        self.setGeometry(0, 0, width+margins[2], height+margins[3]) # D

class ViewBox(pg.ViewBox):
    """Convenience extension of ViewBox providing:
    
        * plot function (necessary for seamless use of pyqtgraph.add_right_axis)
        * ability to override the default padding, which is used by enableAutoRange
    """
    def __init__(self,**kwargs):
        pg.ViewBox.__init__(self,**kwargs)
        self.suggested_padding=[None,None]
    
    def plot(self, *args, **kargs):
        """
        Add and return a new plot.
        See :func:`PlotDataItem.__init__ <pyqtgraph.PlotDataItem.__init__>` for data arguments
        """
        item = pg.PlotDataItem(*args, **kargs)
        self.addItem(item)
        return item
        
    def suggestPadding(self, axis):
        suggested=self.suggested_padding[axis]
        if suggested is None:
            return pg.ViewBox.suggestPadding(self,axis) 
        else:
            return suggested
            
class ColorBarItem(pg.GraphicsWidget):
    """A color bar for an ImageItem.
    
    Vertical, with AxisItem for scale on the right side (could be extended to
    other orientations and scale on other side).
    
    Has two modes. If self.image is None, then it is in manual mode. The LUT and
    levels are set by setManual. Otherwise, it is is in automatic mode, linked to
    self.image, which must be a pgx.ImageItem. It responds to changes in the
    image's lookup table, levels and range. The user can adjust the axis with the
    mouse like a normal axis. Autoscaling works.
    
    The implementation uses a viewbox containing an imageitem with an axisitem
    beside it. The imageitem vertical extent is set to the color range of the image.
    In this way, the autorange functionality of the viewbox and axisitem are
    put to use. It's probably not optimally efficient.
    """
    def __init__(self,parent=None,image=None,label=None,images=()):
        pg.GraphicsWidget.__init__(self,parent)
        """Previous version used manual layout. This worked for initial setup but
        I couldn't figure out how to make it update automatically if e.g. the
        axis width changed. So switched to layout management. This requires
        the ImageItem to be in a QGraphicsLayoutItem, since it is not one itself.
        Putting it in a ViewBox seemed the simplest option."""
        # Backwards compatilbility: retain image argument
        if image is not None:
            assert images==()
            images=(image,)
        images=tuple(images)
        # Setup layout
        self.layout = QtGui.QGraphicsGridLayout()
        self.layout.setHorizontalSpacing(0)
        self.layout.setVerticalSpacing(0)
        self.layout.setContentsMargins(0,0,0,0)
        # Setup ViewBox containing the colorbar 
        self.vb=ViewBox()
        self.vb.setFixedWidth(10)
        self.vb.setLimits(xMin=0,xMax=1)
        self.vb.setMouseEnabled(x=False)
        self.vb.suggested_padding[1]=0
        # Setup colorbar, implemented as an ImageItem
        self.bar=pg.ImageItem()
        # The color bar ImageItem levels run from 0 to 1
        self.bar.setImage(np.linspace(0,1,8192)[None,:])
        self.vb.addItem(self.bar)
        self.layout.addItem(self.vb,0,0)    
        # Setup axis  
        self.axis=AxisItem(orientation='right')   
        self.axis.linkToView(self.vb)
        self.axis.range_changed.connect(self.axis_to_levels)
        self.layout.addItem(self.axis,0,1)
        
        self.setLayout(self.layout)
        self.images=()
        self.images_min={}
        self.images_max={}
        self.manual_lut=None
        self.manual_levels=None
        self.setImages(images)
        if label is not None:
            self.setLabel(label)
            
    def setLabel(self,label):
        self.axis.setLabel(label)
        
    def setImages(self,images):
        for image in self.images:
            # Hack - this connects all slots.
            image.sigLevelsChanged.disconnect()
            image.sigImageChanged.disconnect()
            image.sigLookupTableChanged.disconnect()
        self.images=images
        if self.images!=():
            self.update() # what does this do?
            self.lookupTableChanged(images[0])
            self.imageRangeChanged(images)
            for image in self.images:
                image.sigLevelsChanged.connect(lambda image=image:self.imageLevelsChanged(image))
                image.sigImageChanged.connect(lambda image=image:self.imageRangeChanged([image]))
                image.sigLookupTableChanged.connect(lambda image=image:self.lookupTableChanged(image))
            #self.vb.enableAutoRange(axis=1)
        else:
            self.updateManual()
        self.vb.setMouseEnabled(y=self.images!=())
        self.axis.setButtonsEnabled(self.images!=())
        # Found that without this, setting an image after ColorBarItem.__init__
        # was triggering an update auto range in the AxisItem, which screwed
        # up the level setting. Updating clears the ViewBox's internal flag.
        self.vb.updateAutoRange()
        
    def setImage(self,image):
        self.setImages((image,))
        
    def lookupTableChanged(self,image):
        """Sets the lookup table based on zeroth image."""
        self.bar.setLookupTable(image.lut)
        for im in self.images:
            if image is im:
                continue
            # When setting co-linked images, don't want them to emit the signal.
            im.setLookupTable(image.lut,emit=False)
        
    def imageRangeChanged(self,images):
        """Respond to change in the range of the images."""
        for image in images:
            image_data=image.image
            if image_data is None:
                return
            self.images_min[image]=image_data.min()
            self.images_max[image]=image_data.max()
        self.image_min=min(self.images_min.values())
        self.image_max=max(self.images_max.values())
        # Set spatial extent of bar to range of image
        logger.debug('setting bar extent to %g,%g',self.image_min,self.image_max)
        self.bar.setRect(QtCore.QRectF(0,self.image_min,1,self.image_max-self.image_min))
        self.updateBarLevels()
        
    def imageLevelsChanged(self,image):
        if not np.allclose(self.vb.viewRange()[1],image.levels):
            logger.debug('setYRange %g,%g',*image.levels)
            assert len(image.levels)==2
            if all(np.isfinite(image.levels)):
                self.vb.setYRange(*image.levels,padding=0)
            else:
                logger.info('skipping setYRange because np.levels is %s'%str(image.levels))
        self.updateBarLevels()
        
    def updateBarLevels(self):
        """Update the levels of the bar ImageItem from the image.
        
        These depend on both the image levels and the image range."""
        # Assume all images have same level
        image_levels=self.images[0].levels
        if not hasattr(self,'image_max'):
            # range has not been set yet
            return
        image_range=self.image_max-self.image_min 
        if image_range==0:
            bar_levels=0,0
        else:
            bar_levels=(image_levels[0]-self.image_min)/image_range,(image_levels[1]-self.image_min)/image_range
        logger.debug('setting bar levels to %g,%g',*bar_levels)
        self.bar.setLevels(bar_levels)
    
    def updateManual(self):
        if self.manual_levels is None or self.manual_lut is None:
            return
        self.vb.setYRange(*self.manual_levels,padding=0)
        self.bar.setRect(QtCore.QRectF(0,self.manual_levels[0],1,self.manual_levels[1]-self.manual_levels[0]))
        self.bar.setLookupTable(self.manual_lut)
    
    def setManual(self,lut=None,levels=None):
        self.manual_levels=levels
        self.manual_lut=lut
        self.updateManual()
            
    def axis_to_levels(self):
        logger.debug('axis_to_levels: axis.range=%g,%g',*self.axis.range)
        for image in self.images:
            if image.levels is None:
                continue
            # If new levels significantly different from old ones (use atol=0
            # to only get relative comparison), adjust image.
            if not np.allclose(image.levels,self.axis.range,atol=0):
                image.setLevels(self.axis.range)

            
class PlotWindow(pg.PlotWindow):
    """Adds some features to PlotWindow class."""
    # def __init__(self,**kwargs):
    #     pg.PlotWindow.__init__(self,**kwargs)
    #     # adjust_widget(self,**kwargs) - no, it already sets window title to title
        
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

class RectROI(pg.RectROI):
    def getVertices(self):
        """Return tuple of (x,y) coordinates of vertices."""
        # Lower left corner.
        px,py=self.pos()
        sx,sy=self.size()
        angle=math.radians(self.angle())
        cos=math.cos(angle)
        sin=math.sin(angle)
        ux=sx*cos
        uy=sx*sin
        vx=-sy*sin
        vy=sy*cos
        vertices=(px,py),(px+ux,py+uy),(px+ux+vx,py+uy+vy),(px+vx,py+vy)
        return vertices

# class ImageLayoutItem(pg.ImageItem,QtGui.QGraphicsLayoutItem):
#     def __init__(self,image=None,parent=None, **kargs):
#         QtGui.QGraphicsLayoutItem.__init__(self,parent)
#         pg.ImageItem.__init__(self,image,**kargs)

# class ColorBarItem(pg.GraphicsWidget):
#     """A color bar for an ImageItem.
#     
#     Vertical, with AxisItem for scale on the right side (could be extended to
#     other orientations and scale on other side).
#     """
#     def __init__(self,parent=None,label=None):
#         pg.GraphicsWidget.__init__(self,parent)
#         
#         # Setup layout
#         self.layout = QtGui.QGraphicsGridLayout()
#         self.layout.setHorizontalSpacing(0)
#         self.layout.setVerticalSpacing(0)
#         self.layout.setContentsMargins(0,0,0,0)
#         # Setup ViewBox containing the colorbar 
#         self.vb=pg.ViewBox()
#         self.vb.setFixedWidth(10)
#         self.vb.setLimits(xMin=0,xMax=1)
#         for _ in range(2): # it seems to ignore the padding argument the first time???
#             self.vb.setRange(QtCore.QRectF(0,0,1,1),padding=0)
#         # Setup colorbar, implemented as an ImageItem
#         self.bar=pg.ImageItem()
#         self.bar.setImage(np.linspace(0,1,256)[None,:])
#         self.vb.addItem(self.bar)
#         self.layout.addItem(self.vb,0,0)    
#         # Setup axis  
#         self.axis=AxisItem(orientation='right')   
#         self.axis.linkToView(self.vb)
#        
#         self.layout.addItem(self.axis,0,1)
#         self.setLayout(self.layout)
#         if label is not None:
#             self.setLabel(label)
#             
# class StaticColorBarItem(pg.GraphicsWidget):
#     """Colorbar in which 
#     TODOs:
#         remove buttons on axes - can't use original pg.AxisItem becuase it has bugs.
#             TODO for TODO: report it.
#     """
#     def __init__(self,parent=None,label=None,lut=None,levels=None):
#         """Previous version used manual layout. This worked for initial setup but
#         I couldn't figure out how to make it update automatically if e.g. the
#         axis width changed. So switched to layout management. This requires
#         the ImageItem to be in a QGraphicsLayoutItem, since it is not one itself.
#         Putting it in a ViewBox seemed the simplest option."""
#         pg.GraphicsWidget.__init__(self,parent)
#         # Setup layout
#         self.layout = QtGui.QGraphicsGridLayout()
#         self.layout.setHorizontalSpacing(0)
#         self.layout.setVerticalSpacing(0)
#         self.layout.setContentsMargins(0,0,0,0)
#         # Setup ViewBox containing the colorbar 
#         self.vb=pg.ViewBox(enableMouse=False)
#         self.vb.setFixedWidth(10)
#         for _ in range(2): # it seems to ignore the padding argument the first time???
#             self.vb.setRange(QtCore.QRectF(0,0,1,1),padding=0)
#         # Setup colorbar, implemented as an ImageItem
#         self.bar=pg.ImageItem()
#         self.bar.setImage(np.arange(256)[None,:])
#         self.bar.setRect(QtCore.QRectF(0,0,1,1))
#         self.vb.addItem(self.bar)
#         self.layout.addItem(self.vb,0,0)    
#         # Setup axis  
#         self.axis=pg.AxisItem(orientation='right')   
#         self.layout.addItem(self.axis,0,1)
#         self.setLayout(self.layout)
#         if label is not None:
#             self.setLabel(label)
#         self.setFixedLookupTableLevels(lut,levels)
#     
#     def setFixedLookupTableLevels(self,lut=None,levels=None):
#         if lut is not None and levels is not None:
#             self.bar.setLookupTable(lut)
#         self.axis.setRange(*levels)
#,controllable=True
#self.bar.setRect(QtCore.QRectF(0,0,1,1))
#for _ in range(2): # it seems to ignore the padding argument the first time???
#    self.vb.setRange(QtCore.QRectF(0,0,1,1),padding=0)



            
#self.bar.setLookupTable(lut)
    # def update_image_range(self):
    #     
    #         
    #     
    # def update_image_data(self):
    #     
    #         image_data=self.image.image
    #         if image_data is None:
    #             return
    #         image_min=image_data.min()
    #         image_max=image_data.max()
    #     
    # def update_colormap(self):
    #     
    #         
    # def update(self):
    #     
    #     
    #     if self.fixed_levels is None:
    #         
    #     else:
    #         
    #   
    #     
    #     logger.debug('image_min,max=%g,%g,image_levels=%g,%g,bar_levels=%g,%g',image_min,image_max,*image_levels,*bar_levels)
    #     
    #     #for _ in range(4):
    #         # Strange apparent bug in pyqtgraph.AxisItem - doesn't update
    #         # after only one call. TODO report
    #     #    self.axis.setRange(*image_levels)
    #     self.vb.setYRange(*image_levels,padding=0)
    #             
    # def axis_to_levels(self):
    #     if not np.allclose(self.image.levels,self.axis.range):
    #         logger.debug('axis_to_levels: axis.range=%g,%g',*self.axis.range)
    #         self.image.setLevels(self.axis.range)
        
# class ColorBarItem(pg.GraphicsWidget):
#     """A color bar for an ImageItem.
#     
#     Vertical, with AxisItem for scale on the right side (could be extended to
#     other orientations and scale on other side). Doesn't respond to changes in 
#     ImageItem lookup table or levels - will need appropriate signals from
#     ImageItem for this.
#     """
#     def __init__(self,parent=None,image=None,label=None):
#         pg.GraphicsWidget.__init__(self,parent)
#         self.bar=pg.ImageItem()
#         self.bar.setParentItem(self)
#         self.bar.setImage(np.arange(256)[None,:])
#         self.axis=AxisItem(orientation='right',parent=self)        
#         self.rect_width=10
#         self.left_marg=5        
#         self.setWidth()
#         self.image=None
#         self.setImage(image)
#         if label is not None:
#             self.setLabel(label)
#     def resizeEvent(self,ev):
#         y=0#max(-self.axis.boundingRect().y(),0)
#         self.bar.setRect(QtCore.QRectF(self.left_marg,self.height(),self.rect_width,-self.height()))
#         self.axis.setGeometry(self.left_marg+self.rect_width,y,self.width()-self.rect_width-self.left_marg,self.height()-y)
#     def setLabel(self,label):
#         self.axis.setLabel(label)
#         self.setWidth()
#     def setWidth(self):
#         self.setMinimumWidth(self.left_marg+self.rect_width+self.axis.minimumWidth())
#     def setImage(self,image):
#         if self.image is not None:
#             print('TODO disconnect')
#         self.image=image
#         if self.image is not None:
#             self.update()
#             self.image.sigColorMapChanged.connect(self.update)
#     def update(self):
#         self.bar.setLookupTable(self.image.lut)
#         for _ in range(2):
#             # Strange apparent bug in pyqtgraph.AxisItem - doesn't update
#             # after only one call. TODO report
#             self.axis.setRange(*self.image.levels)