'''
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
'''

sudo apt-get install libgl1-mesa-dev