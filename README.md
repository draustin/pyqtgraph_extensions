# README

Various extensions for [pyqtgraph](https://github.com/pyqtgraph/pyqtgraph).

Installing `pyqtgraph_extensions` creates two namespaces:

* `pyqtgraph_extensions` - various classes and functions providing some of extra functionality for pyqtgraph
* `pyqtgraph_extended` - a namespace merging pyqtgraph_extensions with the original pyqtgraph

In principle, it should be possible to import `pyqtgraph_extended` instead of `pyqtgraph` and have the same behaviour but with new functionality available. So the two options for using this repository are:

    import pyqtgraph as pg
    import pyqtgraph_extensions as pgx

or

    import pyqtgraph_extended as pg

The extensions include:

* `AlignedPlotItem` - a substitute for [pyqtgraph.PlotItem](http://www.pyqtgraph.org/documentation/graphicsItems/plotitem.html?highlight=plotitem#pyqtgraph.PlotItem) in which the internal elements are managed by the parent layout. This allows for better control over the alignment and ensuring that the edges of plots line up.
* Simplified exporting
* Easy adding of a second vertical axis on the right hand side (with linked x axis), likewise for a second horizontal axis on the top.
* Color bar item - MATLAB-like alternative to Pyqtgraph that supports multiple images
* More [GLGraphicsItems](http://www.pyqtgraph.org/documentation/3dgraphics/glgraphicsitem.html)

See `pyqtgraph_extensions/examples` for some examples.

# Dependencies

Required:
* [PyQtGraph](http://www.pyqtgraph.org/)
* [SciPy](https://www.scipy.org/)

Optional:
* [mathx](https://github.com/draustin/mathx)  - required (the polar plots in) for `pyqtgraph_recipes`.

## Test environment

`tox` and `tox-conda`
