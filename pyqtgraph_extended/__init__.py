"""Convenience package combining pyqtgraph with pyqtgraph_extensions in the one namespace.
Provided I haven't made any mistakes, one should be able to import this package
instead of pyqtgraph and obtain identical behavior but with the extra features
of pyqtgraph_extensions available.
"""
from pyqtgraph import *
from pyqtgraph_extensions import *

if __name__=="__main__":
    from pyqtgraph import QtGui,QtCore
    import numpy as np
    if QtCore.QCoreApplication.instance() is not None:
        app=mkQApp()
    
    def test_ColorBarItem():
        ##
        glw=GraphicsLayoutWidget()
        plt=glw.addPlot(title='Testing colormaps',labels={'left':'y','bottom':'x'})
        im=ImageItem()
        im.setLookupTable(get_colormap_lut())
        x=np.arange(100)-50
        y=np.arange(110)[:,None]-55
        z=np.exp(-(x**2+y**2)/100.0)
        im.setImage((z+0*np.random.random(z.shape))*3.4e-29)
        plt.addItem(im)
        cb=ColorBarItem(image=im)
        cb.setLabel('intensity')
        glw.addItem(cb)
        glw.show()
        ##
        return glw
        
    def test_add_right_axis():
        ##
        left_pen=(255,0,0)
        right_pen=(0,128,0)
        pw=PlotWidget(labels={'left':'left axis','bottom':'bottom axis','right':'right axis'})
        pw.getPlotItem().getAxis('left').setPen(left_pen)
        pw.plot([1,2,3],[3,4,5],pen=left_pen)
        vb=add_right_axis(pw,pen=right_pen)
        #vb.addItem(PlotDataItem([2,3,4],[7,6,5],pen=right_pen))
        vb.plot([2,3,4],[7,6,5],pen=right_pen)
        pw.show()
        ##
        return pw
        
    def test_AlignedPlotItem():
        ##
        glw=GraphicsLayoutWidget()
        gl=glw.ci
        gl.setBorder((255,0,0))
        plt1=gl.addAlignedPlot(labels={'left':'left 1','top':'top 1','right':'right 1'},x=[1,2,3],y=[3,4,5])
        gl.addHorizontalSpacer()
        plt2=gl.addAlignedPlot(labels={'left':'left 2','top':'top 2','right':'right 2'})
        gl.addHorizontalSpacer(5)
        gl.addColorBar(label='color',row=2)
        gl.nextRows()
        gl.addVerticalSpacer(50)
        plt3=gl.addAlignedPlot(labels={'left':'left 3'},x=[1,5,6],y=[2,8,1])
        plt3r=add_right_axis(plt3,pen=(255,0,0))
        plt3r.plot([1,2,3],[4,5,6],pen=(255,0,0))
        glw.show()
        ##
        return glw
    
    def test_GraphicsLayout():
        ##
        gv=GraphicsView()
        gl=GraphicsLayout()
        gl.setBorder((255,0,0))
        #glw.ci.layout.setSpacing(setSpacing(0)
        #gl.setSpacing(0)
        plt1=AlignedPlot(gl,labels={'left':'left 1','top':'top 1','right':'right 1'})
        gl.nextRows()
        
        gv.setCentralItem(gl)
        gv.show()
        ##
        return gl
        
    if __name__=="__main__":
        ret_vals=[fun() for fun in (test_ColorBarItem,
        test_add_right_axis,test_AlignedPlotItem,test_GraphicsLayout)]
        close_all()
        