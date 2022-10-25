""" This script is for base module for camera handlers.

Copyright (c) 2022 AItoAir
"""
import cv2
import time
from abc import ABC, abstractmethod

class BaseFrameHandler(ABC):
    def __init__(self, img_ext='.jpg') -> None:
        super().__init__()
        self._stack_frame = False
        self.img_ext = img_ext

    def create_video_writer(self, video_name, fps):
        self.video_name = video_name
        return cv2.VideoWriter(video_name,
                               cv2.VideoWriter_fourcc(*'mp4v'),
                               int(fps),
                               (self._width, self._height))

    def start_recording(self, video_name, fps):
        self.writer = self.create_video_writer(video_name, fps=fps)
        self._stack_frame = True

    def stop_recording(self):
        if hasattr(self, 'writer'):
            self._stack_frame = False
            time.sleep(0.5) # wait for last frame to be written
            self.writer.release()
            del self.writer
            print(f'{self.video_name} saved')

    @abstractmethod
    def get_frame_as_arr(self):
        raise NotImplementedError("get_frame_as_arr() is not implemented")

    @abstractmethod
    def __del__(self):
        raise NotImplementedError("__del__() is not implemented")

    def resize_frame(self, frame, resize_height):
        height = frame.shape[0]
        resize_ratio = resize_height / height
        return cv2.resize(
            frame,
            None,
            fx=resize_ratio,
            fy=resize_ratio,
            interpolation=cv2.INTER_AREA
        )
