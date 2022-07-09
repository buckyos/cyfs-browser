# -*- coding: UTF-8 -*-

import os, sys
from distutils import cmd
sys.path.append(os.path.dirname(__file__))
import subprocess
import shutil
from common import ChangeDir

def is_dir_exists(dir):
    if os.path.exists(dir) and os.path.isdir(dir):
        return True
    return False

def make_file_not_exist(source):
    if not os.path.exists(source):
        return
    if os.path.isdir(source):
        shutil.rmtree(source)
    elif os.path.isfile(source):
        os.remove(source)
    

def make_dir_exist(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)


def delete_special_suffix_file(paths, suffixs):
    assert type(paths) is list and type(suffixs) is list
    for path in paths:
        files = os.listdir(path)
        for file in files:
            suffix = os.path.splitext(file)[-1]
            if suffix != "" and suffix in suffixs:
                abs_path = os.path.join(path, file)
                print(abs_path)
                if os.path.exists(abs_path):
                    os.remove(abs_path)


def copy_dir(src, dst):
    try:
        shutil.copytree(src, dst, symlinks=True)
    except Exception as error:
        print("copy %s to %s failed, error: %s" %(src, dst, error))
        raise


def make_unzip(tar_file, dest_dir, step=0):
    assert type(step) is int
    try:
        with ChangeDir(dest_dir):
            subprocess.check_call(
                'tar xzf %s --strip-components=%s' % (tar_file, step),
                shell=True)
    except Exception as error:
        print("Unzip %s failed, error: %s" %(tar_file, error))
        raise


def make_zip(tar_file, source):
    try:
        work_dir = os.path.dirname(source)
        files = str(os.path.basename(source)).strip().replace(" ", "\ ")
        print(work_dir, files, tar_file)
        subprocess.check_call('tar -czf %s %s' %(tar_file, files), shell=True, cwd=work_dir)
    except Exception as error:
        print("Zip %s into %s failed, error: %s" %(files, tar_file, error))
        raise


def update_files(src, dst):
    if os.path.exists(dst):
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def get_repo_version(root):
    try:
        with ChangeDir(root):
            git_rev = subprocess.check_output(
                ['git', 'rev-parse', '--short', 'HEAD']).decode('ascii')
            return git_rev.rstrip()
    except Exception as error:
        print("Could not get repository version, error: %s" % error)
        raise


### downlaod and upload from local dir
def download_file(remote_path, local_opath):  
    try:
        cmd_args = ['cp', remote_path, local_opath]
        if is_windows():
            cmd_args = ['copy', remote_path, local_opath]
        print(" ".join(cmd_args))
        subprocess.check_call(cmd_args)
    except Exception as error:
        print("Copy %s to %s failed, error: %s" %(remote_path, local_opath, error))
        raise
    

def upload_file(local_path, remote_path):
    try:
        cmd_args = ['cp', local_path, remote_path]
        if is_windows():
            cmd_args = ['copy', local_path, remote_path]
        print(" ".join(cmd_args))
        subprocess.check_call(cmd_args)
    except Exception as error:
        print("Copy %s to %sfailed, error: %s" %(local_path, remote_path, error))
        raise


def is_windows():
    import platform
    uname = platform.uname()
    return uname.system == 'Windows' or 'Microsoft' in uname.release