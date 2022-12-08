# -*- coding: UTF-8 -*-

import os
import sys
import shutil
import subprocess
import platform
import argparse
from util import is_dir_exists, make_dir_exist, make_file_not_exist
from common import cyfs_runtime_path, cyfs_tools_path, ts_sdk_path, static_page_path

# root = os.path.normpath(os.path.join(
#     os.path.dirname(os.path.abspath(__file__)), os.pardir, os.pardir))

IS_WIN = platform.system() == 'Windows'
_NPM = 'npm.cmd' if IS_WIN else 'npm'
_EXE = '.exe' if IS_WIN else ''
DEFAULT_CPU = "X86"

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

def get_current_branch_name(local_path):
    try:
        cmd = ['git', 'symbolic-ref', '--short', 'HEAD']
        return subprocess.check_output(cmd, cwd=local_path).decode('ascii').rstrip()
    except Exception as e:
        print('Execute cmd %s failed: %s' % (' '.join(cmd), e))
        return None

def git_clone_repo(repo_url, local_path, branch_name):
    try:
        cmd = ['git', 'clone', '-b', branch_name, repo_url]
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

def git_checkout(local_path, branch_name):
    try:
        cmd = ['git', 'checkout', branch_name ]
        execute_cmd(cmd, cwd=local_path)
    except Exception as e:
        print('Execute cmd %s failed: %s' % (' '.join(cmd), e))
        raise

def fetch_source_code(root, repo_url, branch_name, local_repo_name=None):
    try:
        repo_name = local_repo_name or get_repo_name_from_url(repo_url)
        local_path = os.path.join(root, repo_name)
        if not os.path.exists(os.path.join(local_path, '.git')):
            git_clone_repo(repo_url, root, branch_name)
        else:
            git_reset_repo(local_path)
            current_branch_name = get_current_branch_name(local_path)
            if current_branch_name == None or current_branch_name != branch_name:
                git_checkout(local_path, branch_name)
            git_pull_repo(repo_url, local_path)
        return local_path
    except Exception as e:
        msg = 'Get %s failed: %s' % (repo_url, e)
        print(msg)
        sys.exit(msg)

def get_runtime_dependencies(root, channel, target_cpu, version):
    local_path = build_cyfs_runtime(root, channel, version)
    copy_runtime_target(root, local_path, target_cpu)

def get_brnach_by_channel(channel):
    assert channel in ['nightly', 'beta']
    channel_branch_map = {
        'nightly': 'main',
        'beta': 'beta',
    }
    return channel_branch_map[channel]

def build_cyfs_runtime(root, channel, version):
    branch_name = get_brnach_by_channel(channel)
    os.environ['CHANNEL'] = channel
    os.environ['VERSION'] = version
    try:
        local_path = fetch_source_code(root, CYFS_URL, branch_name)
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

def copy_runtime_target(root, local_path, target_cpu):
    target_bin_path = os.path.join(local_path, 'src', 'target', 'release')
    for bin_name in CYFS_RUNTIMES:
        bin_name += _EXE
        local_bin = os.path.join(target_bin_path, bin_name)
        if not os.path.exists(local_bin):
            msg = 'CYFS runtime bin is not available, please check!'
            print(msg)
            sys.exit(msg)

        base_path = cyfs_runtime_path(root, target_cpu)
        make_dir_exist(base_path)
        shutil.copy(local_bin, os.path.join(base_path, bin_name))

def get_tools_dependencies(root, channel, target_cpu, version):
    local_path = build_cyfs_tools(root, channel, version)
    copy_tools_target(root, local_path, target_cpu)

def build_cyfs_tools(root, channel, version):
    branch_name = get_brnach_by_channel(channel)
    os.environ['CHANNEL'] = channel
    os.environ['VERSION'] = version
    try:
        local_path = fetch_source_code(root, CYFS_URL, branch_name)
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

def copy_tools_target(root, local_path, target_cpu):
    target_bin_path = os.path.join(local_path, 'src', 'target', 'release')

    for bin_name in CYFS_TOOLS:
        bin_name += _EXE
        local_bin = os.path.join(target_bin_path, bin_name)
        if not os.path.exists(local_bin):
            msg = 'CYFS tool bin %s is not available, please check!' % local_bin
            print(msg)
            sys.exit(msg)

        base_path = cyfs_tools_path(root, target_cpu)
        make_dir_exist(base_path)
        shutil.copy(local_bin, os.path.join(base_path, bin_name))

