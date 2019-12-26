import math, os
import numpy as np
import pyqtgraph_extended as pg
import mathx
from mathx import usv


class ImageWithProjsAlignedPlot:
    """Plot items for an image and its projections/marginals, and a colorbar,
    all aligned by a GraphicsLayout."""

    def __init__(self, gl=None, cornertexts=None):
        """Create plot items and colorbar.
        All items are managed by GraphicsLayout gl. If gl is not created,
        a GraphicsLayoutWidget is created too (for interactive plotting).
        The origin (upper left corner cell) is gl's current row and column."""

        def show(plt, axes):
            for axis in axes:
                plt.showAxis(axis)
                plt.getAxis(axis).setStyle(showValues=False)

        s = {}
        if gl is None:
            self.widget = pg.GraphicsLayoutWidget()
            self.widget.show()
            gl = self.widget.ci
        else:
            self.widget = None
        row_0 = gl.currentRow
        col_0 = gl.currentCol
        vspace = 10
        hspace = 10
        vp = gl.addAlignedPlot(row_0 + 0, col_0)  # labels={'left':'&omega;','top':'intensity'}
        show(vp, ('bottom', 'right'))
        vp.getAxis('top').show()
        vp.getAxis('bottom').setHeight(0)
        gl.addHorizontalSpacer(hspace, row_0 + 5, col_0 + 3)
        ip = gl.addAlignedPlot(row_0 + 0, col_0 + 4)
        show(ip, ('top', 'left', 'right', 'bottom'))
        gl.addHorizontalSpacer(hspace, row_0 + 2, col_0 + 7)
        cbar = pg.ColorBarItem()
        gl.addItem(cbar, row_0 + 2, col_0 + 8)
        gl.addVerticalSpacer(vspace, row_0 + 4, col_0)
        hp = gl.addAlignedPlot(row_0 + 5, col_0 + 4)  # ,labels={'left':'intensity','bottom':'t'})
        show(hp, ('top', 'right'))
        hp.getAxis('left').setWidth(0)
        hp.getAxis('right').setWidth(0)
        ip.setXLink(hp)
        ip.setYLink(vp)
        gl.setColumnStretchFactor(2, col_0 + 5)
        gl.setRowStretchFactor(2, row_0 + 2)

        self.layout = gl
        self.plots = {'vert': vp, 'horz': hp, 'image': ip}
        self.cbar = cbar

        if cornertexts is not None:
            if len(cornertexts) == 0:
                cornertexts = {'vert': '(a)', 'image': '(b)', 'horz': '(c)'}
            self.cornertexts = {}
            for plot_name, text in cornertexts.items():
                self.cornertexts[plot_name] = pg.cornertext(text, self.plots[plot_name])


class ImageWithProjsAligned(ImageWithProjsAlignedPlot):
    """Extends :class:`.ImageWithProjsAlignedPlot' to include the image item and
    projection curve items."""

    def __init__(self, gl=None, cornertexts=None):
        ImageWithProjsAlignedPlot.__init__(self, gl, cornertexts)
        self.image = self.plots['image'].image()
        self.horz_proj = self.plots['horz'].plot()
        self.vert_proj = self.plots['vert'].plot()
        self.horz_buffers = []
        self.vert_buffers = []
        self.cbar.setImage(self.image)

    def set(self, x, y, image, horz_proj=None, vert_proj=None, pen=pg.mkPen(), **kwargs):
        """Set image and projection data

        TODO: more flexibility and more consistent semantics with options on
            pyqtgraph plotting commands
        Args:
            x (vector of length m): the x axis
            y (vector of length n): the y axis
            image (mxn array): the image
            horz_proj (vector of length m): horizontal projection. If None, use
                sum over y axis of image
            vert_proj (vector of length n): vertical projection. If None, use
                sum over x axis of image
            pen: passed on to the projection setData methods
            lut: passed on to image setImage method
        """
        if any([x is None, y is None, image is None]):
            return
        x = x.squeeze()
        y = y.squeeze()
        if horz_proj is None:
            horz_proj = image.sum(1)
        if vert_proj is None:
            vert_proj = image.sum(0)
        self.image.setImage(image, autoLevels=False, **kwargs)
        self.image.setRect(pg.axes_to_rect(x, y))
        self.horz_proj.setData(x, horz_proj, pen=pen)
        self.vert_proj.setData(vert_proj, y, pen=pen)

    def add_buffers(self, num, pen_style=pg.QtCore.Qt.SolidLine):
        pens = [pg.mkPen(color=col, style=pen_style) for col in ['r', 'g', 'b', 'm', 'c', 'y']]
        ret = []
        for i in range(num):
            self.horz_buffers.append(self.plots['horz'].plot(pen=pens[i]))
            self.vert_buffers.append(self.plots['vert'].plot(pen=pens[i]))
            ret.append(len(self.horz_buffers) - 1)
        return ret  # returns indices of buffers that were just added (to be used in set_buffer_data())

    def set_buffer_data(self, indx, x, y, h_data, v_data):
        x = x.squeeze()
        y = y.squeeze()
        self.vert_buffers[indx].setData(v_data, y)
        self.horz_buffers[indx].setData(x, h_data)

    def hide_show_buffer(self, indx, val):
        if val:
            self.vert_buffers[indx].show()
            self.horz_buffers[indx].show()
        else:
            self.vert_buffers[indx].hide()
            self.horz_buffers[indx].hide()

    def clear_buffer(self, indx):
        self.vert_buffers[indx].clear()
        self.horz_buffers[indx].clear()


