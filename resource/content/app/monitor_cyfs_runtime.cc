
#include "content/app/monitor_cyfs_runtime.h"
#include "build/build_config.h"
#include "base/logging.h"
#include "base/process/process_handle.h"
#include "base/task/task_runner_util.h"


namespace {
#if BUILDFLAG(IS_WIN)
  constexpr base::FilePath::CharType kCYFSRuntimeExecuteName[] = FILE_PATH_LITERAL("cyfs-runtime.exe");
  constexpr base::FilePath::CharType kIPFSRuntimeExecuteName[] = FILE_PATH_LITERAL("ipfs-proxy.exe");
#else
  constexpr base::FilePath::CharType kCYFSRuntimeExecuteName[] = FILE_PATH_LITERAL("cyfs-runtime");
  constexpr base::FilePath::CharType kIPFSRuntimeExecuteName[] = FILE_PATH_LITERAL("ipfs-proxy");
#endif

  static constexpr int kDefaultCYFSRuntimePort = 38090;
  static constexpr int kDefaultIPFSRuntimePort = 38095;

  static constexpr base::TimeDelta check_delta = base::Seconds(2);

base::FilePath GetLocalAppData() {
  base::FilePath app_data_dir;
  int key = base::DIR_ROAMING_APP_DATA;
#if BUILDFLAG(IS_MAC)
  key = base::DIR_APP_DATA;
#endif
  if (!base::PathService::Get(key, &app_data_dir)) {
    VLOG(1) << "Can't get app data dir";
  }
  return app_data_dir;
}

base::FilePath GetRuntimeExeDir() {
  base::FilePath file_path = GetLocalAppData();
  if (file_path.empty()) {
    return base::FilePath();
  }
  return file_path.AppendASCII("cyfs").AppendASCII("services").AppendASCII("runtime");
}

bool IsRuntimeBinding() {
  auto file_path = GetLocalAppData().AppendASCII("cyfs").AppendASCII("etc").AppendASCII("desc");
  auto desc_file = file_path.AppendASCII("device.desc");
  auto sec_file = file_path.AppendASCII("device.sec");
  auto desc_files = { desc_file, desc_file };
  auto pred = [](const base::FilePath& path) { return base::PathExists(path); };
  bool is_bind = std::all_of(desc_files.begin(), desc_files.end(), pred);
  VLOG(1) << "Current user is " << (is_bind ? "bind" : "not bind");
  return is_bind;
}

base::Process LaunchProcess(const base::FilePath& path,
                    std::vector<std::string>& args,
                    const base::LaunchOptions& options) {
  base::CommandLine cmdLine(path);
  for (auto arg : args) {
    cmdLine.AppendArg(arg);
  }
  base::Process process = base::LaunchProcess(cmdLine, options);
  if (process.IsValid()) {
    VLOG(1) << "Launch process " << path << " successfully, with pid " << process.Pid();
  } else {
    VLOG(1) << "Launch process " << path << " failed";
  }
  return process;
}

}

MonitorRuntimeWork::MonitorRuntimeWork() {
  LOG(INFO) << __FUNCTION__;
  thread_ = std::make_unique<base::Thread>("Monitor-Runtime-Thread");
  thread_->Start();
  thread_->task_runner()->PostTask(
      FROM_HERE,
      base::BindOnce(
          &MonitorRuntimeWork::MonitorWork,
          weak_factory_.GetWeakPtr()));
  thread_->task_runner()->PostTask(
      FROM_HERE,
      base::BindOnce(
          &MonitorRuntimeWork::StartMonitorWork,
          weak_factory_.GetWeakPtr()));
}

MonitorRuntimeWork::~MonitorRuntimeWork() {
  StopMonitorWork();
}

void MonitorRuntimeWork::StartMonitorWork() {
  LOG(INFO) << __FUNCTION__;
  timer_.Start(FROM_HERE, check_delta, this, &MonitorRuntimeWork::MonitorWork);
}

