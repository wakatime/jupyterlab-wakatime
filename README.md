# waka_jlab

[![Github Actions Status](https://github.com/AllanChain/waka-jlab/workflows/Build/badge.svg)](https://github.com/AllanChain/waka-jlab/actions/workflows/build.yml)
A JupyterLab WakaTime extension.

## Requirements

- JupyterLab >= 4.0.0

## Install

> [!Warning]
>
> This plugin is at a VERY early stage!

1.  Install [wakatime-cli](https://github.com/wakatime/wakatime-cli):

        curl -fsSL https://raw.githubusercontent.com/wakatime/vim-wakatime/master/scripts/install_cli.py | python

    If the above command doesn't work, download [install_cli.py](https://raw.githubusercontent.com/wakatime/vim-wakatime/master/scripts/install_cli.py) and run it manually with Python 3.

2.  Create a `~/.wakatime.cfg` file with contents:

        [settings]
        api_key = XXXX

    Replace `XXXX` with your actual [api key](https://wakatime.com/settings#apikey).

3.  Execute (NOT available yet):

        pip install waka_jlab

## Uninstall

To remove the extension, execute:

```bash
pip uninstall waka_jlab
```

The following content is generated with the template:

---

## Troubleshoot

If you are seeing the frontend extension, but it is not working, check
that the server extension is enabled:

```bash
jupyter server extension list
```

If the server extension is installed and enabled, but you are not seeing
the frontend extension, check the frontend extension is installed:

```bash
jupyter labextension list
```

## Contributing

### Development install

Note: You will need NodeJS to build the extension package.

The `jlpm` command is JupyterLab's pinned version of
[yarn](https://yarnpkg.com/) that is installed with JupyterLab. You may use
`yarn` or `npm` in lieu of `jlpm` below.

```bash
# Clone the repo to your local environment
# Change directory to the waka_jlab directory
# Install package in development mode
pip install -e "."
# Link your development version of the extension with JupyterLab
jupyter labextension develop . --overwrite
# Server extension must be manually installed in develop mode
jupyter server extension enable waka_jlab
# Rebuild extension Typescript source after making changes
jlpm build
```

You can watch the source directory and run JupyterLab at the same time in different terminals to watch for changes in the extension's source and automatically rebuild the extension.

```bash
# Watch the source directory in one terminal, automatically rebuilding when needed
jlpm watch
# Run JupyterLab in another terminal
jupyter lab
```

With the watch command running, every saved change will immediately be built locally and available in your running JupyterLab. Refresh JupyterLab to load the change in your browser (you may need to wait several seconds for the extension to be rebuilt).

By default, the `jlpm build` command generates the source maps for this extension to make it easier to debug using the browser dev tools. To also generate source maps for the JupyterLab core extensions, you can run the following command:

```bash
jupyter lab build --minimize=False
```

### Development uninstall

```bash
# Server extension must be manually disabled in develop mode
jupyter server extension disable waka_jlab
pip uninstall waka_jlab
```

In development mode, you will also need to remove the symlink created by `jupyter labextension develop`
command. To find its location, you can run `jupyter labextension list` to figure out where the `labextensions`
folder is located. Then you can remove the symlink named `waka-jlab` within that folder.

### Packaging the extension

See [RELEASE](RELEASE.md)
