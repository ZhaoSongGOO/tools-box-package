#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json

from plugin_cli.base.result import Err, Ok
from plugin_cli.plugin.plugin import Plugin
from plugin_cli.plugin.plugin_auto_register import AutoRegister


def json_format(i, o):
    try:
        with open(i, "r") as in_file:
            data = json.load(in_file)
            with open(o, "w") as out_file:
                json.dump(data, out_file, indent=4)
        return Ok()
    except Exception as e:
        return Err(1, f"{e}")


def json_unformat(i, o):
    try:
        with open(i, "r") as in_file:
            data = json.load(in_file)
            with open(o, "w") as out_file:
                json.dump(data, out_file, separators=(",", ":"))
        return Ok()
    except Exception as e:
        return Err(1, f"{e}")


@AutoRegister(name="json-parser")
class JSONParserPlugin(Plugin):
    def __init__(self):
        super().__init__()
        self.commands = {"format": json_format, "unformat": json_unformat}

    def accept(self, args):
        return self.commands[args.command](args.input, args.output)

    def help(self):
        return "reduce json v0.1"

    def build_command_args(self, subparser):
        subparser_subparsers = subparser.add_subparsers(
            title="command",
            description="format|unformat",
            dest="command",
            required=True,
        )

        subparser_subparser = subparser_subparsers.add_parser(
            "format", help="format json file"
        )

        subparser_subparser.add_argument(
            "--input",
            dest="input",
            required=True,
            help="Specify the source file name",
        )

        subparser_subparser.add_argument(
            "--output",
            dest="output",
            required=True,
            help="Specify the output file name",
        )

        subparser_subparser = subparser_subparsers.add_parser(
            "unformat", help="unformat json file"
        )

        subparser_subparser.add_argument(
            "--input",
            dest="input",
            required=True,
            help="Specify the source file name",
        )

        subparser_subparser.add_argument(
            "--output",
            dest="output",
            required=True,
            help="Specify the output file name",
        )