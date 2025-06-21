#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2024 The DSM Authors, All rights reserved.
# Licensed under the Apache License Version 2.0 that can be found in the
# LICENSE file in the root directory of this source tree

import os

from dsm.core.utils.log import Log


class Env:
    env_map = {}

    @staticmethod
    def get_env(key):
        if key == "root_path" and key not in Env.env_map.keys():
            Log.fatal(
                "You have not initialized the DSM environment yet. "
                "You can initialize the workspace using dsm init {path}"
            )
        return Env.env_map[key]

    @staticmethod
    def set_env(key, value):
        Env.env_map[key] = value


def init_env():
    current_dir = os.getcwd()
    file_name = ".dsm"
    result = None
    while True:
        files = os.listdir(current_dir)
        if file_name in files:
            result = current_dir
            break
        parent_dir = os.path.dirname(current_dir)
        if current_dir == parent_dir:
            Log.warning(
                "You have not initialized the DSM environment yet. "
                "You can initialize the workspace using dsm init {path}"
            )
            break
        current_dir = parent_dir
    Env.set_env("root_path", result)
