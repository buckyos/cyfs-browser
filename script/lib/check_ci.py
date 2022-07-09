# -*- coding: UTF-8 -*-

import os, sys
import shutil
sys.path.append(os.path.dirname(__file__))
from common import (
    make_file_not_exist,
    get_code_zip_name,
    remote_code_zip,
    remote_extensions_path,
    remote_nft_web_path,
    local_extension_path,
    local_code_zip,
    local_nft_web_path,
    static_page_path,
    pkg_dir,
    dmg_dir,
    package_application_path,
    src_path,
    ts_sdk_path,
    remote_base_cache_path,
    build_target_dir,
    cache_zip_name,
    cache_mark_file,
    local_cache_mark_file,
    remote_cache_mark_file,
    remote_cache_zip_file,
    local_cache_zip_file,
    build_application_path,
    package_application_path
)
from util import (
    download_file,
    upload_file,
    make_dir_exist,
    delete_special_suffix_file,
    make_unzip,
    upload_file,
    get_repo_version,
    make_zip,
    is_dir_exists,
)

class CheckForCIBuild:
    """ Check requirement for CI build"""
    def __init__(self, root, target_cpu, project_name, app_name):
        self._package_suffixs = [".pkg", ".dmg"]
        self._root = root
        self._project_name = project_name
        self._target_cpu = target_cpu
        self._app_name = app_name

        self._src_path = src_path(self._root)
        self._static_page_path = static_page_path(self._root, self._target_cpu)
        self._ts_sdk_path = ts_sdk_path(self._root, self._target_cpu)

        self._code_zip = get_code_zip_name()

        self._remote_base_path = os.environ.get('CYFS_BROWSER_SRC_PATH')
        assert self._remote_base_path

        self._commit_id_file = cache_mark_file(target_cpu)

        self._build_dir = build_target_dir(self._target_cpu, self._project_name)


    def update_nft_web_files(self):
        try:
            os.chdir(self._root)
            _local_nft_web_path = local_nft_web_path(self._root)
            make_file_not_exist(_local_nft_web_path)
            _remote_nft_web_path = remote_nft_web_path(self._remote_base_path)
            download_file(_remote_nft_web_path, _local_nft_web_path)
            if os.path.exists(_local_nft_web_path):
                print("Download nft web files success")

            base_dst = self._static_page_path
            # make_file_not_exist(os.path.join(base_dst, "nft_tool"))
            assert os.path.exists(base_dst) and os.path.isdir(base_dst)
            src_dir = _local_nft_web_path
            for (root, _, files) in os.walk(src_dir):
                for file in files:
                    src_path = os.path.abspath(os.path.join(root, file))
                    dst_path = os.path.join(base_dst, os.path.relpath(src_path, src_dir))
                    make_dir_exist(os.path.dirname(dst_path))
                    print("{} => {}".format(src_path, dst_path))
                    shutil.copy(src_path, dst_path)
            print("Update nft web files")
        except Exception as e:
            print("Update nft web files failed, error %s" % e)


    def clean_trash_package_file(self):
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


    def copy_chromium_source_code(self):
        if not os.path.exists(self._src_path):
            _local_code_zip = local_code_zip(self._root, self._code_zip)
            if not os.path.exists(_local_code_zip):
                print("Chromium code is not exists, need download chromium zip file!")
                _remote_code_zip = remote_code_zip(self._remote_base_path, self._code_zip)
                download_file(_remote_code_zip, _local_code_zip)
            if os.path.exists(_local_code_zip):
                print("%s already exists" %(_local_code_zip))
                make_unzip(_local_code_zip, self._root)
                if os.path.exists(src_path):
                    print("%s already exists" %(self._src_path))
                else:
                    print("%s is not exists" %(self._src_path))
                    sys.exit(-1)
        else:
            print("%s already exists" %(self._src_path))


    def update_default_extensions(self):
        os.chdir(self._root)
        local_path = local_extension_path(self._root)
        if not os.path.exists(local_path):
            remote_extensions = remote_extensions_path(self._remote_base_path)
            download_file(remote_extensions, local_path)
        assert os.path.exists(local_path)

        extenions_path = os.path.join(self._src_path, "chrome", "app", "Extensions")
        # make_dir_exist(src_extenions_path)
        assert os.path.exists(extenions_path)
        upload_file(local_path, extenions_path)

        copys = list(filter(lambda x: x.endswith(".zip"), os.listdir(local_path)))
        copys.append("readme.md")

        gni_file = os.path.join(extenions_path, "cyfs_extension.gni")
        with open(gni_file, "w") as f:
            f.write("cyfs_default_extenions = [\n")
            # for line in [ "readme.md", "metamask-chrome-10.9.3.zip"]:
            for file_name in copys:
                f.write("  \"")
                f.write(file_name)
                f.write("\",\n")
            f.write("]\n\n")


    def check_requirements(self):
        if not is_dir_exists(self._static_page_path):
            print("CYFS PAHE file %s is not available, please check!!" % self._static_page_path)
            sys.exit(-1)

        if not is_dir_exists(self._ts_sdk_path):
            print("CYFS TS SDK file %s is not available, please check!!" % self._ts_sdk_path)
            sys.exit(-1)

        ## to do [check runtime and tools]


        self.copy_chromium_source_code()
        self.update_default_extensions()
        self.update_nft_web_files()


        if not is_dir_exists(os.path.join(self._src_path, "chrome")):
            print("Chromium source code is not available, please check!")
            sys.exit(-1)



    ### update or download last build cache
    def remote_zip_file(self, zip_name):
        assert self._remote_base_path is not None
        base_cache_path = remote_base_cache_path(self._remote_base_path)
        return remote_cache_zip_file(base_cache_path, self._target_cpu, zip_name)


    def local_zip_file(self, zip_name):
        return local_cache_zip_file(self._root, self._target_cpu,  zip_name)


    def get_local_and_remote_cache_version_file(self):
        assert self._remote_base_path is not None
        local_mark = local_cache_mark_file(self._root, self._target_cpu, self._commit_id_file)
        base_cache_path = remote_base_cache_path(self._remote_base_path)
        remote_mark = remote_cache_mark_file(base_cache_path, self._target_cpu, self._commit_id_file)
        return [local_mark, remote_mark]


    def get_last_cache_version(self):
        [local_mark, remote_mark] = self.get_local_and_remote_cache_version_file()
        download_file(remote_mark, local_mark)
        last_commit_id = ""
        with open(local_mark, "r+") as f:
            last_commit_id = f.read().strip()
            f.close()
        return last_commit_id


    def update_last_cache_version(self, commit_id):
        [local_mark, remote_mark] = self.get_local_and_remote_cache_version_file()
        with open(local_mark, "w+") as f:
            f.write(commit_id)
            print("Update lastest build cache id = %s" %(commit_id))
            f.close()
        upload_file(local_mark, remote_mark)


    def update_build_cache_and_version(self):
        commit_id = get_repo_version(self._root)
        try:
            zip_name = cache_zip_name(self._build_dir, commit_id)
            print("Zip cache file %s for %s" %(zip_name, self._target_cpu))
            local_zip_file = self.local_zip_file(zip_name)

            app_path = build_application_path(self._build_dir, self._app_name)
            if not is_dir_exists(app_path):
                print(" %s is not exists, can't zip into %s" %(app_path, local_zip_file))
                return
            make_zip(local_zip_file, app_path)
            if os.path.exists(local_zip_file):
                remote_zip_file = self.remote_zip_file(zip_name)
                upload_file(local_zip_file, remote_zip_file)
                self.update_last_cache_version(commit_id)
        except Exception as e:
            print("Update build cache failed, error: %s" % e)
            raise


    def get_match_build_cache(self):
        try:
            commit_id = self.get_repo_version()
            last_commit_id = self.get_last_cache_version()
            print('Local repo commit id = %s, remote cache commit id = %s' %(commit_id, last_commit_id))

            if commit_id != last_commit_id:
                return False

            print("Current commit_id equal remote cache file id, commit_id = %s" %(commit_id))

            zip_name = cache_zip_name(self._build_dir, last_commit_id)
            local_zip_file = self.local_zip_file(zip_name)
            if not os.path.exists(local_zip_file):
                print("Begin download cache %s from %s " %(zip_name, remote_zip_file))
                remote_zip_file = self.remote_zip_file(zip_name)
                download_file(remote_zip_file, local_zip_file)
                print("End download cache %s from %s " %(zip_name, remote_zip_file))


            if os.path.exists(local_zip_file):
                print("{} is exists" %(local_zip_file))
                print("Begin unzip cache %s for %s " %(local_zip_file, self._target_cpu))
                make_unzip(local_zip_file, os.path.dirname(local_zip_file))
                print("End unzip cache %s for %s " %(local_zip_file, self._target_cpu))
                app_dir = package_application_path(self._target_cpu, self._app_name)
                if os.path.exists(app_dir):
                    print("Get the match build cache success, target_cpu = %s" %(self._target_cpu))
                    return True

        except Exception as e:
            print(e)
            return False




