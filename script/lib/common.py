
# -*- coding: UTF-8 -*-

from cmath import log
import os
import datetime
import platform

log_dir = None

class ChangeDir(object):
    """Changes the working directory and resets it on exit."""
    def __init__(self, path):
        self.prev_path = os.getcwd()
        self.path = path

    def __enter__(self):
        os.chdir(self.path)

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_value:
            print('was in %s; %s before that' % (self.path, self.prev_path))
        os.chdir(self.prev_path)


def build_target_dir(target_cpu, project_name):
    return "{}-{}".format(target_cpu, project_name)


def get_log_fd(root, build_dir, log_name):
    file_name = '%s-%s-%s.log' %(datetime.datetime.now().strftime('%Y%m%d%H%M%S'), build_dir, log_name)
    print(file_name)
    log_dir = os.path.join(root, "build_log")
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    return open(os.path.join(log_dir, file_name), 'a+')


def target():
    return "chrome"
    

def app_name():
    if platform.system() == "Windows":
        return ""
    elif platform.system() == "Darwin":
        return "Cyfs Browser.app"
    else:
        return ""



###  chromium source code
def get_code_zip_name():
    if platform.system() == "Windows":
        return ""
    elif platform.system() == "Darwin":
        return "chromium_mac_code.tar.gz"
    else:
        return ""


def local_code_zip(root, code_zip):
    return os.path.join(root, code_zip)


def src_path(root):
    return os.path.join(root, "src")



### defaule extensions
def local_extension_path(root):
    return os.path.join(root, "Extensions")


def remote_extensions_path(remote_base_path):
    return "%s/%s/%s" %(remote_base_path, "chromium_extensions", "Extensions")



### ndf_web
def local_nft_web_path(root):
    return os.path.join(root, "nft_web")


def remote_nft_web_path(remote_base_path):
    return "%s/%s/%s/%s" %(remote_base_path, "cyfs-nft", "nft-web", "pub")


### cache zip 
def cache_zip_name(build_dir, commit_id):
    assert type(build_dir) is str
    return "%s_%s.tar.gz" %(build_dir, commit_id)


def remote_code_zip(remote_base_path, code_zip):
    if platform.system() == "Windows":
        return "%s/%s/%s" %(remote_base_path, "chromium_code_pc", code_zip)
    elif platform.system() == "Darwin":
        return "%s/%s/%s" %(remote_base_path, "chromium_code_mac", code_zip)
    else:
        return ""


def remote_base_cache_path(remote_base_path):
    if platform.system() == "Windows":
        return "%s/%s/%s" %(remote_base_path, "browser_build_cache", "windows")
    elif platform.system() == "Darwin":
        return "%s/%s/%s" %(remote_base_path, "browser_build_cache", "mac")
    else:
        return ""


### cyfs dep 
def cyfs_tools_path(root, target_cpu):
    if platform.system() == "Windows":
        return os.path.join(root, "browser_install", "cyfs-runtime-pack", "tools")
    elif platform.system() == "Darwin":
        return os.path.join(root, "dmg", target_cpu, "tools")
    else:
        return None


def static_page_path(root, target_cpu):
    if platform.system() == "Windows":
        return os.path.join(root, "browser_install", "cyfs-runtime-pack", "www")
    elif platform.system() == "Darwin":
        return os.path.join(root, "dmg", target_cpu, "www")
    else:
        return None


def ts_sdk_path(root, target_cpu):
    return os.path.join(static_page_path(root, target_cpu), "cyfs_sdk")



### only for macos pkg and dmg
def dmg_dir(root, target_cpu):
    return os.path.join(root, "dmg", target_cpu)


def package_path(root, target_cpu):
    return os.path.join(root, "dmg", target_cpu, "package")


def pkg_dir(root, target_cpu):
    return os.path.join(root, "dmg", target_cpu, "package", "build")


### application 
def package_application_path(root, target_cpu, app_name):
    return os.path.join(root, "dmg", target_cpu, app_name)


def build_application_path(root, build_dir, app_name):
    return os.path.join(root, "src", "out", build_dir, app_name)



### build cache mark 
def cache_mark_file(target_cpu):
    return "%s_commit_id" %(target_cpu)


def local_cache_mark_file(root, target_cpu, file_name):
    return os.path.join(root, target_cpu, file_name)


def remote_cache_mark_file(root, target_cpu, file_name):
    return "%s/%s/%s" %(root, target_cpu, file_name)



### build cahe zip 
def local_cache_zip_file(root, target_cpu, zip_name):
    return os.path.join(root, "dmg", target_cpu,  zip_name)


def remote_cache_zip_file(remote_cache_dir, target_cpu, zip_name):
    return "%s/%s/%s" %(remote_cache_dir, target_cpu, zip_name)




def get_last_args_file(src_root, build_dir):
    return os.path.join(src_root, "out", build_dir, "args.gn")

def toolchain_ninja_file(src_root, build_dir):
    return os.path.join(src_root, "out", build_dir, "toolchain.ninja")