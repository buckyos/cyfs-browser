## Build Windows Cyfs Browser


### Install prerequisites

Follow the instructions for your platform:

Windows 10  
rust 1.57+  
node 14+  
[Windows SDK 10.0.20348.0](https://developer.microsoft.com/zh-cn/windows/downloads/sdk-archive/)  
Visual Studio 2019  
[NSIS](https://nsis.sourceforge.io/Download)  


### Clone and initialize the repo

Once you have the prerequisites installed, you can get the code and initialize the build environment.

1. downlaod depot_tools and set env variables
```cmd
git clone https://chromium.googlesource.com/chromium/tools/depot_tools.git

setx path "%path%;${path_to_depot_tools}"
```

##### disadble update chromium source background
```cmd
set DEPOT_TOOLS_UPDATE=0
set DEPOT_TOOLS_WIN_TOOLCHAIN=0
```

2.Get Cyfs Browser and Chromium source
```cmd
git clone https://github.com/buckyos/cyfs-browser.git ${root}

cd ${root}

fetch chromium

gclient sync --force --nohooks --with_branch_heads

cd ${root}/src

git fetch --tags

git checkout -b cyfs_branch 103.0.5047.0

gclient sync --with_branch_heads --with_tags
```

### Build Cyfs Browser

1. Update and compile Cyfs componment
```cmd
cd ${root}/script

python(python3) prepare_cyfs_dependency.py
```

2. Compile Cyfs Browser source code
```cmd
cd ${root}/script

python(python3) build.py --project-name=${project_name} --version=${version}

### like this: python(python3) build.py --project-name=Browser --version=1
```

3.Find the Cyfs Browser installation package

`${root}/\browser_install/Cyfs_Browser_${version}.exe`