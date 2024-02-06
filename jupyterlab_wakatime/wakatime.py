import os
import platform

from jupyterlab._version import __version__ as jlab_version

from ._version import __version__ as extension_version


def get_os_name():
    name = platform.system().lower()
    if (
        name.startswith("cygwin")
        or name.startswith("mingw")
        or name.startswith("msys")
    ):
        return "windows"
    if name == "linux" and "ANDROID_DATA" in os.environ:
        return "android"
    return name


USER_AGENT = f"jupyterlab/{jlab_version} jupyterlab-wakatime/{extension_version}"
HOME_FOLDER = os.path.realpath(
    os.environ.get("WAKATIME_HOME") or os.path.expanduser("~")
)
RESOURCES_FOLDER = os.path.join(HOME_FOLDER, ".wakatime")
WAKATIME_CLI = os.path.join(RESOURCES_FOLDER, "wakatime-cli")
if get_os_name() == "windows":
    WAKATIME_CLI += ".exe"
