"""Extensions and improvements to pyqtgraph.
"""
import os,sys
import pyqtgraph as pg
from pyqtgraph import QtGui,QtCore
import pyqtgraph.exporters as pgex
from scipy.interpolate import interp1d
from pyqtgraph.graphicsItems.GradientEditorItem import Gradients
import numpy as np
import subprocess

from .AxisItem import *
from .misc import *
from .AlignedPlotItem import *

# Bring line styles into the namespace for convenience
for v in ('SolidLine','DashLine','DashDotLine','DashDotDotLine','DotLine'):
    vars()[v]=getattr(QtCore.Qt,v)

# Switch to using white background and black foreground
pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')

# Ubuntu font has rubbish Greek letters
#print(QtGui.QApplication.font().family())
if QtGui.QApplication.font().family()=='Ubuntu':
    QtGui.QApplication.setFont(pg.QtGui.QFont('Sans Serif'))

# Greek letters in PDF export on Windows look shite - tried this but didn't fix it
# if QtGui.QApplication.font().family()=="MS Shell Dlg 2":
#     QtGui.QApplication.setFont(pg.QtGui.QFont('Sans Serif'))

# Note that for changing the font size, found that
# pg.QtGui.QApplication.font().setPointSize(12) 
# doesn't work whereas
# pg.QtGui.QApplication.setFont(pg.QtGui.QFont('Sans Serif',10))
# does, at least in IPython notebook.

# Tableau discrete color schemes
# https://github.com/jiffyclub/palettable/blob/master/palettable/tableau/tableau.py
# http://www.randalolson.com/2014/06/28/how-to-make-beautiful-data-visualizations-in-python-with-matplotlib/
tableau10=[ ( 31, 119, 180),
            (255, 127,  14),
            ( 44, 160,  44),
            (214,  39,  40),
            (148, 103, 189),
            (140,  86,  75),
            (227, 119, 194),
            (127, 127, 127),
            (188, 189,  34),
            ( 23, 190, 207)]
tableau20=[ (31, 119, 180),
            (174, 199, 232),
            (255, 127, 14),
            (255, 187, 120),    
            (44, 160, 44), 
            (152, 223, 138),
            (214, 39, 40),
            (255, 152, 150),    
            (148, 103, 189), 
            (197, 176, 213), 
            (140, 86, 75),
            (196, 156, 148),    
            (227, 119, 194),
            (247, 182, 210), 
            (127, 127, 127), 
            (199, 199, 199),    
            (188, 189, 34), 
            (219, 219, 141), 
            (23, 190, 207),
            (158, 218, 229)] 
            
def get_colormap_lut(name='flame'):
    """Get lookup table from one of pyqtgraph's gradient editor's presets.
    
    Result is suitable for ImageItem.setLookupTable. Gradient names listed in
    Gradients.keys(). Not sure how 'hsv' mode works.
    """
    gradient=Gradients[name]
    ticks=gradient['ticks']
    v=np.array([tick[0] for tick in ticks])
    c=np.array([tick[1] for tick in ticks])
    #print v.shape,c.shape
    n=256.
    vu=np.arange(n)/n
    return interp1d(v,c,axis=0)(vu)
    
def add_right_axis(plti,pen=None,label=None,enableMenu=False):
    """Add right-hand axis to pg.PlotItem.
    Following examples/MultiplePlotAxes. Returns a pyqtgraph_ex.ViewBox which is
    just a normal pyqtgraph.ViewBox with convenience plotting functions.
    Known limitation: vertical panning only moves original axis, not added one.
    Function is thus best suited for static plots rather than GUIs.
    
    Implementation: the viewbox is added to the plti's scene. This means that if
    plti is managed by a layout, then calling clear() on the layout will not
    remove plti from the scene (since the layout doesn't know about it).
    pyqtgraph_extensions.GraphicsLayoutWidget.clear() fixes this.
    """
    if isinstance(plti,pg.PlotWidget):
        plti=plti.plotItem
    vb=ViewBox(enableMenu=enableMenu)
    plti.showAxis('right')
    #vb.setParentItem(plti) - no, mucks up coordinate system
    plti.scene().addItem(vb)
    axis=plti.getAxis('right')
    axis.setStyle(showValues=True)
    axis.linkToView(vb)
    if pen is not None:
        axis.setPen(pen)
    if label is not None:
        axis.setLabel(label)
    vb.setXLink(plti.vb)    
    def updateViews():
        vb.setGeometry(plti.vb.sceneBoundingRect())
    updateViews()
    plti.vb.sigResized.connect(updateViews)
    return vb
    
