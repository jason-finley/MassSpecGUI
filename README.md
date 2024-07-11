# MassSpecGUI

Run lassosel.py to create a border on displayed image and calculate average value contained in selected area.

rectsel.py does the same thing but selected area is a rectange instead of a lasso selction.


Dependents:
customlasso.py needed for lassosel.py,
graphics.py needed for rectsel.py

matplotlib.widgets was modified for lassosel.py to take in matrix and label class variables for LassoSelector and "self.verts = None" line was removed from _release.
