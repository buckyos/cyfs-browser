## Build Windows CYFS Browser  


### Install prerequisites

Follow the instructions for your platform:

- Debian 10+  
- python3  
  


### Clone and initialize the repo  

Once you have the prerequisites installed, you can get the code and initialize the build environment.

- Downlaod depot_tools and set env variables
```cmd
git clone https://chromium.googlesource.com/chromium/tools/depot_tools.git

export PATH="{you_depot_tools_path}:$PATH"

source {you_depot_tools_path}/cipd_bin_setup.sh

cipd_bin_setup
```

- Get CYFS Browser and Chromium source
```cmd
git clone https://github.com/buckyos/cyfs-browser.git ${root}

cd ${root}

fetch --nohooks android

gclient sync

cd ${root}/src

git fetch --tags

git checkout -b cyfs_branch 103.0.5047.0

gclient sync --with_branch_heads --with_tags

cd src
./build/install-build-deps-android.sh

sudo apt-get install ninja-build
```


--------------------------
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

`${root}/out/android/X86/CYFS_Browser_${1.0.channel_number.version}-channel.apk`

note: if channel is nightly then channel_number is 0, and channel_number is 1 when channle is beta
