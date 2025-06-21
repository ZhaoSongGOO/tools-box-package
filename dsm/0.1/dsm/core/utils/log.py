#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright 2024 The DSM Authors, All rights reserved.
# Licensed under the Apache License Version 2.0 that can be found in the
# LICENSE file in the root directory of this source tree
import datetime
import sys


def get_format_time_str():
    current_time = datetime.datetime.now()
    formatted_time = current_time.strftime("%Y/%m/%d %H:%M:%S")
    return formatted_time


class BaseLog:
    def info(self, msg):
        pass

    def success(self, msg):
        pass

    def error(self, msg):
        pass

    def fatal(self, msg):
        pass

    def warning(self, msg):
        pass


class Log:
    green_color_code = "\033[92m"
    red_color_code = "\033[91m"
    yellow_color_code = "\033[93m"
    blue_color_code = "\033[94m"
    reset_color_code = "\033[0m"

    @staticmethod
    def print(msg):
        print(msg, flush=True)

    @staticmethod
    def info(msg):
        print_msg = f"[DSM][INFO] {msg}"
        print(
            f"{Log.blue_color_code}[{get_format_time_str()}]{print_msg}{Log.reset_color_code}",
            flush=True,
        )

    @staticmethod
    def success(msg):
        print_msg = f"[DSM][SUCCESS] {msg}"
        print(
            f"{Log.green_color_code}[{get_format_time_str()}]{print_msg}{Log.reset_color_code}",
            flush=True,
        )

    @staticmethod
    def error(msg):
        print_msg = f"[DSM][ERROR] {msg}"
        print(
            f"{Log.red_color_code}[{get_format_time_str()}]{print_msg}{Log.reset_color_code}",
            flush=True,
        )

    @staticmethod
    def fatal(msg):
        print_msg = f"[DSM][FATAL] {msg}"
        print(
            f"{Log.red_color_code}[{get_format_time_str()}]{print_msg}{Log.reset_color_code}",
            flush=True,
        )
        sys.exit(1)

    @staticmethod
    def warning(msg):
        print_msg = f"[DSM][WARNING] {msg}"
        print(
            f"{Log.yellow_color_code}[{get_format_time_str()}]{print_msg}{Log.reset_color_code}",
            flush=True,
        )


class LocalFileLog(BaseLog):
    def __init__(self):
        self.contents = []

    def info(self, msg):
        self.contents.append(msg)
        Log.info(msg)

    def success(self, msg):
        self.contents.append(msg)
        Log.success(msg)

    def error(self, msg):
        self.contents.append(msg)
        Log.error(msg)

    def fatal(self, msg):
        self.contents.append(msg)
        self.save()
        Log.fatal(msg)

    def warning(self, msg):
        self.contents.append(msg)
        Log.warning(msg)

    def save(self):
        with open("rtf_result.log", "w") as f:
            f.write("\n".join(self.contents))
