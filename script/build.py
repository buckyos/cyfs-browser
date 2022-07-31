# -*- coding: UTF-8 -*-

import os
import sys
import argparse
import platform
import subprocess

from lib.patch import apply_patchs
from lib.ninja import build_browser
from lib.pack import make_installer
from lib.common import MAC_CPUS, static_page_path, src_path, ts_sdk_path, cyfs_tools_path
from lib.util import is_dir_exists
from lib.git_patch import GitPatcher


root = os.path.normpath(os.path.join(os.path.dirname(
        os.path.abspath(__file__)), os.pardir))

IS_MAC = platform.system() == "Darwin"

def _parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-name",
        help="The project name.",
        type=str,
        required=True)
    parser.add_argument("--version",
        help="The build version.",
        type=str,
        required=True)
    parser.add_argument("--target-cpu",
        help="The target cpu, like X86 and ARM, just for Macos",
        type=str,
        default='ARM',
        required=False)
    opt = parser.parse_args(args)

    assert opt.project_name.strip()
    assert opt.version.strip()
    if IS_MAC:
        assert opt.target_cpu.strip()
        assert opt.target_cpu in MAC_CPUS
    else:
        opt.target_cpu = None

    return opt

def check_requirements(target_cpu):
    _static_page_path = static_page_path(root, target_cpu)
    if not is_dir_exists(_static_page_path):
        sys.exit("cyfs static page %s is not available, please check!" % _static_page_path)

    _ts_sdk_path = ts_sdk_path(root, target_cpu)
    if not is_dir_exists(_ts_sdk_path):
        sys.exit("cyfs ts sdk %s is not available, please check!" % _ts_sdk_path)

    _cyfs_tools_path = cyfs_tools_path(root, target_cpu)
    if not is_dir_exists(_cyfs_tools_path):
        sys.exit("cyfs ts sdk %s is not available, please check!" % _cyfs_tools_path)

    _chrome_src_path = os.path.join(src_path(root), "chrome")
    if not is_dir_exists(_chrome_src_path):
        sys.exit("chromium src %s is not available, please check!" % _chrome_src_path)

    check_chromium_branch(src_path(root))

def check_chromium_branch(src):
    default_branch = "cyfs_branch"
    try:
        cmd = ['git', 'symbolic-ref', '--short', 'HEAD']
        git_br = subprocess.check_output(cmd, cwd=src).decode('ascii').rstrip()
        if git_br != default_branch:
            raise Exception("Current branch is not cyfs branch ")
    except Exception as e:
        msg = "Check chromium code branch failed, error: %s" % e
        print(msg)
        sys.exit(msg)

def main(args):
    opt = _parse_args(args)
    check_requirements(opt.target_cpu)
    ### patch
    # apply_patchs(root)
    GitPatcher.update(root)
    ### use chromium gn and ninja tool compile source code
    build_browser(src_path(root), opt.project_name, opt.target_cpu)

    ### pack
    make_installer(root, opt.project_name, opt.version, opt.target_cpu)

    print("Build finished!!")


if __name__ == "__main__":
    try:
        print(str(sys.argv))
        sys.exit(main(sys.argv[1:]))
    except KeyboardInterrupt:
        sys.stderr.write("interrupted\n")
        sys.exit(1)
