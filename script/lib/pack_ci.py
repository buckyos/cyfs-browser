
import os, sys, platform
sys.path.append(os.path.dirname(__file__))

import subprocess
import shutil
from util import is_dir_exists, make_dir_exist, make_file_not_exist
from common import pack_base_path, pkg_base_path, pkg_build_path, build_app_path, pack_app_path
from common import src_path, build_target, build_target_path, application_name
from common import static_page_path, nsis_bin_path, pkg_prefix


class Pack:
    def __init__(self, root, target_cpu, project_name, version, channel, reuse_last_build):
        self._root = root
        self._reuse_last_build = reuse_last_build
        self._target_cpu = target_cpu
        self._project_name = project_name
        self._channel = channel
        self._build_target = build_target(target_cpu, project_name)
        channel_version = 1 if self._channel == "beta" else 0
        self._version = '1.0.%s.%s' % (channel_version, version)

    @property
    def static_page_path(self):
        return static_page_path(self._root, self._target_cpu)

    @property
    def pack_base_path(self):
        return pack_base_path(self._root, self._target_cpu)

    def execute_cmd(self, cmd, log_file=None):
        try:
            subprocess.check_call(
                cmd, shell=True, stdout=log_file, stderr=log_file)
        except Exception as error:
            print("Execute command: %s failed, error: %s" % (cmd, error))
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
                    self.pack_base_path, "browser_setup.nsi")

    def pack(self):
        self.check_requirements()
        self.copy_files_for_pack()
        self.make_nsis_installer()
        self.clean()

    def clean(self):
        local_installer_bin = os.path.join(self.pack_base_path, "mini_installer.exe")
        os.remove(local_installer_bin)

    def check_requirements(self):
        pass

    def copy_browser_installer(self):
        try:
            src_path = os.path.join(self.out_path, "mini_installer.exe")
            dst_path = os.path.join(self.pack_base_path, "mini_installer.exe")
            make_file_not_exist(dst_path)
            shutil.copyfile(src_path, dst_path)
            assert os.path.exists(dst_path), ' Copy %s to %s failed' % (src_path, dst_path)
            os.remove(src_path)
        except Exception as e:
            print("Copy browser installer failed: %s" % e)

    def copy_extensions(self):
        try:
            print('Begin copy extensions')
            src_path = os.path.join(self._root, "Extensions")
            dst_path = os.path.join(self.pack_base_path, "Extensions")
            make_file_not_exist(dst_path)
            shutil.copytree(src_path, dst_path)
            assert os.path.exists(dst_path), ' Copy %s to %s failed' % (src_path, dst_path)
            make_file_not_exist(src_path)
            print('End copy extensions')
        except Exception as e:
            print("Copy extensions failed, error: %s" % e)
            raise

    def copy_files_for_pack(self):
        if not self._reuse_last_build:
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

    @property
    def pack_app_path(self):
        return pack_app_path(self._root, self._target_cpu, application_name())

    @property
    def build_app_path(self):
        return build_app_path(self._root, self._build_target, application_name())

    def pack(self):
        self.check_requirements()
        self.copy_files_for_pack()
        one_step_pkg =self.build_pkg('%s_browser_package' % (pkg_prefix()))
        two_step_pkg = self.build_pkg('%s_browser' % (pkg_prefix()))
        make_file_not_exist(one_step_pkg)
        self.build_dmg()
        self.add_custom_icon_for_dmg()
        make_file_not_exist(two_step_pkg)
        make_file_not_exist(self.pack_app_path)

    def check_requirements(self):
        pass

    def copy_files_for_pack(self):
        self.copy_browser_app()

    def copy_browser_app(self):
        assert is_dir_exists(self.build_app_path), ("Build app %s failed" % self.build_app_path)

        self.delete_build_dir(self.pkg_build_path)
        self.delete_build_dir(self.pack_base_path)

        make_file_not_exist(self.pack_app_path)
        assert not os.path.exists(self.pack_app_path)
        # assert is_dir_exists(self.build_app_path), ("Build app %s failed" % self.build_app_path)

        print("Copy %s to %s" % (self.build_app_path, self.pack_app_path))
        shutil.copytree(self.build_app_path, self.pack_app_path, symlinks=True)
        assert is_dir_exists(self.pack_app_path), "Copy application  failed"
        shutil.rmtree(self.build_app_path)


    def delete_build_dir(self, path, exts=[".pkg", ".dmg"]):
        try:
            if not os.path.exists(path):
                return

            def _delete_if_needed(file):
                return bool([ext for ext in exts if file.lower().endswith(ext)])

            files = [os.path.join(path, file) for file in os.listdir(path)]
            delete_files = filter(lambda x: _delete_if_needed(x), files)
            for file in delete_files:
                print("Deleting file %s" % file)
                os.remove(file)
        except Exception as e:
            print("Delete build dir failed, error: %s" % e)
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
        dst = os.path.join(self.pkg_build_path, "uninstall.sh")
        shutil.copyfile(os.path.join(self.pkg_base_path, "uninstall.sh"), dst)
        os.chmod(dst, 0o755)

        cmd = "hdiutil create -fs HFS+ -srcfolder %s -ov -format UDZO -volname cyfs-browser-installer %s" % (
            self.pkg_build_path, self.dmg_file)
        print("-> Begin build dmg , cmd = %s" % cmd)
        self.execute_cmd(cmd)
        print("<- End build dmg")
        assert os.path.exists(self.dmg_file),  "Build dmg %s failed" % (self.dmg_file)
        print("Build dmg %s succeeded" % (self.dmg_file))

    def add_custom_icon_for_dmg(self):
        print('Begin add custom icon for dmg')
        os.chdir(self.pack_base_path)
        cmd = 'cp app.icns app_copy.icns && sips -i app_copy.icns'
        self.execute_cmd(cmd)
        cmd = 'DeRez -only icns app_copy.icns > icns.rsrc'
        self.execute_cmd(cmd)
        cmd = 'Rez -append icns.rsrc -o %s' % os.path.basename(self.dmg_file)
        self.execute_cmd(cmd)
        cmd = 'SetFile -a C %s' % os.path.basename(self.dmg_file)
        self.execute_cmd(cmd)
        print('End add custom icon for dmg')
        


PACK_TYPE_MAP = {
    'Windows':   PackForWindows,
    'Darwin':     PackForMacos
}


def PackFactory(type_name, root, target_cpu, project_name, version, channel, reuse_last_build):
    """Factory to build Pack class instances."""
    class_ = PACK_TYPE_MAP.get(type_name)
    if not class_:
        raise KeyError('unrecognized pack type: %s' % type_name)
    return class_(root, target_cpu, project_name, version, channel, reuse_last_build)


def make_installer(root, target_cpu, project_name, version, channel, reuse_last_build):
    assert platform.system() in ["Windows", "Darwin"]
    try:
        pack = PackFactory(platform.system(), root, target_cpu, project_name, version, channel, reuse_last_build)
        pack.pack()
    except Exception:
        print("Make Installer failed, error: %s" % Exception)


