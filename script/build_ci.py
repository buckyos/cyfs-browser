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


root = os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), os.pardir))

IS_MAC = platform.system() == "Darwin"
IS_WIN = platform.system() == "Windows"

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


def main(args):
    opt = _parse_args(args)
    current_os = platform.system()
    assert current_os in ['Windows', 'Darwin']
    check = CheckFactory(current_os, root, opt.target_cpu, opt.project_name)
    is_match_cache = check.get_match_build_cache()
    if not is_match_cache:
        print("There have not match build cache, so need compile")
        check.check_requirements()
        ### patch
        GitPatcher.update(root)
        check.update_default_extensions()
        ## use chromium gn and ninja tool compile source code
        build_browser(src_path(root), opt.project_name, opt.target_cpu)
    else:
        print("Get match build cache, so not need compile")

    ### pack
    make_installer(root, opt.target_cpu, opt.project_name, opt.version)
    if not is_match_cache:
        check.update_build_cache_and_version()

    print("Build finished!!")


if __name__ == "__main__":
    try:
        print(str(sys.argv))
        sys.exit(main(sys.argv[1:]))
    except KeyboardInterrupt:
        sys.stderr.write("interrupted\n")
        sys.exit(1)
