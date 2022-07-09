# -*- coding: UTF-8 -*-

import os, sys, platform
import shutil

sys.path.append(os.path.dirname(__file__))
from common import (
    static_page_path,
    src_path,
    ts_sdk_path,
    pkg_dir,
    dmg_dir,
    package_application_path
)
from util import is_dir_exists, delete_special_suffix_file

class CheckForBuild:
    def __init__(self, root, target_cpu, app_name):
        self._package_suffixs = [".pkg", ".dmg"]
        self._root = root
        self._target_cpu = target_cpu

        self._app_name = app_name

        self._src_path = src_path(self._root)
        self._static_page_path = static_page_path(self._root, self._target_cpu)
        self._ts_sdk_path = ts_sdk_path(self._root, self._target_cpu)


    def check_requirements(self):
        if not is_dir_exists(self._static_page_path):
            print("CYFS PAHE file %s is not available, please check!!" % self._static_page_path)
            sys.exit(-1)

        if not is_dir_exists(self._ts_sdk_path):
            print("CYFS TS SDK file %s is not available, please check!!" % self._ts_sdk_path)
            sys.exit(-1)

        ## to do [check runtime and tools]

        if not is_dir_exists(os.path.join(self._src_path, "chrome")):
            print("Chromium source code is not available, please check!")
            sys.exit(-1)
            

    def clean_trash_package_file(self):
        if platform.system() == "Darwin":
            print("Begin clean trash package file")
            _pkg_dir = pkg_dir(self._root, self._target_cpu)
            _dmg_dir = dmg_dir(self._root, self._target_cpu)
            delete_dir = []
            if os.path.exists(_pkg_dir):
                delete_dir.append(_pkg_dir)
            if os.path.exists(_dmg_dir):
                delete_dir.append(_dmg_dir)
            if delete_dir:
                delete_special_suffix_file(delete_dir, self._package_suffixs)
            print("Delete pkg and dmg file")
            app_path = package_application_path(self._root, self._target_cpu, self._app_name)
            print("Delete %s" %(app_path))
            if os.path.exists(app_path):
                shutil.rmtree(app_path)
            print("End clean trash package file")