class ImageWithProjsAndLogAlignedPlot:
    """Plot items for an image, its projections, a colour bar as wells as two
    additional items for logged (historical) image projections"""

    def __init__(self, gl=None, cornertexts=None):
        self.recursion_prevent = False

        def show(plt, axes):
            for axis in axes:
                plt.showAxis(axis)
                plt.getAxis(axis).setStyle(showValues=False)

        if gl is None:
            self.widget = pg.GraphicsLayoutWidget()
            self.widget.show()
            gl = self.widget.ci
        else:
            self.widget = None
        row_0 = gl.currentRow
        col_0 = gl.currentCol
        vspace = 10
        hspace = 10
        vlog = gl.addAlignedPlot(row_0 + 0, col_0 + 0)
        show(vlog, ('bottom', 'right'))
        vlog.showAxis('top')
        gl.addHorizontalSpacer(2, row_0 + 0, col_0 + 3)
        vproj = gl.addAlignedPlot(row_0 + 0, col_0 + 4)
        show(vproj, ('bottom', 'left', 'right'))
        vproj.showAxis('top')
        vproj.getAxis('left').setWidth(15)
        gl.addHorizontalSpacer(hspace, row_0 + 0, col_0 + 7)
        imageplot = gl.addAlignedPlot(row_0 + 0, col_0 + 8)
        show(imageplot, ('top', 'left', 'right', 'bottom'))
        cbar = pg.ColorBarItem()
        gl.addItem(cbar, row_0 + 2, col_0 + 12)
        gl.addVerticalSpacer(vspace, row_0 + 4, col_0 + 0)
        gl2 = gl.addLayout(row_0 + 5, 0, rowspan=12, colspan=6)
        logimg = gl2.addAlignedPlot(0, 0)
        show(logimg, ('top', 'left', 'right', 'bottom'))
        hproj = gl.addAlignedPlot(row_0 + 5, col_0 + 8)
        show(hproj, ('left', 'bottom', 'top'))
        hproj.showAxis('right')
        gl.addVerticalSpacer(vspace, row_0 + 9, col_0 + 8)
        hlog = gl.addAlignedPlot(row_0 + 10, col_0 + 8)
        show(hlog, ('left', 'top'))
        hlog.showAxis('right')
        gl.setRowStretchFactor(row_0 + 6, col_0 + 2)
        gl.setColumnStretchFactor(row_0 + 6, col_0 + 9)

        self.image_cornertext = pg.cornertext(' ', imageplot)
        self.logimg_cornertext = pg.cornertext(' ', logimg)

        # initialise plots
        self.layout = gl
        self.plots = {'vert': vproj, 'horz': hproj, 'image': imageplot, 'vert_log': vlog, 'horz_log': hlog,
                      'log_image': logimg}
        self.cbar = cbar
        self.image = imageplot.image()
        self.hproj = hproj.plot()
        self.vproj = vproj.plot()
        self.hproj_log = hproj.plot()
        self.vproj_log = vproj.plot()
        self.hproj_ref = hproj.plot()
        self.vproj_ref = vproj.plot()
        self.hlog = hlog.image()
        self.vlog = vlog.image()
        self.logimg = logimg.image()

        # link axes and colorbar
        imageplot.setXLink(hproj)
        hproj.setXLink(hlog)
        vlog.sigXRangeChanged.connect(lambda: self.log_time_axis_link('v'))
        hlog.sigYRangeChanged.connect(lambda: self.log_time_axis_link('h'))
        imageplot.setYLink(vproj)
        vproj.setYLink(vlog)
        self.cbar.setImages([self.image])

    def set_image(self, x, y, image, pen=pg.mkPen('k'), datetimestr=None, **kwargs):
        """
        Args:
            kwargs: passed on to image.setImage
        """
        if any([x is None, y is None, image is None]):
            return
        horz_proj = image.sum(1)
        vert_proj = image.sum(0)
        x = x.squeeze()
        y = y.squeeze()
        self.image.setImage(image, autoLevels=False, **kwargs)
        self.image.setRect(pg.axes_to_rect(x, y))
        self.hproj.setData(x, horz_proj, pen=pen)
        self.vproj.setData(vert_proj, y, pen=pen)
        if datetimestr is not None:
            self.image_cornertext.setText(datetimestr, color='00FF00')

    def set_log(self, x, y, time, h_log, v_log, **kwargs):
        x = x.squeeze()
        y = y.squeeze()
        self.vlog.setImage(image=v_log, autoLevels=True, **kwargs)
        self.hlog.setImage(image=h_log, autoLevels=True, **kwargs)
        if len(time) > 1:
            self.hlog.setRect(pg.axes_to_rect(x, time))
            self.vlog.setRect(pg.axes_to_rect(time, y))

    def set_log_lines(self, x, y, hData, vData):
        x = x.squeeze()
        y = y.squeeze()
        self.vproj_log.setData(vData, y, pen=pg.mkPen('b'))
        self.hproj_log.setData(x, hData, pen=pg.mkPen('b'))

    def set_log_img(self, x, y, img, datetimestr=None, **kwargs):
        x = x.squeeze()
        y = y.squeeze()
        self.logimg.setImage(image=img, autoLevels=True, **kwargs)
        if datetimestr is not None:
            self.logimg_cornertext.setText(datetimestr, color='0000FF')

    def clear_log(self):
        self.logimg.clear()
        self.vlog.clear()
        self.hlog.clear()
        self.vproj_log.clear()
        self.hproj_log.clear()

    def log_time_axis_link(self, direction):
        if direction is 'v':
            lims = self.plots['vert_log'].vb.state['viewRange'][0]
            if self.recursion_prevent is True:
                return
            self.recursion_prevent = True
            self.plots['horz_log'].setYRange(lims[0], lims[1])
            self.recursion_prevent = False
        else:
            lims = self.plots['horz_log'].vb.state['viewRange'][1]
            if self.recursion_prevent is True:
                return
            self.recursion_prevent = True
            self.plots['vert_log'].setXRange(lims[0], lims[1])
            self.recursion_prevent = False

    def set_ref_lines(self, x, y, hData, vData):
        x = x.squeeze()
        y = y.squeeze()
        self.vproj_ref.setData(vData, y, pen=pg.mkPen('g'))
        self.hproj_ref.setData(x, hData, pen=pg.mkPen('g'))

    def clear_ref(self):
        self.vproj_ref.clear()
        self.hproj_ref.clear()




