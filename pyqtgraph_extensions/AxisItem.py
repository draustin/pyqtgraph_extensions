import os,logging,time
import pyqtgraph as pg
from pyqtgraph import QtCore,QtGui
from functools import partial

logger=logging.getLogger(__name__)

# TODO create a ColorBarAxisItem subclass designed to go next to a colorbar and
# control an image.

class AxisItem(pg.AxisItem):
    """Replacement for pyqtgraph.AxisItem, with:
        * buttons to set the limits manually (with a dialog box), to set to the full
        extent (auto range) and to toggle autorange on/off
        * ability to handle zero height (for top/bottom) or zero width (for left/right)
        which is useful for certain complex grid layouts (TODO: example)
    """
    range_changed=QtCore.pyqtSignal()
    
    def __init__(self, orientation, pen=None, linkView=None, parent=None, maxTickLength=-5, showValues=True):
        pg.AxisItem.__init__(self,orientation,pen,linkView,parent,maxTickLength,showValues)
        self.set_lmt_btns=[]
        self.aset_lmt_btns=[]
        path=os.path.dirname(os.path.abspath(__file__))
        self.autorange_toggle_off_pixmap=QtGui.QPixmap(os.path.join(path,'autorange_toggle_off.png'))
        self.autorange_toggle_on_pixmap=QtGui.QPixmap(os.path.join(path,'autorange_toggle_on.png'))
        for type in range(2):
            # set limit button
            btn=pg.ButtonItem(QtGui.QPixmap(os.path.join(path,'ellipsis.png')), 14,self)
            btn.setZValue(-1000)
            btn.setFlag(btn.ItemNegativeZStacksBehindParent)
            btn.clicked.connect(partial(self.set_lmt_btn_clicked,type)) # late binding if function used
            self.set_lmt_btns.append(btn)
            # autoset limit button
            btn=pg.ButtonItem(pg.pixmaps.getPixmap('auto'), 14,self)
            btn.setZValue(-1000)
            btn.setFlag(btn.ItemNegativeZStacksBehindParent)
            btn.clicked.connect(partial(self.aset_lmt_btn_clicked,type)) # late binding if function used
            self.aset_lmt_btns.append(btn)
        # enable autorange button
        btn=pg.ButtonItem(self.autorange_toggle_off_pixmap,14,self)
        btn.setZValue(-1000)
        btn.setFlag(btn.ItemNegativeZStacksBehindParent)
        btn.clicked.connect(self.enable_auto_range_btn_clicked) # late binding if function used
        self.enable_auto_range_btn=btn
        self.mouseHovering=False
        self.buttons_enabled=True
        self.updateButtons()
        
    def close(self):
        for btn in self.set_lmt_btns:
            btn.setParent(None)
        self.set_lmt_btns=None
        for btn in self.aset_lmt_btns:
            btn.setParent(None)
        self.aset_lmt_btns=None
        self.enable_auto_range_btn.setParent(None)
        self.enable_auto_range_btn=None
        pg.AxisItem.close(self)
        
    def axis(self):
        return int(self.orientation in {'left','right'})
        
    def linkToView(self,view):
        old_view=self.linkedView()
        pg.AxisItem.linkToView(self,view)
        view=self.linkedView()
        if old_view is not None:
            old_view.sigStateChanged.disconnect(self.respond_linked_view_state_change)
        if view is not None:
            view.sigStateChanged.connect(self.respond_linked_view_state_change)
            
    def respond_linked_view_state_change(self):
        s=not (self.linkedView().autoRangeEnabled()[self.axis()] is False)
        self.auto_range_enabled=s
        path=os.path.dirname(os.path.abspath(__file__))
        self.enable_auto_range_btn.setPixmap(QtGui.QPixmap(os.path.join(path,'autorange_toggle_'+('on' if s else 'off')+'.png')))
        
    def resizeEvent(self, ev):
        ## Set the position of the label
        nudge = 5
        br = self.label.boundingRect()
        p = QtCore.QPointF(0, 0)
        if self.orientation == 'left':
            p.setY(int(self.size().height()/2 + br.width()/2))
            #p.setX(-nudge)
            p.setX(self.size().width()-self.neededSpace())
        elif self.orientation == 'right':
            p.setY(int(self.size().height()/2 + br.width()/2))
            #p.setX(int(self.size().width()-br.height()+nudge))
            p.setX(self.labelPos())
        elif self.orientation == 'top':
            #p.setY(-nudge)
            p.setY(self.size().height()-self.neededSpace())
            p.setX(int(self.size().width()/2. - br.width()/2.))
        elif self.orientation == 'bottom':
            p.setX(int(self.size().width()/2. - br.width()/2.))
            p.setY(self.labelPos())
            #p.setY(int(self.size().height()-br.height()+nudge))
            #p.setY(self.label_y)
        
        self.label.setPos(p)
        self.picture = None
        
        if not hasattr(self,'set_lmt_btns') or self.set_lmt_btns is None:  ## already closed down
            return
        lower=self.set_lmt_btns[0]
        rect=self.mapRectFromItem(lower,lower.boundingRect())
        rh=rect.height()
        y0=0
        y1=rh
        y2=rh*2
        ym0=self.size().height()-rh
        ym1=ym0-rh
        rw=rect.width()
        x0=0
        x1=rw
        x2=rw*2
        xm0=self.size().width()-rw
        xm1=xm0-rw
        if self.orientation=='left':
            self.set_lmt_btns[0].setPos(0,ym0)
            self.set_lmt_btns[1].setPos(0,y0)
            self.aset_lmt_btns[0].setPos(0,ym1)
            self.aset_lmt_btns[1].setPos(0,y1)
            self.enable_auto_range_btn.setPos(0,y2)
        elif self.orientation=='bottom':
            self.set_lmt_btns[0].setPos(x0,ym0)
            self.set_lmt_btns[1].setPos(xm0,ym0)
            self.aset_lmt_btns[0].setPos(x1,ym0)
            self.aset_lmt_btns[1].setPos(xm1,ym0)
            self.enable_auto_range_btn.setPos(x2,ym0)
        elif self.orientation=='right':
            self.set_lmt_btns[0].setPos(xm0,ym0)
            self.set_lmt_btns[1].setPos(xm0,y0)
            self.aset_lmt_btns[0].setPos(xm0,ym1)
            self.aset_lmt_btns[1].setPos(xm0,y1)
            self.enable_auto_range_btn.setPos(xm0,y2)
        elif self.orientation=='top':
            self.set_lmt_btns[0].setPos(x0,0)
            self.set_lmt_btns[1].setPos(xm0,0)
            self.aset_lmt_btns[0].setPos(x1,0)
            self.aset_lmt_btns[1].setPos(xm1,0)
            self.enable_auto_range_btn.setPos(x2,0)
            
    def set_lmt_btn_clicked(self,type):
        # TODO bug here - sometimes the dialog doesn't show the right range
        logger.debug('range[type]=%s',self.range[type])
        value,ok=QtGui.QInputDialog.getDouble(self.parent(),self.label.toPlainText(),('Lower','Upper')[type]+' limit:',self.range[type],decimals=3)
        if ok:
            self.set_view_range(type,value)
            
    def aset_lmt_btn_clicked(self,type):
        v=self.linkedView()
        if v==None:
            return
        bounds=v.childrenBoundingRect()
        if self.orientation in {'left','right'}:
            #print bounds.bottom(),bounds.top()
            if type==0:
                v=bounds.top()
            else:
                v=bounds.bottom()
        else:
            if type==0:
                v=bounds.left()
            else:
                v=bounds.right()
        self.set_view_range(type,v)    
            
    def set_view_range(self,type,value):
        v=self.linkedView()
        if v==None:
            range=self.range
            range[type]=value
            self.setRange(*range)
        else:
            ranges=v.viewRange()
            if self.orientation in {'left','right'}:
                range=ranges[1]
                range[type]=value
                v.setRange(yRange=range,padding=0)
            else:
                range=ranges[0]
                range[type]=value
                v.setRange(xRange=range,padding=0)
                
    def setRange(self,mn,mx):
        # Override superclass method to emit signal
        super().setRange(mn,mx)
        self.range_changed.emit()
        
                
    def enable_auto_range_btn_clicked(self):
        v=self.linkedView()
        if v==None:
            return
        if self.auto_range_enabled:
            v.disableAutoRange(self.axis())
        else:
            v.enableAutoRange(self.axis())
        #self.auto_range_enabled=not self.auto_range_enabled
        
    def setButtonsEnabled(self,enabled):
        self.buttons_enabled=enabled
        
    def hoverEvent(self, ev):
        if ev.enter:
            self.mouseHovering = True
        if ev.exit:
            self.mouseHovering = False
        self.updateButtons()
        
    def updateButtons(self):
        btns=self.set_lmt_btns+self.aset_lmt_btns+[self.enable_auto_range_btn]
        try:
            if self.mouseHovering and self._exportOpts is False and self.buttons_enabled:
                for btn in btns:
                    btn.show()
            else:
                for btn in btns:
                    btn.hide()
        except RuntimeError:
            pass  # this can happen if the plot has been deleted.
            
    def _updateMaxTextSize(self, x):
        ## Informs that the maximum tick size orthogonal to the axis has
        ## changed; we use this to decide whether the item needs to be resized
        ## to accomodate.
        ## Dane: Overridden because original algorithm never shrunk text
        if self.orientation in ['left', 'right']:
            if x > self.textWidth or x < self.textWidth-5:
                self.textWidth = x
                if self.style['autoExpandTextSpace'] is True:
                    self._updateWidth()
                    #return True  ## size has changed
        else:
            if x > self.textHeight or x < self.textHeight-5:
                self.textHeight = x
                if self.style['autoExpandTextSpace'] is True:
                    self._updateHeight()
                    #return True  ## size has changed
 
    def labelPos(self):
        """Calculate position (x for left/right, y for top/bottom) of axis label"""
        if self.orientation in ('left','right'):
            # Tick label
            if not self.style['showValues']:
                w = 0
            elif self.style['autoExpandTextSpace'] is True:
                w = self.textWidth
            else:
                w = self.style['tickTextWidth']
            # Offset between ticks and tick labels
            w += self.style['tickTextOffset'][0] if self.style['showValues'] else 0
            # The ticks themselves
            w += max(0, self.style['tickLength'])
            return w
        else:
            # Tick label
            if not self.style['showValues']:
                h = 0
            elif self.style['autoExpandTextSpace'] is True:
                h = self.textHeight
            else:
                h = self.style['tickTextHeight']
            # Offset between ticks and tick labels
            h += self.style['tickTextOffset'][1] if self.style['showValues'] else 0
            # The ticks themselves
            h += max(0, self.style['tickLength'])
            return h
    
    def neededSpace(self):
        """Calculate needed space (width for left/right, height for top/bottom)"""
        s=self.labelPos()
        if self.label.isVisible():
            s+=self.label.boundingRect().height()*0.8
            #r=self.label.boundingRect()
            #s+=(r.width() if self.orientation in ('left','right') else r.height())*0.8
        return s
        
    def boundingRect(self):
        linkedView = self.linkedView()
        if linkedView is None or self.grid is False:
            rect = self.mapRectFromParent(self.geometry())
            ## extend rect if ticks go in negative direction
            ## also extend to account for text that flows past the edges
            tl = self.style['tickLength']
            if self.orientation == 'left':
                rect.setLeft(rect.left()-max(self.neededSpace()-self.width(),0))
                rect = rect.adjusted(0, -15, -min(0,tl), 15)
            elif self.orientation == 'right':
                rect.setWidth(self.neededSpace())
                rect = rect.adjusted(min(0,tl), -15, 0, 15)
            elif self.orientation == 'top':
                rect.setTop(rect.top()-max(self.neededSpace()-rect.height(),0))
                rect = rect.adjusted(-15, 0, 15, -min(0,tl))
            elif self.orientation == 'bottom':
                rect.setHeight(self.neededSpace())
                rect = rect.adjusted(-15, min(0,tl), 15, 0)
            return rect
        else:
            return self.mapRectFromParent(self.geometry()) | linkedView.mapRectToItem(self, linkedView.boundingRect())
            
    def setExportMode(self, export, opts=None):
        pg.AxisItem.setExportMode(self, export, opts)
        self.updateButtons()
        
