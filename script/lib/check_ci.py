# -*- coding: UTF-8 -*-

import os, sys
sys.path.append(os.path.dirname(__file__))
import platform
import subprocess
import shutil
import zipfile
from common import local_extension_path, static_page_path, ts_sdk_path
from common import src_path, build_target, pack_app_path, local_nft_web_path, local_nft_bin_path
from util import make_dir_exist, is_dir_exists, make_file_not_exist

IS_WIN = platform.system() == 'Windows'
_CP = "COPY" if IS_WIN else "cp"

def download_file(remote_path, local_opath):
    try:
        cmd = [_CP, remote_path, local_opath]
        print(" ".join(cmd))
        subprocess.check_call(cmd)
    except Exception as error:
        print("Copy %s to %s failed, error: %s" %
              (remote_path, local_opath, error))
        raise

def upload_file(local_path, remote_path):
    try:
        cmd = [_CP, local_path, remote_path]
        print(" ".join(cmd))
        subprocess.check_call(cmd)
    except Exception as error:
        print("Copy %s to %sfailed, error: %s" %
              (local_path, remote_path, error))
        raise

class CheckForCIBuild:
    default_branch = "cyfs_branch"
    def __init__(self, root, target_cpu, project_name):
        self._root = root
        self._target_cpu = target_cpu
        self._build_target = build_target(target_cpu, project_name)
        self._cache_version = ""

    @property
    def src_path(self):
        return src_path(self._root)

    @property
    def chrome_path(self):
        return os.path.join(self.src_path, "chrome")

    @property
    def remote_base_path(self):
        try:
            server_url = os.environ.get('CYFS_BROWSER_SRC_PATH')
            if server_url and type(server_url) == str:
                return server_url
        except Exception as e:
            print("Error: Please set the $CYFS_BROWSER_SRC_PATH environment variable")
            raise

    @property
    def remote_extensions_path(self):
        return "%s/%s/%s" % (self.remote_base_path, "chromium_extensions", "Extensions")

    @property
    def remote_nft_web_path(self):
        return "%s/%s/%s/%s" % (self.remote_base_path, "cyfs-nft", "nft-web", "pub")

    @property
    def remote_nft_bin_path(self):
        return "%s/%s/%s/%s" % (self.remote_base_path, "cyfs-nft", "nft-creator", "pub")

    @property
    def local_nft_web_path(self):
        return local_nft_web_path(self._root)

    @property
    def local_nft_bin_path(self):
        return local_nft_bin_path(self._root)

    @property
    def local_extension_path(self):
        return local_extension_path(self._root)

    @property
    def static_page_path(self):
        return static_page_path(self._root, self._target_cpu)

    @property
    def ts_sdk_path(self):
        return ts_sdk_path(self._root, self._target_cpu)

    @property
    def cache_mark_file(self):
        return "%s_commit_id.txt" % (self._target_cpu) if self._target_cpu else "commit_id.txt"

    def download_nft_web_files(self):
        make_file_not_exist(self.local_nft_web_path)
        download_file(self.remote_nft_web_path, self.local_nft_web_path)
        assert os.path.exists(self.local_nft_web_path)

    def download_nft_files(self):
        make_file_not_exist(self.local_nft_bin_path)
        download_file(self.remote_nft_bin_path, self.local_nft_bin_path)
        assert os.path.exists(self.local_nft_bin_path)

    def download_default_extensions(self):
        if not os.path.exists(self.local_extension_path):
            download_file(self.remote_extensions_path,
                          self.local_extension_path)
        assert os.path.exists(self.local_extension_path)

    def get_cache_version(self, mark_pair):
        try:
            (local_mark, remote_mark) = mark_pair
            download_file(remote_mark, local_mark)
            with open(local_mark, "r+") as f:
                self._cache_version = f.read().strip()
        except Exception as e:
            print("Failed to get cache version, error: %s" % e)
        finally:
            return

    def update_cache_version(self, mark_pair, commit_id):
        (local_mark, remote_mark) = mark_pair
        with open(local_mark, "w+") as f:
            f.write(commit_id)
            print("Update build cache version = %s" % (commit_id))
        upload_file(local_mark, remote_mark)

    def check_chromium_branch(self):
        try:
            cmd = ['git', 'symbolic-ref', '--short', 'HEAD']
            git_br = subprocess.check_output(cmd, cwd=self.src_path).decode('ascii').rstrip()
            if git_br != self.default_branch:
                raise Exception("Current branch is not cyfs branch ")
        except Exception as e:
            msg = "Check chromium code branch failed, error: %s" % e
            print(msg)
            sys.exit(msg)

    def get_repo_version(self):
        try:
            cmd = ['git', 'rev-parse', '--short', 'HEAD']
            git_rev = subprocess.check_output(cmd, cwd=self.src_path).decode('ascii').rstrip()
            return git_rev
        except Exception as error:
            print("Could not get repository version, error: %s" % error)
            raise


