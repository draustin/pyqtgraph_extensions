import pyqtgraph as pg
from pyqtgraph import QtCore,QtGui
from . import AxisItem
from .misc import LegendItem,ImageItem
from pyqtgraph.python2_3 import basestring

class AlignedPlot(QtCore.QObject):
    sigRangeChanged = QtCore.Signal(object, object)    ## Emitted when the ViewBox range has changed
    sigYRangeChanged = QtCore.Signal(object, object)   ## Emitted when the ViewBox Y range has changed
    sigXRangeChanged = QtCore.Signal(object, object)   ## Emitted when the ViewBox X range has changed          
            
    def __init__(self, name=None, labels=None, title=None, viewBox=None, axisItems=None, create=None, **kargs):
        """
        Note: supplied axisItems are not added to the layout. This allows for manual
            placement
        """
        QtCore.QObject.__init__(self)
        self.layout=None
        if create is None:
            create={}
        for v in ('title','left','right','top','bottom'):
            create.setdefault(v,True)
        self.create=create
        # ViewBox
        if viewBox is None:
            viewBox = pg.ViewBox(enableMenu=False)
        self.vb = viewBox
        self.vb.sigStateChanged.connect(self.viewStateChanged)
        if name is not None:
            self.vb.register(name)
        self.vb.sigRangeChanged.connect(self.sigRangeChanged)
        self.vb.sigXRangeChanged.connect(self.sigXRangeChanged)
        self.vb.sigYRangeChanged.connect(self.sigYRangeChanged)
        ## Create and place axis items
        if axisItems is None:
            axisItems = {}
        self.axisItems=axisItems
        self.axes = {}
        for k, pos in (('top',    (create['title']+0,               create['left']+0)),
                       ('bottom', (create['title']+create['top']+1, create['left']+0)),
                       ('left',   (create['title']+create['top'],   0)),
                       ('right',  (create['title']+create['top'],   create['left']+1))):
            if not create[k]:
                continue
            if k in axisItems:
                axis = axisItems[k]
            else:
                axis = AxisItem(orientation=k)
            axis.linkToView(self.vb)
            self.axes[k] = {'item': axis, 'pos': pos}
            axis.setZValue(-1000)
            axis.setFlag(axis.ItemNegativeZStacksBehindParent)
        # Title
        if create['title']:
            self.titleLabel = pg.LabelItem('') #  size='11pt' - leave size as is
            self.setTitle(None)  ## hide
        
        if create['right']:
            self.hideAxis('right')
        if create['top']:
            self.hideAxis('top')
        if create['left']:
            self.showAxis('left')
        if create['bottom']:
            self.showAxis('bottom')
        
        self.items = []
        
        if labels is None:
            labels = {}
        for label in list(self.axes.keys()):
            if label in kargs:
                labels[label] = kargs[label]
                del kargs[label]
        for k in labels:
            if isinstance(labels[k], basestring):
                labels[k] = (labels[k],)
            self.setLabel(k, *labels[k])
                
        if title is not None:
            self.setTitle(title)
        
        self.log_x=False
        self.log_y=False
        
        if len(kargs) > 0:
            self.plot(**kargs)

    def insertInLayout(self,layout,origin):
        assert self.layout is None
        self.layout=layout
        create=self.create
        layout.addItem(self.vb,row=origin[0]+create['title']+create['top'],col=origin[1]+create['left'])
        for k,alignment in (('top',pg.QtCore.Qt.AlignBottom),
                            ('bottom',pg.QtCore.Qt.AlignTop),
                            ('left',pg.QtCore.Qt.AlignRight),
                            ('right',pg.QtCore.Qt.AlignLeft)):
            if not create[k]:
                continue
            axis=self.axes[k]['item']
            pos=self.axes[k]['pos']
            # Dane: found this necessary
            self.layout.layout.setAlignment(axis,alignment)
            if k not in self.axisItems: # 8/11/2016 hack to allow external positioning of axes
                self.layout.addItem(axis,row=origin[0]+pos[0],col=origin[1]+pos[1])
        if create['title']:
            self.layout.addItem(self.titleLabel,origin[0]+0,origin[1],colspan=3)

    ## Wrap a few methods from viewBox. 
    #Important: don't use a settattr(m, getattr(self.vb, m)) as we'd be leaving the viebox alive
    #because we had a reference to an instance method (creating wrapper methods at runtime instead).
    
    for m in ['setXRange', 'setYRange', 'setXLink', 'setYLink', 'setAutoPan',         # NOTE: 
              'setAutoVisible', 'setRange', 'autoRange', 'viewRect', 'viewRange',     # If you update this list, please 
              'setMouseEnabled', 'setLimits', 'enableAutoRange', 'disableAutoRange',  # update the class docstring 
              'setAspectLocked', 'invertY', 'invertX', 'register', 'unregister']:                # as well.
                
        def _create_method(name):
            def method(self, *args, **kwargs):
                return getattr(self.vb, name)(*args, **kwargs)
            method.__name__ = name
            return method
        
        locals()[m] = _create_method(m)
        
    del _create_method
  
    def addItem(self, item, *args, **kargs):
        """
        Add a graphics item to the view box. 
        If the item has plot data (PlotDataItem, PlotCurveItem, ScatterPlotItem), it may
        be included in analysis performed by the PlotItem.
        """
        self.items.append(item)
        vbargs = {}
        if 'ignoreBounds' in kargs:
            vbargs['ignoreBounds'] = kargs['ignoreBounds']
        self.vb.addItem(item, *args, **vbargs)
        name = None
        if hasattr(item, 'implements') and item.implements('plotData'):
            name = item.name()
        if name is not None and hasattr(self, 'legend') and self.legend is not None:
            self.legend.addItem(item, name=name)
        if hasattr(item, 'setLogMode'):
            item.setLogMode(self.log_x,self.log_y)
        
    def removeItem(self, item):
        """
        Remove an item from the internal ViewBox.
        """
        if item.scene() is not None:
            self.vb.removeItem(item)
            
    def clear(self):
        """
        Remove all items from the ViewBox.
        """
        for i in self.items[:]:
            self.removeItem(i)
            
    def plot(self, *args, **kargs):
        """
        Add and return a new plot.
        See :func:`PlotDataItem.__init__ <pyqtgraph.PlotDataItem.__init__>` for data arguments
        
        Extra allowed arguments are:
            clear    - clear all plots before displaying new data
            params   - meta-parameters to associate with this data
        """
        clear = kargs.get('clear', False)
        params = kargs.get('params', None)
          
        if clear:
            self.clear()
            
        item = pg.PlotDataItem(*args, **kargs)
            
        if params is None:
            params = {}
        self.addItem(item, params=params)
        
        return item
        
    def image(self,*args,**kwargs):
        clear=kwargs.get('clear',False)
        params=kwargs.get('params',None)
        if clear:
            self.clear()
        item=ImageItem(*args,**kwargs)
        rect=kwargs.get('rect',None)
        if rect is not None:
            try:
                item.setRect(rect)
            except AttributeError:
                item.setRect(QtCore.QRectF(*rect))
        levels=kwargs.get('levels',None)
        if levels is not None:
            item.setLevels(levels)
        self.addItem(item)
        return item
        
    def setLabel(self, axis, text=None, units=None, unitPrefix=None, **args):
        """
        Set the label for an axis. Basic HTML formatting is allowed.
        
        ==============  =================================================================
        **Arguments:**
        axis            must be one of 'left', 'bottom', 'right', or 'top'
        text            text to display along the axis. HTML allowed.
        units           units to display after the title. If units are given,
                        then an SI prefix will be automatically appended
                        and the axis values will be scaled accordingly.
                        (ie, use 'V' instead of 'mV'; 'm' will be added automatically)
        ==============  =================================================================
        """
        self.getAxis(axis).setLabel(text=text, units=units, **args)
        self.showAxis(axis)
        
    def setLabels(self, **kwds):
        """
        Convenience function allowing multiple labels and/or title to be set in one call.
        Keyword arguments can be 'title', 'left', 'bottom', 'right', or 'top'.
        Values may be strings or a tuple of arguments to pass to setLabel.
        """
        for k,v in kwds.items():
            if k == 'title':
                self.setTitle(v)
            else:
                if isinstance(v, basestring):
                    v = (v,)
                self.setLabel(k, *v)
        
        
    def showLabel(self, axis, show=True):
        """
        Show or hide one of the plot's axis labels (the axis itself will be unaffected).
        axis must be one of 'left', 'bottom', 'right', or 'top'
        """
        self.getAxis(axis).showLabel(show)

    def setTitle(self, title=None, **args):
        """
        Set the title of the plot. Basic HTML formatting is allowed.
        If title is None, then the title will be hidden.
        """
        if title is None:
            self.titleLabel.hide()
            self.titleLabel.setFixedHeight(0)
            #setVisible(False)
            #self.titleLabel.setPreferredHeight(0)
            #self.layout.setRowFixedHeight(0, 0)
            #self.titleLabel.setMaximumHeight(0)
        else:
            #self.titleLabel.setMaximumHeight(30)
            #self.layout.setRowFixedHeight(0, 30)
            #self.titleLabel.setPreferredHeight(30)
            #self.titleLabel.setVisible(True)
            self.titleLabel.show()
            self.titleLabel.setFixedHeight(30)
            self.titleLabel.setText(title, **args)

    def showAxis(self, axis, show=True):
        """
        Show or hide one of the plot's axes.
        axis must be one of 'left', 'bottom', 'right', or 'top'
        """
        s = self.getAxis(axis)
        p = self.axes[axis]['pos']
        if show:
            s.show()
        else:
            s.hide()
            
    def hideAxis(self, axis):
        """Hide one of the PlotItem's axes. ('left', 'bottom', 'right', or 'top')"""
        self.showAxis(axis, False)
        
    def addLegend(self, size=None, offset=(30, 30)):
        """
        Create a new LegendItem and anchor it over the internal ViewBox.
        Plots will be automatically displayed in the legend if they
        are created with the 'name' argument.
        """
        self.legend = LegendItem(size, offset)
        self.legend.setParentItem(self.vb)
        return self.legend
        
    def viewStateChanged(self):
        pass
        #self.updateButtons()
        
    def getAxis(self, name):
        """Return the specified AxisItem. 
        *name* should be 'left', 'bottom', 'top', or 'right'."""
        return self.axes[name]['item']

    def scene(self):
        return self.layout.scene()
        
    def implements(self, interface=None):
        return interface in ['ViewBoxWrapper']

    def getViewBox(self):
        """Return the :class:`ViewBox <pyqtgraph.ViewBox>` contained within."""
        return self.vb
        
    def updateLogMode(self):
        x = self.log_x
        y = self.log_y
        for i in self.items:
            if hasattr(i, 'setLogMode'):
                i.setLogMode(x,y)
        self.getAxis('bottom').setLogMode(x)
        self.getAxis('top').setLogMode(x)
        self.getAxis('left').setLogMode(y)
        self.getAxis('right').setLogMode(y)
    
    def setLogMode(self, x=None, y=None):
        """
        Set log scaling for x and/or y axes.
        This informs PlotDataItems to transform logarithmically and switches
        the axes to use log ticking. 
        
        Note that *no other items* in the scene will be affected by
        this; there is (currently) no generic way to redisplay a GraphicsItem
        with log coordinates.
        
        """
        if x is not None:
            self.log_x=x
        if y is not None:
            self.log_y=y
        self.updateLogMode()
        
    def close(self):
        for k in self.axes:
            i = self.axes[k]['item']
            i.close()
        self.axes = None
        self.scene().removeItem(self.vb)
        self.vb = None
        
    def setXYLink(self,other):
        """Shorthand for calling setXLink and setYLink in sequence."""
        self.setXLink(other)
        self.setYLink(other)