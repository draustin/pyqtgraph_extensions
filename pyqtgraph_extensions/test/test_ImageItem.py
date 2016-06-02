"""
Check out how ImageItem behaves with nan values and how to make a mask e.g. to
grey out undefined phase values.
More investigation than testing.
"""
import numpy as np
import pyqtgraph_extended as pg
##
x=np.arange(100)
y=np.arange(120)[:,None]
f=np.exp(-((x-50)**2+(y-60)**2)/200)
fp=f.copy()
fp[0,0]=float('nan')
fp[f<0.2]=float('nan')
plt=pg.plot()
im=pg.ImageItem(fp)
im.setRect(pg.axes_to_rect(x,y))
im.setLookupTable(pg.get_colormap_lut())
im.setLevels((0,1))
plt.addItem(im)
##
f3=pg.makeARGB(f,pg.get_colormap_lut(),levels=(0,1),useRGBA=True)[0]#[:,:,[1,2,3,0]]
f3[f<0.1]=[128,128,128,128]
plt=pg.plot()
im=pg.ImageItem(f3)
im.setRect(pg.axes_to_rect(x,y))
#im.setLookupTable(pg.get_colormap_lut())
plt.addItem(im)
