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
root_update_files = ['chrome/browser/resources/cyfs_init/starting.png']
update_files = []
not_update_suffix = ['.log']

create_patch_args = ['--src-prefix=a/', '--dst-prefix=b/', '--full-index']
get_diff_args = ['--diff-filter=M', '--name-only', '--ignore-space-at-eol']

sub_paths = ['third_party\devtools-frontend\src']


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
    patch_record = 'patch_files.json'
    def __init__(self, root, src_path, root_patch_path, root_resource_path, is_3rd_party = False, commid_ids=[]):
        assert len(commid_ids) == 2 or len(commid_ids) == 0
        self._root = root
        self._root_src_path = os.path.join(root, "src")
        self._src_path = src_path
        self._is_3rd_party = is_3rd_party
        self._root_resource_path = root_resource_path
        self._root_patch_path = root_patch_path

        self._resource_path = root_resource_path
        self._patch_path = root_patch_path
        if self._is_3rd_party:
            relpath = os.path.relpath(self._src_path, self._root_src_path)
            self._patch_path = os.path.join(root_patch_path, relpath)

        self._commid_ids = commid_ids

        self._success_patch = []
        self._failure_patch = []

    @property
    def src_path(self):
        return self._src_path

    @property
    def change_record_file(self):
        return os.path.join(self._root_resource_path, self.change_record)

    @property
    def patch_record_file(self):
        return os.path.join(self._root_patch_path, self.patch_record)

    @property
    def commid_ids(self):
        return self._commid_ids

    @property
    def patch_path(self):
        os.makedirs(self._patch_path, exist_ok=True)
        return self._patch_path

    @property
    def resource_path(self):
        os.makedirs(self._resource_path, exist_ok=True)
        return self._resource_path

    @staticmethod
    def git_cmd_output(command, **kwargs):
        try:
            print('Git Cmd: %s' % (' '.join(command)))
            return subprocess.check_output(command, **kwargs).decode('utf-8').strip()
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
        print(change_lines)
        unstaged_changes = dict()
        try:
            for line in change_lines.split('\x00'):
                assert len(line) >= 4, 'Unexpected change line format %s' % line
                if line[1] == ' ':
                    continue  # Already staged for commit.
                path = line[3:]
                unstaged_changes[path] = line[1]
        except Exception as e:
            print('get_unstaged_files failed: %s' % e)
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

    def update_patch_records(self):
        relpath = os.path.relpath(self.patch_path, self._root_patch_path)
        json_data = dict()
        try:
            with open(self.patch_record_file, 'r') as f:
                json_data = json.load(f)
        except Exception as e:
            print('load json failed: %s' % e)

        json_data.update({relpath: self._success_patch})
        with open(self.patch_record_file, 'w') as f:
            json.dump(json_data, f, indent=4, default=str)


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
        self.update_patch_records()
        self.delete_last_create_patch()
        if self._failure_patch:
            print('Patch failed: %s' % ' '.join(self._failure_patch))

    def update_change_file_record(self, change_infos):
        ### first update for chromium source code
        if not self._is_3rd_party:
            json_string = dict()
            for action, file_records in change_infos.items():
                change_file_info = json_string[action] = dict()
                change_file_info['update_time'] = datetime.datetime.now()
                change_file_info['files'] = file_records
            with open(self.change_record_file, 'w') as f:
                json.dump(json_string, f, indent=4, default=str)
        ### for 3rd party code
        else:
            json_data = dict()
            with open(self.change_record_file, 'r') as f:
                json_data = json.load(f)
            relpath = os.path.relpath(self._src_path, self._root_src_path)

            for action, file_records in change_infos.items():
                    file_records = [ (relpath + os.sep + file_name) for file_name in file_records]
                    file_records = [ os.path.normpath(x) for x in file_records]
                    json_data[action]['files'] += file_records
                    json_data[action]['update_time'] = datetime.datetime.now()
            with open(self.change_record_file, 'w') as f:
                json.dump(json_data, f, indent=4, default=str)


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
        if not self._is_3rd_party:
            unstaged_files += root_update_files
        staged_files = self.get_files_by_action('M')
        staged_files = [x for x in staged_files if os.path.splitext(x)[
            1] in not_patched_suffix]
        need_copy_files = unstaged_files + staged_files
        for file in need_copy_files:
            src_path = os.path.join(self.src_path, file)
            is_dir = os.path.isdir(src_path)
            relpath = os.path.relpath(self.src_path, self._root_src_path)
            dst_path = os.path.join(self.resource_path, relpath, file)
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
    def update_patch(cls, root, src_path, resource_path, patch_path, is_3rd_party):
        update_patcher = cls(root, src_path, resource_path, patch_path, is_3rd_party)
        update_patcher.create_patch()
        update_patcher.update_change_files()


def main(args):
    print('Begin create patch')
    this_path = os.path.dirname(os.path.abspath(__file__))
    root = os.path.normpath(os.path.join(this_path, os.pardir))

    root_patch_path = os.path.join(root, 'patch_code')
    root_resource_path = os.path.join(root, 'resource')
    # change_record_file = os.path.join(root_resource_path, 'change_files.json')


    ### Create patch for chromium src
    print('Begin create patch for chromium src')
    src_path = os.path.join(root, 'src')
    UpdatePatcher.update_patch(root, src_path, root_patch_path, root_resource_path, False)
    print('End create patch for chromium src')

    ## Crearte patch for chromium 3rd party src
    print('Begin create patch for chromium 3rd party src')
    for sub_path in sub_paths:
        src_path = os.path.join(src_path, sub_path)
        assert os.path.exists(src_path)
        UpdatePatcher.update_patch(root, src_path, root_patch_path, root_resource_path, True)
    print('End create patch for chromium src')

    print('End create patch')


if __name__ == '__main__':
    try:
        print(str(sys.argv))
        sys.exit(main(sys.argv[1:]))
    except KeyboardInterrupt:
        sys.stderr.write("interrupted\n")
        sys.exit(1)
