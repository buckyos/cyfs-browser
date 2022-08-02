
import os, sys, platform
import re
sys.path.append(os.path.dirname(__file__))

import subprocess
import shutil
from util import is_dir_exists, make_dir_exist, make_file_not_exist
from common import pack_base_path,pkg_base_path,pkg_build_path, src_path, get_chromium_version
from common import pack_app_path,build_target, build_app_path, build_target_path


class Pack:
    def __init__(self, root, target_cpu, project_name, version):
        self._root = root
        self._target_cpu = target_cpu
        self._project_name = project_name
        self._version = version
        self._build_target = build_target(target_cpu, project_name)

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

    _product_name = 'Cyfs_Browser'

    include_files = [
        'Cyfs_Browser.exe', 'chrome_proxy.exe',
    ]
    include_version_files = [
        'chrome_100_percent.pak','chrome_200_percent.pak', 'resources.pak',
        'chrome.dll', 'chrome_elf.dll', 'mojo_core.dll', 'mojo_core.dll',
        'd3dcompiler_47.dll', 'libEGL.dll', 'libGLESv2.dll',
        'vk_swiftshader.dll', 'vulkan-1.dll',
        'chrome_pwa_launcher.exe', 'notification_helper.exe',
        'vk_swiftshader_icd.json', 'v8_context_snapshot.bin',
        'snapshot_blob.bin', 'icudtl.dat',
        'Logo.png', 'SmallLogo.png',
    ]

    include_dirs = [
        'MEIPreload', 'Locales', 'swiftshader', 'resources'
    ]

    @property
    def product_base_path(self):
        return os.path.join(self.pack_base_path, self._product_name)

    @property
    def out_path(self):
        return build_target_path(src_path(self._root), self._build_target)

    @property
    def nsis_bin_path(self):
        nsis_bin = 'C:\\Program Files (x86)\\NSIS\\Bin\\makensis.exe'
        assert os.path.exists(nsis_bin)
        return nsis_bin

    @property
    def nsis_script(self):
        return os.path.join(
                    self.pack_base_path, 'browser_runtime_setup.nsi')

    def pack(self):
        self.check_requirements()
        self.copy_files_for_pack()
        self.make_nsis_installer()

    def check_requirements(self):
        pass

    def make_nsis_installer(self):
        try:
            cmd = [self.nsis_bin_path,  '/DBrowserVersion=%s' %
                       self._version, self.nsis_script]
            self.execute_cmd(cmd)
            print('Make installer success')
        except Exception as e:
            msg = 'Make nsis installer failed, error: %s' % e
            print(msg)
            sys.exit(msg)

    def copy_browser_file(self):
        copy_number = 0
        make_dir_exist(self.product_base_path)
        ## {build_dir}/* ==> {package}/*
        for file_ in self.include_files:
            src_path = os.path.join(self.out_path, file_)
            dst_path = os.path.join(self.product_base_path, file_)
            shutil.copyfile(src_path, dst_path)
            copy_number = copy_number + 1

        version = get_chromium_version(self._root)
        version_dir = os.path.join(self.product_base_path, version)
        make_dir_exist(version_dir)
        ## {build_dir}/* ==> {package}/{version}/*
        for file_ in self.include_version_files:
            src_path = os.path.join(self.out_path, file_)
            dst_path = os.path.join(version_dir, file_)
            shutil.copyfile(src_path, dst_path)
            print('%s => %s' % (src_path, dst_path))
            copy_number = copy_number + 1
        manifest_file = '{}.manifest'.format(version)
        shutil.copyfile(os.path.join(self.out_path, manifest_file),
                        os.path.join(version_dir, manifest_file))
        copy_number = copy_number + 1

        ## {build_dir}/*/* ==> {package}/{version}/*/*
        def check_not_need_copy(file):
            _suffixs = ['lib', 'pdb', 'info']
            return bool([ext for ext in _suffixs if file.lower().endswith(ext)])

        for dir_ in self.include_dirs:
            root = os.path.normpath(os.path.join(self.out_path, dir_))
            for (base, _, files) in os.walk(root):
                copy_files = [x for x in files if not check_not_need_copy(x)]
                for file in copy_files:
                    src_path = os.path.abspath(os.path.join(base, file))
                    dst_path = os.path.join(
                        version_dir, os.path.relpath(src_path, self.out_path))
                    make_dir_exist(os.path.dirname(dst_path))
                    print('Copy %s to %s' % (src_path, dst_path))
                    shutil.copyfile(src_path, dst_path)
                    copy_number = copy_number + 1
        print('Copy %s file for nsis' % (copy_number))

    def copy_files_for_pack(self):
        self.copy_browser_file()


