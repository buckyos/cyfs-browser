
# -*- coding: UTF-8 -*-

import os
import platform
import subprocess

MAC_CPUS = ["X86", "ARM"]

IS_MAC = platform.system() == "Darwin"
IS_WIN = platform.system() == "Windows"


def build_target(target_cpu, project_name):
    assert project_name is not None
    return "%s-%s" % (target_cpu, project_name) if target_cpu is not None else project_name

def src_path(root):
    return os.path.join(root, "src")

def local_extension_path(root):
    return os.path.join(root, "Extensions")

def cyfs_runtime_path(root, target_cpu):
    return os.path.join(pack_base_path(root, target_cpu), "runtime")

def cyfs_tools_path(root, target_cpu):
    return os.path.join(cyfs_runtime_path(root, target_cpu), "tools")

def static_page_path(root, target_cpu):
    return os.path.join(cyfs_runtime_path(root, target_cpu), "www")

def ts_sdk_path(root, target_cpu):
    return os.path.join(static_page_path(root, target_cpu), "cyfs_sdk")

def application_name():
    if IS_WIN:
        return "CYFS_Browser.exe"
    elif IS_MAC:
        return "CYFS Browser.app"
    raise Exception("Unsupported platform")

def pkg_prefix():
    return 'cyfs'

def code_zip_name():
    if IS_WIN:
        return "chromium_code_pc.zip"
    elif IS_MAC:
        return "chromium_mac_code.tar.gz"
    raise Exception("Unsupported platform")

def nsis_bin_path():
    default_nsis_bin_path = 'C:\\Program Files (x86)\\NSIS\\Bin\\makensis.exe'
    path = os.environ.get('NSIS_BIN_PATH', default=default_nsis_bin_path)
    assert os.path.exists(path), 'Must to set CYFS_BROWSER_SRC_PATH'
    return path

def get_vcvars_path(name='64'):
    """
    Returns the path to the corresponding vcvars*.bat path

    As of VS 2019, name can be one of: 32, 64, all, amd64_x86, x86_amd64
    """
    vswhere_exe = '%ProgramFiles(x86)%\\Microsoft Visual Studio\\Installer\\vswhere.exe'
    result = subprocess.run(
        '"{}" -prerelease -latest -property installationPath'.format(vswhere_exe),
        shell=True,
        check=True,
        stdout=subprocess.PIPE,
        universal_newlines=True)
    vcvars_path = os.path.join(result.stdout.strip(), 'VC/Auxiliary/Build/vcvars{}.bat'.format(name))
    if not os.path.exists(vcvars_path):
        raise RuntimeError(
            'Could not find vcvars batch script in expected location: {}'.format(vcvars_path))
    return vcvars_path

def pack_base_path(root, target_cpu):
    if IS_WIN:
        return os.path.join(root, "out", "win", target_cpu)
    elif IS_MAC:
        return os.path.join(root, "out", "mac", target_cpu)
    raise Exception("Unsupported platform")

def pkg_base_path(root, target_cpu):
    assert IS_MAC, 'Current function just for Macos'
    return os.path.join(pack_base_path(root, target_cpu), "package")

def pkg_build_path(root, target_cpu):
    assert IS_MAC, 'Current function just for Macos'
    return os.path.join(pkg_base_path(root, target_cpu), "build")

def pack_app_path(root, target_cpu, app):
    assert IS_MAC, 'Current function just for Macos'
    return os.path.join(pack_base_path(root, target_cpu), app)

def build_target_path(src_root, target):
    return os.path.join(src_root, "out", target)

def build_app_path(root, target, app):
    assert IS_MAC, 'Current function just for Macos'
    return os.path.join(build_target_path(src_path(root), target), app)

def last_args_file(src_root, target):
    return os.path.join(build_target_path(src_root, target), "args.gn")

def toolchain_ninja_file(src_root, target):
    return os.path.join(build_target_path(src_root, target), "toolchain.ninja")

def remote_extensions_path(remote_base_path, channel):
    path = os.path.join(remote_base_path, "chromium_extensions", "Extensions", channel)
    return os.path.normpath(path)

def remote_code_path(remote_base_path):
    if IS_MAC:
        return os.path.normpath(os.path.join(remote_base_path, "chromium_code_mac"))
    if IS_WIN:
        return os.path.normpath(os.path.join(remote_base_path, "chromium_code_pc"))
    raise Exception("Unsupported platform")

def remote_cache_path(remote_base_path):
    if IS_MAC:
        return os.path.normpath(os.path.join(remote_base_path, "browser_build_cache", "mac"))
    if IS_WIN:
        return os.path.normpath(os.path.join(remote_base_path, "browser_build_cache", "windows"))
    raise Exception("Unsupported platform")

def get_deafult_macos_gn_args_array(target_cpu):
    assert target_cpu in MAC_CPUS
    args_array = [
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
        args_array.append('target_cpu="x64"')
    elif target_cpu == 'ARM':
        args_array.append('target_cpu="arm64"')
    return args_array

def get_deafult_windows_gn_args_array():
    args_array = [
        'is_debug=false',
        'dcheck_always_on=false',
        'is_component_build=false',
        'symbol_level=0',
        'blink_symbol_level=0',
        'ffmpeg_branding="Chrome"',
        'proprietary_codecs=true',
        'target_cpu="x64"',
    ]
    return args_array

def get_default_args_array(target_cpu):
    if IS_WIN:
        return get_deafult_windows_gn_args_array()
    elif IS_MAC:
        return get_deafult_macos_gn_args_array(target_cpu)
    raise Exception("Unsupported platform")

