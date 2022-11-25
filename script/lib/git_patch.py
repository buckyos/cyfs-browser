import os
import sys
import subprocess
import json
import hashlib
import re
import datetime
import collections
import shutil

patch_suffix = '.patch'
patchinfo_suffix = '.patchinfo'

INDEX_PATTERN = re.compile(r'^diff --git \w/(.+) \w/(?P<FilePath>.+)')

FileInfo = collections.namedtuple('FileInfo', 'name hash')


def get_file_hash(file):
    assert os.path.exists(file)
    with open(file, 'rb') as f:
        sha1obj = hashlib.sha1()
        sha1obj.update(f.read())
        return sha1obj.hexdigest()

def get_patch_apply_to(full_file):
    origin_files = []
    with open(full_file, 'r') as f:
        for line in f.readlines():
            file_declaration = INDEX_PATTERN.match(line)
            if file_declaration:
                filename = file_declaration.group('FilePath')
                origin_files.append(filename)
    return origin_files

def git_cmd(command, **kwargs):
    try:
        print('Git Cmd : %s' % (' '.join(command)))
        subprocess.call(command, **kwargs)
    except subprocess.CalledProcessError as e:
        print('Git cmd %s failed, error: %s' % (command, e))
        raise

def reset_repo_files(src_path, all_repo_paths):
    if not isinstance(all_repo_paths, list):
        all_repo_paths = [ all_repo_paths ]
    try:
        cmd = ['git', 'checkout'] + all_repo_paths
        git_cmd(cmd, cwd=src_path)
    except Exception as e:
        msg = 'Reset repo files failed, error: %s' % e
        print(msg)
        sys.exit(msg)

def apply_patch(src_path, patch):
    try:
        cmd = ['git', 'apply', patch,
               '--ignore-space-change', '--ignore-whitespace']
        git_cmd(cmd, cwd=src_path)
    except Exception as e:
        msg = 'Apply patch cmd %s failed: %s' % (''.join(cmd), e)
        print(msg)
        sys.exit(msg)

def get_patch_info(patch_info):
    patch_infos = []
    with open(patch_info, 'r') as f:
        info = json.load(f)
        patch_infos.append(FileInfo(info['file'], info['hash']))
        for item in info['apply_to']:
            patch_infos.append(FileInfo(item['file'], item['hash']))
    return patch_infos

class GitPatch:
    def __init__(self, src_path, patch_base_path, patch_name):
        self._src_path = os.path.normpath(src_path)
        self._base_path = os.path.normpath(patch_base_path)
        self._patch_name = patch_name

        self._patch_path = os.path.normpath(os.path.join(self._base_path, self._patch_name))
        origin_files = get_patch_apply_to(self._patch_path)
        self._origin_files = [ os.path.normpath(x) for x in origin_files]

        pacth_info_file = self._patch_name[:-len(patch_suffix)] + patchinfo_suffix
        self._patch_info_path = os.path.normpath(os.path.join(self._base_path, pacth_info_file))

    def write_patch_info(self):
        json_string = dict()
        json_string['write_time'] = datetime.datetime.now()
        json_string['file'] = self._patch_name
        json_string['hash'] = get_file_hash(self._patch_path)
        origin_file_infos = json_string["apply_to"] = list()
        for origin_file in self._origin_files:
            origin_file_full_path = os.path.join(self._src_path, origin_file)
            file_hash = get_file_hash(origin_file_full_path)
            file_info = {'file': origin_file, 'hash': file_hash}
            origin_file_infos.append(file_info)

        with open(self._patch_info_path, 'w') as f:
            json.dump(json_string, f, indent=4, default=str)

    def reset_related_file(self):
        print('Begin Reset last modify file %s ' % (' '.join(self._origin_files)))
        reset_repo_files(self._src_path, self._origin_files)
        print('End Reset last modify file')

    def apply_patch(self):
        print('Begin Applying patche %s' % self._patch_path)
        apply_patch(self._src_path, self._patch_path)
        print('End Applying patche %s' % self._patch_path)