class CheckForWindowsCIBuild(CheckForCIBuild):
    _product_name = "Cyfs_Browser"
    _code_zip_name = "chromium_code_pc.7z"

    def __init__(self, root, target_cpu, project_name):
        super().__init__(self, root, target_cpu, project_name)

    @property
    def remote_code_path(self):
        return "%s/%s" % (self.remote_base_path, "chromium_code_pc")

    @property
    def remote_cache_path(self):
        return "%s/%s/%s" % (self.remote_base_path, "browser_build_cache", "windows")

    @property
    def install_path(self):
        return os.path.join(self._root, "browser_install")

    @property
    def browser_file_path(self):
        return os.path.join(self.install_path, self._product_name)

    @property
    def cache_version_file(self):
        local_mark = os.path.join(self._root, self.cache_mark_file)
        remote_mark = "%s/%s" % (self.remote_cache_path, self.cache_mark_file)
        return (local_mark, remote_mark)

    def cache_zip_name(self, commit_id):
        return "%s-%s.zip"(self._build_target, commit_id)

    def copy_chromium_source_code(self):
        if os.path.exists(self.src_path):
            print("%s already exists" % (self.src_path))
            return

        print("Chromium code is not exists, need download chromium zip file!")
        local_code_zip = os.path.join(self._root, self._code_zip_name)
        if not os.path.exists(local_code_zip):
            print("Chromium code zip is not exists, need download chromium zip file!")
            remote_code_zip = "%s/%s" % (self.remote_code_path,
                                         self._code_zip_name)
            download_file(remote_code_zip, local_code_zip)

        assert os.path.exists(
            local_code_zip), "Chromium code zip is not available, please check!"

        print("%s already exists" % (local_code_zip))
        with zipfile.ZipFile(local_code_zip, 'r', zipfile.ZIP_DEFLATED, True) as zf:
            zf.extractall(self._root)
        if os.path.exists(src_path):
            print("%s already exists" % (self.src_path))
        else:
            print("%s is not exists" % (self.src_path))
            sys.exit(-1)

    def check_requirements(self):
        assert is_dir_exists(self.static_page_path)
        assert is_dir_exists(self.ts_sdk_path)

        self.copy_chromium_source_code()
        self.download_default_extensions()
        self.download_nft_web_files()
        self.download_nft_files()

        assert is_dir_exists(self.chrome_path)
        self.check_chromium_branch()

    def remote_zip_file(self, zip_name):
        return "%s/%s" % (self.remote_cache_path, zip_name)

    def local_zip_file(self, zip_name):
        return os.path.join(self.install_path, zip_name)

    def update_build_cache_and_version(self):
        commit_id = self.get_repo_version()
        try:
            zip_name = self.cache_zip_name(commit_id)
            print("Zip cache file %s" % zip_name)
            local_zip = self.local_zip_file(zip_name)
            with zipfile.ZipFile(local_zip, "w", zipfile.ZIP_DEFLATED, True) as zf:
                for base, _, filenames in os.walk(self.browser_file_path):
                    fpath = os.path.relpath(base, self.browser_file_path)
                    for filename in filenames:
                        zf.write(os.path.join(base, filename),
                                 os.path.join(fpath, filename))
            if os.path.exists(local_zip):
                remote_zip_file = self.remote_zip_file(zip_name)
                upload_file(local_zip, remote_zip_file)
                self.update_cache_version(self.cache_version_file, commit_id)
        except Exception as e:
            print("Update build cache failed, error: %s" % e)
            raise

    def get_match_build_cache(self):
        ok = False
        try:
            commit_id = self.get_repo_version()
            self.get_cache_version(self.cache_version_file)
            if commit_id != self._cache_version:
                print("There is no match build cache")
                return ok

            print("Current Get match build cache, version = %s" % (commit_id))

            zip_name = self.cache_zip_name(commit_id)
            local_zip = self.local_zip_file(zip_name)
            if not os.path.exists(local_zip):
                remote_zip_file = self.remote_zip_file(zip_name)
                print("Begin download cache %s from %s " %
                      (zip_name, remote_zip_file))
                download_file(remote_zip_file, local_zip)
                print("End download cache %s from %s " %
                      (zip_name, remote_zip_file))

            if os.path.exists(local_zip):
                print("Begin unzip cache %s" % (local_zip))
                with zipfile.ZipFile(local_zip, 'r', zipfile.ZIP_DEFLATED, True) as zf:
                    zf.extractall(self.install_path)
                print("End unzip cache %s" % (local_zip))
            if is_dir_exists(self.browser_file_path):
                ok = True
        except Exception as e:
            print(e)
        finally:
            return ok


