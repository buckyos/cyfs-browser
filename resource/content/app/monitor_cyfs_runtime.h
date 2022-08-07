#ifndef CONTENT_APP_MONITOR_CYFS_RUNTIME_IMPL_H_
#define CONTENT_APP_MONITOR_CYFS_RUNTIME_IMPL_H_

#include <vector>
#include "base/logging.h"
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
#include "base/observer_list.h"

#include "base/memory/weak_ptr.h"

#include "chrome/common/pref_names.h"
#include "chrome/browser/profiles/profile.h"
#include "components/prefs/pref_service.h"
#include "chrome/browser/profiles/profile_manager.h"


using ExePath = base::FilePath::StringType;

#if BUILDFLAG(IS_WIN)
class ProcessPathPrefixFilter : public base::ProcessFilter {
 public:
  explicit ProcessPathPrefixFilter(const ExePath& process_path_prefix);

  // base::ProcessFilter:
  bool Includes(const base::ProcessEntry& entry) const override;

 private:
  const ExePath process_path_prefix_;
};
#endif

class MonitorRuntimeWork {
public:

  class Observer {
   public:
    Observer() {}
    virtual ~Observer() {}
    virtual void OnChangeRuntimePort(int port) = 0;

  };

  MonitorRuntimeWork(int interval);

  ~MonitorRuntimeWork();

  void StartMonitorWork();

  void StopMonitorWork();

  void AddObserver(Observer* observer);

  void RemoveObserver(Observer* observer);

private:
  void MonitorWork();

  void CheckRuntimeProcessRunStatus();

  base::FilePath GetLocalAppData();

  base::FilePath GetRuntimeExeDir();

  base::Process StartRuntimeProcessCore(bool anonymous, int proxy_port);

  uint16_t GetavailableTcpPort();

#if BUILDFLAG(IS_WIN)
  std::vector<uint16_t> GetAllTcpConnectionsPort();

  bool IsParentProcess(const base::ProcessId& son_process_id,
                              const base::ProcessId& parent_process_id);

  std::vector<base::ProcessId> FindProcesses(const ExePath& executable_name,
                              const base::ProcessFilter* filter);

  base::Process LaunchRuntimeProcess(const base::CommandLine& cmdline,
                              const base::LaunchOptions& options);
#else
  std::vector<base::ProcessId> FindProcesses(const ExePath& executable_name);
#endif
  bool IsRuntimeBinding();

  void StartRuntimeProcess();

  void updateRuntimePort(int port);

private:
  std::unique_ptr<base::Thread> thread_;
  base::RepeatingTimer timer_;
  base::TimeDelta cycleTime_;
  std::vector<base::ProcessId> process_list_{};
  int last_runtime_port_{38090};
  int default_runtime_port_{38090};

  base::ObserverList<Observer>::Unchecked observer_list_;
  base::WeakPtrFactory<MonitorRuntimeWork> weak_factory_{this};
};

#endif