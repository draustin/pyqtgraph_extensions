import os,logging
import pyqtgraph as pg
from pyqtgraph import QtGui,QtCore
import pyqtgraph_extensions as pgx
import numpy as np

logging.basicConfig(level=logging.DEBUG)
logging.getLogger(pgx.__name__).setLevel(level=logging.DEBUG)

def test_ColorBarItem_manual():
    ##
    glw=pg.GraphicsLayoutWidget()
    plt=glw.addPlot(title='Testing colormaps',labels={'left':'y','bottom':'x'})
    im=pgx.ImageItem()
    im.setLookupTable(pgx.get_colormap_lut())
    x=np.arange(100)-50
    y=np.arange(110)[:,None]-55
    z=5e9*np.exp(-(x**2+y**2)/100.0)
    im.setImage(z+np.random.random(z.shape))
    plt.addItem(im)
    cb=pgx.ColorBarItem()
    cb.setManual(lut=im.lut,levels=im.levels)
    #cb.setLabel('intensity')
    glw.addItem(cb)
    glw.show()
    ##
    return glw


def test_ColorBarItem():
    ##
    glw=pg.GraphicsLayoutWidget()
    plt=glw.addPlot(title='Testing colormaps',labels={'left':'y','bottom':'x'})
    im=pgx.ImageItem()
    im.setLookupTable(pgx.get_colormap_lut())
    x=np.arange(100)-50
    y=np.arange(110)[:,None]-55
    z=5e9*np.exp(-(x**2+y**2)/100.0)
    im.setImage(z+np.random.random(z.shape))
    plt.addItem(im)
    cb=pgx.ColorBarItem(image=im)
    #cb.setLabel('intensity')
    glw.addItem(cb)
    glw.show()
    ##
    return glw
    
def test_add_right_axis():
    ##
    left_pen=(255,0,0)
    right_pen=(0,128,0)
    pw=pg.PlotWidget(labels={'left':'left axis','bottom':'bottom axis','right':'right axis'})
    pw.getPlotItem().getAxis('left').setPen(left_pen)
    pw.plot([1,2,3],[3,4,5],pen=left_pen)
    vb=pgx.add_right_axis(pw,pen=right_pen)
    #vb.addItem(pg.PlotDataItem([2,3,4],[7,6,5],pen=right_pen))
    vb.plot([2,3,4],[7,6,5],pen=right_pen)
    pw.show()
    ##
    return pw
    
def test_AlignedPlotItem():
    ##
    glw=pgx.GraphicsLayoutWidget()
    gl=glw.ci
    gl.setBorder((255,0,0))
    plt1=gl.addAlignedPlot(labels={'left':'left 1','top':'top 1','right':'right 1'},x=[1,2,3],y=[3,4,5])
    gl.addHorizontalSpacer()
    plt2=gl.addAlignedPlot(labels={'left':'left 2','top':'top 2','right':'right 2'})
    plt2.setYLink(plt1)
    gl.addHorizontalSpacer(5)
    gl.addColorBar(label='color',rel_row=2)
    gl.nextRows()
    gl.addVerticalSpacer(50)
    gl.nextRow()
    plt3=gl.addAlignedPlot(labels={'left':'left 3'},x=[1,5,6],y=[2,8,1])
    plt3r=pgx.add_right_axis(plt3,pen=(255,0,0))
    plt3r.plot([1,2,3],[4,5,6],pen=(255,0,0))
    gl.setColumnStretchFactor(2,rel_col=-2)
    gl.setRowStretchFactor(2,rel_row=2)
    glw.show()
    ##
    return glw
 
def test_GraphicsLayout():
    ##
    gv=pg.GraphicsView()
    gl=pgx.GraphicsLayout()
    gl.setBorder((255,0,0))
    #glw.ci.layout.setSpacing(setSpacing(0)
    #gl.setSpacing(0)
    gl.addLabel('cow',col=1)
    gl.nextRow()
    plt1=gl.addAlignedPlot(labels={'left':'left 1','top':'top 1','right':'right 1','bottom':'bottom 2'},title='adfasfdasfjsadhflasdjflafasdfdasfdsadfasfasdfasdfasdfasdfasfsadfadsasdhfsadfsdlafasdfsadl')
    gl.nextRows()
    
    gv.setCentralItem(gl)
    gv.show()
    ##
    return gl
    
    
