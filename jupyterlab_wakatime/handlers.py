import asyncio
from contextlib import suppress
import json
import os.path
import platform
import shlex
import subprocess
from typing import TypedDict

from jupyter_server.base.handlers import APIHandler
from jupyter_server.utils import url_path_join
import tornado

from .wakatime import USER_AGENT, WAKATIME_CLI


class RequestData(TypedDict):
    filepath: str
    iswrite: bool
    timestamp: float


class RouteHandler(APIHandler):
    # The following decorator should be present on all verb methods (head, get, post,
    # patch, put, delete, options) to ensure only authorized user can request the
    # Jupyter server
    @tornado.web.authenticated
    async def post(self):
        try:
            data: RequestData = tornado.escape.json_decode(self.request.body)
            cmd_args: list[str] = ["--plugin", USER_AGENT]

            root_dir = os.path.expanduser(self.contents_manager.root_dir)
            filepath = os.path.abspath(os.path.join(root_dir, data["filepath"]))
            cmd_args.extend(["--entity", filepath])
            if data["timestamp"]:
                cmd_args.extend(["--time", str(data["timestamp"])])
            if data["iswrite"]:
                cmd_args.append("--write")
        except:
            self.set_status(400)
            return self.finish()
        self.log.info("wakatime-cli " + shlex.join(cmd_args))

        if platform.system() == "Windows":
            subprocess.call([WAKATIME_CLI, *cmd_args])
            return self.finish()

        proc = await asyncio.create_subprocess_exec(
            WAKATIME_CLI,
            *cmd_args,
            "--log-to-stdout",
            "--verbose",
            stdout=asyncio.subprocess.PIPE,
        )
        stdout, _ = await proc.communicate()
        stdout = stdout.decode().strip()

        if proc.returncode == 112:
            self.log.warning("WakaTime rate limited")
        elif proc.returncode == 102:
            self.log.warning("WakaTime API error. May be connection issue")
        elif proc.returncode == 104:
            self.log.error("WakaTime API key invalid")
        elif proc.returncode == 103:
            self.log.error("WakaTime failed to parse config file")
        elif proc.returncode == 110:
            self.log.error("WakaTime failed to read config file")
        elif proc.returncode == 111:
            self.log.error("WakaTime failed to write config file")
        for line in stdout.split("\n"):
            with suppress(json.JSONDecodeError):
                log = json.loads(line)
                if log.get("level") != "error":
                    continue
                self.log.error("WakaTime error: %s", log.get("message", line))
        self.finish()


def setup_handlers(web_app):
    if not os.path.exists(WAKATIME_CLI):
        raise RuntimeWarning(
            "JupyterLab Wakatime plugin failed to find " + WAKATIME_CLI
        )

    host_pattern = ".*$"
    base_url = web_app.settings["base_url"]
    route_pattern = url_path_join(base_url, "jupyterlab-wakatime", "heartbeat")
    handlers = [(route_pattern, RouteHandler)]
    web_app.add_handlers(host_pattern, handlers)
