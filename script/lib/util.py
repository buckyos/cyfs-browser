# -*- coding: UTF-8 -*-

import shutil
import os


def is_dir_exists(dir):
    return os.path.exists(dir) and os.path.isdir(dir)

def make_file_not_exist(source):
    if not os.path.exists(source):
        return
    if os.path.isdir(source):
        shutil.rmtree(source)
    elif os.path.isfile(source):
        os.remove(source)
    assert not os.path.exists(source)

def clean_dir(dir):
    if os.path.exists(dir):
        shutil.rmtree(dir)
    os.makedirs(dir)

def make_dir_exist(dir):
    os.makedirs(dir, exist_ok=True)
    assert os.path.exists(dir)

