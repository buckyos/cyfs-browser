
import os, sys
import subprocess
import shutil

class Patch:
    def __init__(self, root):
        self._root = root
        self._patchs_path = os.path.join(root, "patch_code")
        self._resource_dir = os.path.join(root, "resource")
        self._patch_mark_file = os.path.join(root, "PATCH_VERSION")
        self._src_root = os.path.join(root, "src")

        self._image_suffixs = ["png", "jpg", "ico", "icns", "icon"]


    def apply_patchs(self):
        if not os.path.exists(self._patchs_path):
            return
        last_version = self.get_patch_version()
        print("Last patch version %s" % last_version)
        need_apply_patchs = self.get_apply_patchs(last_version)
        if not need_apply_patchs:
            print("There hasn't apply patch file")
            return

        print("Begin patching")
        self.execute_apply_patch(need_apply_patchs)
        print("End patching")


    def get_apply_patchs(self, last_patch_version):
        need_apply_patchs = []
        patch_files = os.listdir(self._patchs_path)
        # patch_files = [ patch_file for patch_file in patch_files if patch_file.endswith(".diff") ]
        patch_files = list(filter(lambda x: x.endswith(".diff"), patch_files))
        patch_files.sort(key=lambda x: int(x[:-5]))
        if len(last_patch_version) != 0:
            for i in range(0, len(patch_files)):
                version = patch_files[i].split(".")[0]
                if int(version) > int(last_patch_version):
                    need_apply_patchs.append(os.path.join(self._patchs_path, patch_files[i]))
        else:
            # need_apply_patchs = [ os.path.join(self._patchs_path, file) for file in patch_files ]
            need_apply_patchs = list(map(lambda x: os.path.join(self._patchs_path, x), patch_files))
        return need_apply_patchs


    def execute_apply_patch(self, need_apply_patchs):
        try:
            os.chdir(self._src_root)
            for patch in need_apply_patchs:
                cmd = "patch -p1 --ignore-whitespace < %s" %(patch)
                print("Apply patch cmd = %s" %(cmd))
                if subprocess.check_call(cmd, shell=True) == 0:
                    version = os.path.splitext(os.path.basename(patch))[0]
                    print("Apply patch %s success, update patch version to %s" %(patch, version))
                    self.update_patch_version(version)
                else:
                    print("Apply patch {} failed".format(patch))
                    sys.exit(-1)
        except Exception as e:
            print("Execute Apply patch cmd failed, error: %s" % e)
            raise


    def update_resource_file(self):
        if not os.path.exists(self._resource_dir):
            return
        for root, _, files in os.walk(self._resource_dir):
            for file in files:
                try:
                    if os.path.splitext(file)[-1][1:] not in self._image_suffixs:
                        continue
                    src_file = os.path.abspath(os.path.join(root, file))
                    dst_file = os.path.join(self._src_root, os.path.relpath(src_file, self._resource_dir))
                    print("copy %s to %s" %(src_file, dst_file))
                    shutil.copy(src_file, dst_file)
                except IOError as e:
                    print(e)
                    sys.exit(-1)


    def update_patch_version(self, version):
        with open(self._patch_mark_file, "w+") as f:
            f.write(version)
            f.close()


    def get_patch_version(self):
        if os.path.exists(self._patch_mark_file):
            with open(self._patch_mark_file, "r+") as f:
                version = f.read().strip()
                f.close()
                return version
        else:
            return ""


def apply_patchs(root):
    patch = Patch(root)
    patch.apply_patchs()
    patch.update_resource_file()


def main():
    root = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, os.pardir))
    apply_patchs(root, "patch_code", "resource", "PATCH_VERSION")


if __name__ == "__main__":
    main()