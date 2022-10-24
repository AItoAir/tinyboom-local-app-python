""" This script has util functions to run tbm application.

author Jeong Doowon
date Oct/22/2022
Copyright (c) 2022 AItoAir. All rights reserved.
"""
import cv2
import json

def draw_detection_in_frame(frame_arr, raw_det_result):
    color = (255, 0, 0)
    if raw_det_result:
        det_result_json = json.loads(raw_det_result)
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
