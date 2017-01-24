from . import *

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

def image_axes_cbar(x,y,im,labels={},title=None,**kwargs):
    glw=GraphicsLayoutWidget()
    plot=glw.addAlignedPlot(labels=labels,title=title)
    image=plot.image(im,rect=axes_to_rect(x,y),**kwargs)
    cbar=glw.addColorBar(image=image,rel_row=2)
    glw.show()
    return glw,plot,image,cbar