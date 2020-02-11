#!/usr/bin/env python
# encoding: utf-8
"""
@author: Shanda Lau 刘祥德
@license: (C) Copyright 2019-now, Node Supply Chain Manager Corporation Limited.
@contact: shandalaulv@gmail.com
@software: 
@file: config.py
@time: 2019/11/15 10:43
@version 1.0
@desc:
"""
import json
import logging
import os
import time
from pathlib import Path

import psutil


class Environment(object):
    PROD = 'prod'
    TEST = 'test'
    DEV = 'dev'


LOG_LEVER = logging.DEBUG

PROJECT_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
CANDIDATE_SAVE_DIR = PROJECT_DIR / 'data/candidates'
CANDIDATE_SAVE_DIR.mkdir(exist_ok=True, parents=True)

LOG_DIR = PROJECT_DIR / 'log'
LOG_DIR.mkdir(exist_ok=True, parents=True)

STREAM_SAVE_DIR = PROJECT_DIR / 'data/videos'
STREAM_SAVE_DIR \
    .mkdir(exist_ok=True, parents=True)

SAMPLE_SAVE_DIR = PROJECT_DIR / 'data/samples'
SAMPLE_SAVE_DIR \
    .mkdir(exist_ok=True, parents=True)

OFFLINE_STREAM_SAVE_DIR = PROJECT_DIR / 'data/offline'
OFFLINE_STREAM_SAVE_DIR \
    .mkdir(exist_ok=True, parents=True)

FRAME_SAVE_DIR = PROJECT_DIR / 'data/frames'
FRAME_SAVE_DIR \
    .mkdir(exist_ok=True, parents=True)

VIDEO_CONFIG_DIR = PROJECT_DIR / 'vcfg'
VIDEO_CONFIG_DIR.mkdir(exist_ok=True, parents=True)

LABEL_IMAGE_PATH = PROJECT_DIR / 'data/labels/image'
LABEL_TARGET_PATH = PROJECT_DIR / 'data/labels/target'
LABEL_IMAGE_PATH.mkdir(exist_ok=True, parents=True)
LABEL_TARGET_PATH.mkdir(exist_ok=True, parents=True)
LABEL_SAVE_PATH = PROJECT_DIR / 'data/labels'
BINARY_SAVE_PATH = PROJECT_DIR / 'data/labels/binarys'

INFORM_SAVE_PATH = PROJECT_DIR / 'vcfg'

WEBSOCKET_SERVER_IP = '118.190.136.20'
# WEBSOCKET_SERVER_IP = '192.168.1.7'
WEBSOCKET_SERVER_PORT = 3400

MODEL_PATH = PROJECT_DIR / 'model/bc-model.pth'

from enum import Enum


class MonitorType(Enum):
    PROCESS_BASED = 1,
    THREAD_BASED = 2,
    PROCESS_THREAD_BASED = 3
    RAY_BASED = 4
    TASK_BASED = 5


class Env(Enum):
    DEV = 1,
    TEST = 2,
    DEPLOYMENT = 3,


# select monitor type, process-based means the system will create a process for each component,such as detector,
# stream receiver, frame dispatcher and frame collector...
# Required much resources because system divide resources into process units,
# which are limited by CPU cores
# MONITOR = MonitorType.PROCESS_BASED

ENV = Env.DEV

MONITOR = MonitorType.TASK_BASED

enable_options = {
    0: False,
    1: False,
    2: False,
    3: False,
    4: False,
    5: True,
    6: False
}


#
# enable_options = {
#     0: True,
#     1: True,
#     2: True,
#     3: True,
#     4: True,
#     5: False,
#     6: False,
#     7: False,
#     8: False,
# }

class Config(object):
    """
    Base configuration class, built-in json to object method
    """

    def to_json(self):
        return json.dumps(self.__dict__)

    @classmethod
    def from_json(cls, json_dict):
        # json_dict = json.loads(json_str)
        return cls(**json_dict)


