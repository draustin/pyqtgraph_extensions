# README #

This repository contains two packages:

* pyqtgraph_extensions --- various classes and functions providing lots of extra functionality for pyqtgraph
* pyqtgraph_extended --- a namespace merging pyqtgraph_extensions with the original pyqtgraph

In principle, it should be possible to import pyqtgraph_extended instead of pyqtgraph and have the same behaviour but with new functionality available. So the two options for using this repository are:

    import pyqtgraph as pg
    import pyqtgraph_extensions as pgx

or 

    import pyqtgraph_extended as pg


## make it work on raspberry pi

```
sudo apt-get install libblas-dev
sudo apt-get install liblapack-dev
sudo apt-get install python-dev
sudo apt-get install libatlas-base-dev
sudo apt-get install gfortran
sudo apt-get install python-setuptools
sudo easy_install scipy
```