def polar_grid_anchor(phi):
    c = math.cos(phi)
    s = math.sin(phi)
    l = 0.5/max(abs(c), abs(s))
    return 0.5 - c*l, 0.5 + s*l


def plot_radial_grid_lines(plot, rs, color='k', label_format=None, labels=None, label_angle=math.pi/4):
    if labels is None:
        if label_format is None:
            labels = [None]*len(rs)
        else:
            labels = [label_format%r for r in rs]

    def plot_circle(r, label, label_angle):
        phi = np.arange(102)/100*2*math.pi
        plot.plot(np.cos(phi)*r, np.sin(phi)*r, pen=color)
        if label is not None:
            text = pg.TextItem(label, color=color, anchor=(0.5, 0.8),
                               angle=-90 + math.degrees(label_angle))  # (0.5,0.8)) # polar_grid_anchor(label_angle)
            text.setPos(math.cos(label_angle)*r, math.sin(label_angle)*r)
            plot.addItem(text)

    if not hasattr(label_angle, '__iter__'):
        label_angle = [label_angle]*len(rs)
    for r, label, label_angle in zip(rs, labels, label_angle):
        plot_circle(r, label, label_angle)


def plot_azimuthal_grid_lines(plot, phis, r=1, color='k', label_format=None, labels=None, unit=math.pi, phi_0=0,
        phi_dir=1):
    if labels is None:
        if label_format is None:
            labels = [None]*len(phis)
        else:
            labels = [label_format%(phi/unit) for phi in phis]

    def plot_line(phi_true, label):
        c = math.cos(phi_true)
        s = math.sin(phi_true)
        plot.plot([0, c*r], [0, s*r], pen=color)
        if label is not None:
            text = pg.TextItem(html=label, anchor=polar_grid_anchor(phi_true))
            text.setColor(color)
            text.setPos(c*r, s*r)
            plot.addItem(text)

    phi_trues = phi_0 + phi_dir*phis
    for phi_true, label in zip(phi_trues, labels):
        plot_line(phi_true, label)


