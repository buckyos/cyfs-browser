
#include "content/app/monitor_cyfs_runtime.h"
#include "build/build_config.h"

#if BUILDFLAG(IS_WIN)
#include <Windows.h>
#include <shlobj.h>
#include <tcpmib.h>
#include <IPHlpApi.h>
#include <WinSock2.h>
#include <shellapi.h>

#pragma comment(lib,"ws2_32.lib")
#pragma comment(lib,"Iphlpapi.lib")
#endif

namespace {
#if BUILDFLAG(IS_WIN)
  const wchar_t kExecuteName[] = L"cyfs-runtime.exe";
  const wchar_t kCyfsDir[] = L"cyfs";
  const wchar_t kServicesDir[] = L"services";
  const wchar_t kRuntimeDir[] = L"runtime";
#else
  const char kExecuteName[] = "cyfs-runtime";
  const char kCyfsDir[] = "cyfs";
  const char kServicesDir[] = "services";
  const char kRuntimeDir[] = "runtime";
#endif

  const char KAnonymous[] = "--anonymous";
  static constexpr int kMinPort = 8090;
  static constexpr int kMaxPort = 65535;
  static bool kUseDefaultPort = true;
}

#if BUILDFLAG(IS_WIN)
ProcessPathPrefixFilter::ProcessPathPrefixFilter(const ExePath& process_path_prefix)
  : process_path_prefix_(process_path_prefix) {}

// base::ProcessFilter:
bool ProcessPathPrefixFilter::Includes(const base::ProcessEntry& entry) const {
  // Test if |entry|'s file path starts with the prefix we're looking for.
  base::Process process(::OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION,
                                      FALSE, entry.th32ProcessID));
  if (!process.IsValid())
    return false;

  DWORD path_len = MAX_PATH;
  wchar_t path_string[MAX_PATH];
  if (::QueryFullProcessImageName(process.Handle(), 0, path_string,
                                  &path_len)) {
    base::FilePath file_path(path_string);
    return base::StartsWith(file_path.value(), process_path_prefix_,
                            base::CompareCase::INSENSITIVE_ASCII);
  }
  LOG(WARNING) << "QueryFullProcessImageName failed for PID "
                << entry.th32ProcessID;
  return false;
}
#endif

MonitorRuntimeWork::MonitorRuntimeWork(int interval) {
  cycleTime_ = base::Seconds(interval);
  thread_ = std::make_unique<base::Thread>("Monitor-Cyfs-Runtime-Thread");
  thread_->Start();
  thread_->task_runner()->PostTask(FROM_HERE,
        base::BindOnce(&MonitorRuntimeWork::StartRuntimeProcess, weak_factory_.GetWeakPtr()));
  thread_->task_runner()->PostTask(FROM_HERE,
        base::BindOnce(&MonitorRuntimeWork::StartMonitorWork, weak_factory_.GetWeakPtr()));
}

MonitorRuntimeWork::~MonitorRuntimeWork() {
  StopMonitorWork();
}

void MonitorRuntimeWork::StartMonitorWork() {
  timer_.Start(FROM_HERE, cycleTime_, this, &MonitorRuntimeWork::MonitorWork);
}

void MonitorRuntimeWork::StopMonitorWork() {
  LOG(INFO) << "MonitorRuntimeWork::StopMonitorWork";
#if BUILDFLAG(IS_WIN)
  {
    ProcessPathPrefixFilter target_path_filter(GetRuntimeExeDir().value());
    base::KillProcesses(kExecuteName, 0 , &target_path_filter);
  }
#else
  for (auto process_id : process_list_) {
    base::Process process = base::Process::Open(process_id);
    if (process.IsValid()) {
      LOG(INFO) << "Stop runtime work process, pid = " << std::to_string(process_id);
      auto pid = process.Pid();
      int result = kill(pid, SIGKILL);
      if (result == -1) {
        LOG(ERROR) << "kill(" << pid << ", SIGKILL)";
      } else {
        // The child is definitely on the way out now. BlockingReap won't need to
        // wait for long, if at all.
        const pid_t result = HANDLE_EINTR(waitpid(pid, NULL, 0));
        if (result == -1) {
            LOG(ERROR) << "waitpid(" << pid << ", NULL, 0)";
        }
      }
    }
  }
  #endif
  timer_.Stop();
}

void MonitorRuntimeWork::AddObserver(Observer* observer) {
  observer_list_.AddObserver(observer);
}

void MonitorRuntimeWork::RemoveObserver(Observer* observer) {
  observer_list_.RemoveObserver(observer);
}

