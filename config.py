from pydantic import BaseSettings

class TBMSetting(BaseSettings):
    tbm_path: str = "/home/obj_detector_clip_x86_64.tbm"
    dll_directory: str = "/home/Ubuntu2204_x86_64_tinyboom_dll"

class FrameSetting(BaseSettings):
    height: int = 480

tbm_setting = TBMSetting()
frame_setting = FrameSetting()
