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

from .wakatime import USER_AGENT, WAKATIME_CLI, download_cli


class BeatData(TypedDict):
    filepath: str
    iswrite: bool
    timestamp: float
    debug: bool


class BeatHandler(APIHandler):
    # The following decorator should be present on all verb methods (head, get, post,
    # patch, put, delete, options) to ensure only authorized user can request the
    # Jupyter server
    @tornado.web.authenticated
    async def post(self):
        if not os.path.exists(WAKATIME_CLI):
            self.finish(json.dumps({"code": 127}))
            await download_cli(self.log)
            return
        try:
            data: BeatData = tornado.escape.json_decode(self.request.body)
            cmd_args: list[str] = ["--plugin", USER_AGENT]

            root_dir = os.path.expanduser(self.contents_manager.root_dir)
            filepath = os.path.abspath(os.path.join(root_dir, data["filepath"]))
            cmd_args.extend(["--entity", filepath])
            if data["timestamp"]:
                cmd_args.extend(["--time", str(data["timestamp"])])
            if data["iswrite"]:
                cmd_args.append("--write")
            if data.get("debug"):
                cmd_args.append("--verbose")
        except:
            return self.finish(json.dumps({"code": 400}))
        if data.get("debug"):
            self.log.info("wakatime-cli " + shlex.join(cmd_args))

        # Async subprocess is required for non-blocking access to return code
        # However, it's not supported on Windows
        # As a workaround, create a Popen instance and leave it alone
        if platform.system() == "Windows":
            if not data.get("debug"):
                subprocess.Popen([WAKATIME_CLI, *cmd_args])
                return self.finish(json.dumps({"code": 0}))
            proc = subprocess.run([WAKATIME_CLI, *cmd_args], stdout=subprocess.PIPE)
            stdout = proc.stdout.decode().strip()
        else:
            proc = await asyncio.create_subprocess_exec(
                WAKATIME_CLI,
                *cmd_args,
                "--log-to-stdout",
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
                level = log.get("level", "")
                if hasattr(self.log, level):
                    getattr(self.log, level)(
                        "WakaTime %s: %s", level, log.get("message")
                    )
        return self.finish(json.dumps({"code": proc.returncode}))


class StatusHandler(APIHandler):
    @tornado.web.authenticated
    async def get(self):
        if not os.path.exists(WAKATIME_CLI):
            self.finish(json.dumps({"time": ""}))
            await download_cli(self.log)
            return

        cmd = [WAKATIME_CLI, "--today", "--output=raw-json"]
        if platform.system() == "Windows":
            proc = subprocess.run(cmd, stdout=subprocess.PIPE, encoding="utf8")
            if proc.returncode:
                return self.finish(json.dumps({"time": ""}))
            stdout = proc.stdout.strip()
        else:
            proc = await asyncio.create_subprocess_exec(
                *cmd, stdout=asyncio.subprocess.PIPE
            )
            stdout, _ = await proc.communicate()
            if proc.returncode:
                return self.finish(json.dumps({"time": ""}))
            stdout = stdout.decode().strip()
        data = json.loads(stdout).get("data", {})
        time = data.get("grand_total", {}).get("digital", "")
        self.finish(json.dumps({"time": time}))


def setup_handlers(web_app):
    host_pattern = ".*$"
    base_url = url_path_join(web_app.settings["base_url"], "jupyterlab-wakatime")
    handlers = [
        (url_path_join(base_url, "heartbeat"), BeatHandler),
        (url_path_join(base_url, "status"), StatusHandler),
    ]
    web_app.add_handlers(host_pattern, handlers)
