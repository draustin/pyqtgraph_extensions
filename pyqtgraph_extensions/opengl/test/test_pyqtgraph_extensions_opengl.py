import numpy as np
import pyqtgraph as pg
import pyqtgraph_extensions.opengl as pglx

def test_GLViewWidget(qtbot):
    view=pglx.GLViewWidget(title='test_GLViewWidget')
    ai=pglx.GLAxisItem()
    view.addItem(ai)
    view.show()
    view._repr_png_()
    return view
    
def test_text(qtbot):
    view=pglx.GLViewWidget(title={'string':'test_text','color':(1,0,0),'font':pg.QtGui.QFont('',20)})
    for n in range(10):
        ti=pglx.GLTextItem(str(n),np.random.random(3),np.random.random(3))
        view.addItem(ti)
    view.show()
    return view
    
def test_box(qtbot):
    ##
    view=pglx.GLViewWidget()
    view.setTitle(string='test_box',color=(0,0,1))
    b=pglx.GLWireBoxItem()
    b.size=[1,2,3]
    view.addItem(b)
    ai=pglx.GLAxisItem()
    view.addItem(ai)
    ti=pglx.GLTextItem('0.5,1,1.5',[0.5,1,1.5])
    view.addItem(ti)
    view.show()
    ##
    return view
    
#ret_vals=[fun() for fun in (test_GLViewWidget,test_text,test_box)]