class ServerConfig(Config):
    """
    Server configuration definitions
    """

    def __init__(self, env, http_ip, http_port, wc_ip, wc_port, root, classify_model_path, stream_save_path,
                 sample_save_dir,
                 frame_save_dir,
                 candidate_save_dir, offline_stream_save_dir) -> None:
        self.env = env
        self.http_ip = http_ip
        self.http_port = http_port
        self.wc_ip = wc_ip
        self.wc_port = wc_port
        self.classify_model_path = classify_model_path
        self.stream_save_path = stream_save_path
        self.sample_save_dir = sample_save_dir
        self.frame_save_dir = frame_save_dir
        self.candidate_save_dir = candidate_save_dir
        self.offline_stream_save_dir = offline_stream_save_dir
        self.root = root
        self.convert_to_poxis()

    def set_root(self, root):
        self.root = root
        self.convert_to_poxis()

    def set_candidate_save_dir(self, cdp):
        self.candidate_save_dir = cdp
        self.convert_to_poxis()

    def convert_to_poxis(self, ):
        if self.root == '':
            self.stream_save_path = Path(os.path.join(PROJECT_DIR, self.stream_save_path))
            self.sample_save_dir = Path(os.path.join(PROJECT_DIR, self.sample_save_dir))
            self.frame_save_dir = Path(os.path.join(PROJECT_DIR, self.frame_save_dir))
            self.candidate_save_dir = Path(os.path.join(PROJECT_DIR, self.candidate_save_dir))
            self.classify_model_path = Path(os.path.join(PROJECT_DIR, self.classify_model_path))
            self.offline_stream_save_dir = Path(os.path.join(PROJECT_DIR, self.offline_stream_save_dir))
        else:
            self.stream_save_path = Path(os.path.join(self.root, self.stream_save_path))
            self.sample_save_dir = Path(os.path.join(self.root, self.sample_save_dir))
            self.frame_save_dir = Path(os.path.join(self.root, self.frame_save_dir))
            self.candidate_save_dir = Path(os.path.join(self.root, self.candidate_save_dir))
            self.classify_model_path = Path(os.path.join(self.root, self.classify_model_path))
            self.offline_stream_save_dir = Path(os.path.join(self.root, self.offline_stream_save_dir))


class VideoConfig(Config):
    """
    Video configuration object
    """

    def __init__(self, index, name, shape, ip, port, suffix, headers, m3u8_url, url, roi, resize, show_window,
                 window_position, routine, sample_rate, draw_boundary, enable, filtered_ratio, max_streams_cache,
                 online, sample_internal, detect_internal, search_window_size,similarity_thresh, pre_cache, render, save_box, show_box,
                 rtsp,
                 enable_sample_frame,
                 rtsp_saved_per_frame,
                 future_frames, bbox,
                 alg):
        self.index = index
        self.name = name
        self.shape = shape
        self.ip = ip
        self.port = port
        self.suffix = suffix
        self.headers = headers
        self.m3u8_url = m3u8_url
        self.url = url
        self.roi = roi
        self.resize = resize
        self.show_window = show_window
        self.window_position = window_position
        self.routine = routine
        self.sample_rate = sample_rate
        self.draw_boundary = draw_boundary
        self.enable = enable
        self.filtered_ratio = filtered_ratio
        self.max_streams_cache = max_streams_cache
        self.online = online
        self.sample_internal = sample_internal
        self.save_box = save_box
        self.show_box = show_box
        self.rtsp = rtsp
        self.enable_sample_frame = enable_sample_frame
        self.rtsp_saved_per_frame = rtsp_saved_per_frame
        self.future_frames = future_frames
        self.detect_internal = detect_internal
        self.search_window_size = search_window_size
        self.similarity_thresh = similarity_thresh
        self.pre_cache = pre_cache
        self.render = render
        self.bbox = bbox
        self.alg = alg


class LabelConfig:
    """
    Image label class
    """

    def __init__(self, start, end, center):
        self.start = start
        self.end = end
        self.center = center


# example usage
# User("tbrown", "Tom Brown").to_json()
# User.from_json(User("tbrown", "Tom Brown").to_json()).to_json()
class SystemStatus(Enum):
    RUNNING = 1,
    SHUT_DOWN = 2,
    RESUME = 3


class ObjectClass(Enum):
    DOLPHIN = 0,
    OTHER = 1,


_timer = getattr(time, 'monotonic', time.time)
num_cpus = psutil.cpu_count() or 1


def timer():
    return _timer() * num_cpus


pid_cpuinfo = {}


def cpu_usage():
    id = os.getpid()
    p = psutil.Process(id)
    # while True:
    #     print(p.cpu_percent())