class TimeAxisItem(AxisItem):
    def tickStrings(self, values, scale, spacing):
        """Copied from pyqtgraph examples."""
        strns = []
        if len(values)==0:
            return AxisItem.tickStrings(self,values,scale,spacing)
        rng = max(values)-min(values)
        #if rng < 120:
        #    return pg.AxisItem.tickStrings(self, values, scale, spacing)
        if rng < 3600*24:
            string = '%H:%M:%S'
            label1 = '%b %d -'
            label2 = ' %b %d, %Y'
        elif rng >= 3600*24 and rng < 3600*24*30:
            string = '%d'
            label1 = '%b - '
            label2 = '%b, %Y'
        elif rng >= 3600*24*30 and rng < 3600*24*30*24:
            string = '%b'
            label1 = '%Y -'
            label2 = ' %Y'
        elif rng >=3600*24*30*24:
            string = '%Y'
            label1 = ''
            label2 = ''
        for x in values:
            try:
                strns.append(time.strftime(string, time.localtime(x)))
            except ValueError:  ## Windows can't handle dates before 1970
                strns.append('')
        try:
            label = time.strftime(label1, time.localtime(min(values)))+time.strftime(label2, time.localtime(max(values)))
        except ValueError:
            label = ''
        #self.setLabel(text=label)
        return strns
        