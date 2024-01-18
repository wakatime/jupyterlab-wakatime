import asyncio
import os.path
import shlex
from typing import TypedDict

from jupyter_server.base.handlers import APIHandler
from jupyter_server.utils import url_path_join
from jupyterlab._version import __version__ as jlab_version
import tornado

from ._version import __version__ as extension_version

HOME_FOLDER = os.path.realpath(
    os.environ.get("WAKATIME_HOME") or os.path.expanduser("~")
)
RESOURCES_FOLDER = os.path.join(HOME_FOLDER, ".wakatime")
WAKATIME_CLI = os.path.join(RESOURCES_FOLDER, "wakatime-cli")
USER_AGENT = f"jupyterlab/{jlab_version} jupyterlab-wakatime/{extension_version}"


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
            cmd_args.append("--log-to-stdout")

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
        proc = await asyncio.create_subprocess_exec(
            WAKATIME_CLI,
            *cmd_args,
            stdout=asyncio.subprocess.PIPE,
        )
        stdout, _ = await proc.communicate()
        if proc.returncode != 0:
            self.set_status(500)
            self.log.error("wakatime error: %s", stdout.decode())
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
