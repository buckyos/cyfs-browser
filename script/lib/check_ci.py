# -*- coding: UTF-8 -*-

import os, sys, json
import hashlib
sys.path.append(os.path.dirname(__file__))
import subprocess
import shutil
import zipfile
import urllib.request
from common import local_extension_path, static_page_path, ts_sdk_path, application_name, code_zip_name
from common import src_path, build_target, pack_app_path, build_app_path, pack_base_path
from common import remote_extensions_path, remote_cache_path, remote_code_path
from util import make_dir_exist, is_dir_exists, make_file_not_exist, clean_dir

def download_file(remote_path, local_path, is_dir=False):
    try:
        print('Begin Download file %s to %s' % (remote_path, local_path))
        if is_dir:
            shutil.copytree(remote_path, local_path, dirs_exist_ok=True)
        else:
            shutil.copy(remote_path, local_path)
        print('End Download file %s' % remote_path)
        assert os.path.exists(local_path), ('%s is not available' % local_path)
    except Exception as error:
        print("Download  %s failed, error: %s" % (remote_path, error))
        raise

def upload_file(local_path, remote_path, is_dir=False):
    try:
        os.makedirs(os.path.dirname(remote_path), exist_ok=True)
        print('Begin Upload file %s to %s' % (local_path, remote_path))
        if is_dir:
            shutil.copytree(local_path, remote_path, dirs_exist_ok=True)
        else:
            shutil.copy(local_path, remote_path)
        print('End Upload file %s' % local_path)
        assert os.path.exists(remote_path)
    except Exception as error:
        print("Upload %s failed, error: %s" % (local_path, error))
        raise

def get_crx_info_by_type(base_url, type):
    try:
        get_info_url = "%s/getextensioninfobytype/%s" % (base_url, type)
        print('get_crx_info_by_type %s' %get_info_url)
        with urllib.request.urlopen(get_info_url) as f:
            data = f.read().decode('utf-8')
            json_data = json.loads(data)
            return json_data['crx_infos']
    except Exception as e:
        raise 'get crx info by type failed, error: %s' %e

def download_crx_file(download_url, crx_file):
    if os.path.exists(crx_file):
        os.unlink(crx_file)
    response = urllib.request.urlopen(download_url)
    CHUNK = 16 * 1024
    with open(crx_file, 'wb') as fp:
        while True:
            chunk = response.read(CHUNK)
            if not chunk:
                break
            fp.write(chunk)

def check_md5(file_name, md5_hash):
    with open(file_name, 'rb') as fp:
        data = fp.read()
        actual_hash= hashlib.md5(data).hexdigest()
        if actual_hash != md5_hash:
            print('Download file %s is not match md5 %s'%(file_name, md5_hash))
            return False
    return True
       
def download_crx(base_path, type):
    if not 'BASE_EXTENSION_URL' in os.environ:
        print('No need download crx from remote server')
        return False;

    base_url = os.environ.get('BASE_EXTENSION_URL')
    print('Download crx from %s' % base_url)
    json_data = {}
    try:
        crx_infos = get_crx_info_by_type(base_url, type)
        for item in crx_infos:
            print('item - %s' %item)
            crx_name = item['crx_name']
            crx_file = os.path.join(base_path, crx_name)
            download_url = "%s/downloadextension/%s" %(base_url, crx_name)
            download_crx_file(download_url, crx_file)
            if os.path.exists(crx_file):
                if not check_md5(crx_file, item['md5']):
                    raise Exception('%s Download file failed' % download_url)
                print('Download %s success' %(crx_name))
                json_data[crx_name.split('.')[0]] = { "default_version": item["version"]}
            else:
                print('Download %s failed' %(crx_name))
    except Exception as e:
        print('Download crx from remote crx server failed, error %s' %e)
        raise e
    
    print('Generate default extension info file')
    json_file = os.path.join(base_path, "default_extensions.json");
    with open(json_file, 'w', encoding='utf-8') as fw:
        json.dump(json_data, fw, indent=4, ensure_ascii=False)
    
    return True


