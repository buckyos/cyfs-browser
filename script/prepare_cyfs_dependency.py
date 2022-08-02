# -*- coding: UTF-8 -*-

import os
import sys
import shutil
import subprocess
import platform
from lib.util import is_dir_exists, make_dir_exist, make_file_not_exist
from lib.common import runtime_pack_path, tools_pack_path, cyfs_ts_pack_path, web_page_pack_path

root = os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), os.pardir))

IS_WIN = platform.system() == 'Windows'
_NPM = 'npm.cmd' if IS_WIN else 'npm'
_EXE = '.exe' if IS_WIN else ''

CYFS_URL = 'https://github.com/buckyos/CYFS.git'
CYFS_TS_SDK_URL = 'https://github.com/buckyos/cyfs-ts-sdk.git'
CYFS_WEB_PAGE_URL = 'https://github.com/buckyos/cyfs-browser-webpage.git'
CYFS_RUNTIMES = ['cyfs-runtime']

CYFS_TOOLS = ['cyfs-client', 'pack-tools']

def execute_cmd(cmd, **kwargs):
    try:
        print('Execute cmd: %s' % ' '.join(cmd))
        log_fd = kwargs.pop('log_fd', None)
        kwargs['stdout'] = log_fd
        kwargs['stderr'] = log_fd
        subprocess.check_call(cmd, **kwargs)
    except Exception as e:
        print('Execute cmd %s failed: %s' % (' '.join(cmd), e))
        raise

def get_repo_name_from_url(url):
    return url.rsplit('/', 1)[1].split('.')[0]

def git_reset_repo(local_path):
    try:
        cmd = ['git', 'reset', '--hard']
        execute_cmd(cmd, cwd=local_path)
    except Exception as e:
        print('Execute cmd %s failed: %s' % (' '.join(cmd), e))
        raise

def git_pull_repo(repo_url, local_path):
    try:
        cmd = ['git', 'pull', repo_url]
        execute_cmd(cmd, cwd=local_path)
    except Exception as e:
        print('Execute cmd %s failed: %s' % (' '.join(cmd), e))
        raise

def git_clone_repo(repo_url, local_path):
    try:
        cmd = ['git', 'clone', repo_url]
        execute_cmd(cmd, cwd=local_path)
    except Exception as e:
        print('Execute cmd %s failed: %s' % (' '.join(cmd), e))
        raise

def fetch_source_code(root, repo_url, local_repo_name=None):
    try:
        repo_name = local_repo_name or get_repo_name_from_url(repo_url)
        local_path = os.path.join(root, repo_name)
        if not os.path.exists(os.path.join(local_path, '.git')):
            git_clone_repo(repo_url, root)
            # cmd = ['git', 'clone', repo_url]
            # cwd = root
        else:
            git_reset_repo(local_path)
            git_pull_repo(repo_url, local_path)
        # execute_cmd(cmd, cwd=cwd)
        return local_path
    except Exception as e:
        msg = 'Get %s failed: %s' % (repo_url, e)
        print(msg)
        sys.exit(msg)


def get_runtime_dependencies():
    local_path = build_cyfs_runtime()
    copy_runtime_target(local_path)

def build_cyfs_runtime():
    try:
        local_path = fetch_source_code(root, CYFS_URL)
        src_path = os.path.join(local_path, 'src')
        cmd_args = ['cargo', 'build']
        for tool in CYFS_RUNTIMES:
            cmd_args.extend(['-p', tool])
        cmd_args.append('--release')
        execute_cmd(cmd_args, cwd=src_path)
        return local_path
    except Exception as e:
        msg = 'Build CYFS RUNTIME failed, error: %s' % e
        print(msg)
        sys.exit(msg)

