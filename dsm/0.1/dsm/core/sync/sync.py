#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright 2024 The DSM Authors, All rights reserved.
# Licensed under the Apache License Version 2.0 that can be found in the
# LICENSE file in the root directory of this source tree
import os
import subprocess

from dsm.core.deps.deps import Deps
from dsm.core.fetcher.fetcher import FetcherFactory
from dsm.core.env.env import Env
from dsm.core.utils.log import Log


class NeedSync:
    def __init__(self, target, meta_data, force):
        self.target_path = os.path.join(Env.get_env("root_path"), target)
        self.force = force
        self.meta_data = meta_data

    def __bool__(self):
        return (
            self.force
            or not os.path.exists(self.target_path)
            or not any(os.scandir(self.target_path))
        )


class GitNeedSync(NeedSync):
    def __init__(self, target, meta_data, force):
        super().__init__(target, meta_data, force)

    def __bool__(self):
        result_from_super = super().__bool__()
        if result_from_super:
            return result_from_super
        commit = self.meta_data["commit"]
        current_path = os.getcwd()
        os.chdir(self.target_path)
        result = False
        try:
            current_commit = (
                subprocess.check_output("git rev-parse HEAD", shell=True)
                .decode("utf-8")
                .strip()
            )
            if current_commit != commit:
                print(current_commit, commit)
                result = True
        except Exception as e:
            # if have any exception, should sync resource again.
            result = True
        finally:
            os.chdir(current_path)
            return result


class ActionNeedSync(NeedSync):
    def __init__(self, target, meta_data, force):
        super().__init__(target, meta_data, force)

    def __bool__(self):
        return True


class PackageNeedSync(NeedSync):
    def __init__(self, target, meta_data, force):
        super().__init__(target, meta_data, force)

    def __bool__(self):
        result_from_super = super().__bool__()
        if result_from_super:
            return result_from_super
        result = False
        sha256 = self.meta_data["sha256"]
        current_path = os.getcwd()
        os.chdir(self.target_path)
        try:
            with open("SHA256", "r") as f:
                if sha256 != f.read():
                    result = True
        except Exception as e:
            result = True
        finally:
            os.chdir(current_path)
            return result


def need_sync_factory(sync_type, target, meta_data, force):
    if sync_type == "git":
        return GitNeedSync(target, meta_data, force)
    elif sync_type == "package":
        return PackageNeedSync(target, meta_data, force)
    elif sync_type == "action":
        return ActionNeedSync(target, meta_data, force)
    else:
        Log.fatal(f"Need Sync not support for type {sync_type}")


def check_circle(deps: Deps):
    tasks = []
    index = {}
    rindex = []
    tag = 0
    for dep_name in deps.deps_meta_data.keys():
        index[dep_name] = tag
        rindex.append(dep_name)
        tag += 1
    matrix = [[0] * tag for _ in range(tag)]
    for dep_name in deps.deps_meta_data.keys():
        dep = deps.get_target(dep_name)
        dep_deps = []
        if "deps" in dep:
            dep_deps = dep["deps"]
        for dd in dep_deps:
            if dd not in index:
                Log.fatal(f'Target "{dd}" not found')
            matrix[index[dep_name]][index[dd]] = 1
    has_schedule = []
    while len(tasks) < tag:
        had_circle = True
        for i in range(tag):
            if i in has_schedule:
                continue
            s = 0
            for j in range(tag):
                s += matrix[j][i]
            if s == 0:
                had_circle = False
                matrix[i] = [0] * tag
                has_schedule.append(i)
                tasks.append({"name": rindex[i], "dep": deps.get_target(rindex[i])})
        if had_circle:
            circle_details = []
            for src in range(tag):
                for dest in range(tag):
                    if matrix[src][dest] != 0:
                        circle_details.append(f'"{rindex[src]}"---->"{rindex[dest]}"')
            Log.fatal(f"Circular reference：\n\t{'\n\t'.join(circle_details)}")

    return tasks


def set_ignore(ignored_files):
    exclude_file = os.path.join(Env.get_env("root_path"), ".git", "info", "exclude")
    if not os.path.exists(os.path.dirname(exclude_file)):
        return
    if os.path.exists(exclude_file):
        with open(exclude_file, "r") as f:
            ignored_files = set(
                ignored_files + [line.strip() for line in f.readlines() if line.strip()]
            )
    with open(exclude_file, "w") as f:
        f.write("\n".join(ignored_files) + "\n")


class Sync:
    def __init__(self, args):
        self.force = args.force

    def run(self, deps: Deps):
        tasks = check_circle(deps)
        ignore_files = []
        index = len(tasks) - 1
        while index >= 0:
            task_name = tasks[index]["name"]
            task = tasks[index]["dep"]
            index -= 1
            if task_name not in deps.deps_meta_data.keys():
                Log.fatal(f"{task_name} not in DEPS file.")
            if not need_sync_factory(task["type"], task_name, task, self.force):
                continue
            FetcherFactory.generate(task["type"]).fetch(task, task_name)
            if "ignore" not in task or task["ignore"]:
                ignore_files.append(task_name)
        set_ignore(ignore_files)
