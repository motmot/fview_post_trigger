import warnings, time
import enthought.traits.api as traits
import motmot.fview.traited_plugin as traited_plugin
import numpy as np
from enthought.traits.ui.api import View, Item, Group, ButtonEditor
import socket
import threading
import motmot.FlyMovieFormat.FlyMovieFormat as FMF

class Listener(object):
    def __init__(self,target):
        self.target = target
        self.recvsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        my_host = '' # get fully qualified hostname
        my_port = 30041 # arbitrary number
        self.recvsock.bind(( my_host, my_port))
        self.listen_thread = threading.Thread(target=self.run)
        self.listen_thread.setDaemon(True)
        self.listen_thread.start()
    def run(self):
        while 1:
            msg,host = self.recvsock.recvfrom(4096)
            assert msg == 'x'
            self.target.trigger.set()

class Saver(object):
    def __init__(self,backlog,format):
        self.backlog = backlog
        self.format = format
        self.quit_when_done = threading.Event()
        self.thread = threading.Thread(target=self.run)
        self.thread.start()
    def run(self):
        filename = time.strftime( 'movie%Y%m%d_%H%M%S.fmf' )
        depth = FMF.format2bpp_func(self.format)
        fmf_saver = FMF.FlyMovieSaver(filename,version=3,
                                      format=self.format,
                                      bits_per_pixel=depth,
                                      )
        while 1:
            try:
                frame,timestamp = self.backlog.pop(0)
            except IndexError:
                # no frame available
                if self.quit_when_done.isSet():
                    break
                else:
                    time.sleep(0.05) # wait 50 msec
                    continue # try again
            fmf_saver.add_frame(frame,timestamp)
    def close(self):
        self.quit_when_done.set()
    def append(self,x):
        self.backlog.append(x)

class FviewPostTrigger(traited_plugin.HasTraits_FViewPlugin):
    plugin_name = 'post trigger'

    n_frames_pre = traits.Int(300)
    n_frames_post = traits.Int(300)
    n_buffered_frames = traits.Int(0)
    n_unbuffered_saved_frames = traits.Int(0)

    trigger = traits.Any()
    fire_trigger = traits.Button()
    listener = traits.Instance(Listener,transient=True)
    frames = traits.Any()
    fmf_saver = traits.Any()

    traits_view = View(
        Group(
        Item('n_frames_pre'),
        Item('n_frames_post'),
        Item('n_buffered_frames',style='readonly'),
        Item('fire_trigger'),
        ))

    def __init__(self,*args,**kwargs):
        self.trigger = threading.Event()
        super(FviewPostTrigger,self).__init__(*args,**kwargs)
        # handle trigger from network
        self.listener = Listener(self)
        self.frames = []

    def _fire_trigger_fired(self):
        # handle trigger from GUI
        self.trigger.set()
        self.trig_now = True

    def camera_starting_notification(self,cam_id,
                                     pixel_format=None,
                                     max_width=None,
                                     max_height=None):
        self.im_format = pixel_format

    def process_frame(self,cam_id,buf,buf_offset,timestamp,framenumber):
        draw_points = []
        draw_linesegs = []

        if self.trigger.isSet():
            print 'firing'
            self.trigger.clear()
            if self.fmf_saver is None:
                self.fmf_saver = Saver(self.frames,self.im_format)
                self.frames = []
                self.n_unbuffered_saved_frames = 0
            else:
                print 'still saving current movie -- not saving new one'

        if self.fmf_saver is not None:
            # save this frame
            self.fmf_saver.append((np.array(buf,copy=True),timestamp))
            self.n_unbuffered_saved_frames += 1
            if self.n_unbuffered_saved_frames >= self. n_frames_post:
                # end recording
                self.fmf_saver.close()
                self.fmf_saver = None
        else:
            # buffer this frame
            self.frames.append( (np.array(buf,copy=True),timestamp) )
            if len(self.frames) >= self.n_frames_pre:
                del self.frames[:-self.n_frames_pre]

        self.n_buffered_frames = len(self.frames)

        return draw_points, draw_linesegs