def add_top_axis(plti,pen=None,label=None,enableMenu=False):
    """Add top axis to pg.PlotItem.
    Following examples/MultiplePlotAxes. Returns a pyqtgraph_ex.ViewBox which is
    just a normal pyqtgraph.ViewBox with convenience plotting functions.
    Known limitation: horizontal panning only moves original axis, not added one.
    Function is thus best suited for static plots rather than GUIs.
    """
    if isinstance(plti,pg.PlotWidget):
        plti=plti.plotItem
    vb=ViewBox(enableMenu=enableMenu)
    plti.showAxis('top')
    plti.scene().addItem(vb)
    axis=plti.getAxis('top')
    axis.linkToView(vb)
    if pen is not None:
        axis.setPen(pen)
    if label is not None:
        axis.setLabel(label)
    vb.setYLink(plti.vb)    
    def updateViews():
        vb.setGeometry(plti.vb.sceneBoundingRect())
    updateViews()
    plti.vb.sigResized.connect(updateViews)
    return vb

def addLegend(plot,**kwargs):
    """Add a legend to plot.
    kwargs passed on to LegendItem.__init__. This function is necessary to use
    pyqtgraph_extensions.LegendItem instead of pyqtgraph's original one."""
    plot.legend = LegendItem(**kwargs)
    # Attempted hack to allow adding legends to ViewBox...
    # if hasattr(plot,'vb'):
    #     vb=plot.vb
    # else:
    #     vb=plot
    # doesn't work.
    plot.legend.setParentItem(plot.vb)
    return plot.legend

# todo: option to remove margins of GraphicsLayouts:
# Necessary for bitmap output (PDF is cropped somehow)
# See http://stackoverflow.com/questions/27092164/margins-in-pyqtgraphs-graphicslayout
# and
# http://comments.gmane.org/gmane.comp.python.pyqtgraph/234
def export(o,filename,fmt='png',mkdir=False,fmt_opts={},exporter_params={}):
    # If a list of formats, process one by one
    if not isinstance(fmt,basestring):
        raise NotImplementedError('Decided not to accept multiple formats...')
        fmts=fmt
        for fmt in fmts:
            export(o,filename,fmt,mkdir,fmt_opts)
        return
    fmt=fmt.lower()
    dir=os.path.dirname(filename)
    if len(dir)>0:
        if not os.path.isdir(dir):
            if mkdir:
                os_ex.mkdir(dir)
            else:
                raise ValueError('Path %s doesn''t exist'%dir)
   
    if isinstance(o,pg.GraphicsLayoutWidget) or isinstance(o,GraphicsLayoutWidget):
        # Ensures resizing is done (and maybe other things - but without this
        # it can be wrong if run in a script
        o.show()
        pg.QtGui.QApplication.processEvents()
        o.repaint() # this is crucial - something about executing code rather than
        # waiting for the user means this doesn't get called and the layout can
        # be wrong
        pg.QtGui.QApplication.processEvents()
        # Passing the QGraphicsScene to the exporter ensures that all items in the
        # scene being exported
        item=o.scene()
    elif isinstance(o,pg.PlotWidget):
        item=o.getPlotItem()
    elif isinstance(o,pg.GraphicsItem):
        item=o
    else:
        raise ValueError('Don''t know how to export it')
    if fmt in ('png','tif'):
        exporter=pgex.ImageExporter(item)
        for key,value in exporter_params.items():
            exporter.parameters()[key]=value
        exporter.export(filename+'.'+fmt)
    elif fmt=='svg':
        pgex.SVGExporter(item).export(filename+'.'+fmt)
    elif fmt in ('svg','pdf','eps','svg-png','svg-pdf-png'):
        # generate svg
        pgex.SVGExporter(item).export(filename+'.'+'svg') 
        # Convert from svg to required
        def convert(final_fmt):
            subprocess.call(['inkscape','--export-'+final_fmt+'='+filename+'.'+final_fmt,
                '--export-area-drawing',filename+'.svg','--export-dpi=300'])
            if final_fmt=='pdf':
                if not fmt_opts.get('interpolate',False):
                    # Stop ugly interpolation of bitmaps
                    with open(filename+'.'+final_fmt,"rb") as f:
                        data = f.read()
                    data=data.replace(b'Interpolate true',b'Interpolate false')
                    with open(filename+'.'+final_fmt,"wb") as f:
                        f.write(data)
        if fmt in ('pdf','eps'):
            convert(fmt)
        elif fmt=='svg-png':
            convert('png')
        elif fmt=='svg-pdf-png':
            convert('png')
            convert('pdf')
    else:
        raise ValueError('Unknown format %s'%fmt)
        
def close_all():
    """Shortcut for QApplication.closeAllWindows."""
    pg.QtGui.QApplication.closeAllWindows()
    
