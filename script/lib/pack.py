
import os, sys
sys.path.append(os.path.dirname(__file__))

from logging import exception
import subprocess
import shutil
from util import is_dir_exists, make_dir_exist, copy_dir
from common import (
    dmg_dir, 
    package_path, 
    pkg_dir, 
    build_application_path, 
    package_application_path, 
    build_target_dir
)


class Package:
    def __init__(self, root, target_cpu, project_name, version, app):
        self._root = root
        self._target_cpu = target_cpu
        self._project_name = project_name
        self._version = version
        self._app = app

        self._base_path = dmg_dir(self._root, self._target_cpu)
        self._package_path = package_path(self._root, self._target_cpu)
        self._pkg_build_dir = pkg_dir(self._root, self._target_cpu)
        make_dir_exist(self._pkg_build_dir)


    def copy_app_for_package(self):
        target_dir = build_target_dir(self._target_cpu, self._project_name)
        src = build_application_path(self._root, target_dir, self._app)
        dst = package_application_path(self._root, self._target_cpu, self._app)
        assert not os.path.exists(dst)
        if not is_dir_exists(src):
            print("Generator application %s failed" %src)
            sys.exit(-1)

        print("Copy application %s to %s" %(src, dst))
        copy_dir(src, dst)
        if not is_dir_exists(dst):
            print("%s is not available, please check!" %dst)
            sys.exit(-1)


    def check_requirements(self):
        self.copy_app_for_package()
        os.chdir(self._base_path)
        if os.path.exists("www") and os.path.exists("cyfs-runtime"):
            return
        print("Missing some components, please check!")
        sys.exit(-1)


    def build_pkg(self):
        pkgproj = os.path.join(self._package_path, "cyfs_browser_package.pkgproj")
        pkg = os.path.join(self._pkg_build_dir, "cyfs_browser_package.pkg")
        cmd = "/usr/local/bin/packagesbuild --package-version %s %s" %(self._version, pkgproj)
        print("-> Begin build pkg, cmd = %s" % cmd)
        self.execute_cmd(cmd)
        print("<- End build pkg")
        if not os.path.exists(pkg):
            sys.exit(-1)


    def build_dmg(self):
        self.copy_uninstall_script()
        dmg_file = "cyfs-browser-installer-%s.dmg" %(self._version)
        cmd = "hdiutil create -fs HFS+ -srcfolder %s -volname cyfs-browser-installer %s" %(self._pkg_build_dir, dmg_file)
        print("-> Begin build dmg , cmd = %s" % cmd)
        self.execute_cmd(cmd)
        print("<- End build dmg")
        if not os.path.exists(dmg_file):
            sys.exit(-1)


    def copy_uninstall_script(self):
        try:
            src = os.path.join(self._package_path, "uninstall.sh")
            dst = os.path.join(self._pkg_build_dir, "uninstall.sh")
            shutil.copyfile(src, dst)
            cmd = "chmod %s %s" %("775", dst)
            self.execute_cmd(cmd)
        finally:
            return


    def execute_cmd(self, cmd, log_file=None):
        try:
            subprocess.check_call(cmd, shell=True, stdout=log_file, stderr=log_file)
        except exception as error:
            print("Execute command: %s failed, error: %s" %(cmd, error))
            raise


    def pack(self):
        self.check_requirements()
        self.build_pkg()
        self.build_dmg()


def make_installer(root, target_cpu, project_name, version, app):
    package = Package(root, target_cpu, project_name, version, app)
    package.pack()


def main():
    # root = os.path.join(os.path.abspath(os.__file__), os.pardir, os.pardir)
    root = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, os.pardir))

    make_installer(root, "ARM", "Browser", "200", "Cyfs Browser.app")

if __name__ == "__main__":
    main()
