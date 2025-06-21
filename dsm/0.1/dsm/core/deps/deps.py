#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2024 The DSM Authors, All rights reserved.
# Licensed under the Apache License Version 2.0 that can be found in the
# LICENSE file in the root directory of this source tree

import os

from dsm.core.env.env import Env
from dsm.core.utils.log import Log


class Deps:
    def __init__(self, path, target):
        deps_file_name = "DEPS"
        if target is not None:
            deps_file_name = f"{deps_file_name}.{target}"
        deps_file_path = os.path.join(Env.get_env("root_path"), path, deps_file_name)
        with open(deps_file_path, "r") as deps_file:
            local_env = {}
            exec(deps_file.read(), local_env)
        self.deps_meta_data = local_env["deps"]

    def get_target(self, target_name):
        if target_name not in self.deps_meta_data:
            Log.fatal(f"{target_name} not found!")
        return self.deps_meta_data[target_name]
