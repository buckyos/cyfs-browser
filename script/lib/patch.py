import shutil
import subprocess
import os
import sys

def excute_patch_cmd(patch, reverse=False):
    try:
        # patch -p1 --ignore-whitespace < patch
        cmd = ["patch", "-p1", "--ignore-whitespace", "-i", patch]
        if reverse: cmd.append("-R")
        print("Apply patch cmd = %s" % (" ".join(cmd)))
        subprocess.run(cmd, check=True)
    except Exception as e:
        print("Execute patch cmd %s failed, error: %s" % (cmd, e))
        raise

def get_version_from_file(file):
    file_name = os.path.basename(file)
    return file_name.split(".")[0]
class Patch:
    patch_suffix = ".diff"
    def __init__(self, root):
        self._root = root
        self._version = None
        self.get_patch_version()

    @property
    def src_path(self):
        return os.path.join(self._root, "src")

    @property
    def patch_base_path(self):
        return os.path.join(self._root, "patch_code")

    @property
    def resource_base_path(self):
        return os.path.join(self._root, "resource")

    @property
    def patch_version_file(self):
        return os.path.join(self._root, "PATCH_VERSION")

    def apply_patchs(self):
        if not os.path.exists(self.patch_base_path): return
        print("Last patch version %s" % (self._version if self._version else "----"))

        def check_need_apply(file):
            version = get_version_from_file(file)
            return int(version) > int(self._version)

        all_patch_files = list(filter(lambda x: x.endswith(
            self.patch_suffix), os.listdir(self.patch_base_path)))
        all_patch_files.sort(key=lambda x: int(x[:-len(self.patch_suffix)]))
        patches_to_apply = all_patch_files

        if self._version is not None:
            patches_to_apply = list(
                filter(lambda x: check_need_apply(x), all_patch_files))

        patches_to_apply = list(map(lambda x: os.path.join(
            self.patch_base_path, x), patches_to_apply))
        if not patches_to_apply:
            print("Current patch is latest, no need to apply")
            return

        print("Begin patching")
        os.chdir(self.src_path)
        for patch in patches_to_apply:
            excute_patch_cmd(patch)
            print("Apply patch %s success" % patch)
            self.update_patch_version(patch)
        print("End patching")

    def update_resource_file(self):
        if not os.path.exists(self.resource_base_path): return

        def _update_if_needed(file_name):
            image_suffixs = ["png", "jpg", "ico", "icns", "icon"]
            return bool([ext for ext in image_suffixs if file_name.lower().endswith(ext)])

        for root, _, files in os.walk(self.resource_base_path):
            copy_files = filter(lambda x: _update_if_needed(x), files)
            copy_files = map(lambda x: os.path.join(root, x), copy_files)
            for f in copy_files:
                dst_file = os.path.join(self.src_path, os.path.relpath(f, self.resource_base_path))
                os.makedirs(os.path.dirname(dst_file), exist_ok=True)
                shutil.copy(f, dst_file)

    def update_patch_version(self, patch):
        try:
            version = get_version_from_file(patch)
            self._version = version
            with open(self.patch_version_file, "w+") as f:
                f.write(version)
        except Exception as e:
            print("Update patch version failed, error: %s" % e)
            sys.exit(-1)

    def get_patch_version(self):
        try:
            if os.path.exists(self.patch_version_file):
                with open(self.patch_version_file, "r+") as f:
                    self._version = f.read().strip()
        except Exception as e:
            print("Get patch version failed, error: %s" % e)

def apply_patchs(root):
    patch = Patch(root)
    patch.apply_patchs()
    patch.update_resource_file()

def main():
    root = os.path.normpath(
        os.path.join(os.path.dirname(os.path.abspath(__file__)),
                     os.pardir, os.pardir)
    )
    apply_patchs(root)

if __name__ == "__main__":
    main()
