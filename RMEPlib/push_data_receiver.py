#!/usr/bin/env python3
# coding=utf-8

import socket
import time
import threading
import queue
from . import logger


class PushDataReceiver(object):
    def __init__(self, robot, port=40924):
        self.robot = robot
        self.ip = robot.ip
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.log = logger.Logger(self)
        self.running = False

    def __del__(self):
        self.log.info("Shuting down PushDataReceiver ...")
        if self.running:
            self.running = False
            self.thread.join()
            self.log.info(
                'Shutted down PushDataReceiver thread successfully.')
            self.socket.close()
        else:
            self.log.info(
                'PushDataReceiver thread has not been started. Skip ...')

    def bind(self, retry=3):
        self.log.info("Binding to %s:%s ..." % (self.ip, self.port))

        try:
            self.socket.bind((self.ip, self.port))
            self.log.info("Push port bound.")
        except socket.error as e:
            self.log.warn("Fail to bind Push port. Error: %s" % e)
            if retry > 0:
                time.sleep(self.retry_interval)
                self.log.warn("Retrying...")
                self.connect(retry-1)
            else:
                self.log.error("Failed to retry")
                self.bind(3)

    def start(self):
        self.bind()
        self.running = True
        self.thread = threading.Thread(target=self.update)
        self.thread.start()
        self.log.info('PushDataReceiver thread started.')

    def update(self):
        self.socket.settimeout(1)
        while self.running:
            try:
                recv = self.socket.recv(4096).decode('utf-8')
                self.robot.push_buffer.appendleft()
            except socket.timeout:
                continue
            except socket.error as e:
                self.log.warn("Error at decoding: %s" % e)


if __name__ == "__main__":
    test = PushDataReceiver('127.0.0.1')
    test.start()
    import time
    time.sleep(3)
