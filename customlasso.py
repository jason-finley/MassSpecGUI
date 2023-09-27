from matplotlib.widgets import _SelectorWidget
from matplotlib.lines import Line2D
from matplotlib.widgets import _api


class myLassoSelector(_SelectorWidget):
    @_api.rename_parameter("3.5", "lineprops", "props")
    def __init__(self, ax, onselect, tensor, label, useblit=True, props=None, button=None):
        super().__init__(ax, onselect, useblit=useblit, button=button)
        self.verts = None
        props = {
            **(props if props is not None else {}),
            # Note that self.useblit may be != useblit, if the canvas doesn't
            # support blitting.
            'animated': self.useblit, 'visible': False,
        }
        line = Line2D([], [], **props)
        self.ax.add_line(line)
        self._selection_artist = line
        self.tensor = tensor
        self.total_average = "None"
        self.averages = []
        self.type = None
        self.label = label

    def _press(self, event):
        self.verts = [self._get_data(event)]
        self._selection_artist.set_visible(True)
        self.average = None
        self.update()

    def _release(self, event):
        if self.verts is not None:
            self.verts.append(self._get_data(event))
            self.total_average, self.averages = self.onselect(self.verts, self.tensor)

        self._selection_artist.set_data([[], []])
        self._selection_artist.set_visible(False)
        if type(self.total_average) != str:
            self.label.config(text = round(self.total_average, 9))
        else:
            self.label.config(text = self.total_average)


    def _onmove(self, event):
        if self.verts is None:
            return
        self.verts.append(self._get_data(event))
        self._selection_artist.set_data(list(zip(*self.verts)))

        self.update()