def test_GraphicsLayout2():
    ##
    gv=pg.GraphicsView()
    gl=pgx.GraphicsLayout()
    gl.setBorder((255,0,0))
    #glw.ci.layout.setSpacing(setSpacing(0)
    #gl.setSpacing(0)
    gl.addLabel('cow',col=1)
    gl.nextRow()
    plt1=gl.addAlignedPlot(labels={'top':'top 1','right':'right 1'},create={'left':False,'title':False})
    gl.nextRows()
    
    gv.setCentralItem(gl)
    gv.show()
    ##
    return gl
    
def test_complex_layout():
    ##
    hspace=20
    vspace=20
    glw=pgx.GraphicsLayoutWidget()
    gl=glw.ci
    plots={}
    #top
    plt=gl.addAlignedPlot(col=4,labels={'left':'intensity','top':'x'})
    plt.getAxis('bottom').setStyle(showValues=False)
    plt.showAxis('right')
    plt.getAxis('right').setStyle(showValues=False)
    plt.getAxis('left').setWidth(0)
    plots['top']=plt
    gl.nextRows()
    gl.addVerticalSpacer(vspace)
    gl.nextRow()
    # left
    plt=gl.addAlignedPlot(labels={'left':'y','bottom':'intensity'})
    for axis in ('top','right'):
        plt.showAxis(axis)
        plt.getAxis(axis).setStyle(showValues=False)
    plt.getAxis('bottom').setHeight(0)
    plots['left']=plt
    gl.addHorizontalSpacer(hspace)
    # middle
    plt=gl.addAlignedPlot()
    for axis in ('top','bottom','left','right'):
        plt.showAxis(axis)
        plt.getAxis(axis).setStyle(showValues=False)
    plots['middle']=plt
    gl.addHorizontalSpacer(hspace)
    # right
    plt=gl.addAlignedPlot(labels={'right':'y','top':'intensity'})
    for axis in ('left','bottom'):
        plt.getAxis(axis).setStyle(showValues=False)
    plt.getAxis('top').setHeight(0)
    plots['right']=plt
    gl.nextRows()
    gl.addVerticalSpacer(vspace)
    gl.nextRow()
    # bottom
    plt=gl.addAlignedPlot(col=4,labels={'left':'intensity','bottom':'x'})
    for axis in ('top','right'):
        plt.showAxis(axis)
        plt.getAxis(axis).setStyle(showValues=False)
    plt.getAxis('left').setWidth(0)
    plots['bottom']=plt
    
    gl.setRowStretchFactor(2,row=7)
    gl.setColumnStretchFactor(2,col=5)
    glw.show()
    ##
    glw._repr_png_()
    return glw
    
def test_PlotWindow():
    fig=pgx.plot([1,2,3])
    fig._repr_png_()
    
def test_cornertext():
    plt=pg.plot([1,2,3],[1,4,9])
    pgx.cornertext('(top left, default)',plt)
    pgx.cornertext('(top right, red)',plt,(1,0),color='r')
    pgx.cornertext('(bottom right, bold italic)',plt,(1,1),bold=True,italic=True)

def test_AlignedPlotItem_log():
    glw=pgx.GraphicsLayoutWidget()
    plt=glw.addAlignedPlot()
    plt.plot(range(1,100),np.arange(1,100)**2)
    plt.setLogMode(x=True,y=True)
    glw.show()
    return glw
    
def test_AnchoredPlotItem():
    glw=pg.GraphicsLayoutWidget()
    plt=glw.addPlot()
    plt.plot(range(10),np.arange(10)**2)
    ini=pgx.AnchoredPlotItem(plt,anchor=(1,0),offset=(-50,0))
    ini.plot(range(10),-np.arange(10)**2)
    glw.show()
    return glw

def test_all():
    ret_vals=[fun() for fun in (test_ColorBarItem,
    test_add_right_axis,test_AlignedPlotItem,test_GraphicsLayout,test_GraphicsLayout2,test_cornertext,test_complex_layout,test_PlotWindow,test_AlignedPlotItem)]
    pgx.export(ret_vals[-3],os.path.join(os.path.expanduser('~'),'test'),('png','svg'))
    pgx.close_all()
    

    
    
if __name__=="__main__":
    if QtCore.QCoreApplication.instance() is not None:
        app = QtGui.QApplication([])
    #test_all()
    #f=test_AnchoredPlotItem()
    f=test_ColorBarItem_manual()
    