def get_cyfs_ts_dependencies(root, channel, target_cpu, version):
    local_path = build_cyfs_ts_sdk(root, channel, version)
    copy_cyfs_ts_target(root, local_path, target_cpu)

def build_cyfs_ts_sdk(root, channel, version):
    channel_branch_map = {
        'nightly': 'master',
        'beta': 'beta',
    }
    branch_name = channel_branch_map[channel]
    try:
        local_path = fetch_source_code(root, CYFS_TS_SDK_URL, branch_name)
        execute_cmd([_NPM, 'install'], cwd=local_path)
        execute_cmd([_NPM, 'run', 'build','h5', channel], cwd=local_path)
        return local_path
    except Exception as e:
        msg = 'Build CYFS TS SDK failed, with %s' % e
        print(msg)
        sys.exit(msg)

def copy_cyfs_ts_target(root, local_path, target_cpu):
    target_file_path = os.path.join(local_path, 'out')
    bin_name = 'cyfs.js'

    local_bin = os.path.join(target_file_path, bin_name)
    if not os.path.exists(local_bin):
        msg = 'CYFS TS SDK is not available, please check!'
        print(msg)
        sys.exit(msg)

    pack_path = ts_sdk_path(root, target_cpu)
    make_dir_exist(pack_path)
    shutil.copy(local_bin, os.path.join(pack_path, bin_name))

def get_web_page_dependencies(root, channel, target_cpu, version):
    local_path = build_cyfs_browser_webpage(root, channel, version)
    copy_web_page_target(root, local_path, target_cpu)

def build_cyfs_browser_webpage(root, channel, version):
    branch_name = get_brnach_by_channel(channel)
    try:
        local_path = fetch_source_code(root, CYFS_WEB_PAGE_URL, branch_name)
        execute_cmd([_NPM, 'install'], cwd=local_path)
        execute_cmd([_NPM, 'run', 'build'], cwd=local_path)
        return local_path
    except Exception as e:
        msg = 'Build BROWSER PAGE failed, with %s' % e
        print(msg)
        sys.exit(msg)

def copy_web_page_target(root, local_path, target_cpu):
    dir_name = 'www'
    local_pages = os.path.join(local_path, dir_name)
    if not is_dir_exists(local_pages):
        msg = 'CYFS WEB PAGE is not available, please check!'
        print(msg)
        sys.exit(msg)

    pack_path = static_page_path(root, target_cpu)
    make_file_not_exist(pack_path)
    shutil.copytree(local_pages, pack_path)

def prepare_cyfs_components(root, channel, target_cpu, version):
    get_runtime_dependencies(root, channel, target_cpu, version)
    get_tools_dependencies(root, channel, target_cpu, version)
    get_web_page_dependencies(root, channel, target_cpu, version)
    get_cyfs_ts_dependencies(root, channel, target_cpu, version)


def _parse_args(args):
    root = os.path.normpath(os.path.join(
            os.path.dirname(os.path.abspath(__file__)), os.pardir, os.pardir))
    parser = argparse.ArgumentParser()
    parser.add_argument("--root",
                    help="The components build path",
                    type=str,
                    default=root,
                    required=False)
    parser.add_argument("--version",
                    help="The build version.",
                    type=str,
                    default='0',
                    required=False)
    parser.add_argument("--channel",
                    help="The cyfs channel, like nightly and beta",
                    type=str,
                    default='nightly',
                    required=False)
    parser.add_argument("--target-cpu",
                    help="The target cpu, like X86 and ARM",
                    type=str,
                    default=DEFAULT_CPU,
                    required=False)
    opt = parser.parse_args(args)
    return opt


def main(args):
    opt = _parse_args(args)
    channel = opt.channel if opt.channel else 'nightly'
    assert channel in [ 'nightly', 'beta']
    version = opt.version if opt.version else '0'
    prepare_cyfs_components(opt.root, channel, opt.target_cpu,  version)


if __name__ == '__main__':
    try:
        print(''.join(sys.argv))
        sys.exit(main(sys.argv[1:]))
    except KeyboardInterrupt:
        sys.stderr.write('interrupted\n')
        sys.exit(1)
