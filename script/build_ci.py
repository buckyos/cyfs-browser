# -*- coding: UTF-8 -*-

import os
import sys
import argparse
import platform


from lib.check_ci import CheckFactory
from lib.ninja import build_browser
from lib.pack_ci import make_installer
from lib.common import src_path, MAC_CPUS
from lib.git_patch import GitPatcher

version_template = '''CYFS_MAJOR=%s
CYFS_MINOR=%s
CYFS_NIGHTLY=%s
CYFS_BUILD=%s
'''

IS_MAC = platform.system() == "Darwin"
IS_WIN = platform.system() == "Windows"
DEFAULT_CPU = "X86"

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
                        help="The target cpu, like X86 and ARM",
                        type=str,
                        default=DEFAULT_CPU,
                        required=False)
    parser.add_argument("--channel",
                    help="The cyfs channel, like nightly and beta",
                    type=str,
                    default='nightly',
                    required=False)
    opt = parser.parse_args(args)

    assert opt.project_name.strip()
    assert opt.version.strip()
    if IS_MAC:
        assert opt.target_cpu.strip()
        assert opt.target_cpu in MAC_CPUS

    return opt

def set_env_variables():
    print('Begin setting environment variables')
    if IS_WIN:
        depot_tool_path = os.environ.get('DEPOT_TOOL_PATH')
        print('depot_tool_path = %s' % depot_tool_path)
        assert os.path.exists(depot_tool_path), 'Please provide [DEPOT_TOOL_PATH] env variable'
        os.environ['PATH'] = depot_tool_path + os.path.pathsep + os.environ['PATH']
        os.environ['DEPOT_TOOLS_WIN_TOOLCHAIN']="0"
        print('current path = %s ' % os.environ['path'])
    else:
        pass
    print('End setting environment variables')

def update_product_version(root, channel, version):
    channel_number = 1 if channel == 'beta' else 0
    product_version_file = os.path.join(root, "src", "chrome", "CYFS_VERSION")
    with open(product_version_file, 'w') as f:
        f.write(version_template %('1', '0', channel_number, version))

def main(args):
    root = os.path.normpath(os.path.join(
            os.path.dirname(os.path.abspath(__file__)), os.pardir))
    opt = _parse_args(args)
    current_os = platform.system()
    assert current_os in ['Windows', 'Darwin']
    set_env_variables()

    check = CheckFactory(current_os, root, opt.target_cpu, opt.project_name, opt.channel)
    check.check_requirements()

    reuse_last_build = False
    if current_os == 'Windows':
        reuse_last_build = check.get_match_build_cache()
    if not reuse_last_build:
        check.check_browser_src_files()
        ### patch
        GitPatcher.update(root)
        update_product_version(root, opt.channel, opt.version)

        check.update_default_extensions()
        # use chromium gn and ninja tool compile source code
        build_browser(src_path(root), opt.project_name, opt.target_cpu)
    else:
        print('Now can use last build object')

    ### pack
    make_installer(root, opt.target_cpu, opt.project_name, opt.version, opt.channel, reuse_last_build)
    if not reuse_last_build and current_os == 'Windows':
        check.update_build_cache_and_version()

    print("Build finished!!")


if __name__ == "__main__":
    try:
        print(str(sys.argv))
        sys.exit(main(sys.argv[1:]))
    except KeyboardInterrupt:
        sys.stderr.write("interrupted\n")
        sys.exit(1)