def plot(*args, **kargs):
    """
    Create and return a :class:`PlotWindow <pyqtgraph.PlotWindow>` 
    (this is just a window with :class:`PlotWidget <pyqtgraph.PlotWidget>` inside), plot data in it.
    Accepts a *title* argument to set the title of the window.
    All other arguments are used to plot data. (see :func:`PlotItem.plot() <pyqtgraph.PlotItem.plot>`)
    """
    pg.mkQApp()
    #if 'title' in kargs:
        #w = PlotWindow(title=kargs['title'])
        #del kargs['title']
    #else:
        #w = PlotWindow()
    #if len(args)+len(kargs) > 0:
        #w.plot(*args, **kargs)
        
    pwArgList = ['title', 'labels', 'name', 'left', 'right', 'top', 'bottom', 'background']
    pwArgs = {}
    dataArgs = {}
    for k in kargs:
        if k in pwArgList:
            pwArgs[k] = kargs[k]
        else:
            dataArgs[k] = kargs[k]
        
    w = PlotWindow(**pwArgs)
    if len(args) > 0 or len(dataArgs) > 0:
        w.plot(*args, **dataArgs)
    pg.plots.append(w)
    w.show()
    return w
    
def axes_to_rect(x,y):
    """Return QRectF covering first and last elements of axis vectors.
    
    Args:
        x: array with one nonsingleton dimension
        y: array with one nonsingleton dimension
    
    Returns:
        QRectF with top-left corner x[0],y[0] and lower-right corner x[-1],y[-1]
    """
    x=np.array(x).squeeze()
    y=np.array(y).squeeze()
    Dx=x[1]-x[0]
    Dy=y[1]-y[0]
    return QtCore.QRectF(x[0]-Dx/2,y[0]-Dy/2,x[-1]-x[0]+Dx,y[-1]-y[0]+Dy)
    
def image_axes(x,y,im,parent=None,**kwargs):
    if parent is None:
        parent=pg.PlotWindow()
    item=pg.ImageItem(image=im,**kwargs)
    item.setRect(axes_to_rect(x,y))
    parent.addItem(item)
    return item,parent
    
def cornertext(text,parent,corner=(0,0),**kwargs):
    """Put text in the corner of a ViewBox (e.g. for labelling subpanels).
    
    Args:
        text (str): the text
        parent: any plot-like object - a ViewBox, AlignedPlotItem, PlotItem, PlotWidget
        corner (2-tuple of 0,1): (0,0) for upper left, (1,1) for lower right, ...
        kwargs: passed on to LabelItem.__init__
    
    Returns:
        LabelItem: created object, whose parent is the appropriate view box
    """
    # Convert parent to a pg.ViewBox
    if isinstance(parent,pg.PlotWidget):
        parent=parent.getPlotItem()
    if isinstance(parent,pg.PlotItem) or isinstance(parent,AlignedPlotItem):
        parent=parent.getViewBox()
    # Use the GraphicsWidgetAnchor base class of
    # LabelItem to lock its position to the viewbox
    li=pg.LabelItem(text,**kwargs)    
    li.setParentItem(parent)
    li.anchor(corner,corner)
    return li
    
def adjust_widget(widget,window_title=None,size=None,**kwargs):
    """Apply some adjustments to a widget. Unused kwargs are returned."""
    if window_title is not None:
        widget.setWindowTitle(window_title)
    if size is not None:
        widget.resize(*size)
    return kwargs
    
class AnchoredPlotItem(pg.PlotItem,pg.GraphicsWidgetAnchor):
    def __init__(self,parent_item,anchor=(0,0),offset=(10,10),size=(100,100),**kwargs):
        pg.PlotItem.__init__(self,**kwargs)
        pg.GraphicsWidgetAnchor.__init__(self)
        self.setParentItem(parent_item)
        self.anchor(anchor,anchor,offset)
        self.resize(*size)

from .GraphicsLayout import *

# somehow these cause crashing when exiting...
# def make_application():
#     global application
#     if QtGui.QApplication.instance() is None:
#         application=QtGui.QApplication(sys.argv)
#     else:
#         application=None
#         
# def exec_application():
#     global application
#     if application is not None:
#         sys.exit(application.exec_())
    
# Probably won't be necessary:
# class  QGraphicsLayoutSpacer(QtGui.QGraphicsLayoutItem):
#     def __init__(self,height=0,width=0):
#         QtGui.QGraphicsLayoutItem.__init__(self)
#         self.height=height
#         self.width=width
#     def sizeHint(self,which,constraint):
#         return QtCore.QSizeF(self.width,self.height)
#             
# class QGraphicsRectWidget(QtGui.QGraphicsLayoutItem,QtGui.QGraphicsRectItem):
#     def __init__(self,parent=None):
#         QtGui.QGraphicsRectItem.__init__(self,parent)
#         QtGui.QGraphicsLayoutItem.__init__(self,parent)
#     def setGeometry(self,rect):
#         self.setRect(rect)
#     def sizeHint(self,which,constraint):
#         return QtCore.QSizeF(0,0)
