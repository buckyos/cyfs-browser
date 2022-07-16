# Cyfs Browser(Macos)


## Install prerequisites

Follow the instructions for your platform:

rust 1.57+  
node 14+  
Xcode 13.1+  
macOS SDK 12.0+  
[Packages](http://s.sudre.free.fr/Software/Packages/about.html)  

[note]
Build Cyfs Browser code must be use Xcode Developer tool
```bash
xcode-select -s /Applications/Xcode.app/Contents/Developer
```


## Clone and initialize the repo

Once you have the prerequisites installed, you can get the code and initialize the build environment.

1. downlaod depot_tools and set env variables
```bash
git clone https://chromium.googlesource.com/chromium/tools/depot_tools.git

export PATH="$PATH:${path_to_depot_tools}"
```

##### disadble update chromium source background
```bash
export DEPOT_TOOLS_UPDATE=0
```


2.Get Cyfs Browser and Chromium source
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

## Build Cyfs Browser

1. Update and compile Cyfs componment
```bash
cd ${root}/script

python(python3) prepare_cyfs_dependency.py
```

2. Compile Cyfs Browser source code
[note] if you build machine is macos, you must to set target-cpu argument like `ARM` and `X86`
ARM is mean m1 cpu machine, and X86 is mean x86 cpu machine
```bash
cd ${root}/script

python(python3) build.py --project-name=${project_name} --version=${version} --target-cpu=${target_cpu}

### like this: python(python3) build.py --project-name=Browser --version=1 --target-cpu=ARM
```

3.Find the Cyfs Browser installation package

`${root}/dmg/${target_cpu}/cyfs-browser-installer-${version}.dmg`