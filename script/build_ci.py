# -*- coding: UTF-8 -*-

import os
import sys
import argparse
import platform


from lib.check_ci import CheckForCIBuild
from lib.patch import apply_patchs
from lib.ninja import build_browser
from lib.pack import make_installer
from lib.common import (app_name, src_path)


root = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir))


def _parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-name", help="The project name.", type=str, required=True)
    parser.add_argument("--version", help="The build version.", type=str, required=True)
    parser.add_argument("--target-cpu", help="The target cpu, like X86 and ARM", type=str, required=True)
    # parser.add_argument("--local-resource-path", help="local resource path like dtool", type=str)
    opt = parser.parse_args(args)
    if opt.project_name == None or opt.project_name == "":
        print("Please provide current project name!!")
        sys.exit(-1)

    if opt.version == None or opt.version == "":
        print("Please provide current build version!!")
        sys.exit(-1)

    if opt.target_cpu == None or opt.target_cpu == "":
        print("Please provide current target cpu, like X86 and ARM!!")
        sys.exit(-1)

    if platform.system() == "Darwin":
        assert opt.target_cpu in [ "X86", "ARM" ]

    return opt


def main(args):
    opt = _parse_args(args)
    app = app_name()
    check = CheckForCIBuild(root, opt.target_cpu, opt.project_name, app)
    check.clean_trash_package_file()
    if not check.get_match_build_cache():
        check.check_requirements()
        ### patch => ninja
        apply_patchs(root)
        ### use chromium gn and ninja tool compile source code
        build_browser(src_path(root), opt.target_cpu, opt.project_name, app)
        ### if is_ci is true, then we need update build cache to LAN shared directory
        check.update_build_cache_and_version()
    else:
        print("Get match build cache, so not need compile")


    ### pack
    make_installer(root, opt.target_cpu, opt.project_name, opt.version, app)

    print("Build finished!!")


if __name__ == "__main__":
    try:
        print(str(sys.argv))
        sys.exit(main(sys.argv[1:]))
    except KeyboardInterrupt:
        sys.stderr.write("interrupted\n")
        sys.exit(1)
