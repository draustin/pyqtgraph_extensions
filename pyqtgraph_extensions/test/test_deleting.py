import pyqtgraph as pg
import pyqtgraph_extensions as pgx
from pyqtgraph import QtGui

def make_gl():
    gl=pg.GraphicsLayoutWidget()
    for r in range(3):
        for c in range(2):
            gl.addPlot()
        gl.nextRow()
    return gl
    
def make_glx():
    gl=pgx.GraphicsLayoutWidget()
    for r in range(1):
        for c in range(2):
            gl.addAlignedPlot()
        gl.nextRows()
    return gl

def test_standalone(make):
    for _ in range(100):
        gl=make()
        gl.show()

def test_in_widget(make):
    w=QtGui.QWidget()
    hb=QtGui.QHBoxLayout()
    w.setLayout(hb)
    w.resize(800,800)
    w.show()
    
    for _ in range(10):
        gl=make()
        hb.addWidget(gl)
        QtGui.QApplication.processEvents()
        hb.removeWidget(gl)
        gl.deleteLater()
        QtGui.QApplication.processEvents()
    
    return w
    
# 27/6/2016 gives error. but clear works
w=test_in_widget(make_glx)


        