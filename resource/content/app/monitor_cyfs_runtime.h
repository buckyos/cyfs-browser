#ifndef CONTENT_APP_MONITOR_CYFS_RUNTIME_IMPL_H_
#define CONTENT_APP_MONITOR_CYFS_RUNTIME_IMPL_H_

#include <vector>
#include <string>
#include <map>

#include "base/sequence_checker.h"
#include "base/time/clock.h"
#include "base/time/tick_clock.h"
#include "base/time/time.h"
#include "base/timer/timer.h"

#include "base/command_line.h"
#include "base/process/launch.h"
#include "base/process/process.h"
#include "base/process/process_handle.h"
#include "base/process/process_iterator.h"
#include "base/process/kill.h"
#include "base/threading/thread.h"
#include "base/files/file_util.h"
#include "base/files/file_path.h"
#include "base/path_service.h"

#include "base/memory/weak_ptr.h"

#include "chrome/common/pref_names.h"
#include "chrome/browser/profiles/profile.h"
#include "components/prefs/pref_service.h"
#include "chrome/browser/profiles/profile_manager.h"


class MonitorRuntimeWork {
public:

  MonitorRuntimeWork();

  ~MonitorRuntimeWork();
private:
  void StartMonitorWork();

  void StopMonitorWork();

  void MonitorWork();

  void StopRuntimeProcess(const std::vector<base::FilePath>& binary_paths);

  void CheckRuntimeProcessRunStatus(base::FilePath::StringType process_name);

  void StartRuntimeProcess(base::FilePath::StringType process_name);

  base::Process StartCYFSRuntimeProcess();

  base::Process StartIPFSRuntimeProcess();

private:

  std::unique_ptr<base::Thread> thread_;
  base::RepeatingTimer timer_;

  base::WeakPtrFactory<MonitorRuntimeWork> weak_factory_{this};
};

#endif