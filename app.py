#!/usr/bin/env python
# encoding: utf-8
"""
@author: Shanda Lau 刘祥德
@license: (C) Copyright 2019-now, Node Supply Chain Manager Corporation Limited.
@contact: shandalaulv@gmail.com
@software: 
@file: app.py
@time: 11/22/19 11:11 AM
@version 1.0
@desc:
"""

import argparse
import warnings

from classfy.model import DolphinClassifier
from interface import *
# from multiprocessing import Process
from utils import sec2time
# from apscheduler.schedulers.background import BackgroundScheduler
from utils.scheduler import ClosableBlockingScheduler

warnings.filterwarnings("ignore")


# from apscheduler.schedulers.blocking import BlockingScheduler
# from apscheduler.schedulers import blocking


# from torch.multiprocessing import Pool, Process, set_start_method


class DolphinDetectionServer:

    def __init__(self, cfg: ServerConfig, vcfgs: List[VideoConfig], switcher_options, cd_id, dt_id) -> None:
        self.cfg = cfg
        self.cfg.cd_id = cd_id
        self.cfg.dt_id = dt_id
        self.vcfgs = [c for c in vcfgs if switcher_options[str(c.index)]]
        if not len(self.vcfgs):
            raise Exception('Empty video stream configuration enabling.')
        # self.classifier = DolphinClassifier(model_path=self.cfg.classify_model_path, device_id=cd_id)
        self.classifier = None
        self.ssd_detector = None
        self.dt_id = dt_id
        # self.scheduler = BackgroundScheduler()
        # self.scheduler = BlockingScheduler()
        if self.cfg.detect_mode == ModelType.CLASSIFY:
            self.classifier = DolphinClassifier(model_path=self.cfg.classify_model_path, device_id=cd_id)
        # if self.cfg.detect_mode == ModelType.SSD:
        # self.ssd_detector = SSDDetector(model_path=self.cfg.detect_model_path, device_id=dt_id)
        self.monitor = detection.EmbeddingControlBasedTaskMonitor(self.vcfgs, self.cfg,
                                                                  self.cfg.stream_save_path,
                                                                  self.cfg.sample_save_dir, self.cfg.frame_save_dir,
                                                                  self.cfg.candidate_save_dir,
                                                                  self.cfg.offline_stream_save_dir)
        self.scheduler = ClosableBlockingScheduler(stop_event=self.monitor.shut_down_event)
        # self.http_server = HttpServer(self.cfg.http_ip, self.cfg.http_port, self.cfg.env, self.cfg.candidate_save_dir)
        if not self.cfg.run_direct:
            self.scheduler.add_job(self.monitor.monitor, 'cron',
                                   month=self.cfg.cron['start']['month'],
                                   day=self.cfg.cron['start']['day'],
                                   hour=self.cfg.cron['start']['hour'],
                                   minute=self.cfg.cron['start']['minute'])

    def run(self):
        """
        System Entry
        """
        # ray.init()
        start_time = time.time()
        start_time_str = time.strftime('%Y-%m-%d-%H:%M:%S', time.localtime(start_time))
        logger.info(
            f'*******************************Dolphin Detection System: Running Environment [{self.cfg.env}] at '
            f'[{start_time_str}]********************************')
        # self.http_server.run()
        if self.cfg.run_direct:
            self.monitor.monitor()
        else:
            self.scheduler.start()
        end_time = time.time()
        end_time_str = time.strftime('%Y-%m-%d-%H:%M:%S', time.localtime(end_time))
        run_time = sec2time(end_time - start_time)
        logger.info(
            f'*******************************Dolphin Detection System: Shut down at [{end_time_str}].'
            f'Total Running Time '
            f'[{run_time}]********************************')


def load_cfg(args):
    if args.env is not None:
        if args.env == Environment.DEV:
            args.cfg = 'vcfg/server-dev.json'
            args.vcfg = 'vcfg/video-dev.json'
        if args.env == Environment.TEST:
            args.cfg = 'vcfg/server-test.json'
            args.vcfg = 'vcfg/video-test.json'
        if args.env == Environment.PROD:
            args.cfg = 'vcfg/server-prod.json'
            args.vcfg = 'vcfg/video-prod.json'
    server_config = load_server_config(args.cfg)
    video_config = load_video_config(args.vcfg)
    switcher_options = load_json_config(args.sw)
    if args.http_ip is not None:
        server_config.http_ip = args.http_ip
    if args.http_port is not None:
        server_config.http_port = args.http_port
    if args.wc_ip is not None:
        server_config.wc_ip = args.wc_ip
    if args.wc_port is not None:
        server_config.http_port = args.wc_port
    if args.root is not None:
        server_config.set_root(args.root)
    if args.cdp is not None:
        server_config.set_candidate_save_dir(args.cdp)
    if args.run_direct is not None:
        server_config.run_direct = args.run_direct
    if args.send_msg is not None:
        server_config.send_msg = args.send_msg
    if args.enable is not None:
        enables = args.enable.split(",")
        for e in enables:
            switcher_options[e] = True
    if args.disable is not None:
        disables = args.disable.split(",")
        for e in disables:
            switcher_options[e] = False

    if args.use_sm is not None:
        enables = args.use_sm.split(",")
        enables = [int(e) for e in enables]
        for cfg in video_config:
            if cfg.index in enables:
                cfg.use_sm = True

    if args.push_stream is not None:
        enables = args.push_stream.split(",")
        enables = [int(e) for e in enables]
        for cfg in video_config:
            if cfg.index in enables:
                cfg.push_stream = True

    return server_config, video_config, switcher_options