void MonitorRuntimeWork::StopMonitorWork() {
  LOG(INFO) << __FUNCTION__;
  auto ipfs_binary_path = GetRuntimeExeDir().Append(kIPFSRuntimeExecuteName);
  auto cyfs_binary_path = GetRuntimeExeDir().Append(kCYFSRuntimeExecuteName);
  std::vector<base::FilePath> binary_paths = {ipfs_binary_path, cyfs_binary_path};
  StopRuntimeProcess(binary_paths);

  timer_.Stop();
  if (thread_) {
    thread_->Stop();
    thread_.reset(nullptr);
  }
  for (auto binary_path: binary_paths) {
    base::KillProcesses(binary_path.value(), -1, nullptr);
  }
}

void MonitorRuntimeWork::StopRuntimeProcess(const std::vector<base::FilePath>& binary_paths) {
  for (auto binary_path : binary_paths) {
    if (!base::PathExists(binary_path)) {
      LOG(ERROR) << "Can't find executable file " << binary_path;
      return;
    }
    std::vector<std::string> args{"--stop"};
    base::LaunchOptions launchopts;
  #if BUILDFLAG(IS_WIN)
    launchopts.start_hidden = true;
  #endif
    (void)LaunchProcess(binary_path, args, launchopts);
  }
}

void MonitorRuntimeWork::MonitorWork() {
  LOG(INFO) << "Check runtime process status";
  CheckRuntimeProcessRunStatus(kCYFSRuntimeExecuteName);
  CheckRuntimeProcessRunStatus(kIPFSRuntimeExecuteName);
}

base::Process MonitorRuntimeWork::StartIPFSRuntimeProcess() {
  LOG(INFO) << __FUNCTION__;
  auto binary_path = GetRuntimeExeDir().Append(kIPFSRuntimeExecuteName);
  if (!base::PathExists(binary_path)) {
    LOG(ERROR) << "Can't find executable file " << binary_path;
    return base::Process();
  }

  std::vector<std::string> args;
  args.push_back(std::string("--proxy-port=") + (std::to_string(kDefaultIPFSRuntimePort)));

  base::LaunchOptions launchopts;
#if BUILDFLAG(IS_WIN)
  launchopts.start_hidden = true;
#endif

  return LaunchProcess(binary_path, args, launchopts);
}

base::Process MonitorRuntimeWork::StartCYFSRuntimeProcess() {
  LOG(INFO) << __FUNCTION__;
  auto binary_path = GetRuntimeExeDir().Append(kCYFSRuntimeExecuteName);
  if (!base::PathExists(binary_path)) {
    LOG(ERROR) << "Can't find executable file " << binary_path;
    return base::Process();
  }

  std::vector<std::string> args;
  if (!IsRuntimeBinding()) {
    args.push_back("--anonymous");
  }
  args.push_back(std::string("--proxy-port=") + (std::to_string(kDefaultCYFSRuntimePort)));

  base::LaunchOptions launchopts;
#if BUILDFLAG(IS_WIN)
  launchopts.start_hidden = true;
#endif

  return LaunchProcess(binary_path, args, launchopts);
}

void MonitorRuntimeWork::StartRuntimeProcess(base::FilePath::StringType process_name) {
  base::Process process;
  if (process_name == kCYFSRuntimeExecuteName) {
    process = StartCYFSRuntimeProcess();
  } else if (process_name == kIPFSRuntimeExecuteName) {
    process = StartIPFSRuntimeProcess();
  }
  if (process.IsValid()) {
      LOG(INFO) << "Reload runtime process " << process_name << " successfully.";
  } else {
      LOG(INFO) << "Reload runtime process " << process_name << " failed.";
  }
}

void MonitorRuntimeWork::CheckRuntimeProcessRunStatus(base::FilePath::StringType process_name) {
  LOG(INFO) << __FUNCTION__;
  std::vector<base::ProcessId> all_pids;
  {
    base::NamedProcessIterator process_it(process_name, nullptr);
    while (const base::ProcessEntry* entry = process_it.NextProcessEntry()) {
      all_pids.push_back(entry->pid());
    }
  }
  if (all_pids.empty()) {
    LOG(INFO) << "Not found running runtime process. maybe need reload";
    StartRuntimeProcess(process_name);
  } else {
    LOG(INFO) << process_name << " is running.";
  }
}


