
import os, sys, platform
sys.path.append(os.path.dirname(__file__))

from logging import exception
import subprocess
import shutil
from util import is_dir_exists, make_dir_exist, make_file_not_exist
from common import pack_base_path, pkg_base_path, pkg_build_path, build_app_path, pack_app_path
from common import include_files, include_version_files, include_dirs
from common import src_path, build_target, get_chromium_version, build_target_path
from common import local_nft_web_path, local_nft_bin_path, local_extension_path, static_page_path


class Pack:
    def __init__(self, root, target_cpu, project_name, version):
        self._root = root
        self._target_cpu = target_cpu
        self._project_name = project_name
        self._version = version
        self._build_target = build_target(target_cpu, project_name)

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
        except exception as error:
            print("Execute command: %s failed, error: %s" % (cmd, error))
            raise

    def copy_nft_web_files(self):
        try:
            src_path = local_nft_web_path(self._root)
            for (root, _, files) in os.walk(src_path):
                for file in files:
                    src = os.path.abspath(os.path.join(root, file))
                    dst = os.path.join(self.static_page_path,
                                       os.path.relpath(src, src_path))
                    make_dir_exist(os.path.dirname(dst))
                    print("Copy %s to %s" % (src, dst))
                    shutil.copyfile(src, dst)
        except Exception as e:
            print("Update nft files failed, error %s" % e)
            raise

    def pack(self):
        raise NotImplementedError()


class PackForWindows(Pack):
    _product_name = "Cyfs_Browser"

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

    def __init__(self, root, target_cpu, project_name, version):
        assert platform.system() == "windows"
        super(PackForWindows, self).__init__(self, root, project_name, version, target_cpu)

    @property
    def out_path(self):
        return build_target_path(src_path(self._root), self._build_target)

    @property
    def product_base_path(self):
        return os.path.join(self.pack_base_path, self._product_name)

    @property
    def nsis_bin_path(self):
        return "C:\\Program Files (x86)\\NSIS\\Bin"

    @property
    def nsis_script(self):
        return os.path.join(
                    self.pack_base_path, "browser_runtime_setup.nsi")

    def pack(self):
        self.check_requirements()
        self.copy_files_for_pack()
        self.make_nsis_installer()

    def check_requirements(self):
        pass

    def copy_browser_file(self):
        copy_number = 0
        make_file_not_exist(self.product_base_path)
        ## {build_dir}/* ==> {package}/*
        for file_ in include_files:
            src_path = os.path.join(self.out_path, file_)
            dst_path = os.path.join(self.product_base_path, file_)
            shutil.copyfile(src_path, dst_path)
            copy_number = copy_number + 1

        version = get_chromium_version(self._root)
        version_dir = os.path.join(self.product_base_path, version)
        make_dir_exist(version_dir)
        ## {build_dir}/* ==> {package}/{version}/*
        for file_ in include_version_files:
            src_path = os.path.join(self.out_path, file_)
            dst_path = os.path.join(version_dir, file_)
            shutil.copyfile(src_path, dst_path)
            print("%s => %s" % (src_path, dst_path))
            copy_number = copy_number + 1
        manifest_file = "{}.manifest".format(version)
        shutil.copyfile(os.path.join(self.out_path, manifest_file),
                        os.path.join(version_dir, manifest_file))
        copy_number = copy_number + 1

        def check_not_need_copy(file):
            _suffixs = ['.lib', '.pdb', '.info']
            return bool([ext for ext in _suffixs if file.lower().endswith(ext)])

        ## {build_dir}/*/* ==> {package}/{version}/*/*
        for dir_ in include_dirs:
            root = os.path.normpath(os.path.join(self.out_path, dir_))
            for (base, _, files) in os.walk(root):
                copy_files = [x for x in files if not check_not_need_copy(x)]
                copy_files = map(lambda x: os.path.join(base, x), copy_files)
                for file in copy_files:
                    dst_file = os.path.join(
                        version_dir, os.path.relpath(file, self.out_path))
                    make_dir_exist(os.path.dirname(dst_file))
                    print("Copy %s to %s" % (file, dst_file))
                    shutil.copyfile(file, dst_file)
                    copy_number = copy_number + 1
        print("Copy %s file for nsis" % (copy_number))

    def copy_extensions(self):
        src_path = local_extension_path(self._root)
        dst_path = os.path.join(self.product_base_path, "Extensions")
        make_file_not_exist(dst_path)
        print("Copy {} to {}" % (src_path, dst_path))
        shutil.copytree(src_path, dst_path)

    def copy_nft_bin_files(self):
        try:
            src_path = local_nft_bin_path(self._root)
            for (root, _, files) in os.walk(src_path):
                for file in files:
                    src = os.path.abspath(os.path.join(root, file))
                    dst = os.path.join(self.product_base_path,
                                       os.path.relpath(src, src_path))
                    make_dir_exist(os.path.dirname(dst))
                    print("Copy %s to %s" % (src, dst))
                    shutil.copyfile(src, dst)
        except Exception as e:
            print("Update nft files failed, error %s" % e)
            raise

    def copy_files_for_pack(self):
        self.copy_browser_file()
        self.copy_extensions()
        self.copy_nft_web_files()
        self.copy_nft_bin_files()

    def make_nsis_installer(self):
        pass


