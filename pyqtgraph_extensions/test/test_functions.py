import numpy as np
import pyqtgraph_extended as pg

def test_image_axes_cbar(qtbot):
    x=np.arange(-50,50)[:,None]
    y=np.arange(-60,60)
    z=np.exp(-(x**2+y**2)/20**2)
    fig=pg.image_axes_cbar(x,y,z,labels={'left':'y','bottom':'x'})
    return fig
    
if __name__=="__main__":
    fig=test_image_axes_cbar(None)
    