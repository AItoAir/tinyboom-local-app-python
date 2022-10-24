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
from utility.tbm_communicator import TBMCommunicator
from utility.util_functions import draw_detection_in_frame

app = FastAPI()
app.mount("/templates", StaticFiles(directory="templates"), name="templates")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
   return templates.TemplateResponse('index.html', {"request": request})

def gen(camera):
    """Video streaming generator function."""
    if not NO_INFERENCE_MODE:
        tbm_communicator = TBMCommunicator(tbm_setting.tbm_path, tbm_setting.dll_directory)
        tbm_socket_client = tbm_communicator.get_socket_client()
    else:
        print("NO_INFERENCE_MODE is True. No inference will be done.")

    while True:
        frame_arr = camera.get_frame_as_arr()
        if not NO_INFERENCE_MODE:
            retval, buffer = cv2.imencode('.jpg', frame_arr)
            # cv2.imwrite("frame.jpg", frame_arr)
            # frame arr to base64 encode
            frame_as_base64 = base64.b64encode(buffer)
            frame_as_base64_str = frame_as_base64.decode('utf-8') # base64 as string

            tbm_input = \
                tbm_communicator.get_tbm_socket_input_msg(frame_as_base64_str)
            raw_det_result = \
                tbm_communicator.get_streaming_inference_thru_tbm(tbm_socket_client, tbm_input)

            frame_to_display = draw_detection_in_frame(frame_arr, raw_det_result)
        else:
            frame_to_display = frame_arr
        frame_to_display = camera.resize_frame(frame_to_display, frame_setting.height)
        _, jpeg = cv2.imencode(camera.img_ext, frame_to_display)
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
                        default="pexels-tima-miroshnichenko-6536354.mp4",
                        help="It inputs video not web camera.",
                        type=str)
    parser.add_argument("--no_inference", "-n",
                        action="store_true",
                        default=False,
                        help="No inference mode. "
                             "It only display frame data without loading TBM models.")
    args = parser.parse_args()
    frame_source = args.camera_idx if args.camera_idx is not None else args.video_path
    # either parameter has to be set.
    assert frame_source is not None, "Either camera index or video path has to be set."
    FRAME_STREAMER = FrameGenerator(frame_source)
    NO_INFERENCE_MODE = args.no_inference

    uvicorn.run(app, host="0.0.0.0", port=1338)