def copy_runtime_target(local_path):
    target_bin_path = os.path.join(local_path, 'src', 'target', 'release')
    for bin_name in CYFS_RUNTIMES:
        bin_name += _EXE
        local_bin = os.path.join(target_bin_path, bin_name)
        if not os.path.exists(local_bin):
            msg = 'CYFS runtime bin is not available, please check!'
            print(msg)
            sys.exit(msg)

        for base_path in runtime_pack_path(root):
            make_dir_exist(base_path)
            shutil.copy(local_bin, os.path.join(base_path, bin_name))

def get_tools_dependencies():
    local_path = build_cyfs_tools()
    copy_tools_target(local_path)

def build_cyfs_tools():
    try:
        local_path = fetch_source_code(root, CYFS_URL)
        src_path = os.path.join(local_path, 'src')
        cmd_args = ['cargo', 'build']
        for tool in CYFS_TOOLS:
            cmd_args.extend(['-p', tool])
        cmd_args.append('--release')
        execute_cmd(cmd_args, cwd=src_path)
        return local_path
    except Exception as e:
        print('Build CYFS TOOLS failed, with %s' % e)
        raise

def copy_tools_target(local_path):
    target_bin_path = os.path.join(local_path, 'src', 'target', 'release')

    for bin_name in CYFS_TOOLS:
        bin_name += _EXE
        local_bin = os.path.join(target_bin_path, bin_name)
        if not os.path.exists(local_bin):
            msg = 'CYFS tool bin %s is not available, please check!' % local_bin
            print(msg)
            sys.exit(msg)

        for base_path in tools_pack_path(root):
            make_dir_exist(base_path)
            shutil.copy(local_bin, os.path.join(base_path, bin_name))

def get_cyfs_ts_dependencies():
    local_path = build_cyfs_ts_sdk()
    copy_cyfs_ts_target(local_path)

def build_cyfs_ts_sdk():
    try:
        local_path = fetch_source_code(root, CYFS_TS_SDK_URL)
        execute_cmd([_NPM, 'install'], cwd=local_path)
        execute_cmd([_NPM, 'run', 'build:h5'], cwd=local_path)
        return local_path
    except Exception as e:
        msg = 'Build CYFS TS SDK failed, with %s' % e
        print(msg)
        sys.exit(msg)

def copy_cyfs_ts_target(local_path):
    target_file_path = os.path.join(local_path, 'out')
    bin_name = 'cyfs.js'

    local_bin = os.path.join(target_file_path, bin_name)
    if not os.path.exists(local_bin):
        msg = 'CYFS TS SDK is not available, please check!'
        print(msg)
        sys.exit(msg)

    for pack_path in cyfs_ts_pack_path(root):
        make_dir_exist(pack_path)
        shutil.copy(local_bin, os.path.join(pack_path, bin_name))

def get_web_page_dependencies():
    local_path = build_cyfs_browser_webpage()
    copy_web_page_target(local_path)

def build_cyfs_browser_webpage():
    try:
        local_path = fetch_source_code(root, CYFS_WEB_PAGE_URL)
        execute_cmd([_NPM, 'install'], cwd=local_path)
        execute_cmd([_NPM, 'run', 'build'], cwd=local_path)
        return local_path
    except Exception as e:
        msg = 'Build CYFS BROWSER PAGE failed, with %s' % e
        print(msg)
        sys.exit(msg)

def copy_web_page_target(local_path):
    dir_name = 'www'
    local_pages = os.path.join(local_path, dir_name)
    if not is_dir_exists(local_pages):
        msg = 'CYFS WEB PAGE is not available, please check!'
        print(msg)
        sys.exit(msg)

    for pack_path in web_page_pack_path(root):
        make_file_not_exist(pack_path)
        shutil.copytree(local_pages, pack_path)

def main():
    get_runtime_dependencies()
    get_tools_dependencies()
    get_web_page_dependencies()
    get_cyfs_ts_dependencies()

if __name__ == '__main__':
    try:
        print(''.join(sys.argv))
        sys.exit(main())
    except KeyboardInterrupt:
        sys.stderr.write('interrupted\n')
        sys.exit(1)