if __name__ == '__main__':
    # if MONITOR == MonitorType.RAY_BASED:
    #     # ray.init(object_store_memory=8 * 1024 * 1024)

    #     ray.init()
    #     try:
    #         monitor = detection.EmbeddingControlBasedRayMonitor.remote(VIDEO_CONFIG_DIR / 'video.json',
    #                                                                    STREAM_SAVE_DIR, SAMPLE_SAVE_DIR,
    #                                                                    FRAME_SAVE_DIR,
    #                                                                    CANDIDATE_SAVE_DIR, OFFLINE_STREAM_SAVE_DIR)
    #         m_id = monitor.monitor.remote()
    #         ray.get(m_id)
    #         print(ray.errors(all_jobs=True))
    #     except Exception as e:
    #         print(e)
    # if MONITOR == MonitorType.PROCESS_THREAD_BASED:
    #     monitor = detection.EmbeddingControlBasedThreadAndProcessMonitor(VIDEO_CONFIG_DIR / 'video.json',
    #                                                                      STREAM_SAVE_DIR, SAMPLE_SAVE_DIR,
    #                                                                      FRAME_SAVE_DIR,
    #                                                                      CANDIDATE_SAVE_DIR, OFFLINE_STREAM_SAVE_DIR)
    #     monitor.monitor()
    #
    # elif MONITOR == MonitorType.PROCESS_BASED:
    #     monitor = detection.EmbeddingControlBasedProcessMonitor(VIDEO_CONFIG_DIR / 'video.json', STREAM_SAVE_DIR,
    #                                                             SAMPLE_SAVE_DIR,
    #                                                             FRAME_SAVE_DIR,
    #                                                             CANDIDATE_SAVE_DIR, OFFLINE_STREAM_SAVE_DIR)
    #
    #     monitor.monitor()
    # elif MONITOR == MonitorType.TASK_BASED:
    #     monitor = detection.EmbeddingControlBasedTaskMonitor(VIDEO_CONFIG_DIR / 'video.json', STREAM_SAVE_DIR,
    #                                                          SAMPLE_SAVE_DIR,
    #                                                          FRAME_SAVE_DIR,
    #                                                          CANDIDATE_SAVE_DIR, OFFLINE_STREAM_SAVE_DIR)
    #     monitor.monitor()
    #
    # else:
    #     monitor = detection.EmbeddingControlBasedThreadMonitor(VIDEO_CONFIG_DIR / 'video.json', STREAM_SAVE_DIR,
    #                                                            SAMPLE_SAVE_DIR,
    #                                                            FRAME_SAVE_DIR,
    #                                                            CANDIDATE_SAVE_DIR, OFFLINE_STREAM_SAVE_DIR)
    #     monitor.monitor()
    parser = argparse.ArgumentParser()
    # Basic options
    parser.add_argument('--env', type=str, default='dev',
                        help='System environment.')

    parser.add_argument('--cfg', type=str, default='vcfg/server-dev.json',
                        help='Server configuration file represented by json format.')

    parser.add_argument('--vcfg', type=str, default='vcfg/video-dev.json',
                        help='Video configuration file represented by json format.')

    parser.add_argument('--sw', type=str, default='vcfg/switcher.json',
                        help='Control video switcher')

    parser.add_argument('--http_ip', type=str, help='Http server ip address')
    parser.add_argument('--http_port', type=int, help='Http server listen port')
    parser.add_argument('--wc_ip', type=str, help='Websocket server ip address')
    parser.add_argument('--wc_port', type=int, help='Websocket server listen port')
    parser.add_argument('--root', type=str,
                        help='Redirect data root path,default path is [PROJECT DIR/data/...].' +
                             'PROJECT DIR is depend on which project is deployed.' +
                             'If root param is set,data path is redirected as [root/data/...]')
    parser.add_argument('--cdp', type=str,
                        help='Dolphin video stream storage relative path.default path is [$PROJECT DIR$/data/candidate].' +
                             'If cdp param is set,stream storage path is redirected as [$root$/$cdp$] ' +
                             'or [$PROJECT DIR$]/$cdp$.')
    parser.add_argument('--cd_id', type=int, default=1, help='classifier GPU device id')
    parser.add_argument('--dt_id', type=int, default=2, help='detection GPU device id')
    parser.add_argument('--run_direct', action='store_true', default=False, help='timing start or run directly.')
    parser.add_argument('--enable', type=str, default="5", help='Enable video index')
    parser.add_argument('--disable', type=str, default=None, help='Disable video index')
    parser.add_argument('--send_msg', action='store_true', default=False, help='timing start or run directly.')
    parser.add_argument('--use_sm', default=None, help='use share memory to cache frames')
    parser.add_argument('--push_stream', default=None, help='use share memory to cache frames')
    args = parser.parse_args()
    server_config, video_config, switcher_options = load_cfg(args)
    server = DolphinDetectionServer(server_config, video_config, switcher_options, args.cd_id, args.dt_id)
    server.run()

# process = Process(target=monitor.monitor)
# process.start()
# process.join()
