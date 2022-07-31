import os
import sys
import shutil
import subprocess
import json
import datetime

patch_suffix = '.patch'
not_patched_suffix = ['.png', '.jpg', '.jpeg', '.ico', '.icon', '.svg', '.icns', '.grd', '.grdp', '.xtb']
not_patched_begin_path = ['out']
not_patched_end_path = []
not_patched_file = []

update_suffix = ['.xtb', '.grd', '.grdp']
update_files = ['chrome/browser/resources/cyfs_init/starting.png']
not_update_suffix = ['.log']

create_patch_args = ['--src-prefix=a/', '--dst-prefix=b/', '--full-index']
get_diff_args = ['--diff-filter=M', '--name-only', '--ignore-space-at-eol']


def check_patch_filter(file):
    is_need_patched = False
    if file in not_patched_file:
        return is_need_patched
    suffix = os.path.splitext(file)[1]
    if suffix in not_patched_suffix:
        return is_need_patched
    for begin_path in not_patched_begin_path:
        if file.startswith(begin_path):
            return is_need_patched
    for end_path in not_patched_end_path:
        if file.endswith(end_path):
            return is_need_patched
    return True


class UpdatePatcher:
    change_record = 'change_files.json'
    def __init__(self, root, src_path=[], patch_path=None, commid_ids=[], resource_path=None):
        assert len(commid_ids) == 2 or len(commid_ids) == 0
        self._root = root
        self._src_path = src_path or 'src'
        self._resource_path = resource_path or 'resource'
        self._patch_path = patch_path or 'patch_code'
        self._commid_ids = commid_ids

        self._success_patch = []
        self._failure_patch = []

    @property
    def src_path(self):
        return os.path.join(self._root, self._src_path)

    @property
    def change_record_file(self):
        return os.path.join(self.resource_path, self.change_record)

    @property
    def commid_ids(self):
        return self._commid_ids

    @property
    def patch_path(self):
        path = os.path.join(self._root, self._patch_path)
        os.makedirs(path, exist_ok=True)
        return path

    @property
    def resource_path(self):
        path = os.path.join(self._root, self._resource_path)
        os.makedirs(path, exist_ok=True)
        return path

    @staticmethod
    def git_cmd_output(command, **kwargs):
        try:
            print('Git Cmd: %s' % (' '.join(command)))
            return subprocess.check_output(command, **kwargs).decode('ascii').strip()
        except subprocess.CalledProcessError as e:
            print('Git cmd %s failed, error: %s' % (' '.join(command), e))
            raise

    @staticmethod
    def git_cmd(command, **kwargs):
        try:
            print('Git Cmd: %s' % (' '.join(command)))
            return subprocess.call(command, **kwargs)
        except subprocess.CalledProcessError as e:
            print('Git cmd %s failed, error: %s' % (' '.join(command), e))
            raise

    @staticmethod
    def get_unstaged_files(src_path):
        ''' Returns a dict mapping modified file paths (relative to checkout root)
            to one-character codes identifying the change, e.g. 'M' for modified,
            'D' for deleted, '?' for untracked.
        '''
        cmd = ['git', 'status', '-z', '--untracked-files=all']
        change_lines = UpdatePatcher.git_cmd_output(
            cmd, cwd=src_path).rstrip('\x00')
        unstaged_changes = dict()
        for line in change_lines.split('\x00'):
            assert len(line) >= 4, 'Unexpected change line format %s' % line
            if line[1] == ' ':
                continue  # Already staged for commit.
            path = line[3:]
            unstaged_changes[path] = line[1]
        return unstaged_changes

    def add_patch_status(self, patch_name, is_ok=True):
        if is_ok:
            self._success_patch.append(patch_name)
        else:
            self._failure_patch.append(patch_name)

    def get_modified_paths(self):
        cmd = ['git', 'diff']
        cmd.extend(self.commid_ids)
        cmd.extend(get_diff_args)
        all_paths = UpdatePatcher.git_cmd_output(
            cmd, cwd=self.src_path).splitlines()
        print('The following files have changed:\n %s \n' %
              (' \n'.join(all_paths)))
        return list(filter(check_patch_filter, all_paths))

    def write_patch_file(self, origin_file):
        is_ok = True
        try:
            patch_name = origin_file.replace('/', '-') + patch_suffix
            full_path = os.path.join(self.patch_path, patch_name)
            cmd = ['git', 'diff']
            cmd.extend(self.commid_ids)
            cmd.append('--output=%s' % full_path)
            cmd.extend(create_patch_args)
            cmd.append(origin_file)
            UpdatePatcher.git_cmd(cmd, cwd=self.src_path)
            print('Create patch file: %s success' % full_path)
        except Exception as e:
            print('Write patch file %s is not available, origin file %s, error: %s' % (
                full_path, origin_file, e))
            is_ok = False
        finally:
            self.add_patch_status(patch_name, is_ok)

    def write_patch_files(self):
        print('Begin write pacth files')
        modify_files = self.get_modified_paths()
        for path in modify_files:
            print('%s need create patch' % path)
            assert os.path.exists(os.path.join(self.src_path, path))
            self.write_patch_file(path)
        print('End write pacth files')

    def delete_last_create_patch(self):
        print('Begin delete last create patchs')
        all_files = os.listdir(self.patch_path)
        all_patch_files = [x for x in all_files if x.endswith('.patch')]
        remove_patchs = [
            x for x in all_patch_files if x not in self._success_patch]
        for path in remove_patchs:
            full_path = os.path.join(self.patch_path, path)
            print('Delete patch file %s' % full_path)
            os.remove(full_path)
        print('End delete last create patchs')

    def create_patch(self):
        self.write_patch_files()
        self.delete_last_create_patch()
        if self._failure_patch:
            print('Patch failed: %s' % ' '.join(self._failure_patch))

    def update_change_file_record(self, change_infos):
        json_string = dict()
        for action, file_records in change_infos.items():
            change_file_info = json_string[action] = dict()
            change_file_info['update_time'] = datetime.datetime.now()
            change_file_info['files'] = file_records
        full_path = os.path.join(self.resource_path, self.change_record)
        with open(full_path, 'w') as f:
            json.dump(json_string, f, indent=4, default=str)

    def get_files_by_action(self, action_):
        unstaged_file_infos = UpdatePatcher.get_unstaged_files(self.src_path)
        return [file for (file, action) in unstaged_file_infos.items() if action == action_]

    def update_change_files(self):
        ''' Update the change files which untracked by current repository
            and record the change files to json file for apply patches
        '''
        print('Begin update add files')
        unstaged_files = self.get_files_by_action('?')
        unstaged_files = [x for x in unstaged_files if os.path.splitext(x)[
            1] not in not_update_suffix]
        unstaged_files += update_files
        staged_files = self.get_files_by_action('M')
        staged_files = [x for x in staged_files if os.path.splitext(x)[
            1] in not_patched_suffix]
        need_copy_files = unstaged_files + staged_files
        for file in need_copy_files:
            src_path = os.path.join(self.src_path, file)
            is_dir = os.path.isdir(src_path)
            dst_path = os.path.join(self.resource_path, file)
            os.makedirs(os.path.dirname(dst_path), exist_ok=True)
            print('Copy %s to %s' % (src_path, dst_path))
            if not is_dir:
                shutil.copy(src_path, dst_path)
            else:
                shutil.copytree(src_path, dst_path, dirs_exist_ok=True)
        change_infos = {'Add': unstaged_files, 'Update': staged_files}
        self.update_change_file_record(change_infos)
        print('End update add files')

    @classmethod
    def update_patch(cls, root):
        update_patcher = cls(root)
        update_patcher.create_patch()
        update_patcher.update_change_files()


def main():
    this_path = os.path.dirname(os.path.abspath(__file__))
    root = os.path.normpath(os.path.join(this_path, os.pardir, os.pardir))
    # commit_ids = ['dd97e81','f659c44']
    UpdatePatcher.update_patch(root)


if __name__ == '__main__':
    try:
        # print(str(sys.argv))
        # sys.exit(main(sys.argv[1:]))
        main()
    except KeyboardInterrupt:
        sys.stderr.write("interrupted\n")
        sys.exit(1)
