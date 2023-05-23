## Build MacOs CYFS Browser


### Install prerequisites

Follow the instructions for your platform:

rust 1.57+  
node 14+  
Xcode 13.1+  
macOS SDK 12.0+  
[Packages](http://s.sudre.free.fr/Software/Packages/about.html)  

[note]
Build CYFS Browser code must be use Xcode Developer tool
```bash
xcode-select -s /Applications/Xcode.app/Contents/Developer
```


### Clone and initialize the repo

Once you have the prerequisites installed, you can get the code and initialize the build environment.

- Downlaod depot_tools and set env variables
```bash
git clone https://chromium.googlesource.com/chromium/tools/depot_tools.git

export PATH="$PATH:${path_to_depot_tools}"
```

- Disadble update chromium source background
```bash
export DEPOT_TOOLS_UPDATE=0
```


- Get CYFS Browser and Chromium source
```bash
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
[note] if you build machine is macos, you must to set target-cpu argument like `ARM` and `X86`
ARM is mean m1 cpu machine, and X86 is mean x86 cpu machine
```bash
cd ${root}/script

python(python3) build.py --project-name=${project_name} --version=${version} --target-cpu=${target_cpu} --channel=${channel}

### like this: python(python3) build.py --project-name=Browser --version=1 --target-cpu=ARM --channel=beta
```

- Compile CYFS Related dependencies
```cmd
cd ${root}/script/lib

python(python3) build.py  --version=${version} --channel=${channel} --target_cpu=${target_cpu}

### like this: python(python3) build.py --version=1 --channel=beta --target_cpu=X86
```

- Find the CYFS Browser installation package

`${root}/out/mac/{target_cpu}/}/CYFS_Browser-1.0.${channel_number}.${version}-${target_cpu}.dmg`

note: if channel is nightly then channel_number is 0, and channel_number is 1 when channle is beta