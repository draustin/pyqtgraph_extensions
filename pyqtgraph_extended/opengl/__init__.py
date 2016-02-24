from pyqtgraph.opengl import *
from pyqtgraph_extensions.opengl import *

if __name__=="__main__":
    def test_GLViewWidget():
        view=GLViewWidget()
        ai=GLAxisItem()
        view.addItem(ai)
        view.show()
        return view
    view=test_GLViewWidget()