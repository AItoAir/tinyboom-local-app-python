""" This script is to run fastapi server using Tinyboom models.

author Jeong Doowon
date Jul/28/2022
Copyright (c) 2022 AItoAir. All rights reserved.
"""
import argparse
import uvicorn
import cv2
import base64

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from config import tbm_setting, frame_setting
from frame_handler.frame_generator import FrameGenerator
from utility.util_functions import draw_detection_in_frame, \
                                   get_inference_from_tbm, \
                                   load_tbm, tbm_input_msg

app = FastAPI()
app.mount("/templates", StaticFiles(directory="templates"), name="templates")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
   return templates.TemplateResponse('index.html', {"request": request})

socket_client = load_tbm(tbm_setting.tbm_path, tbm_setting.dll_directory)
def gen(camera):
    """Video streaming generator function."""
    while True:
        frame_arr = camera.get_frame_as_arr()
        retval, buffer = cv2.imencode('.jpg', frame_arr)
        # cv2.imwrite("frame.jpg", frame_arr)
        # frame arr to base64 encode
        frame_as_base64 = base64.b64encode(buffer)
        frame_as_base64_str = frame_as_base64.decode('utf-8') # base64 as string
        tbm_input = tbm_input_msg(frame_as_base64_str)
        det_result = get_inference_from_tbm(
            socket_client,
            tbm_setting.tbm_path,
            tbm_setting.dll_directory,
            tbm_input
        )
        frame_arr = draw_detection_in_frame(frame_arr, det_result)
        frame_arr = camera.resize_frame(frame_arr, frame_setting.height)
        _, jpeg = cv2.imencode(camera.img_ext, frame_arr)
        frame_byte = jpeg.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_byte + b'\r\n')

@app.get('/video_feed', response_class=HTMLResponse)
async def video_feed():
    return StreamingResponse(
        gen(FRAME_STREAMER),
        media_type='multipart/x-mixed-replace; boundary=frame'
    )

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--camera_idx", "-c",
                        # default=0,
                        help="Camera index in your system",
                        type=int)
    parser.add_argument("--video_path", "-v",
                        default="20221021_A_10_11_12.mp4",
                        help="Video path to run",
                        type=str)
    args = parser.parse_args()
    frame_source = args.camera_idx if args.camera_idx is not None else args.video_path
    FRAME_STREAMER = FrameGenerator(frame_source)

    uvicorn.run(app, host="0.0.0.0", port=1338)
