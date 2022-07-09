# cyfs-browser

## Cyfs Browser

## Overview

This repository holds the build tools needed to build the Cyfs desktop browser for macOS.
  - [Chromium](https://chromium.googlesource.com/chromium/src.git)
    - Fetches code via `depot_tools`.
    - sets the branch for Chromium (ex: 65.0.3325.181).


## Install prerequisites

Follow the instructions for your platform:

rust 1.57+
node 14+


## Clone and initialize the repo

Once you have the prerequisites installed, you can get the code and initialize the build environment.

1. downlaod depot_tools and set env variables
```bash
    git clone https://chromium.googlesource.com/chromium/tools/depot_tools.git
    export PATH="$PATH:/path/to/depot_tools
```

##### disadble update chromium source background
```bash
export DEPOT_TOOLS_UPDATE=0
```


2.Get Cyfs Browser and Chromium source
```bash
git git@github.com:buckyos/cyfs-browser.git path-to-your-project-folder
cd path-to-your-project-folder

fetch chromium
```

3.Checkout chromium code to special tag

```bash
    cd src
    git checkout 2839da9a719287e08fad7bc9de4bfcc87a4bb87b

```

## Build Cyfs Browser

1. Update and compile Cyfs componment
```bash
python prepare_cyfs_dependency.py
```

2. Compile Cyfs Browser source code
[note] if you build machine is macos, you must to set target-cpu argument like `ARM` and `X86`
ARM is mean m1 cpu machine, and X86 is mean x86 cpu machine
```bash
python build.py --project-name=${Browser} --version=${version} --target-cpu=ARM
```