class CheckForCIBuild:
    default_branch = "cyfs_branch"
    def __init__(self, root, target_cpu, project_name, channel):
        self._root = root
        self._channel = channel
        self._target_cpu = target_cpu
        self._build_target = build_target(target_cpu, project_name)
        self._cache_version = ""
        base_url = os.environ.get('CYFS_BROWSER_SRC_PATH')
        path = os.path.normpath(base_url)
        print('CYFS_BROWSER_SRC_PATH = %s' % path)
        assert os.path.exists(path), 'Must to set CYFS_BROWSER_SRC_PATH'
        self._remote_base_path = path

    @property
    def src_path(self):
        return src_path(self._root)

    @property
    def install_path(self):
        return pack_base_path(self._root, self._target_cpu)

    @property
    def chrome_path(self):
        return os.path.join(self.src_path, "chrome")

    @property
    def remote_base_path(self):
        return self._remote_base_path

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
        return "%s_commit_id.txt" % (self._target_cpu)

    def download_default_extensions(self):
        clean_dir(self.local_extension_path)
        if download_crx(self.local_extension_path, self._channel) == False:
            download_file(remote_extensions_path(self.remote_base_path, self._channel), self.local_extension_path, True)
        old_extensions = [ os.path.join(self.local_extension_path, x) 
            for x in os.listdir(self.local_extension_path) if x.endswith('.zip') ]
        for filename in old_extensions:
            os.remove(filename)


    def update_default_extensions(self):
        pass

    def get_cache_version(self, mark_tuple):
        try:
            download_file(mark_tuple[1], mark_tuple[0])
            with open(mark_tuple[0], "r+") as f:
                self._cache_version = f.read().strip()
        except Exception as e:
            print("Failed to get cache version, error: %s" % e)
        finally:
            return

    def update_cache_version(self, mark_tuple, commit_id):
        with open(mark_tuple[0], "w+") as f:
            f.write(commit_id)
            print("Update build cache version = %s" % (commit_id))
        upload_file(mark_tuple[0], mark_tuple[1])

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
            git_rev = subprocess.check_output(cmd, cwd=self._root).decode('ascii').rstrip()
            return git_rev
        except Exception as error:
            print("Could not get repository version, error: %s" % error)
            raise

class CheckForWindowsCIBuild(CheckForCIBuild):

    @property
    def browser_file_path(self):
        return os.path.join(self.install_path, "mini_installer.exe")

    @property
    def cache_version_file(self):
        local_mark = os.path.join(self.install_path, self.cache_mark_file)
        remote_mark = os.path.join(remote_cache_path(self.remote_base_path), self._target_cpu, self.cache_mark_file)
        return (local_mark, remote_mark)

    def cache_installer_name(self, commit_id, bin='mini_installer.exe'):
        return "%s-%s-%s" % (self._build_target, commit_id, bin)

    def copy_chromium_source_code(self):
        if os.path.exists(self.src_path):
            print('%s already exists' % (self.src_path))
            return

        local_code_zip = os.path.join(self._root, code_zip_name())
        if not os.path.exists(local_code_zip):
            remote_code_zip = os.path.join(remote_code_path(self.remote_base_path), code_zip_name())
            download_file(remote_code_zip, local_code_zip)

        print('Begin unzip %s to %s' % (local_code_zip, self.src_path))
        with zipfile.ZipFile(local_code_zip, 'r', zipfile.ZIP_DEFLATED, True) as zf:
            zf.extractall(self._root)
        print("End unzip %s" % local_code_zip)
        if not os.path.exists(self.src_path):
            msg = "%s is not exists" % (self.src_path)
            print(msg)
            sys.exit(msg)
        os.remove(local_code_zip)

    def check_requirements(self):
        assert is_dir_exists(self.static_page_path)
        assert is_dir_exists(self.ts_sdk_path)

        self.download_default_extensions()

    def check_browser_src_files(self):
        self.copy_chromium_source_code()
        assert is_dir_exists(self.chrome_path)
        self.check_chromium_branch()

    def remote_installer_file(self, installer_name):
        return os.path.join(remote_cache_path(self.remote_base_path), self._target_cpu, installer_name)

    def local_installer_file(self, installer_name):
        return os.path.join(self.install_path, installer_name)
  
    def update_build_cache_and_version(self):
        commit_id = self.get_repo_version()
        try:
            installer_name = self.cache_installer_name(commit_id)
            local_installer = self.local_installer_file(installer_name)
            origin_installer = self.local_installer_file('mini_installer.exe')
            if os.path.exists(origin_installer):
                os.rename(origin_installer, local_installer)
                upload_file(local_installer, self.remote_installer_file(installer_name))
                self.update_cache_version(self.cache_version_file, commit_id)
                os.remove(local_installer)
        except Exception as e:
            print("Update build cache failed, error: %s" % e)
            raise

    def get_match_build_cache(self):
        is_match = False
        try:
            commit_id = self.get_repo_version()
            self.get_cache_version(self.cache_version_file)
            if commit_id != self._cache_version:
                print("There is no match build cache")
                return is_match

            installer_name = self.cache_installer_name(commit_id)
            local_installer = self.local_installer_file(installer_name)
            origin_installer = self.local_installer_file('mini_installer.exe')
            make_file_not_exist(origin_installer)


            if not os.path.exists(local_installer):
                download_file(self.remote_installer_file(installer_name), local_installer)
            os.rename(local_installer, origin_installer)

            if os.path.exists(origin_installer): is_match = True
        except Exception as e:
            print('Get match build cache failed, error: %s' % e)
        finally:
            return is_match