class CheckForMacosCIBuild(CheckForCIBuild):
    _app_name = "Cyfs Browser.app"
    _code_zip_name = "chromium_mac_code.tar.gz"

    def __init__(self, root, target_cpu, project_name):
        assert target_cpu, ("Build in Macos, must be provide avaliable target cpu argument")
        super().__init__(self, root, target_cpu, project_name)

    @property
    def remote_code_path(self):
        return "%s/%s" % (self.remote_base_path, "chromium_code_mac")

    @property
    def remote_cache_path(self):
        return "%s/%s/%s" % (self.remote_base_path, "browser_build_cache", "mac")

    @property
    def cache_version_file(self):
        local_mark = os.path.join(self._root, self.cache_mark_file)
        remote_mark = "%s/%s/%s" % (self.remote_cache_path,
                                    self._target_cpu, self.cache_mark_file)
        return (local_mark, remote_mark)

    def cache_zip_name(self, commit_id):
        return "%s-%s.tar.gz"(self._build_target, commit_id)

    def copy_chromium_source_code(self):
        if os.path.exists(self.src_path):
            print("%s already exists" % (self.src_path))
            return

        print("Chromium code is not exists, need download chromium zip file!")
        _local_code_zip = os.path.join(self._root, self._code_zip_name)
        if not os.path.exists(_local_code_zip):
            print("Chromium code zip is not exists, need download chromium zip file!")
            _remote_code_zip = "%s/%s/%s" % (self.remote_cache_path,
                                             self._target_cpu, self._code_zip_name)
            download_file(_remote_code_zip, _local_code_zip)

        if not os.path.exists(_local_code_zip):
            print("Chromium source code is not available, please check!")
            sys.exit(-1)

        print("%s already exists" % (_local_code_zip))
        self.make_unzip(_local_code_zip, self._root)
        if os.path.exists(self.src_path):
            print("%s already exists" % (self.src_path))
        else:
            print("%s is not exists" % (self.src_path))
            sys.exit(-1)

    def update_default_extensions(self):
        extenions_path = os.path.join(
            self.src_path, "chrome", "app", "Extensions")
        make_dir_exist(extenions_path)
        assert os.path.exists(extenions_path)
        shutil.copyfile(self.local_extension_path, extenions_path)

        copys = list(filter(lambda x: x.endswith(".zip"),
                     os.listdir(self.local_extension_path)))
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
        assert is_dir_exists(self.static_page_path)
        assert is_dir_exists(self.ts_sdk_path)

        self.copy_chromium_source_code()
        self.download_default_extensions()
        self.download_nft_web_files()
        self.update_default_extensions()

        assert is_dir_exists(self.chrome_path)
        self.check_chromium_branch()

    def make_unzip(self, tar_file, dst_dir, step=0):
        assert type(step) is int
        try:
            cmd = 'tar xzf %s --strip-components=%s' % (tar_file, step)
            subprocess.check_call(cmd, shell=True, cwd=dst_dir)
        except Exception as error:
            print("Unzip %s failed, error: %s" % (tar_file, error))
            raise

    def make_zip(self, tar_file, source):
        try:
            work_path = os.path.dirname(source)
            path = str(os.path.basename(source)).strip().replace(" ", "\ ")
            cmd = 'tar -czf %s %s' % (tar_file, path)
            subprocess.check_call(cmd, shell=True, cwd=work_path)
        except Exception as error:
            print("Zip %s into %s failed, error: %s" % (path, tar_file, error))
            raise

    def remote_zip_file(self, zip_name):
        return "%s/%s/%s" % (self.remote_cache_path, self._target_cpu, zip_name)

    def local_zip_file(self, zip_name):
        return os.path.join(self._root, "dmg", self._target_cpu, zip_name)

    def update_build_cache_and_version(self):
        commit_id = self.get_repo_version()
        try:
            zip_name = self.cache_zip_name(commit_id)
            print("Zip cache file %s for %s" % (zip_name, self._target_cpu))
            local_zip_file = self.local_zip_file(zip_name)
            make_file_not_exist(local_zip_file)
            app_path = pack_app_path(self._build_target, self._app_name)
            if not is_dir_exists(app_path):
                print(" %s is not exists, can't zip into %s" %
                      (app_path, local_zip_file))
                return
            self.make_zip(local_zip_file, app_path)
            if os.path.exists(local_zip_file):
                remote_zip_file = self.remote_zip_file(zip_name)
                upload_file(local_zip_file, remote_zip_file)
                self.update_cache_version(self.cache_version_file, commit_id)
        except Exception as e:
            print("Update build cache failed, error: %s" % e)
            raise

    def get_match_build_cache(self):
        ok = False
        try:
            commit_id = self.get_repo_version()
            self.get_cache_version(self.cache_version_file)
            if commit_id != self._cache_version:
                print("There is no match build cache")
                return ok

            print("Current Get match build cache, version = %s" % (commit_id))

            zip_name = self.cache_zip_name(commit_id)
            local_zip_file = self.local_zip_file(zip_name)
            if not os.path.exists(local_zip_file):
                print("Begin download cache %s from %s " %
                      (zip_name, remote_zip_file))
                remote_zip_file = self.remote_zip_file(zip_name)
                download_file(remote_zip_file, local_zip_file)
                print("End download cache %s from %s " %
                      (zip_name, remote_zip_file))

            if os.path.exists(local_zip_file):
                print("{} is exists" % (local_zip_file))
                print("Begin unzip cache %s for %s " %
                      (local_zip_file, self._target_cpu))
                self.make_unzip(local_zip_file, os.path.dirname(local_zip_file))
                print("End unzip cache %s for %s " %
                      (local_zip_file, self._target_cpu))
                app_dir = pack_app_path(self._target_cpu, self._app_name)
                if os.path.exists(app_dir):
                    print("Get the match build cache success, target_cpu = %s" % (
                        self._target_cpu))
                    ok = True
        except Exception as e:
            print(e)
        finally:
            return ok


CHECK_TYPE_MAP = {
    'Windows':   CheckForWindowsCIBuild,
    'Darwin':     CheckForMacosCIBuild
}


def CheckFactory(type_name, root, target_cpu, project_name, version):
    """Factory to build Checkout class instances."""
    class_ = CHECK_TYPE_MAP.get(type_name)
    if not class_:
        raise KeyError('unrecognized checkout type: %s' % type_name)
    return class_(root, target_cpu, project_name, version)
