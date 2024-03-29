
import os, sys, platform
import argparse
sys.path.append(os.path.dirname(__file__))

import subprocess
import shutil
from util import is_dir_exists, make_dir_exist, make_file_not_exist
from common import pack_base_path,pkg_base_path,pkg_build_path, src_path, nsis_bin_path
from common import pack_app_path,build_target, build_app_path, build_target_path, application_name
from common import pkg_prefix, MAC_CPUS

IS_MAC = platform.system() == "Darwin"
IS_WIN = platform.system() == "Windows"
DEFAULT_CPU = "X86"

class Pack:
    def __init__(self, root, target_cpu, project_name, version, channel):
        self._root = root
        self._target_cpu = target_cpu
        self._project_name = project_name
        self._channel = channel
        self._build_target = build_target(target_cpu, project_name)
        channel_version = 1 if self._channel == "beta" else 0
        self._version = '1.0.%s.%s' % (channel_version, version)

    @property
    def pack_base_path(self):
        return pack_base_path(self._root, self._target_cpu)

    def execute_cmd(self, cmd, log_file=None):
        try:
            subprocess.check_call(
                cmd, shell=True, stdout=log_file, stderr=log_file)
        except Exception as error:
            print('Execute command: %s failed, error: %s' % (cmd, error))
            raise

    def pack(self):
        raise NotImplementedError()


class PackForWindows(Pack):

    @property
    def out_path(self):
        return build_target_path(src_path(self._root), self._build_target)

    @property
    def nsis_bin_path(self):
        nsis_bin = nsis_bin_path()
        assert os.path.exists(nsis_bin)
        return nsis_bin

    @property
    def nsis_script(self):
        return os.path.join(
                    self.pack_base_path, 'browser_setup.nsi')

    def pack(self):
        self.check_requirements()
        self.copy_files_for_pack()
        self.make_nsis_installer()

    def check_requirements(self):
        pass

    def copy_browser_installer(self):
        try:
            src_path = os.path.join(self.out_path, "mini_installer.exe")
            dst_path = os.path.join(self.pack_base_path, "mini_installer.exe")
            make_file_not_exist(dst_path)
            shutil.copyfile(src_path, dst_path)
            assert os.path.exists(dst_path), ' Copy %s to %s failed' % (src_path, dst_path)
        except Exception as e:
            print("copy browser installer failed: %s" % e)

    def copy_extensions(self):
        extension_path = os.path.join(self.pack_base_path, "Extensions")
        make_dir_exist(extension_path)

    def copy_files_for_pack(self):
        self.copy_browser_installer()
        self.copy_extensions()

    def make_nsis_installer(self):
        try:
            cmd = [self.nsis_bin_path,
            '/DBrowserVersion=%s' % self._version,
            '/Dchannel=%s' % self._channel,
            self.nsis_script
        ]
            self.execute_cmd(cmd)
            print('Make installer success')
        except Exception as e:
            msg = 'Make nsis installer failed, error: %s' % e
            print(msg)
            sys.exit(msg)


