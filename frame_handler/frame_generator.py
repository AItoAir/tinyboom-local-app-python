""" This script is to create frame from webcam.

Copyright (c) 2022 AItoAir
"""
import sys
import cv2
import os

from frame_handler.base_frame_handler import BaseFrameHandler

def is_linux():
    return sys.platform.startswith('linux')
def is_windows():
    return sys.platform.startswith('win')

class FrameGenerator(BaseFrameHandler):
    def __init__(self, frame_source):
        super().__init__()
        if isinstance(frame_source, int):
            # load from webcam
            args = ()
            if is_windows():
                args = (cv2.CAP_DSHOW,)
            self.video = cv2.VideoCapture(frame_source, *args)
        else:
            assert os.path.exists(frame_source), "Video file does not exist."
            # load from video file
            self.video = cv2.VideoCapture(frame_source)

    @property
    def _width(self):
        return int(self.video.get(cv2.CAP_PROP_FRAME_WIDTH))

    @property
    def _height(self):
        return int(self.video.get(cv2.CAP_PROP_FRAME_HEIGHT))

    def __del__(self):
        self.video.release()

    def get_frame_as_arr(self):
        success, image = self.video.read()
        return image
