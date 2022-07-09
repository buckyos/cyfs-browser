# -*- coding: UTF-8 -*-

import os
import sys
import shutil
import subprocess
import platform
from lib.util import is_dir_exists, make_dir_exist, make_file_not_exist
from lib.common import dmg_dir, cyfs_tools_path, static_page_path, ts_sdk_path, ChangeDir


ROOT_PATH = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir))

NPM = 'npm'
if platform.system() == "Windows":
    NPM += '.cmd'



def execute_cmd(cmd, log_file=None):
    try:
        print("cmd : %s" %cmd)
        subprocess.check_call(cmd, stdout=log_file, stderr=log_file)
    except Exception as e:
        print("Execute cmd %s failed: %s" % (cmd, e))
        raise



def get_runtime_dependencies():
    build_cyfs_runtime()
    copy_runtime_target()

def build_cyfs_runtime():
    try:
        os.chdir(ROOT_PATH)

        git_flag = os.path.join(ROOT_PATH, "CYFS", ".git")
        if not os.path.exists(git_flag):
            os.chdir(ROOT_PATH)
            git_cmd_args = ["git", "clone", "https://github.com/buckyos/CYFS.git"]
            execute_cmd(git_cmd_args)
        else:
            os.chdir(os.path.join(ROOT_PATH, "CYFS"))
            git_cmd_args = ["git", "pull"]
            execute_cmd(git_cmd_args)

        src_dir = os.path.join(ROOT_PATH, "CYFS", "src")
        os.chdir(src_dir)

        build_cmd_args = ["cargo", "build", "-p",  "cyfs-runtime", "--release"]
        execute_cmd(build_cmd_args)

    except Exception as e:
        print("Build CYFS RUNTIME failed, with %s" % e)
        raise


def copy_runtime_target():
    target_bin_path = os.path.join(ROOT_PATH, "CYFS", "src", "target", "release")
    bin_name = "cyfs-runtime"

    local_bin = os.path.join(target_bin_path, bin_name)
    if not os.path.exists(local_bin):
        print("CYFS runtime bin is not available, please check!")
        sys.exit(-1)

    if platform.system() == "Darwin":
        for target_cpu in ["ARM", "X86"]:
            dst_dir = dmg_dir(ROOT_PATH, target_cpu)
            shutil.copy(local_bin, os.path.join(dst_dir, bin_name))



def get_tools_dependencies():
    build_cyfs_tools()
    copy_tools_target()


def build_cyfs_tools():
    try:
        git_flag = os.path.join(ROOT_PATH, "CYFS", ".git")
        if not os.path.exists(git_flag):
            os.chdir(ROOT_PATH)
            git_cmd_args = ["git", "clone", "https://github.com/buckyos/CYFS.git"]
            execute_cmd(git_cmd_args)
        else:
            os.chdir(os.path.join(ROOT_PATH, "CYFS"))
            git_cmd_args = ["git", "pull"]
            execute_cmd(git_cmd_args)

        src_dir = os.path.join(ROOT_PATH, "CYFS", "src")
        os.chdir(src_dir)
        build_cmd_args = ["cargo",  "build", "-p", "cyfs-client",  "-p",  "pack-tools",  "--release"]
        execute_cmd(build_cmd_args)
    except Exception as e:
        print("Build CYFS TOOLS failed, with %s" % e)
        raise


def copy_tools_target():
    target_bin_path = os.path.join(ROOT_PATH, "CYFS", "src", "target", "release")
    bin_names = ["cyfs-client", "pack-tools"]

    for bin_name in bin_names:
        local_bin = os.path.join(target_bin_path, bin_name)
        if not os.path.exists(local_bin):
            print("CYFS tool bin %s is not available, please check!" % local_bin)
            sys.exit(-1)

        if platform.system() == "Darwin":
            for target_cpu in ["ARM", "X86"]:
                dst_dir = cyfs_tools_path(ROOT_PATH, target_cpu)
                make_dir_exist(dst_dir)
                shutil.copy(local_bin, os.path.join(dst_dir, bin_name))



def get_cyfs_ts_dependencies():
    build_cyfs_ts_sdk()
    copy_cyfs_ts_target()


def build_cyfs_ts_sdk():
    try:
        src_dir = os.path.join(ROOT_PATH, "cyfs-ts-sdk")
        git_flag = os.path.join(src_dir, ".git")
        if not os.path.exists(git_flag):
            os.chdir(ROOT_PATH)
            git_cmd_args = ["git", "clone", "https://github.com/buckyos/cyfs-ts-sdk.git"]
            execute_cmd(git_cmd_args)
        else:
            os.chdir(src_dir)
            git_cmd_args = ["git", "pull"]
            execute_cmd(git_cmd_args)


        os.chdir(src_dir)
        build_cmd_args = [NPM, "install"]
        execute_cmd(build_cmd_args)

        build_cmd_args = [NPM, "run", "build:h5"]
        execute_cmd(build_cmd_args)

    except Exception as e:
        print("Build CYFS TS SDK failed, with %s" % e)
        raise

def copy_cyfs_ts_target():
    target_file_path = os.path.join(ROOT_PATH, "cyfs-ts-sdk", "out")
    bin_name = "cyfs.js"

    local_bin = os.path.join(target_file_path, bin_name)
    if not os.path.exists(local_bin):
        print("CYFS TS SDK is not available, please check!")
        sys.exit(-1)

    if platform.system() == "Darwin":
        for target_cpu in ["ARM", "X86"]:
            dst_dir = ts_sdk_path(ROOT_PATH, target_cpu)
            make_dir_exist(dst_dir)
            shutil.copy(local_bin, os.path.join(dst_dir, bin_name))



def get_cyfs_browser_page_dependencies():
    build_cyfs_browser_webpage()
    copy_cyfs_browser_page_target()


def build_cyfs_browser_webpage():
    try:
        src_dir = os.path.join(ROOT_PATH, "cyfs-browser-webpage")
        git_flag = os.path.join(src_dir, ".git")
        if not os.path.exists(git_flag):
            os.chdir(ROOT_PATH)
            git_cmd_args = ["git", "clone", "https://github.com/buckyos/cyfs-browser-webpage.git"]
            execute_cmd(git_cmd_args)
        else:
            os.chdir(src_dir)
            git_cmd_args = ["git", "pull"]
            execute_cmd(git_cmd_args)

        os.chdir(src_dir)
        build_cmd_args = [NPM, "install"]
        execute_cmd(build_cmd_args)

        build_cmd_args = [NPM, "run", "build"]
        execute_cmd(build_cmd_args)

    except Exception as e:
        print("Build CYFS BROWSER PAGE failed, with %s" % e)
        raise


def copy_cyfs_browser_page_target():
    target_file_path = os.path.join(ROOT_PATH, "cyfs-browser-webpage")
    dir_name = "www"

    local_pages = os.path.join(target_file_path, dir_name)
    if not is_dir_exists(local_pages):
        print("CYFS BROWSER PAGE is not available, please check!")
        sys.exit(-1)

    if platform.system() == "Darwin":
        for target_cpu in ["ARM", "X86"]:
            dst_dir = static_page_path(ROOT_PATH, target_cpu)
            make_file_not_exist(dst_dir)
            shutil.copytree(local_pages, os.path.join(dst_dir))


def main():
    get_runtime_dependencies()
    get_tools_dependencies()
    get_cyfs_browser_page_dependencies()
    get_cyfs_ts_dependencies()



if __name__ == '__main__':
    try:
        print(str(sys.argv))
        sys.exit(main())
    except KeyboardInterrupt:
        sys.stderr.write("interrupted\n")
        sys.exit(1)