def plot_polar_image(r, phi, data, layout=None, r_label_phi=math.pi/4, grid_r=None, levels=None, lut=None,
        cbar_label=None, phi_0=0, phi_dir=1, r_label_fmt='%g', aspect_locked=True, mask_array=None, theta_repeats=None,
        grid_color='w', osamp=1):
    """
    Args:
        r (uniformly sampled vector of shape (n,1) or (n,)): radii
        phi (uniformly sampled vector of shape (m,)): azimuthal angles in radians
        data (array of shape (n,m)): data to plot
        layout (pyqtgraph GraphicsLayout): if None, a GraphicsLayoutWidget is created.
            An AlignedPlotItem is added to the layout.
        mask_array (array of same shape as data): mask for data - where it is negative
            data will be greyed out. The pyqtgraph ImageItem will be in RGB rather
            than scalar format, and the color bar will not be adjustable.
    """
    assert usv.is_usv(r)
    assert usv.is_usv(phi)
    if layout is None:
        layout_ = pg.GraphicsLayoutWidget()
    else:
        layout_ = layout
    plt = layout_.addAlignedPlot()
    plt.hideAxis('left')
    plt.hideAxis('bottom')
    if lut is None:
        lut = pg.get_colormap_lut()
    if isinstance(lut, str):
        lut = pg.get_colormap_lut(lut)
    phip = phi_0 + phi_dir*phi
    x, y, data = mathx.polar_reg_grid_to_rect(r.squeeze(), phip, data, theta_repeats, osamp)
    if mask_array is not None:
        _, _, mask_array = mathx.polar_reg_grid_to_rect(r.squeeze(), phip, mask_array, theta_repeats, osamp)
        if levels is None:
            data_masked = data[mask_array >= 0]
            levels = data_masked.min(), data_masked.max()
        image_data = pg.makeARGB(data.T, lut, levels=levels, useRGBA=True)[0]
        image_data[mask_array.T < 0] = [128, 128, 128, 128]
        image = plt.image(image_data, rect=pg.axes_to_rect(x, y), levels=(0, 255))
    else:
        image = plt.image(data.T, rect=pg.axes_to_rect(x, y), lut=lut)
        if levels is not None:
            image.setLevels(levels)
    if grid_r is None:
        grid_r = np.arange(1, 5)/5*r[-1]
    if len(grid_r) > 0:
        plot_radial_grid_lines(plt, grid_r, grid_color, r_label_fmt,
                               label_angle=phi_0 + phi_dir*np.asarray(r_label_phi))
        phi_lines = (np.round(phi[-1]/(math.pi/2)) - np.arange(4))*math.pi/2
        plot_azimuthal_grid_lines(plt, phi_lines, grid_r[-1], grid_color, '%g&pi;', unit=math.pi, phi_0=phi_0,
                                  phi_dir=phi_dir)
    plt.setAspectLocked(aspect_locked)
    plt.setXRange(x[0], x[-1], padding=0)
    plt.setYRange(y[0], y[-1], padding=0)
    if cbar_label is not None:
        layout_.addHorizontalSpacer(5)
        # Add color bar
        cbar = layout_.addColorBar(label=cbar_label, rel_row=2)
        if mask_array is not None:
            cbar.setManual(lut, levels)
        else:
            cbar.setImage(image)
    if layout is None:
        layout_.show()
        return layout_
    else:
        return plt


def parula():
    with open(os.path.join(os.path.dirname(__file__), 'parula.txt'), 'rb') as f:
        lines = f.readlines()
    r = np.array([[float(num) for num in line.strip().split()] for line in lines])*255
    return r


def parula_white():
    with open(os.path.join(os.path.dirname(__file__), 'parula_white.txt'), 'rb') as f:
        lines = f.readlines()
    r = np.array([[float(num) for num in line.strip().split()] for line in lines])*255
    return r


def jet_white():
    with open(os.path.join(os.path.dirname(__file__), 'jet_white.txt'), 'rb') as f:
        lines = f.readlines()
    r = np.array([[float(num) for num in line.strip().split()] for line in lines])*255
    return r


def jet_white_clip():
    with open(os.path.join(os.path.dirname(__file__), 'jet_white_clip.txt'), 'rb') as f:
        lines = f.readlines()
    r = np.array([[float(num) for num in line.strip().split()] for line in lines])*255
    return r