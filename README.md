# Basecamp Extension

Open Basecamp projects in browser quickly using [Basecamp](https://basecamp.com/). Based on [Basecampy3](https://github.com/phistrom/basecampy3).

![picture1](images/screenshot.png)

## Supported options

- `bc`: list all projects 
- `bc word`: list all project matching `word`

## Setup

This project uses Basecamp 3 API to set it up, please install and configure Basecampy3 to make it work.
```
pip install basecampy3
bc3 configure
```

## Dev
```
ulauncher --no-extensions --dev -v
VERBOSE=1 ULAUNCHER_WS_API=ws://127.0.0.1:5054/com.github.mikolfaro.ulauncher-basecamp PYTHONPATH=/usr/lib/python3/dist-packages /usr/bin/python3 ~/.local/share/ulauncher/extensions/com.github.mikolfaro.ulauncher-basecamp/main.py
```
