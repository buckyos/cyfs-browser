## Build Windows CYFS Browser  


### Install prerequisites

Follow the instructions for your platform:

- Windows 10  
- rust 1.57+  
- node 14+  
- [Windows SDK 10.0.20348.0](https://developer.microsoft.com/zh-cn/windows/downloads/sdk-archive/)  
- Visual Studio 2019  
- [NSIS](https://nsis.sourceforge.io/Download)  


### Clone and initialize the repo  

Once you have the prerequisites installed, you can get the code and initialize the build environment.

- Downlaod depot_tools and set env variables
```cmd
git clone https://chromium.googlesource.com/chromium/tools/depot_tools.git
set DEPOT_TOOLS_PATH={you_depot_tools_path}
set path=%path%;%DEPOT_TOOLS_PATH%
```

- Disadble update chromium source background
```cmd
set DEPOT_TOOLS_UPDATE=0
set DEPOT_TOOLS_WIN_TOOLCHAIN=0
```

- Get CYFS Browser and Chromium source
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

### Build CYFS Browser

- Compile CYFS Browser source code
```cmd
cd ${root}/script

python(python3) build.py --project-name=${project_name} --version=${version} --channel=${channel}

### like this: python(python3) build.py --project-name=Browser --version=1 --channel=beta
```

- Compile CYFS Related dependencies
```cmd
cd ${root}/script/lib

python(python3) build.py  --version=${version} --channel=${channel} 

### like this: python(python3) build.py --version=1 --channel=beta
```

- Find the CYFS Browser installation package

`${root}/outwin/X86/CYFS_Browser_${1.0.channel_number.version}-channel.exe`

note: if channel is nightly then channel_number is 0, and channel_number is 1 when channle is beta