void MonitorRuntimeWork::MonitorWork() {
  LOG(INFO) << "check cyfs runtime process status";
  CheckRuntimeProcessRunStatus();
}

base::FilePath MonitorRuntimeWork::GetLocalAppData() {
#if BUILDFLAG(IS_WIN)
  wchar_t system_buffer[MAX_PATH];
  if (FAILED(SHGetFolderPath(nullptr, CSIDL_APPDATA, nullptr, SHGFP_TYPE_CURRENT,
                            system_buffer)))
    return base::FilePath();
  return base::FilePath(system_buffer);
#else
  base::FilePath app_data_dir;
  if (!base::PathService::Get(base::DIR_APP_DATA, &app_data_dir)) {
    return base::FilePath();
  }
  return app_data_dir;
#endif
}

base::FilePath MonitorRuntimeWork::GetRuntimeExeDir() {
  base::FilePath file_path = GetLocalAppData();
  if (file_path.empty()) {
    VLOG(1) << "Can't get app data dir";
  }
  return file_path.Append(kCyfsDir).Append(kServicesDir).Append(kRuntimeDir);
}

base::Process MonitorRuntimeWork::StartRuntimeProcessCore(bool anonymous, int proxy_port) {
  auto exe_path = GetRuntimeExeDir().Append(kExecuteName);
  if (!base::PathExists(exe_path)) {
    LOG(ERROR) << "Can't find runtime executable in path " << exe_path;
    return base::Process();
  }

  base::CommandLine command_line(exe_path);
  if (anonymous) {
    command_line.AppendArg(KAnonymous);
  }
  command_line.AppendArg(std::string("--proxy-port=") + (std::to_string(proxy_port)));
  base::LaunchOptions launchopts;
#if BUILDFLAG(IS_WIN)
  launchopts.start_hidden = true;
  base::Process runtime_process = LaunchRuntimeProcess(command_line, launchopts);
#else
  base::Process runtime_process = base::LaunchProcess(command_line, launchopts);
#endif

  if (runtime_process.IsValid()) {
    LOG(INFO) << "Start runtime process success, Pid = " << runtime_process.Pid();
    return runtime_process;
  } else {
    LOG(INFO) << "Start runtime process failed";
    return base::Process();
  }
}

#if BUILDFLAG(IS_WIN)
base::Process MonitorRuntimeWork::LaunchRuntimeProcess(const base::CommandLine& cmdline,
                              const base::LaunchOptions& options) {
  const base::FilePath::StringType file = cmdline.GetProgram().value();
  const base::CommandLine::StringType arguments = cmdline.GetArgumentsString();
  LPWSTR work_path_str = const_cast<LPWSTR>(GetRuntimeExeDir().value().c_str());

  SHELLEXECUTEINFO shex_info = {};
  shex_info.cbSize = sizeof(shex_info);
  shex_info.fMask =  SEE_MASK_NOCLOSEPROCESS | SEE_MASK_NO_CONSOLE ;
  shex_info.hwnd = GetActiveWindow();
  shex_info.hwnd = nullptr;
  // shex_info.lpVerb = L"runas";
  shex_info.lpFile = file.c_str();
  shex_info.lpParameters = arguments.c_str();
  shex_info.lpDirectory = work_path_str;
  shex_info.nShow = options.start_hidden ? SW_HIDE : SW_SHOWNORMAL;
  shex_info.hInstApp = nullptr;

  if (!ShellExecuteEx(&shex_info)) {
    DPLOG(ERROR);
    return base::Process();
  }

  if (options.wait)
    WaitForSingleObject(shex_info.hProcess, INFINITE);

  return base::Process(shex_info.hProcess);
}

std::vector<uint16_t> MonitorRuntimeWork::GetAllTcpConnectionsPort() {
  std::vector<uint16_t> idle_ports;
  ULONG size = 0;
  GetTcpTable(nullptr, &size, TRUE);
  std::unique_ptr<char[]> buffer(new char[size]);

  PMIB_TCPTABLE tcp_table = reinterpret_cast<PMIB_TCPTABLE>(buffer.get());
  if (GetTcpTable(tcp_table, &size, FALSE) == NO_ERROR)
    for (size_t i = 0; i < tcp_table->dwNumEntries; i++)
      idle_ports.push_back(ntohs((uint16_t)tcp_table->table[i].dwLocalPort));
  std::sort(std::begin(idle_ports), std::end(idle_ports));
  return idle_ports;
}
#endif