class PackForMacos(Pack):
    _app_name = "Cyfs Browser.app"

    def __init__(self, root, target_cpu, project_name, version):
        assert platform.system() == "Darwin"
        super(PackForMacos, self).__init__(self, root, project_name, version, target_cpu)

    @property
    def pkg_base_path(self):
        return pkg_base_path(self._root, self._target_cpu)

    @property
    def pkg_build_path(self):
        return pkg_build_path(self._root, self._target_cpu)

    @property
    def pkg_proj_file(self):
        return os.path.join(
            self.pkg_base_path, "cyfs_browser_package.pkgproj")

    @property
    def pkg_file(self):
        return os.path.join(self.pkg_build_path, "cyfs_browser_package.pkg")

    @property
    def dmg_file(self):
        return "cyfs-browser-installer-%s.dmg" % (self._version)

    @property
    def pack_app_path(self):
        return pack_app_path(self._root, self._target_cpu, self._app_name)

    @property
    def build_app_path(self):
        return build_app_path(self._root, self._build_target, self._app_name)

    def pack(self):
        self.check_requirements()
        self.copy_files_for_pack()
        self.build_pkg()
        self.build_dmg()

    def check_requirements(self):
        pass

    def copy_files_for_pack(self):
        self.copy_browser_file()
        self.copy_nft_web_files()

    def copy_browser_file(self):
        self.delete_build_dir(self.pkg_build_path)
        self.delete_build_dir(self.pack_base_path)

        make_file_not_exist(self.pack_app_path)
        assert not os.path.exists(self.pack_app_path)
        assert is_dir_exists(
            self.build_app_path), ("Generator application %s failed" % self.build_app_path)

        print("Copy application %s to %s" %
              (self.build_app_path, self.pack_app_path))
        shutil.copytree(self.build_app_path, self.pack_app_path, symlinks=True)
        assert is_dir_exists(self.pack_app_path), "Copy application %s to %s failed" % (
            self.build_app_path, self.pack_app_path)

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

    def build_pkg(self):
        make_dir_exist(self.pkg_build_path)

        # pkgproj = os.path.join(
        #     self.pkg_base_path, "cyfs_browser_package.pkgproj")
        # pkg = os.path.join(self.pkg_build_path, "cyfs_browser_package.pkg")
        cmd = "/usr/local/bin/packagesbuild --package-version %s %s" % (
            self._version, self.pkg_proj_file)
        print("-> Begin build pkg, cmd = %s" % cmd)
        self.execute_cmd(cmd)
        print("<- End build pkg")
        if not os.path.exists(self.pkg_file):
            msg = "Build pkg %s failed" % (self.pkg_file)
            print(msg)
            sys.exit(msg)

    def build_dmg(self):
        dst = os.path.join(self.pkg_build_path, "uninstall.sh")
        shutil.copyfile(os.path.join(self.pkg_base_path, "uninstall.sh"), dst)
        os.chmod(dst, 0o755)

        # dmg_file = "cyfs-browser-installer-%s.dmg" % (self._version)
        cmd = "hdiutil create -fs HFS+ -srcfolder %s -volname cyfs-browser-installer %s" % (
            self.pkg_build_path, self.dmg_file)
        print("-> Begin build dmg , cmd = %s" % cmd)
        self.execute_cmd(cmd)
        print("<- End build dmg")
        if not os.path.exists(self.dmg_file):
            msg = "Build dmg %s failed" % (self.dmg_file)
            print(msg)
            sys.exit(msg)


PACK_TYPE_MAP = {
    'Windows':   PackForWindows,
    'Darwin':     PackForMacos
}


def PackFactory(type_name, root, target_cpu, project_name, version):
    """Factory to build Pack class instances."""
    class_ = PACK_TYPE_MAP.get(type_name)
    if not class_:
        raise KeyError('unrecognized pack type: %s' % type_name)
    return class_(root, target_cpu, project_name, version)


def make_installer(root, target_cpu, project_name, version):
    assert platform.system() in ["windows", "Darwin"]
    try:
        pack = PackFactory(platform.system(), root, target_cpu, project_name, version)
        pack.pack()
    except exception:
        print("Make Installer failed, error: %s" % exception)


def main():
    root = os.path.normpath(os.path.join(os.path.dirname(
            os.path.abspath(__file__)), os.pardir, os.pardir))

    make_installer(root, "ARM", "Browser", "200")

if __name__ == "__main__":
    main()
