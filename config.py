from pydantic import BaseSettings

class TBMSetting(BaseSettings):
    tbm_path: str = "obj_detector_clip_detection.tbm"
    dll_directory: str = "Ubuntu2204_x86_64_tinyboom_dll"

class FrameSetting(BaseSettings):
    height: int = 480

tbm_setting = TBMSetting()
frame_setting = FrameSetting()
