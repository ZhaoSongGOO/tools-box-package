
# -*- coding: utf-8 -*-
from plugin_cli.base.error_code import ErrCode
from plugin_cli.base.result import Err, Ok
from plugin_cli.plugin.plugin import Plugin
from plugin_cli.plugin.plugin_auto_register import AutoRegister

from dsm.core.sync.sync import Sync

from dsm.core.deps.deps import Deps

from dsm.core.env.config import VERSION
from dsm.core.utils.log import Log
from dsm.core.env.env import init_env
import os

class InitProject:
    def __init__(self):
        pass

    def set_content(self, file):
        file.write(f"VERSION={VERSION}\n")

    def create(self, args):
        path = os.path.join(args.path, ".dsm")
        if os.path.exists(path):
            Log.warning(
                "The repository has already been initialized, no need to initialize again."
            )
        else:
            with open(path, "w") as file:
                self.set_content(file)

@AutoRegister(name="dsm")
class DSMPlugin(Plugin):
    def __init__(self):
        super().__init__()

    def accept(self, args):
        '''
        - Invocation timing
            This method willl be triggered when this plugin is called
            and will be passed the command-line arguments entered by the user.
        - Input
            eg: tools-box your-plugin -name a -version 1.0
                args will be Namespace(plugin='create', name='a', version='1.0'),
                You can use args.name or args.version to get value.
        - Return
            Return value must be of type `Err` or `Ok`.
            eg:
                Err(ErrCode.PLUGIN_INTERNAL_OTHER_ERR, "error message)
                Ok()
        '''
        init_env()
        command = args.command
        if command == "sync":
            deps = Deps(args.deps_dir, args.target)
            Sync(args).run(deps)
        elif command == "init":
            InitProject().create(args)
        return Ok()    

    def help(self):
        return "dependencies sync manager(DSM)"

    def build_command_args(self, subparser):
        '''
        The `subparser` is based on the `argparser` library and is used to build
        the user parameter system for the entire CLI. Here, you can construct parameters
        unique to yout own plugin.
        '''
        subparser_subparsers = subparser.add_subparsers(
            title="command",
            description="init or sync",
            dest="command",
            required=True,
        )
        init_subparser = subparser_subparsers.add_parser("init", help="Init a new workspace")
        init_subparser.add_argument("path", type=str, help="Directory need to be inited")

        sync_subparser = subparser_subparsers.add_parser("sync", help="Sync resources")
        sync_subparser.add_argument(
            "-f",
            "--force",
            action="store_true",
            help="Forcefully re-pull and overwrite existing content",
        )
        sync_subparser.add_argument(
            "deps_dir", type=str, help="Directory where DEPS file is located"
        )

        sync_subparser.add_argument(
            "-t",
            "--target",
            type=str,
            default=None,
            help="sync target name, DEPS.a's target name is a",
        )

        