class CheckForMacosCIBuild(CheckForCIBuild):

    @property
    def pack_app_path(self):
        return pack_app_path(self._root, self._target_cpu, application_name())

    @property
    def build_app_path(self):
        return build_app_path(self._root, self._build_target, application_name())

    @property
    def cache_version_file(self):
        local_mark = os.path.join(self.install_path, self.cache_mark_file)
        remote_mark = os.path.join(remote_cache_path(self.remote_base_path), self._target_cpu, self.cache_mark_file)
        return (local_mark, remote_mark)

    def cache_zip_name(self, commit_id):
        return "%s-%s.tar.gz" % (self._build_target, commit_id)

    def copy_chromium_source_code(self):
        if os.path.exists(self.src_path):
            print("%s already exists" % (self.src_path))
            return

        print("Chromium code is not exists, need download chromium zip file!")
        local_code_zip = os.path.join(self._root, code_zip_name())
        if not os.path.exists(local_code_zip):
            remote_code_zip = os.path.join(remote_code_path(self.remote_base_path), code_zip_name())
            download_file(remote_code_zip, local_code_zip)

        print('Begin unzip %s' % local_code_zip)
        self.make_unzip(local_code_zip, self._root)
        print('End unzip %s' % local_code_zip)
        if not os.path.exists(self.src_path):
            msg = '%s is not exists' % (self.src_path)
            print(msg)
            sys.exit(msg)
        os.remove(local_code_zip)

    def update_default_extensions(self):
        extenions_path = os.path.join(
            self.src_path, "chrome", "app", "Extensions")
        make_dir_exist(extenions_path)

        old_extensions = [ os.path.join(extenions_path, x) 
                for x in os.listdir(extenions_path) if x.endswith('.zip')]
        for filename in old_extensions:
            os.remove(filename)

        copys = list(filter(lambda x: x.endswith(".crx"),
                     os.listdir(self.local_extension_path)))
        copys.append("default_extensions.json")
        for filename in copys:
            src_path = os.path.join(self.local_extension_path, filename)
            dst_path = os.path.join(extenions_path, filename)
            shutil.copy(src_path, dst_path)

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

        self.download_default_extensions()

    def check_browser_src_files(self):
        self.copy_chromium_source_code()
        assert is_dir_exists(self.chrome_path)
        self.check_chromium_branch()

    def make_unzip(self, tar_file, dst_dir, step=0):
        assert type(step) is int
        try:
            cmd = 'tar xzf %s --strip-components=%s' % (tar_file, step)
            print(cmd)
            subprocess.check_call(cmd, shell=True, cwd=dst_dir)
        except Exception as error:
            print("Unzip %s failed, error: %s" % (tar_file, error))
            raise

    def make_zip(self, tar_file, source):
        try:
            work_path = os.path.dirname(source)
            path = str(os.path.basename(source)).strip().replace(" ", "\ ")
            cmd = 'tar -czf %s %s' % (tar_file, path)
            print(cmd)
            subprocess.check_call(cmd, shell=True, cwd=work_path)
        except Exception as error:
            print("Zip %s into %s failed, error: %s" % (path, tar_file, error))
            raise

    def remote_zip_file(self, zip_name):
        return os.path.join(remote_cache_path(self.remote_base_path), self._target_cpu, zip_name)

    def local_zip_file(self, zip_name):
        return os.path.join(self.install_path, zip_name)

    def update_build_cache_and_version(self):
        commit_id = self.get_repo_version()
        try:
            zip_name = self.cache_zip_name(commit_id)
            print("Zip cache file %s for %s" % (zip_name, self._target_cpu))
            local_zip_file = self.local_zip_file(zip_name)
            make_file_not_exist(local_zip_file)
            assert is_dir_exists(self.pack_app_path), '%s is not available' % self.pack_app_path

            print('Begin zip %s into %s' % (self.pack_app_path, local_zip_file))
            self.make_zip(local_zip_file, self.pack_app_path)
            print('End zip %s' % self.pack_app_path)
            if os.path.exists(local_zip_file):
                upload_file(local_zip_file, self.remote_zip_file(zip_name))
                self.update_cache_version(self.cache_version_file, commit_id)
                os.remove(local_zip_file)
        except Exception as e:
            print("Update build cache failed, error: %s" % e)
            raise

    def get_match_build_cache(self):
        if os.path.exists(self.pack_app_path):
            shutil.rmtree(self.pack_app_path)

        if os.path.exists(self.build_app_path):
            shutil.rmtree(self.build_app_path)
        is_match = False
        try:
            commit_id = self.get_repo_version()
            self.get_cache_version(self.cache_version_file)
            if commit_id != self._cache_version:
                print("There is no match build cache")
                return is_match

            zip_name = self.cache_zip_name(commit_id)
            local_zip_file = self.local_zip_file(zip_name)
            if not os.path.exists(local_zip_file):
                download_file(self.remote_zip_file(zip_name), local_zip_file)

            print("Begin unzip %s " % local_zip_file)
            self.make_unzip(local_zip_file, os.path.dirname(local_zip_file))
            print("End unzip %s " % local_zip_file)
            if os.path.exists(self.pack_app_path): is_match = True
        except Exception as e:
            print('Get match build cache failed, error: %s' % e)
        finally:
            return is_match


CHECK_TYPE_MAP = {
    'Windows':   CheckForWindowsCIBuild,
    'Darwin':     CheckForMacosCIBuild
}


def CheckFactory(type_name, root, target_cpu, project_name, channel):
    """Factory to build Checkout class instances."""
    class_ = CHECK_TYPE_MAP.get(type_name)
    if not class_:
        raise KeyError('unrecognized checkout type: %s' % type_name)
    return class_(root, target_cpu, project_name, channel)
