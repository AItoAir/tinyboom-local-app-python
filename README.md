# Tinyboom local app python.

## Setup and Launch Guide
Please follow the steps below to setup and launch the app. This local app is built using python and fastapi.
Step 1. Install necessary packages using `requirements.txt`
```
pip insatll -r requirements.txt
```
Step 2. Configure TBM and its DLL path in config.py.  **The path should be absolute path in your local machine.**
```
class TBMSetting(BaseSettings):
    tbm_path: str = "/home/obj_detector_clip_x86_64.tbm"
    dll_directory: str = "/home/Ubuntu2204_x86_64_tinyboom_dll"
```
Step 3. Launch the app with below options. Either option has to be specified.
- Launch with webcamera with index 0
```
python main.py --camera_idx 0
```
- Launch with video file
```
python main.py --video_path {video_file_path}
```

<br>

## Possible issues
This application requires to have opencv. If you see the error below, please install `libgl1-mesa-dev` with the command. `sudo apt-get install libgl1-mesa-dev`
```
jeong@ubuntu:~/tinyboom-local-app-python$ python3 main.py
Traceback (most recent call last):
  File "/home/jeong/tinyboom-local-app-python/main.py", line 10, in <module>
    import cv2
  File "/home/jeong/.local/lib/python3.10/site-packages/cv2/__init__.py", line 181, in <module>
    bootstrap()
  File "/home/jeong/.local/lib/python3.10/site-packages/cv2/__init__.py", line 153, in bootstrap
    native_module = importlib.import_module("cv2")
  File "/usr/lib/python3.10/importlib/__init__.py", line 126, in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
ImportError: libGL.so.1: cannot open shared object file: No such file or directory
```

## LICENSE
This project is licensed under the terms of the Apache License 2.0. Please see the LICENSE file for details.<br>
Licenses of third-party library clarified as below.
- [FastAPI](https://github.com/tiangolo/fastapi/blob/master/LICENSE) : MIT
- [OpenCV](https://github.com/opencv/opencv/blob/master/LICENSE) : Apache 2.0

We appreciate the authors of the third-party libraries.
