# README #

This repository contains two packages:

* pyqtgraph_extensions --- various classes and functions providing lots of extra functionality for pyqtgraph
* pyqtgraph_extended --- a namespace merging pyqtgraph_extensions with the original pyqtgraph

In principle, it should be possible to import pyqtgraph_extended instead of pyqtgraph and have the same behaviour but with new functionality available. So the two optics for use are:

    import pyqtgraph as pg
    import pyqtgraph_extendsions as pgx

or 

    import pyqtgraph_exended as pg