class PackForMacos(Pack):

    @property
    def pack_app_path(self):
        return pack_app_path(self._root, self._target_cpu, application_name())

    @property
    def build_app_path(self):
        return build_app_path(self._root, self._build_target, application_name())

    @property
    def pkg_base_path(self):
        return pkg_base_path(self._root, self._target_cpu)

    @property
    def pkg_build_path(self):
        return pkg_build_path(self._root, self._target_cpu)

    @property
    def dmg_file(self):
        cpu_type = 'aarch64' if self._target_cpu == 'ARM' else 'x86'
        dmg_filename = "cyfs-browser-%s-%s.dmg" % (self._version, cpu_type)
        return os.path.join(self.pack_base_path, dmg_filename)

    def pack(self):
        self.check_requirements()
        self.copy_files_for_pack()
        one_step_pkg =self.build_pkg('%s_browser_package' % (pkg_prefix()))
        two_step_pkg = self.build_pkg('%s_browser' % (pkg_prefix()))
        make_file_not_exist(one_step_pkg)
        self.build_dmg()
        self.add_custom_icon_for_dmg()
        make_file_not_exist(two_step_pkg)

    def add_custom_icon_for_dmg(self):
        pass

    def check_requirements(self):
        pass

    def copy_files_for_pack(self):
        self.delete_build_dir(self.pkg_build_path)
        self.delete_build_dir(self.pack_base_path)

        make_file_not_exist(self.pack_app_path)
        assert not os.path.exists(self.pack_app_path)
        assert is_dir_exists(
            self.build_app_path), ('Generator application %s failed' % self.build_app_path)

        print('Copy application %s to %s' %
              (self.build_app_path, self.pack_app_path))
        shutil.copytree(self.build_app_path, self.pack_app_path, symlinks=True)
        assert is_dir_exists(self.pack_app_path), 'Copy application %s to %s failed' % (
            self.build_app_path, self.pack_app_path)

    def delete_build_dir(self, path, exts=['.pkg', '.dmg']):
        try:
            if not os.path.exists(path): return

            def _delete_if_needed(file):
                return bool([ext for ext in exts if file.lower().endswith(ext)])

            files = [os.path.join(path, file) for file in os.listdir(path)]
            delete_files = filter(lambda x: _delete_if_needed(x), files)
            for file in delete_files:
                print('Deleting file %s' % file)
                os.remove(file)
        except Exception as e:
            print('Delete build dir failed, error: %s' % e)
            raise

    def build_pkg(self, package_name):
        make_dir_exist(self.pkg_build_path)
        this_pkg_file = os.path.join(self.pkg_build_path, '%s.pkg' % package_name)
        make_file_not_exist(this_pkg_file)

        this_pkgproj = os.path.join(self.pkg_base_path, '%s.pkgproj' % package_name)
        cmd = '/usr/local/bin/packagesbuild --package-version %s %s' % (
            self._version, this_pkgproj)
        print('-> Begin build pkg, cmd = %s' % cmd)
        self.execute_cmd(cmd)
        print('<- End build pkg')
        assert os.path.exists(this_pkg_file), 'Build pkg %s failed' % this_pkg_file
        return this_pkg_file

    def build_dmg(self):
        dst = os.path.join(self.pkg_build_path, 'uninstall.sh')
        shutil.copyfile(os.path.join(self.pkg_base_path, 'uninstall.sh'), dst)
        os.chmod(dst, 0o755)

        cmd = 'hdiutil create -fs HFS+ -srcfolder %s -volname cyfs-browser-installer %s' % (
            self.pkg_build_path, self.dmg_file)
        print('-> Begin build dmg , cmd = %s' % cmd)
        self.execute_cmd(cmd)
        print('<- End build dmg')
        assert os.path.exists(self.dmg_file),  "Build dmg %s failed" % (self.dmg_file)
        print("Build dmg %s succeeded" % (self.dmg_file))


PACK_TYPE_MAP = {
    'Windows':   PackForWindows,
    'Darwin':     PackForMacos
}


def PackFactory(type_name, root, target_cpu, project_name, version, channel):
    '''Factory to build Pack class instances.'''
    class_ = PACK_TYPE_MAP.get(type_name)
    if not class_:
        raise KeyError('unrecognized pack type: %s' % type_name)
    return class_(root, target_cpu, project_name, version, channel)


def make_installer(root, project_name, version, target_cpu, channel):
    assert platform.system() in ['Windows', 'Darwin']
    try:
        pack = PackFactory(platform.system(), root,
                           target_cpu, project_name, version, channel)
        pack.pack()
    except Exception as e:
        print('Make Installer failed, error: %s' % e)

def _parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-name",
                        help="The project name.",
                        type=str,
                        required=True)
    parser.add_argument("--version",
                        help="The build version.",
                        type=str,
                        required=True)
    parser.add_argument("--target-cpu",
                        help="The target cpu, like X86 and ARM",
                        type=str,
                        default=DEFAULT_CPU,
                        required=False)
    parser.add_argument("--channel",
                    help="The cyfs channel, like nightly and beta",
                    type=str,
                    default='nightly',
                    required=False)
    opt = parser.parse_args(args)

    assert opt.project_name.strip()
    assert opt.version.strip()
    if IS_MAC:
        assert opt.target_cpu.strip()
        assert opt.target_cpu in MAC_CPUS

    return opt

def main(args):
    root = os.path.normpath(os.path.join(os.path.dirname(
        os.path.abspath(__file__)), os.pardir, os.pardir))
    opt = _parse_args(args)
    make_installer(root, opt.project_name, opt.version, opt.target_cpu, opt.channel)

if __name__ == "__main__":
    try:
        print(str(sys.argv))
        sys.exit(main(sys.argv[1:]))
    except KeyboardInterrupt:
        sys.stderr.write("interrupted\n")
        sys.exit(1)
