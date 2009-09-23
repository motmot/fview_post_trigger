import warnings, time
import enthought.traits.api as traits
import motmot.fview.traited_plugin as traited_plugin
import numpy as np
from enthought.traits.ui.api import View, Item, Group

class FviewPostTrigger(traited_plugin.HasTraits_FViewPlugin):
    plugin_name = 'post trigger'

    n_frames_pre = traits.Int(300)
    n_frames_post = traits.Int(300)

    traits_view = View(
        Group(
        Item('n_frames_pre'),
        Item('n_frames_post'),
        ))

    def camera_starting_notification(self,cam_id,
                                     pixel_format=None,
                                     max_width=None,
                                     max_height=None):
        pass

    def process_frame(self,cam_id,buf,buf_offset,timestamp,framenumber):
        draw_points = []
        draw_linesegs = []

        return draw_points, draw_linesegs
