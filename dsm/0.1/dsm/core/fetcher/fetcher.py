#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2024 The DSM Authors, All rights reserved.
# Licensed under the Apache License Version 2.0 that can be found in the
# LICENSE file in the root directory of this source tree

import random
import string
import os
import subprocess
import shutil
import requests
import hashlib
from dsm.core.env.env import Env
from dsm.core.utils.log import Log


class Fetcher:
    def __init__(self):
        self.root_path = Env.get_env("root_path")
        self.tmp_path = os.path.join(
            self.root_path,
            "TMP_"
            + "".join(random.choices(string.ascii_letters + string.digits, k=10)),
        )

    def fetch(self, meta_data, target):
        pass

    def move(self, target):
        target = os.path.join(self.root_path, target)
        parent_path = os.path.dirname(target)
        if os.path.exists(target):
            shutil.rmtree(target)
        if not os.path.exists(parent_path):
            os.makedirs(parent_path)
        subprocess.check_call(f"mv -f {self.tmp_path} {target}", shell=True)


class GitFetcher(Fetcher):
    def __init__(self):
        super().__init__()

    def fetch(self, meta_data, target):
        repo = meta_data["repo"]
        commit = meta_data["commit"]
        Log.info(f"sync code from {repo}:{commit} to {target}")
        os.makedirs(self.tmp_path)
        os.chdir(self.tmp_path)
        subprocess.check_call("git init", shell=True)
        subprocess.check_call(f"git remote add origin {repo}", shell=True)
        subprocess.check_call(f"git fetch origin {commit}", shell=True)
        subprocess.check_call(f"git checkout {commit}", shell=True)
        os.chdir(self.root_path)
        self.move(target)


class PackageFetcher(Fetcher):
    def __init__(self):
        super().__init__()

    def calculate_file_sha256(self, file_path):
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as file:
            for chunk in iter(lambda: file.read(4096), b""):
                sha256_hash.update(chunk)
        sha256_result = sha256_hash.hexdigest()
        return sha256_result

    def fetch(self, meta_data, target):
        url = meta_data["url"]
        name = meta_data["name"]
        decompress = meta_data["decompress"]
        os.makedirs(self.tmp_path)
        os.chdir(self.tmp_path)
        Log.info(f"fetching package from {url} to {name}")
        response = requests.get(url)
        with open(name, "wb") as file:
            file.write(response.content)

        sha256_result = self.calculate_file_sha256(name)
        with open("SHA256", "w") as f:
            f.write(sha256_result)
        if decompress:
            subprocess.check_call(f"tar -zxf {name}", shell=True)
            subprocess.check_call(f"rm -rf {name}", shell=True)
        os.chdir(self.root_path)
        self.move(target)


class ActionFetcher(Fetcher):
    def __init__(self):
        super().__init__()

    def fetch(self, meta_data, target):
        Log.info(f"Run action {target}")
        work_path = os.path.join(self.root_path, target)
        if not os.path.exists(work_path):
            os.makedirs(work_path)
        actions = meta_data["actions"]
        command_file = os.path.join(work_path, f"DSM_{target}.command")
        with open(command_file, "w") as f:
            f.writelines("\n".join(actions))
        subprocess.check_call(f"bash {command_file}", shell=True, cwd=work_path)
        os.remove(command_file)


class FetcherFactory:
    @staticmethod
    def generate(fetch_type):
        if fetch_type == "git":
            return GitFetcher()
        elif fetch_type == "package":
            return PackageFetcher()
        elif fetch_type == "action":
            return ActionFetcher()
        else:
            return Fetcher()