class PackForMacos(Pack):
    app_name = 'Cyfs Browser.app'

    @property
    def pack_app_path(self):
        return pack_app_path(self._root, self._target_cpu, self.app_name)

    @property
    def build_app_path(self):
        return build_app_path(self._root, self._build_target, self.app_name)

    @property
    def pkg_base_path(self):
        return pkg_base_path(self._root, self._target_cpu)

    @property
    def pkg_build_path(self):
        return pkg_build_path(self._root, self._target_cpu)

    @property
    def pkg_file(self):
        return os.path.join(self.pkg_build_path, 'cyfs_browser_package.pkg')

    @property
    def dmg_file(self):
        return 'cyfs-browser-installer-%s.dmg' % (self._version)

    def pack(self):
        self.check_requirements()
        self.copy_files_for_pack()
        self.build_pkg()
        self.build_dmg()

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

    def build_pkg(self):
        make_dir_exist(self.pkg_build_path)

        pkgproj = os.path.join(
            self.pkg_base_path, 'cyfs_browser_package.pkgproj')
        cmd = '/usr/local/bin/packagesbuild --package-version %s %s' % (
            self._version, pkgproj)
        print('-> Begin build pkg, cmd = %s' % cmd)
        self.execute_cmd(cmd)
        print('<- End build pkg')
        if not os.path.exists(self.pkg_file):
            msg = 'Build pkg %s failed' % (self.pkg_file)
            print(msg)
            sys.exit(msg)

    def build_dmg(self):
        dst = os.path.join(self.pkg_build_path, 'uninstall.sh')
        shutil.copyfile(os.path.join(self.pkg_base_path, 'uninstall.sh'), dst)
        os.chmod(dst, 0o755)

        cmd = 'hdiutil create -fs HFS+ -srcfolder %s -volname cyfs-browser-installer %s' % (
            self.pkg_build_path, self.dmg_file)
        print('-> Begin build dmg , cmd = %s' % cmd)
        self.execute_cmd(cmd)
        print('<- End build dmg')
        if not os.path.exists(self.dmg_file):
            msg = 'Build dmg %s failed' % (self.dmg_file)
            print(msg)
            sys.exit(msg)


PACK_TYPE_MAP = {
    'Windows':   PackForWindows,
    'Darwin':     PackForMacos
}


def PackFactory(type_name, root, target_cpu, project_name, version):
    '''Factory to build Pack class instances.'''
    class_ = PACK_TYPE_MAP.get(type_name)
    if not class_:
        raise KeyError('unrecognized pack type: %s' % type_name)
    return class_(root, target_cpu, project_name, version)


def make_installer(root, project_name, version, target_cpu):
    assert platform.system() in ['Windows', 'Darwin']
    try:
        pack = PackFactory(platform.system(), root,
                           target_cpu, project_name, version)
        pack.pack()
    except Exception as e:
        print('Make Installer failed, error: %s' % e)


def main():
    root = os.path.normpath(os.path.join(os.path.dirname(
        os.path.abspath(__file__)), os.pardir, os.pardir))

    make_installer(root, 'Browser', '200', 'ARM')


if __name__ == '__main__':
    main()
