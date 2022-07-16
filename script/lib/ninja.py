# -*- coding: UTF-8 -*-

import os, sys, subprocess
sys.path.append(os.path.dirname(__file__))
# from util import is_dir_exists, copy_dir
from common import (
    build_target_dir,
    get_log_fd,
    get_last_args_file,
    toolchain_ninja_file,
    target
)

def execute_cmd(cmd, log_file=None):
    try:
        print("Execute cmd %s" % cmd)
        subprocess.check_call(cmd, stdout=log_file, stderr=log_file)
    except Exception as e:
        print("execute cmd %s failed: %s" % (cmd, e))
        raise

def check_map_equals(a, b):
    try:
        if len(a) != len(b):
            return False
        for key, value in a.items():
            if value != b[key]:
                return False
        return True
    except:
        return False

def get_deafult_macos_gn_args_array(target_cpu):
    platforms = [ "X86", "ARM" ]
    assert (target_cpu in platforms)
    default_args_array = [
        'is_debug=false',
        'dcheck_always_on=false',
        'is_component_build=false',
        'enable_nacl=false',
        'target_os="mac"',
        'chrome_pgo_phase=0',
        'clang_use_chrome_plugins=false',
        'enable_hangout_services_extension=false',
        'enable_js_type_check=false',
        'enable_mdns=false',
        'enable_nacl_nonsfi=false',
        'enable_reading_list=false',
        'enable_remoting=false',
        'enable_service_discovery=false',
        'enable_widevine=true',
        'exclude_unwind_tables=true',
        'fieldtrial_testing_like_official_build=true',
        'google_api_key=""',
        'google_default_client_id=""',
        'google_default_client_secret=""',
        'treat_warnings_as_errors=false',
        'use_official_google_api_keys=false',
        'use_unofficial_version_number=false',
        'blink_symbol_level=0',
        'enable_iterator_debugging=false',
        'enable_swiftshader=true',
        'fatal_linker_warnings=false',
        'ffmpeg_branding="Chrome"',
        'is_clang=true',
        'is_official_build=true',
        'proprietary_codecs=true',
        'symbol_level=0',
    ]
    if target_cpu == 'X86':
        default_args_array.append('target_cpu="x64"')
    elif target_cpu == 'ARM':
        default_args_array.append('target_cpu="arm64"')
    return default_args_array

class Build():
    def __init__(self, src_root, target_cpu, project_name, app_name):
        self._target = target()
        self._src_root = src_root
        self._target_cpu = target_cpu
        self._project_name = project_name
        self._app_name = app_name
        self._build_dir = build_target_dir(self._target_cpu, self._project_name)


    def is_ninja_file_exists(self):
        return os.path.exists(toolchain_ninja_file(self._src_root, self._build_dir))


    def get_last_args_map(self):
        last_args_file = get_last_args_file(self._src_root, self._build_dir)
        if not os.path.exists(last_args_file):
            return {}

        last_args_map = {}
        with open(last_args_file, "r+") as f:
            lines = [l.strip() for l in f.readlines()]
            for line in lines:
                values = list(map(lambda x: x.strip(), line.split("=")))
                assert len(values) == 2
                if len(values[0]) and len(values[1]):
                    last_args_map[values[0]] = values[1]
        return last_args_map


    def get_deafult_gn_args_array(self):
        if sys.platform == 'darwin':
            return get_deafult_macos_gn_args_array(self._target_cpu)


    def clean_build_environment(self):
        os.chdir(self._src_root)
        self.clean_build_dir()
        if self.is_ninja_file_exists():
            print("Clean build environment success")
        else:
            print("Clean build environment failed, please check!!")


    def get_deafult_gn_args_string(self):
        default_args_array = self.get_deafult_gn_args_array()
        args_str = ''
        for arg in default_args_array:
            args_str += " %s" %(arg)
        return args_str


    def get_default_args_map(self):
        default_args_array = self.get_deafult_gn_args_array()
        current_args_map = {}
        for line in default_args_array:
            values = list(map(lambda x: x.strip(), line.split("=")))
            if len(values[0]) and len(values[1]):
                current_args_map[values[0]] = values[1]
        return current_args_map


    def clean_build_dir(self):
        try:
            subprocess.check_call('gn clean out/%s ' %(self._build_dir), shell=True)
        finally:
            return


    def start_ninja(self):
        try:
            os.chdir(self._src_root)
            ninja_log_fd = get_log_fd(self._src_root, self._build_dir, 'NINJA')
            cmd_args = ['autoninja', '-C', 'out/%s'%(self._build_dir), self._target]
            execute_cmd(cmd_args, ninja_log_fd)
        except Exception as e:
            print("Start ninja %s failed, error: %s" %(self._build_dir, e))
            sys.exit(-1)


    def need_generate_project(self):
        # if self.is_ninja_file_exists():
        #     return False
        last_args_map = self.get_last_args_map()
        current_args_map = self.get_default_args_map()
        # print("last_args_map = %s" %last_args_map)
        # print("current_args_map = %s" %current_args_map)
        return not check_map_equals(last_args_map, current_args_map)


    def start_gn(self, gn_args):
        try:
            os.chdir(self._src_root)
            gn_log_fd = get_log_fd(self._src_root, self._build_dir, 'GN')
            cmd_args = ['gn', 'gen', 'out/%s' %(self._build_dir), '--args=' + ' '.join(gn_args)]
            execute_cmd(cmd_args, gn_log_fd)
        except Exception as e:
            print("Start gn %s failed, error: %s" %(self._build_dir, e))
            sys.exit(-1)

        if not self.is_ninja_file_exists():
            print("Gn gen %s failed, please check" %(self._build_dir))
            sys.exit(-1)
        print("Gn gen %s success" %(self._build_dir))


    def start_build(self):
        gn_args = self.get_deafult_gn_args_array()
        if self.need_generate_project():
            print("Begin gn gen chromium project %s " %(self._build_dir))
            self.clean_build_environment()
            self.start_gn(gn_args)
            print("End gn gen chromium project %s " %(self._build_dir))

        print("Current chromium project %s is exists" %(self._build_dir))

        print("Begin execute compile script")
        self.start_ninja()
        print("End execute compile script")


def build_browser(src_root, target_cpu, project_name, app_name):
    build = Build(src_root, target_cpu, project_name, app_name)
    build.start_build()



