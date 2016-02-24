        
# class HistogramLUTItem2(pg.HistogramLUTItem):
#     def __init__(self, image=None, fillHistogram=True):
#         pg.HistogramLUTItem.__init__(self,image,fillHistogram)
#         btn=pg.ButtonItem(pg.pixmaps.getPixmap('auto'), 14,self.axis)
# 
# 	
# 	
# class PlotItem2(pg.GraphicsWidget):
#     """pyqtgraph.PlotItem2 with different features:
#         no menu
#         bottons on axis limits to set manually
#         buttons to set to auto range
#         buttons to toggle auto range on/off 
#     """
#     def __init__(self,parent=None):
#         pg.GraphicsWidget.__init__(self,parent)
#         self.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
#         self.layout = QtGui.QGraphicsGridLayout()
#         self.layout.setContentsMargins(1,1,1,1)
#         self.setLayout(self.layout)
#         self.layout.setHorizontalSpacing(0)
#         self.layout.setVerticalSpacing(0)
#         self.vb=pg.ViewBox(parent=self)
#         self.vb.sigStateChanged.connect(self.viewStateChanged)
#         self.vb.sigRangeChanged.connect(self.sigRangeChanged)
#         self.vb.sigXRangeChanged.connect(self.sigXRangeChanged)
#         self.vb.sigYRangeChanged.connect(self.sigYRangeChanged)
#         self.layout.addItem(self.vb, 2, 1)
#         self.axes = {}
#         for k, pos in (('top', (1,1)), ('bottom', (3,1)), ('left', (2,0)), ('right', (2,2))):
#             axis = pg.AxisItem(orientation=k, parent=self)
#             axis.linkToView(self.vb)
#             self.axes[k] = {'item': axis, 'pos': pos}
#             self.layout.addItem(axis, *pos)
#             #axis.setZValue(-1000)
#             #axis.setFlag(axis.ItemNegativeZStacksBehindParent)
#         for i in range(4):
#             self.layout.setRowPreferredHeight(i, 0)
#             self.layout.setRowMinimumHeight(i, 0)
#             self.layout.setRowSpacing(i, 0)
#             self.layout.setRowStretchFactor(i, 1)
#         for i in range(3):
#             self.layout.setColumnPreferredWidth(i, 0)
#             self.layout.setColumnMinimumWidth(i, 0)
#             self.layout.setColumnSpacing(i, 0)
#             self.layout.setColumnStretchFactor(i, 1)
#         self.layout.setRowStretchFactor(2, 100)
#         self.layout.setColumnStretchFactor(1, 100)
#     def viewStateChanged(self):
#         print 'here'
#     def sigRangeChanged(self):
#         print 'here2'
#     def sigXRangeChanged(self):
#         print 'here2'
#     def sigYRangeChanged(self):
#         print 'here2'