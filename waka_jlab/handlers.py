import os.path
import subprocess
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
    def post(self):
        try:
            data: RequestData = tornado.escape.json_decode(self.request.body)
            print(data)
            cmd_args: list[str] = [WAKATIME_CLI, "--plugin", USER_AGENT]

            filepath = os.path.abspath(data["filepath"])
            cmd_args.extend(["--entity", filepath])
            if data["timestamp"]:
                cmd_args.extend(["--time", str(data["timestamp"])])
            if data["iswrite"]:
                cmd_args.append("--write")
        except:
            self.set_status(400)
        print(cmd_args)
        p = subprocess.run(cmd_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(p.stdout.decode("utf8"))
        print(p.stderr.decode("utf8"))
        if p.returncode != 0:
            self.set_status(500)
        self.finish()


def setup_handlers(web_app):
    if not os.path.exists(WAKATIME_CLI):
        raise RuntimeWarning(
            "JupyterLab Wakatime plugin failed to find " + WAKATIME_CLI
        )

    host_pattern = ".*$"
    base_url = web_app.settings["base_url"]
    route_pattern = url_path_join(base_url, "waka-jlab", "heartbeat")
    handlers = [(route_pattern, RouteHandler)]
    web_app.add_handlers(host_pattern, handlers)
