'''This script has TBMCommunicator.

This module is to use socket communication with TBM.

author Jeong
date Oct/24/2022
Copyright (c) 2022 AItoAir. All rights reserved.
'''
import base64
import json
import os
import shutil
import socket
import stat
import subprocess
import time

TIMEOUT_IN_SOCKET_ACCESS = 10
# timeout seconds in socket streaming communication
TIMEOUT_IN_STREAMING = 5

class TBMCommunicator:
    def __init__(self, tbm_path, dll_dir_path):
        self._tbm_path = tbm_path
        self._dll_dir_path = dll_dir_path

    def get_socket_client(self, tmp_dir='tmp_workdir'):
        if os.path.exists(tmp_dir):
            shutil.rmtree(tmp_dir)
        os.makedirs(tmp_dir)
        socket_path = os.path.join(tmp_dir, 'runner.socket')

        env = dict(os.environ)
        if self._dll_dir_path is not None:
            env['LD_LIBRARY_PATH'] = self._dll_dir_path
        cmd = [self._tbm_path, '--socket_path', socket_path]
        runner = subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            env=env
        )

        time_out_sec = TIMEOUT_IN_SOCKET_ACCESS
        while not os.path.exists(socket_path) or not runner.poll() is None:
            time.sleep(0.1)
            time_out_sec -= 0.1
            if time_out_sec <= 0:
                raise Exception('Timeout in socket access. Check if the socket is opened.')

        if not runner.poll() is None:
            raise Exception('Failed to start runner (' + str(runner.poll()) + ')')

        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        client.connect(socket_path)
        print(f"Connected to {self._tbm_path} TBM socket")
        return client

    @staticmethod
    def make_file_executable(file_path):
        if not os.access(file_path, os.X_OK):
            # make it executable
            st = os.stat(file_path)
            os.chmod(file_path, st.st_mode | stat.S_IEXEC)
            if not os.access(file_path, os.X_OK):
                raise Exception('Cannot make tbm executable')

    @classmethod
    def get_tbm_input_data_from_img_path(cls, data_path: str):
        with open(data_path, 'rb') as f:
            data = base64.b64encode(f.read())
        f.close()
        data_b64_str = data.decode('utf-8') # base64 as string
        return cls.get_tbm_socket_input_msg(data_b64_str)

    @staticmethod
    def get_tbm_socket_input_msg(data):
        msg = {'data': data}
        return json.dumps(msg).encode('utf-8')

    @staticmethod
    def inference_thru_socket(client:socket.socket, tbm_input):
        client.send(tbm_input)
        client.settimeout(TIMEOUT_IN_STREAMING)
        inference_response = client.recv(1 * 1024 * 1024).decode('utf-8').rstrip('\x00')
        client.settimeout(None)
        return inference_response

    def get_streaming_inference_thru_tbm(self,
            client:socket.socket,
            tbm_input
        ):
        try:
            ret = self.inference_thru_socket(client, tbm_input)
        except socket.timeout:
            print('Re-open socket')
            # remove hanging client and re-open it
            client.close()
            client = self.get_socket_client()
            ret = self.inference_thru_socket(client, tbm_input)
        return ret
