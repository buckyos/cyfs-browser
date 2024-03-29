# -*- coding: UTF-8 -*-

import os
import sys, platform
import subprocess
sys.path.append(os.path.dirname(__file__))
from common import MAC_CPUS, build_target, last_args_file, toolchain_ninja_file, get_default_args_array
from util import make_dir_exist
import argparse
import datetime

root = os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), os.pardir, os.pardir))

src_path = os.path.join(root, 'src')

IS_MAC = platform.system() == 'Darwin'
IS_WIN = platform.system() == 'Windows'
DEFAULT_CPU = "X86"

def execute_cmd(cmd, **kwargs):
    try:
        print('Execute cmd: %s' % ' '.join(cmd))
        log_fd = kwargs.pop('log_fd', None)
        if log_fd is not None:
            kwargs['stdout'] = log_fd
            kwargs['stderr'] = log_fd
        kwargs['shell'] = IS_WIN
        subprocess.call(cmd, **kwargs)
    except Exception as e:
        print('Execute cmd %s failed: %s' % (' '.join(cmd), e))
        raise

def check_map_equals(a, b):
    is_equal = False
    try:
        if len(a) != len(b): return is_equal
        for key, value in a.items():
            if key not in b: return is_equal
            if value != b[key]: return is_equal
        is_equal = True
    except Exception as e:
        print(e)
    finally:
        return is_equal

class LogRecord:
    def __init__(self, root, build_target, build_type):
        self._build_target = build_target
        self._build_type = build_type
        self._log_root = os.path.join(root, os.pardir, "build_log")
        make_dir_exist(self._log_root)

    def __enter__(self):
        current_time = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        log_file_name = '%s-%s-%s.log' % (current_time, self._build_target, self._build_type)
        file = os.path.join(self._log_root, log_file_name)
        self.f = open(file, 'a+')
        return self.f

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.f.close()

class BuildHelper():
    _target = 'chrome'
    def __init__(self, src_root, project_name, target_cpu):
        self._src_root = src_root
        self._target_cpu = target_cpu
        self._build_target = build_target(target_cpu, project_name)

        self._target = ['chrome']
        if IS_WIN:
            self._target = ['chrome', 'setup', 'mini_installer']

    @property
    def deafult_gn_args_array(self):
        return get_default_args_array(self._target_cpu)

    def is_ninja_file_exists(self):
        return os.path.exists(toolchain_ninja_file(
            self._src_root, self._build_target))

    def get_last_args_map_from_file(self):
        _last_args_file = last_args_file(self._src_root, self._build_target)
        last_args_map = dict()
        if not os.path.exists(_last_args_file):
            return last_args_map
        with open(_last_args_file, 'r+') as f:
            lines = [l.strip() for l in f.readlines()]
            for line in lines:
                values = list(map(lambda x: x.strip(), line.split('=')))
                if len(values[0]) and len(values[1]):
                    last_args_map[values[0]] = values[1]
                else:
                    return dict()
        return last_args_map

    def clean_build_environment(self):
        os.chdir(self._src_root)
        if not self.is_ninja_file_exists(): return
        print('Clean build environment')
        self.clean_build_dir()

    def get_deafult_gn_args_string(self):
        args_str = ''
        for arg in self.deafult_gn_args_array:
            args_str += ' %s' % (arg)
        return args_str

    def get_default_args_map(self):
        current_args_map = dict()
        for line in self.deafult_gn_args_array:
            values = list(map(lambda x: x.strip(), line.split('=')))
            assert len(values) == 2 and values[0].strip() and values[1].strip()
            current_args_map[values[0]] = values[1]
        return current_args_map

    def clean_build_dir(self):
        try:
            cmd = ['gn', 'clean', 'out/%s' % self._build_target]
            execute_cmd(cmd, cwd=self._src_root)
        finally:
            return

    def run_ninja(self):
        try:
            print('Begin run ninja')
            cmd = ['autoninja', '-C', 'out/%s' % (self._build_target) ]
            cmd.extend(self._target)
            with LogRecord(self._src_root, self._build_target, 'NINJA') as log_fd:
                execute_cmd(cmd, log_fd=log_fd, cwd=self._src_root)
        except Exception as e:
            msg = 'Start ninja %s failed, error: %s' % (self._build_target, e)
            print(msg)
            sys.exit(msg)
        print('End run ninja')

    def should_run_gn_gen(self, force=False):
        ''' If 'force' is True, just gn again whether it has been gererate project last time'''
        if force: return True
        if self.is_ninja_file_exists(): return False
        last_args_map = self.get_last_args_map_from_file()
        current_args_map = self.get_default_args_map()
        return not check_map_equals(last_args_map, current_args_map)

    def run_gn_gen(self, gn_args=[]):
        print('Begin gn gen project %s ' % (self._build_target))
        try:
            cmd = ['gn', 'gen', 'out/%s' % (self._build_target),
                    '--args=' + ' '.join(gn_args)]
            with LogRecord(self._src_root, self._build_target, 'GN') as log_fd:
                execute_cmd(cmd, log_fd=log_fd, cwd=self._src_root)
        except Exception as e:
            self.clean_build_dir()
            msg = 'Start gn %s failed, error: %s' % (self._build_target, e)
            print(msg)
            sys.exit(msg)

        if not self.is_ninja_file_exists():
            self.clean_build_dir()
            msg = 'Gn gen %s failed, please check' % (self._build_target)
            print(msg)
            sys.exit(msg)
        print('Gn gen %s success' % (self._build_target))
        print('End gn gen project %s ' % (self._build_target))

    def run_build_target(self):
        print('Begin build browser!')
        if self.should_run_gn_gen():
            self.clean_build_environment()
            self.run_gn_gen(self.deafult_gn_args_array)

        self.run_ninja()

        print('End build browser!')

    @classmethod
    def start_build(cls, src_root, project_name, target_cpu):
        build = BuildHelper(src_root, project_name, target_cpu)
        build.run_build_target()

def build_browser(src_root, project_name, target_cpu):
    BuildHelper.start_build(src_root, project_name, target_cpu)

def main(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('--src-path',
        help='The chromium src path.',
        type=str,
        required=False)
    parser.add_argument('--project-name',
        help='The project name.',
        type=str,
        default='Browser',
        required=True)
    parser.add_argument('--target-cpu',
        help='The target cpu, like X86 and ARM',
        type=str,
        default=DEFAULT_CPU,
        required=False)
    opt = parser.parse_args(args)

    assert opt.project_name and opt.project_name.strip(), \
        'Please provide project name'

    if opt.src_path is None or not os.path.exists(opt.src_path):
        opt.src_path = src_path


    if IS_MAC:
        assert opt.target_cpu in MAC_CPUS

    build_browser(opt.src_path, opt.project_name, opt.target_cpu)

if __name__ == '__main__':
    try:
        print(''.join(sys.argv))
        sys.exit(main(sys.argv[1:]))
    except KeyboardInterrupt:
        sys.stderr.write('interrupted\n')
        sys.exit(1)