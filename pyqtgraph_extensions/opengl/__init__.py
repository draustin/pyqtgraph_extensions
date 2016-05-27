import pyqtgraph as pg
from pyqtgraph import QtGui,QtCore
import pyqtgraph.opengl as pgl
from OpenGL.GL import *
from pyqtgraph.python2_3 import *
import numpy as np
from .. import IPythonPNGRepr

class GLViewWidget(pgl.GLViewWidget,IPythonPNGRepr):
    """Trivial extension to pyqtgraph.opengl.GLViewWidget with sensible initial size."""
    def __init__(self,size_hint=(400,400),title=None):
        pgl.GLViewWidget.__init__(self)
        self.size_hint=size_hint
        self.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        if title is None:
            title={}
        self.title={'string':None,'color':(1,1,1),'font':pg.QtGui.QApplication.font()}
        if isinstance(title,basestring):
            self.title['string']=title
        else:
            self.title.update(title)
        self.setTitle()
    def setTitle(self,string=None,color=None,font=None):
        if string is not None:
            self.title['string']=string
        if color is not None:
            self.title['color']=color
        if font is not None:
            self.title['font']=font
        if self.title['string'] is not None:
            font_metrics=pg.QtGui.QFontMetrics(self.title['font'])
            self.title['width']=font_metrics.width(self.title['string'])
            self.title['height']=font_metrics.height()
        self.updateGL()
    def sizeHint(self):
        return QtCore.QSize(*self.size_hint)
    def paintGL(self, region=None, viewport=None, useItemNames=False):
        pgl.GLViewWidget.paintGL(self,region,viewport,useItemNames)
        glColor(*self.title['color'])
        if self.title['string'] is not None:
            self.renderText((self.size().width()-self.title['width'])/2,self.title['height'],self.title['string'],self.title['font'])
            
    def get_repr_png_image(self):
        """Generate png representation for ipython notebook.
        
        Similar to equivalent in pyqtgraph_extended.GraphicsLayoutWidget but with
        some tweaks for OpenGL.
        
        Took a while to make this work in ipython notebook. The secret was
        self.paintGL and glFlush. Without this, renderPixmap and grabFrameBuffer
        return the screen underneath rather than the GLViewWidget's contents.
        See 
        http://stackoverflow.com/questions/10429452/how-to-take-reliable-qglwidget-snapshot
        
        Failed attempt with renderToArray for reference:

        w,h=self.size().width(),self.size().height()
        a=self.renderToArray((w,h))
        image=QtGui.QImage(a.data,w,h,QtGui.QImage.Format_ARGB32)
        
        Problem is text rendered with renderText isn't shown.
        """
        # without these two, get screen underneath widget
        self.paintGL()
        glFlush() 
        
        # Get frame buffer as image and write it to a buffer
        return self.grabFrameBuffer()

class GLAxisItem(pgl.GLAxisItem):
    """Replacement GLAxisItem with extra features.
    * adjustable line width - couldn't see the lines clearly in the original
    * text labels for axes.
    Paint code stolen from original.
    """
    def __init__(self, size=None, antialias=True, glOptions='translucent',line_width=2,show_labels=True,label_font=None):
        pgl.GLAxisItem.__init__(self,size,antialias,glOptions)
        self.line_width=2
        self.show_labels=show_labels
        if label_font is None:
            label_font=QtGui.QFont()
        self.label_font=label_font
    def paint(self):

        #glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        #glEnable( GL_BLEND )
        #glEnable( GL_ALPHA_TEST )
        self.setupGLState()
        
        if self.antialias:
            glEnable(GL_LINE_SMOOTH)
            glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
        glLineWidth(self.line_width)
        glBegin( GL_LINES )
        
        x,y,z = self.size()
        glColor4f(0, 1, 0, .6)  # z is green
        glVertex3f(0, 0, 0)
        glVertex3f(0, 0, z)
        
        glColor4f(1, 1, 0, .6)  # y is yellow
        glVertex3f(0, 0, 0)
        glVertex3f(0, y, 0)

        glColor4f(0, 0, 1, .6)  # x is blue
        glVertex3f(0, 0, 0)
        glVertex3f(x, 0, 0)
        glEnd()
        
        if self.show_labels:
            glColor(0,0,1)
            self.view().renderText(x,0,0,'x',self.label_font)
            glColor(1,1,0)
            self.view().renderText(0,y,0,'y',self.label_font)
            glColor(0,1,0)
            self.view().renderText(0,0,z,'z',self.label_font)
            
class GLTextItem(pgl.GLGraphicsItem.GLGraphicsItem):
    def __init__(self,string=None,pos=(0,0,0),color=(1,1,1)):
        pgl.GLGraphicsItem.GLGraphicsItem.__init__(self)
        self.pos=pos
        self.string=string
        self.color=color
    def paint(self):
        self.setupGLState()
        v=self.view()
        if self.string is not None:
            glColor(self.color[0],self.color[1],self.color[2])
            v.renderText(self.pos[0],self.pos[1],self.pos[2],self.string)
            
