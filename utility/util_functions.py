""" This script has util functions to run tbm application.

author Jeong Doowon
date Oct/22/2022
Copyright (c) 2022 AItoAir. All rights reserved.
"""
import stat
import time
import os
import shutil
import socket
import subprocess
import base64
import json
import cv2

TIMEOUT_VALUE = 100 # seconds
FPS_CHECK_INTERVAL = 5

def tbm_input_msg(data):
    msg = {'data': data}
    return json.dumps(msg).encode('utf-8')

def get_tbm_input_data_from_img_path(data_path: str):
    with open(data_path, 'rb') as f:
        data = base64.b64encode(f.read())
    f.close()
    data_b64_str = data.decode('utf-8') # base64 as string
    return tbm_input_msg(data_b64_str)

def load_tbm(tbm_path, dll_path, tmp_dir='tmp_workdir') -> socket.socket:
    if not os.access(tbm_path, os.X_OK):
        # make it executable
        st = os.stat(tbm_path)
        os.chmod(tbm_path, st.st_mode | stat.S_IEXEC)
        if not os.access(tbm_path, os.X_OK):
            raise Exception('Cannot make tbm executable')

    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir)
    os.makedirs(tmp_dir)
    socket_path = os.path.join(tmp_dir, 'runner.socket')
    env = dict(os.environ)
    if dll_path is not None:
        env['LD_LIBRARY_PATH'] = dll_path
    cmd = [tbm_path, '--socket_path', socket_path]
    runner = subprocess.Popen(
        cmd,
        stdout=subprocess.DEVNULL,
        env=env
    )

    while not os.path.exists(socket_path) or not runner.poll() is None:
        time.sleep(0.1)

    if not runner.poll() is None:
        raise Exception('Failed to start runner (' + str(runner.poll()) + ')')

    client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    client.connect(socket_path)
    print("Connected to TBM socket")
    return client

def inference_thru_socket(client:socket.socket, tbm_input):
    client.send(tbm_input)
    client.settimeout(TIMEOUT_VALUE)
    ret = client.recv(1 * 1024 * 1024).decode('utf-8').rstrip('\x00')
    client.settimeout(None)
    return ret

def get_inference_from_tbm(client, tbm_path, dll_path, tbm_input):
    try:
        ret = inference_thru_socket(client, tbm_input)
    except socket.timeout:
        print('Re-open socket')
        # remove hanging client and re-open it
        client.close()
        client = load_tbm(tbm_path, dll_path)
        ret = inference_thru_socket(client, tbm_input)
    detect_json = []
    if ret:
        detect_json = json.loads(ret)
    return detect_json

def draw_detection_in_frame(frame_arr, det_result_json):
    color = (255, 0, 0)
    for det in det_result_json:
        bbox = det['bbox']
        # float to int
        bbox = [int(x) for x in bbox]
        cls_name = det['class']
        conf = det['score']
        letter = f"{cls_name} {conf:.2f}"
        cv2.rectangle(frame_arr, (bbox[0], bbox[1]), (bbox[2], bbox[3]), color, 1)
        cv2.putText(frame_arr, letter, (bbox[0], bbox[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
    return frame_arr

if __name__ == '__main__':
    # test
    tbm_path = "../obj_detector_x86_64.tbm"
    dll_path = "/home/Ubuntu2204_x86_64_tinyboom_dll"
    client = load_tbm(tbm_path, dll_path)
    img_path = '/home/UnknownDevice-20221020131928.jpg'
    frame_count = 0
    last_logged = time.time()
    tbm_input = get_tbm_input_data_from_img_path(img_path)
    while True:
        detect_json = get_inference_from_tbm(client, tbm_path, dll_path, tbm_input)
        # print(detect_json)
        # for d in detect_json:
        #     print(d["class_id"], d["class"])
        now = time.time()
        print("here")
        frame_count += 1
        if now - last_logged > FPS_CHECK_INTERVAL:
            fps = frame_count / (now - last_logged)
            print(f'{fps} fps')
            last_logged = now
            frame_count = 0
    client.close()
