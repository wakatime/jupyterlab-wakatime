import sys
import os
import shutil
import platform
from zipfile import ZipFile

import httpx
from jupyterlab._version import __version__ as jlab_version

try:
    from ._version import __version__ as extension_version
except ImportError:
    import warnings

    warnings.warn("Importing 'jupyterlab_wakatime' outside a proper installation.")
    extension_version = "dev"


def architecture():
    arch = platform.machine() or platform.processor()
    if arch == "armv7l":
        return "arm"
    if arch == "aarch64":
        return "arm64"
    if "arm" in arch:
        return "arm64" if sys.maxsize > 2**32 else "arm"
    return "amd64" if sys.maxsize > 2**32 else "386"


OS_NAME = platform.system().lower()
for distro in ("cygwin", "mingw", "msys"):
    if OS_NAME.startswith(distro):
        OS_NAME = "windows"
if OS_NAME == "linux" and "ANDROID_DATA" in os.environ:
    OS_NAME = "android"

ARCH = architecture()
PLUGIN_NAME = "jupyterlab-wakatime"
USER_AGENT = f"jupyterlab/{jlab_version} {PLUGIN_NAME}/{extension_version}"
HOME_FOLDER = os.path.realpath(os.environ.get("WAKATIME_HOME", os.path.expanduser("~")))
RESOURCES_FOLDER = os.path.join(HOME_FOLDER, ".wakatime")
WAKATIME_CLI = os.path.join(RESOURCES_FOLDER, "wakatime-cli")
WAKATIME_BINARY = os.path.join(RESOURCES_FOLDER, f"wakatime-cli-{OS_NAME}-{ARCH}")
if OS_NAME == "windows":
    WAKATIME_CLI += ".exe"
    WAKATIME_BINARY += ".exe"

GITHUB_RELEASES_STABLE_URL = os.environ.get(
    "WAKATIME_RELEASES_URL",
    "https://api.github.com/repos/wakatime/wakatime-cli/releases/latest",
)
GITHUB_DOWNLOAD_URL = os.environ.get(
    "WAKATIME_DOWNLOAD_URL",
    "https://github.com/wakatime/wakatime-cli/releases/latest/download",
)

downloading = False


async def download_cli(logger):
    global downloading
    if downloading:
        return
    downloading = True
    try:
        if not os.path.exists(RESOURCES_FOLDER):
            os.makedirs(RESOURCES_FOLDER)
        if os.path.isdir(WAKATIME_CLI):
            shutil.rmtree(WAKATIME_CLI)
        download_url = f"{GITHUB_DOWNLOAD_URL}/wakatime-cli-{OS_NAME}-{ARCH}.zip"
        zip_file = os.path.join(RESOURCES_FOLDER, "wakatime-cli.zip")
        logger.info("Downloading WakaTime CLI from %s", download_url)

        client = httpx.AsyncClient(follow_redirects=True)
        headers = {"User-Agent": f"github.com/wakatime/{PLUGIN_NAME}"}
        async with client.stream("GET", download_url, headers=headers) as resp:
            with open(zip_file, "wb") as f:
                async for chunk in resp.aiter_bytes():
                    f.write(chunk)
        with ZipFile(zip_file) as zipf:
            zipf.extractall(RESOURCES_FOLDER)

        if OS_NAME != "windows":
            os.chmod(WAKATIME_BINARY, 0x755)
        if not os.path.islink(WAKATIME_CLI):
            if os.path.isfile(WAKATIME_CLI):
                os.remove(WAKATIME_CLI)
            elif os.path.isdir(WAKATIME_CLI):
                shutil.rmtree(WAKATIME_CLI)
            os.link(WAKATIME_BINARY, WAKATIME_CLI)
            if not os.path.exists(WAKATIME_CLI):
                shutil.copy2(WAKATIME_BINARY, WAKATIME_CLI)
        logger.info("WakaTime CLI is downloaded")
    finally:
        downloading = False