class GLWireBoxItem(pgl.GLGraphicsItem.GLGraphicsItem):
    """
    **Bases:** :class:`GLGraphicsItem <pyqtgraph.opengl.GLGraphicsItem>`
    
    Displays a wire box
    """
    
    def __init__(self, size=[1,1,1], center=[0,0,0],color=(1,1,1)):
        pgl.GLGraphicsItem.GLGraphicsItem.__init__(self)
        self._size=size
        self._center=center
        self._color=color
        self.update()
      
    @property
    def size(self):
        """Length of edges of box.
        Defined in local coordinate systeml - does not affect transform."""
        return self._size
    @size.setter
    def size(self,r):
        self._size=r
        self.update()
    
    @property
    def center(self):
        return self._center
    @center.setter
    def center(self,r):
        self._center=r
        self.update()
        
    @property
    def corner(self):
        """Corner of box - edges extend from corner a distance size."""
        return [c-0.5*s for c,s in zip(self._center,self._size)]
    @corner.setter
    def corner(self,r):
        if len(r)==2:
            r,keep=r
        else:
            keep='center'
        if keep is 'center':
            self.size=[2*(c-x) for c,x in zip(self.center,r)]
        elif keep is 'size':
            self.center=[x+0.5*s for x,s in zip(r,self.size)]
    @property
    def color(self):
        return self._color
    @color.setter
    def color(self,r):
        self._color=r
        self.update()
        
    def paint(self):
        self.setupGLState()
            
        glBegin( GL_LINES )
        
        r=[r*0.5 for r in self.size]
        c=self.center

        glColor(*self.color)
        
        for a in range(3):
            for s0 in [-1,1]:
                for s1 in [-1,1]:
                    for l in [-1,1]:
                        if a==0:
                            glVertex3f(r[0]*l+c[0],r[1]*s0+c[1],r[2]*s1+c[2])
                        elif a==1:
                            glVertex3f(r[0]*s0+c[0],r[1]*l+c[1],r[2]*s1+c[2])
                        elif a==2:
                            glVertex3f(r[0]*s0+c[0],r[1]*s1+c[1],r[2]*l+c[2])
                            
        glEnd()
        
class GLContainerWidget(QtGui.QWidget,IPythonPNGRepr):
    """Extension of QWidget that can contain QGLWidgets and still export properly."""
    def get_repr_png_image(self):
        # Does non-OpenGL parts nicely, but OpenGL parts aren't rendered correctly
        # i.e. transparency doesn't work
        pixmap=QtGui.QPixmap.grabWidget(self)
        image=pixmap.toImage()
        # Calling paintGL removes overlays and mixes things up with multiple
        # QGLWidgets. Removed it - TODO thorough test
        # for w in self.findChildren(pg.Qt.QtOpenGL.QGLWidget):
        #     w.paintGL()
        OpenGL.GL.glFlush() # Not sure if needed
        # Overwrite regions of image containing QGLWidgets
        painter=QtGui.QPainter(image)
        #n=0
        for w in self.findChildren(pg.Qt.QtOpenGL.QGLWidget):
            w.makeOverlayCurrent() # needed for text produced by renderText
            w.makeCurrent() # don't know if needed but doesn't hurt
            subimage=w.grabFrameBuffer(True)
            #subimage.save('s%d.png'%n)
            painter.drawImage(w.pos(),subimage)
            #n+=1
        painter.end()
        return image
        
def export(widget,filename,fmt='png'):
    """Export OpenGL widget or widget containing them.
    
    Valid widget types are Qt.QtOpenGL.QGLWidget (including pyqtgraph.GLViewWidget),
    any QWidget. For QWidgets, the grabWidget method is first used to get the 
    non-OpenGL parts, and then the grabFrameBuffer method is called on all
    QGLWidget children, with the results overdrawn.
    """
    QtGui.QApplication.processEvents()
    # Save to one format    
    if isinstance(widget,pg.Qt.QtOpenGL.QGLWidget):
        if fmt=='png':
            widget.grabFrameBuffer().save(filename+'.'+fmt)
        else:
            raise ValueError('Don''t know how to export GLViewWidget with anything other than png')
    elif isinstance(widget,GLContainerWidget):
        image=widget.get_repr_png_image()
        # Make file
        image.save(filename+'.'+fmt)
    else:
        raise ValueError('Don''t know how to export')
        
class GLGridItem(pgl.GLGridItem):
    """
    Extension giving control of color and line width
    Displays a wire-grame grid. 
    """
    
    def __init__(self,color=None,width=1,**kwargs):
        pgl.GLGridItem.__init__(self,**kwargs)
        if color is None:
            color=(1,1,1,0.3)
        self.color=color
        if width is None:
            width=1
        self.width=width
        
    def paint(self):
        self.setupGLState()
        
        glLineWidth(self.width)
        
        if self.antialias:
            glEnable(GL_LINE_SMOOTH)
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
            
        glBegin( GL_LINES )
        
        x,y,z = self.size()
        xs,ys,zs = self.spacing()
        xvals = np.arange(-x/2., x/2. + xs*0.001, xs) 
        yvals = np.arange(-y/2., y/2. + ys*0.001, ys) 
        glColor4f(*self.color)
        for x in xvals:
            glVertex3f(x, yvals[0], 0)
            glVertex3f(x,  yvals[-1], 0)
        for y in yvals:
            glVertex3f(xvals[0], y, 0)
            glVertex3f(xvals[-1], y, 0)
        
        glEnd()
            
    