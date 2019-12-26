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

## Features

See [`pyqtgraph_extensions/examples`](pyqtgraph_extensions/examples) for some examples.

### Axis alignment across multiple plot items

The `AlignedPlotItem` is so-called because it uses its parent's graphics layout object for holding its constituent items (view box, axis items and title) rather than creating one internally. Its constituents can therefore be aligned with those of other items in the parent's graphics layout, including the constituent items of other `AlignedPlotItem` objects. Here's an [example](pyqtgraph_extensions/examples/demo_axis_alignment.py).
![](screenshots/axis_alignment.png)
The extensions include:

### More axis controls

`AxisItem` is reimplemented with its own buttons for autoranging at the upper and lower limits.
![](screenshots/axis_buttons_labelled.png)

### Traditional interactive color bar

`pyqtgraph_extensions` adds a MATLAB-style `ColorBarItem` which can be linked to multiple ImageItems.

![](screenshots/live_colorbaritem.gif)

### Miscellaneous

* Simplified exporting
* Easy adding of a second vertical axis on the right hand side (with linked x axis), likewise for a second horizontal axis on the top.
* More [GLGraphicsItems](http://www.pyqtgraph.org/documentation/3dgraphics/glgraphicsitem.html)

## Dependencies & compatibility

Required:
* Python >= 3.5.
* [PyQtGraph](http://www.pyqtgraph.org/) installed from [conda](https://anaconda.org/anaconda/pyqtgraph) or  [PyPi](https://pypi.org/project/pyqtgraph/).
* [SciPy](https://www.scipy.org/).

Optional:
* [mathx](https://github.com/draustin/mathx)  - required (the polar plots in) for [`pyqtgraph_recipes`](pyqtgraph_recipes).

## Test environment

* `tox` with `tox-conda`
* `pytest` with `pytest-qt`

## Plan / outlook

I developed the various features as needed and will continue on the same basis. When I began writing `pyqtgraph_extensions` I was just starting out with Python, Git/GitHub, and open source tools in general (I'm a convert from MATLAB).

I'd be happy for any/all features to be moved into `pyqtgraph` proper. Feel free to [reach out](mailto:dane_austin@fastmail.com.au).
