"""py.test script for pyqtgraph_recipes
Requires py.test plugin pytest-qt.

According to https://pytest-qt.readthedocs.io/en/latest/tutorial.html, could
call qtbot.addWidget on the widgets to register them for proper destruction.
However, it seems to work if I don't. What IS crucial is passing qtbot as an
argument to the method - this activates the 'fixture':
http://doc.pytest.org/en/latest/fixture.html
Found that in another test script (usp_plot) with more widgets that it crashes
if I don't. So will do so for good practice.
"""
import math
import numpy as np
import fourier
import pyqtgraph_extended as pg
import pyqtgraph_recipes as pgr

def test_plot_polar_image_1(qtbot):
    r=np.linspace(0,3)[:,None]
    num_phi=50
    phi=np.arange(0,num_phi)/num_phi*math.pi
    data=np.cos(phi-math.pi/4)*r*np.exp(-r)
    fig=pgr.plot_polar_image(r,phi,data,r_label_phi=-3*math.pi/4)
    return fig
    
def test_plot_polar_image_2(qtbot):
    r=np.linspace(0,3)[:,None]
    num_phi=50
    phi=np.arange(0,num_phi)/num_phi*math.pi*2
    data=np.cos(phi-math.pi/4)*r*np.exp(-r)
    fig=pgr.plot_polar_image(r,phi,data,theta_repeats=True,r_label_phi=3*math.pi/4,grid_r=[0,1,2],lut=pg.get_colormap_lut('grey'),levels=(-0.1,0.1),cbar_label='intensity')
    return fig
  
def test_plot_polar_image_3(qtbot):
    ##
    r=np.linspace(0,3)[:,None]
    num_phi=50
    phi=np.arange(0,num_phi)/num_phi*math.pi*2
    data=np.cos(phi-math.pi/4)*r*np.exp(-r)
    fig=pgr.plot_polar_image(r,phi,data,theta_repeats=True,mask_array=data,cbar_label='intensity')
    ##
    return fig
    
def test_plot_radial_grid_lines(qtbot):
    p1=pg.PlotWindow()
    pgr.plot_radial_grid_lines(p1,np.arange(0.1,1,0.1))
            
    p2=pg.PlotWindow()
    pgr.plot_radial_grid_lines(p2,np.arange(0.1,1,0.1),'r','%.1f')
    return p1,p2
    
def test_ImageWithProjsAligned(qtbot):
    ip=pgr.ImageWithProjsAligned()
    ip.widget.show()
    return ip

t=np.linspace(-150,150,100)
omega_0=2.35
T0=50
alpha=0.004
Et=2*np.exp(-0.5*(t/T0)**2-1j*(omega_0*t-alpha*t**2))
omega=fourier.conj_axis(t,omega_0)

def test_PhaseSpacePlot(qtbot):
    ipp=pgr.ImageWithProjsAlignedPlot()
    psp=pgr.PhaseSpacePlot(ipp.plots,ftd=fourier.FTD(x=t,k=omega,sign=1),Ex=Et,cbar=ipp.cbar,lut=pg.get_colormap_lut())
    return psp

def test_PhaseSpacePlotAligned(qtbot):
    psp=pgr.PhaseSpacePlotAligned(ftd=fourier.FTD(x=t,k=omega,sign=1),Ex=Et,bound_cond='cyclic')
    return psp
    
if __name__=="__main__":
    figs=[]
    figs.append(test_plot_polar_image_1(None))
    figs.append(test_plot_polar_image_2(None))
    figs.append(test_plot_polar_image_3(None))
    figs.append(test_plot_radial_grid_lines(None))
    figs.append(test_ImageWithProjsAligned(None))
    figs.append(test_PhaseSpacePlot(None))
    figs.append(test_PhaseSpacePlotAligned(None))
    