uint16_t MonitorRuntimeWork::GetavailableTcpPort() {
  if (kUseDefaultPort) {
    return default_runtime_port_;
  }
#if BUILDFLAG(IS_WIN)
  auto idle_ports = GetAllTcpConnectionsPort();
  for (uint16_t port = kMinPort; port != kMaxPort; ++port) {
    if (!std::binary_search(std::begin(idle_ports), std::end(idle_ports), port)) {
      LOG(INFO) << "Get available port " << port;
      return port;
    }
  }
  LOG(ERROR) << "Can't find available local network port for runtime process";
  return last_runtime_port_;
#else
  return last_runtime_port_;
#endif
}

bool MonitorRuntimeWork::IsRuntimeBinding() {
  base::FilePath file_path = GetLocalAppData().Append(kCyfsDir).AppendASCII("etc").AppendASCII("desc");
  base::FilePath desc1 = file_path.AppendASCII("device.desc");
  base::FilePath desc2 = file_path.AppendASCII("device.sec");
  if (base::PathExists(desc1) && base::PathExists(desc2)) {
    LOG(INFO) << desc1 << " and " << desc2 << " file is exists";
    return true;
  }
  LOG(INFO) << "desc file is not exists, maybe user don't have binding runtime";
  return false;
}

void MonitorRuntimeWork::StartRuntimeProcess() {
  int proxy_port = GetavailableTcpPort();
  if (last_runtime_port_ != proxy_port) {
    updateRuntimePort(proxy_port);
  }
  bool anonymous = !IsRuntimeBinding();
  base::Process process = StartRuntimeProcessCore(anonymous, proxy_port);
  if (process.IsValid()) {
      LOG(INFO) << "reload runtime process successfully.";
  } else {
      LOG(INFO) << "Not found running runtime process. maybe need reload";
  }
}

#if BUILDFLAG(IS_WIN)
bool MonitorRuntimeWork::IsParentProcess(const base::ProcessId& son_process_id, const base::ProcessId& parent_process_id) {
  base::win::ScopedHandle snapshot(
      ::CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0));
  PROCESSENTRY32 process_entry = {sizeof(PROCESSENTRY32)};
  if (!snapshot.Get()) {
  LOG(ERROR) << "CreateToolhelp32Snapshot failed: " << GetLastError();
  return false;
  }
  if (!::Process32First(snapshot.Get(), &process_entry)) {
    LOG(ERROR) << "Process32First failed: " << GetLastError();
    return false;
  }
  do {
    if (son_process_id == process_entry.th32ProcessID) {
      if (process_entry.th32ParentProcessID == parent_process_id) {
        return true;
      }
    }
  } while (::Process32Next(snapshot.Get(), &process_entry));

  return false;
}
std::vector<base::ProcessId> MonitorRuntimeWork::FindProcesses(
        const ExePath& executable_name, const base::ProcessFilter* filter) {
  std::vector<base::ProcessId> process_list;
  base::NamedProcessIterator iter(executable_name, filter);
  while (const base::ProcessEntry* entry = iter.NextProcessEntry()) {
    base::Process process = base::Process::Open(entry->pid());
    // Sometimes process open fails. This would cause a DCHECK in
    // process.Terminate(). Maybe the process has killed itself between the
    // time the process list was enumerated and the time we try to open the
    // process?
    if (!process.IsValid()) {
      continue;
    }
    process_list.push_back(process.Pid());
  }
  return process_list;
}
#else
std::vector<base::ProcessId> MonitorRuntimeWork::FindProcesses(const ExePath& executable_name) {
  std::vector<base::ProcessId> all_pids;
  {
    base::NamedProcessIterator process_it(executable_name, nullptr);
    while (const base::ProcessEntry* entry = process_it.NextProcessEntry()) {
      all_pids.push_back(entry->pid());
    }
  }
  return all_pids;
}
#endif

void MonitorRuntimeWork::CheckRuntimeProcessRunStatus() {
  base::FilePath base_path = GetRuntimeExeDir();
#if BUILDFLAG(IS_WIN)
  ProcessPathPrefixFilter target_path_filter(base_path.value());
  process_list_ = FindProcesses(kExecuteName, &target_path_filter);
#else
  process_list_ = FindProcesses(kExecuteName);
#endif
  if (process_list_.empty()) {
    LOG(INFO) << "Not found running runtime process. maybe need reload";
    StartRuntimeProcess();
  } else {
    LOG(INFO) << "Found running runtime process.";
  }
}

void MonitorRuntimeWork::updateRuntimePort(int port) {}
