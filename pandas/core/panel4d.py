""" Panel4D: a 4-d dict like collection of panels """

from pandas.core.panel import Panel
from pandas.core import panelnd

Panel4D = panelnd.create_nd_panel_factory(
    klass_name   = 'Panel4D',
    axis_orders  = [ 'labels','items','major_axis','minor_axis'],
    axis_slices  = { 'labels' : 'labels', 'items' : 'items',
                     'major_axis' : 'major_axis',
                     'minor_axis' : 'minor_axis' },
    slicer       = Panel,
    axis_aliases = { 'major' : 'major_axis', 'minor' : 'minor_axis' },
    stat_axis    = 2)



def panel4d_init(self, data=None, labels=None, items=None, major_axis=None,
                 minor_axis=None, copy=False, dtype=None):
    """
    Represents a 4 dimensonal structured

    Parameters
    ----------
    data : ndarray (labels x items x major x minor), or dict of Panels

    labels : Index or array-like : axis=0
    items  : Index or array-like : axis=1
    major_axis : Index or array-like: axis=2
    minor_axis : Index or array-like: axis=3

    dtype : dtype, default None
    Data type to force, otherwise infer
    copy : boolean, default False
    Copy data from inputs. Only affects DataFrame / 2d ndarray input
    """
    self._init_data(data=data, labels=labels, items=items,
                    major_axis=major_axis, minor_axis=minor_axis,
                    copy=copy, dtype=dtype)

Panel4D.__init__ = panel4d_init