class GitPatcher:
    def __init__(self, src_path, patch_base_path, patchs):
        self._src_path = src_path
        self._patch_base_path = patch_base_path
        self._patchs = patchs
        self._git_patchs = []

    @property
    def src_path(self):
        return self._src_path

    @property
    def patch_base_path(self):
        return self._patch_base_path

    def get_src_file_hash(self, filename):
        full_path = os.path.normpath(os.path.join(self.src_path, filename))
        return get_file_hash(full_path)

    def get_patch_hash(self,filename):
        full_path = os.path.normpath(os.path.join(self.patch_base_path, filename))
        return get_file_hash(full_path)

    def check_if_needed_apply(self, patch_name):
        ''' Last remain patchinfo file will record same name pacth's hash
            if cureent patch file's hash is same like last pacth which have same name,
            it mean this patch no neened apply to chromium src file '''
        patch_info_file = patch_name[:-len(patch_suffix)] + patchinfo_suffix
        patch_info_file_abspath = os.path.normpath(os.path.join(self.patch_base_path, patch_info_file))
        if not os.path.exists(patch_info_file_abspath):
            return True

        all_file_infos = get_patch_info(patch_info_file_abspath)
        origin_file_have_changed = False
        for apply_info in all_file_infos[1:]:
            if self.get_src_file_hash(apply_info.name) != apply_info.hash:
                origin_file_have_changed = True
                print('Chromium src %s changed' % apply_info.name)
                break

        current_patch_hash = self.get_patch_hash(patch_name)
        last_record_patch_info = all_file_infos[0]
        assert last_record_patch_info.name == patch_name
        patch_file_have_changed = current_patch_hash != last_record_patch_info.hash
        if patch_file_have_changed or origin_file_have_changed:
            return True
        return False

    def apply_patchs(self):
        print('Begin apply patches for %s ' %self._src_path)

        for patch in self._patchs:
            if self.check_if_needed_apply(patch):
                git_patch = GitPatch(self.src_path, self.patch_base_path, patch)
                self._git_patchs.append(git_patch)
            else:
                print('Current patch %s is same as last patch, no needed apply patch' % patch)
        print('Found %s patch needs to be applied' % len(self._git_patchs))

        self.perform_apply_for_patches()

        self.handle_obsolet_patch_infos()
        print('End apply patches for %s ' %self._src_path)

    def perform_apply_for_patches(self):
        print('Begin perform apply patches')
        for patch in self._git_patchs:
            # Reset all repo files which may modify by this patch
            patch.reset_related_file()
            # Apply the patch
            patch.apply_patch()
            # update patchinfo
            patch.write_patch_info()
        print('End perform apply patches')

    def get_obsolet_patch_infos(self):
        patch_infos = filter(lambda x: x.endswith(
            patchinfo_suffix), os.listdir(self.patch_base_path))

        def check_if_needed_handle(patch_info):
            patch = patch_info[:-len(patchinfo_suffix)] + patch_suffix
            full_path = os.path.join(self.patch_base_path, patch)
            return not os.path.exists(full_path)

        return list(filter(check_if_needed_handle, patch_infos))

    def restore_last_modify_file(self, file_infos):

        def check_file_hash(filename, hash):
            return hash == get_file_hash(filename)

        for file_info in file_infos:
            full_path = os.path.join(self.src_path, file_info.name)
            if not os.path.exists(full_path): return
            if check_file_hash(full_path, file_info.hash):
                print('Origin file %s have no changed' % full_path)
                return

            reset_repo_files(self.src_path, file_info.name)
            if check_file_hash(full_path, file_info.hash):
                print('Change %s to initial state success' % full_path)
                return

            print('Change %s to initial state failed' % full_path)

    def handle_obsolet_patch_infos(self):
        print('Begin Handle obsolete patch infos')
        obsolet_patch_infos = self.get_obsolet_patch_infos()
        if not obsolet_patch_infos:
            print('No obsolete patch infos need delete')
            return

        full_paths = [os.path.join(self.patch_base_path, x)
                      for x in obsolet_patch_infos]
        for full_path in full_paths:
            origin_file_infos = get_patch_info(full_path)[1:]
            self.restore_last_modify_file(origin_file_infos)
            os.remove(full_path)

        print('End Handle obsolete patch infos')

    @classmethod
    def update(cls, root):
        root_src_path = os.path.join(root, 'src')
        root_resource_path = os.path.join(root, 'resource')
        change_json_file = os.path.join(root_resource_path, 'change_files.json')
        root_patch_base_path = os.path.join(root, 'patch_code')
        patch_json_file = os.path.join(root_patch_base_path, 'patch_files.json')
        patch_json_data = dict()
        try:
            with open(patch_json_file, 'r') as f:
                patch_json_data = json.load(f)
        except Exception as e:
            print('Read %s failed, error: %s' %(patch_json_file, e))

        for relpath, patchs in patch_json_data.items():
            src_path = os.path.normpath(os.path.join(root_src_path, relpath))
            patch_base_path = os.path.normpath(os.path.join(root_patch_base_path, relpath))
            git_patcher = cls(src_path, patch_base_path, patchs)
            git_patcher.apply_patchs()

        need_copy_files = []
        try:
            with open(change_json_file, 'r') as f:
                change_json_data = json.load(f)
                need_copy_files = change_json_data['Add']['files'] + change_json_data['Update']['files']
        except Exception as e:
            print('Read %s failed, error: %s' %(change_json_file, e))

        print('Begin copying files')
        for file in need_copy_files:
            file = os.path.normpath(file)
            src_file = os.path.normpath(os.path.join(root_resource_path, file))
            if not os.path.exists(src_file):
                continue
            is_dir = os.path.isdir(src_file)
            dst_file = os.path.join(root_src_path, file)
            if not os.path.exists(os.path.dirname(dst_file)):
                os.makedirs(os.path.dirname(dst_file), exist_ok=True)
            print('Update Resource File %s to %s' % (src_file, dst_file))
            if not is_dir:
                shutil.copy(src_file, dst_file)
            else:
                shutil.copytree(src_file, dst_file, dirs_exist_ok=True)
        print('End copying files')


def main():
    this_path = os.path.dirname(os.path.abspath(__file__))
    root = os.path.normpath(os.path.join(this_path, os.pardir, os.pardir))
    GitPatcher.update(root)

if __name__ == "__main__":
    main()
