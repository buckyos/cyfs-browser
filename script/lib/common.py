
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


def cyfs_runtime_path(root, target_cpu=None):
    if IS_WIN:
        return os.path.join(root, "browser_install", "cyfs-runtime-pack")
    elif IS_MAC:
        assert target_cpu is not None
        return os.path.join(root, "dmg", target_cpu, "runtime")
    else:
        raise Exception("Unsupported platform")

def cyfs_tools_path(root, target_cpu=None):
    return os.path.join(cyfs_runtime_path(root, target_cpu), "tools")

def static_page_path(root, target_cpu=None):
    return os.path.join(cyfs_runtime_path(root, target_cpu), "www")

def ts_sdk_path(root, target_cpu):
    return os.path.join(static_page_path(root, target_cpu), "cyfs_sdk")

def runtime_pack_path(root):
    if IS_WIN:
        return [cyfs_runtime_path(root, None)]
    elif IS_MAC:
        return [cyfs_runtime_path(root, cpu) for cpu in MAC_CPUS]
    return []

def tools_pack_path(root):
    if IS_WIN:
        return [cyfs_tools_path(root, None)]
    elif IS_MAC:
        return [cyfs_tools_path(root, cpu) for cpu in MAC_CPUS]
    return []

def cyfs_ts_pack_path(root):
    if IS_WIN:
        return [ts_sdk_path(root, None)]
    elif IS_MAC:
        return [ts_sdk_path(root, cpu) for cpu in MAC_CPUS]
    return []

def web_page_pack_path(root):
    if IS_WIN:
        return [static_page_path(root, None)]
    elif IS_MAC:
        return [static_page_path(root, cpu) for cpu in MAC_CPUS]
    else:
        return []

def pack_base_path(root, target_cpu=None):
    if IS_WIN:
        return os.path.join(root, "browser_install")
    elif IS_MAC:
        assert target_cpu is not None
        return os.path.join(root, "dmg", target_cpu)
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
