
# -*- coding: UTF-8 -*-

import os
import platform

MAC_CPUS = ["X86", "ARM"]

IS_MAC = platform.system() == "Darwin"
IS_WIN = platform.system() == "Windows"


def build_target(target_cpu, project_name):
    assert project_name is not None
    return "%s-%s" % (target_cpu, project_name) if target_cpu is not None else project_name

def src_path(root):
    return os.path.join(root, "src")

def local_extension_path(root):
    return os.path.join(root, "Extensions")

def local_nft_bin_path(root):
    return os.path.join(root, "nft")

def local_nft_web_path(root):
    return os.path.join(root, "nft_web")

def cyfs_runtime_path(root, target_cpu):
    return os.path.join(pack_base_path(root, target_cpu), "runtime")

def cyfs_tools_path(root, target_cpu):
    return os.path.join(cyfs_runtime_path(root, target_cpu), "tools")

def static_page_path(root, target_cpu):
    return os.path.join(cyfs_runtime_path(root, target_cpu), "www")

def ts_sdk_path(root, target_cpu):
    return os.path.join(static_page_path(root, target_cpu), "cyfs_sdk")

def application_name():
    return "CYFS Browser.app"

def product_name():
    return "CYFS_Browser"

def code_zip_name():
    if IS_WIN:
        return "chromium_code_pc.zip"
    elif IS_MAC:
        return "chromium_mac_code.tar.gz"
    return None

def nsis_bin_path():
    return 'C:\\Program Files (x86)\\NSIS\\Bin\\makensis.exe'

def pack_base_path(root, target_cpu):
    if IS_WIN:
        return os.path.join(root, "out", "win", target_cpu)
    elif IS_MAC:
        return os.path.join(root, "out", "mac", target_cpu)
    else:
        raise Exception("Unsupported platform")

def pkg_base_path(root, target_cpu):
    assert IS_MAC, 'Current function just for Macos'
    return os.path.join(pack_base_path(root, target_cpu), "package")

def pkg_build_path(root, target_cpu):
    assert IS_MAC, 'Current function just for Macos'
    return os.path.join(pkg_base_path(root, target_cpu), "build")

def pack_app_path(root, target_cpu, app):
    assert IS_MAC, 'Current function just for Macos'
    return os.path.join(pack_base_path(root, target_cpu), app)

def build_target_path(src_root, target):
    return os.path.join(src_root, "out", target)

def build_app_path(root, target, app):
    assert IS_MAC, 'Current function just for Macos'
    return os.path.join(build_target_path(src_path(root), target), app)

def last_args_file(src_root, target):
    return os.path.join(build_target_path(src_root, target), "args.gn")

def toolchain_ninja_file(src_root, target):
    return os.path.join(build_target_path(src_root, target), "toolchain.ninja")

def pack_include_files():
    include_files = [
        'CYFS_Browser.exe', 'chrome_proxy.exe',
    ]
    return include_files

def pack_include_version_files():
    include_version_files = [
        'chrome_100_percent.pak','chrome_200_percent.pak', 'resources.pak',
        'chrome.dll', 'chrome_elf.dll', 'mojo_core.dll', 'mojo_core.dll',
        'd3dcompiler_47.dll', 'libEGL.dll', 'libGLESv2.dll',
        'vk_swiftshader.dll', 'vulkan-1.dll',
        'chrome_pwa_launcher.exe', 'notification_helper.exe',
        'vk_swiftshader_icd.json', 'v8_context_snapshot.bin',
        'snapshot_blob.bin', 'icudtl.dat',
        'Logo.png', 'SmallLogo.png',
    ]
    return include_version_files

def pack_include_dirs():
    include_dirs = [
        'MEIPreload', 'Locales', 'swiftshader', 'resources'
    ]
    return include_dirs

def get_chromium_version(root):
    major = 0
    minor = 0
    build = 0
    patch = 0
    version_file = os.path.join(src_path(root), "chrome", "VERSION")
    for line in open(version_file, 'r'):
        line = line.rstrip()
        if line.startswith('MAJOR='):
            major = line[6:]
        elif line.startswith('MINOR='):
            minor = line[6:]
        elif line.startswith('BUILD='):
            build = line[6:]
        elif line.startswith('PATCH='):
            patch = line[6:]
    return '%s.%s.%s.%s' % (major, minor, build, patch)


def remote_extensions_path(remote_base_path):
    path = os.path.join(remote_base_path, "chromium_extensions", "Extensions")
    return os.path.normpath(path)

def remote_nft_web_path(remote_base_path):
    path = os.path.join(remote_base_path, "cyfs-nft", "nft-web", "pub")
    return os.path.normpath(path)

def remote_nft_bin_path(remote_base_path):
    path = os.path.join(remote_base_path, "cyfs-nft", "nft-creator", "pub")
    return os.path.normpath(path)

def remote_code_path(remote_base_path):
    if IS_MAC:
        return os.path.normpath(os.path.join(remote_base_path, "chromium_code_mac"))
    if IS_WIN:
        return os.path.normpath(os.path.join(remote_base_path, "chromium_code_pc"))
    return None

def remote_cache_path(remote_base_path):
    if IS_MAC:
        return os.path.normpath(os.path.join(remote_base_path, "browser_build_cache", "mac"))
    if IS_WIN:
        return os.path.normpath(os.path.join(remote_base_path, "browser_build_cache", "windows"))
    return None
