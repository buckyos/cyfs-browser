// Copyright 2013 The Chromium Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

#include "components/cyfs_init/cyfs_runtime_init_service.h"

#include <string>
#include <utility>

#include "base/check.h"
#include "base/files/file_path.h"
#include "base/files/file_util.h"
#include "base/json/json_reader.h"
#include "base/logging.h"
#include "base/memory/raw_ptr.h"
#include "base/path_service.h"
#include "base/strings/stringprintf.h"

// #include "base/task/post_task.h"
#include "base/task/thread_pool.h"

#include "components/api_request_helper/api_request_helper.h"
#include "components/prefs/pref_service.h"
#include "components/strings/grit/components_strings.h"
#include "net/http/http_status_code.h"
#include "services/network/public/cpp/shared_url_loader_factory.h"
#include "third_party/abseil-cpp/absl/types/optional.h"
#include "url/gurl.h"

#include "chrome/common/chrome_constants.h"

#include "chrome/browser/browser_process.h"

using namespace api_request_helper;

namespace {

std::string check_url = "http://127.0.0.1:1321/check";
// std::string cyfs_js_url = "http://127.0.0.1:38090/cyfs_sdk/cyfs.js";
std::string cyfs_js_url = "cyfs://static/cyfs_sdk/cyfs.js";

net::NetworkTrafficAnnotationTag kAnnotationTag =
    net::DefineNetworkTrafficAnnotation("brave_adaptive_captcha_service", R"(
        semantics {
          sender:
            "Brave Adaptive Captcha service"
          description:
            "Fetches CAPTCHA data from Brave."
          trigger:
            "The Brave service indicates that it's time to solve a CAPTCHA."
          data: "Brave CAPTCHA data."
          destination: WEBSITE
        }
        policy {
          cookies_allowed: NO
          setting:
            "This feature cannot be disabled by settings."
          policy_exception_justification:
            "Not implemented."
    })");

bool IsRuntimeDescFileExist() {
  base::FilePath user_data_dir;
  if (!base::PathService::Get(chrome::DIR_USER_DATA, &user_data_dir))
    return false;
  base::FilePath file_path =
      user_data_dir.AppendASCII("cyfs").AppendASCII("etc").AppendASCII("desc");
  base::FilePath desc1 = file_path.AppendASCII("device.desc");
  base::FilePath desc2 = file_path.AppendASCII("device.sec");
  if (base::PathExists(desc1) && base::PathExists(desc2)) {
    LOG(INFO) << "all user desc file is exists";
    return true;
  }
  return false;
}
}  // namespace

// CyfsRuntimeInitService
// --------------------------------------------------------

CyfsRuntimeInitService::CyfsRuntimeInitService(
    PrefService* prefs,
    scoped_refptr<network::SharedURLLoaderFactory> url_loader_factory)
    : prefs_(prefs),
      file_task_runner_(base::ThreadPool::CreateSequencedTaskRunner(
          {base::MayBlock(), base::TaskPriority::USER_VISIBLE,
           base::TaskShutdownBehavior::BLOCK_SHUTDOWN})),
      api_request_helper_(
          new api_request_helper::APIRequestHelper(kAnnotationTag,
                                                   url_loader_factory)),
      weak_ptr_factory_(this) {}

CyfsRuntimeInitService::~CyfsRuntimeInitService() {}

void CyfsRuntimeInitService::Start() {}

void CyfsRuntimeInitService::Shutdown() {}

void CyfsRuntimeInitService::RequestRuntimeBindStatus(OnGetStatus callback) {
  file_task_runner_->PostTaskAndReplyWithResult(
      FROM_HERE, base::BindOnce(&IsRuntimeDescFileExist),
      base::BindOnce(&CyfsRuntimeInitService::OnGetRuntimeBindStatus,
                     weak_ptr_factory_.GetWeakPtr(), std::move(callback)));
}

void CyfsRuntimeInitService::OnGetRuntimeBindStatus(OnGetStatus callback,
                                                    bool result) {
  std::move(callback).Run(result);
}

// bool CyfsRuntimeInitService::IsFirstRunning() {
//   base::FilePath user_data_dir;
//   if (!base::PathService::Get(chrome::DIR_USER_DATA, &user_data_dir))
//     return false;
//   base::FilePath first_run_sentinel =
//   user_data_dir.Append(chrome::kFirstRun); if
//   (!base::PathExists(first_run_sentinel)) {
//     base::WriteFile(first_run_sentinel, "");
//     return true;
//   }
//   return false;
// }

void CyfsRuntimeInitService::OnRuntimeProcessResponse(
    OnGetStatus callback,
    int response_code,
    const std::string& response_body,
    const base::flat_map<std::string, std::string>& response_headers) {
  bool result = CheckStatusCode(response_code);
  if (!result) {
    std::move(callback).Run(result);
    return;
  }

  std::string activation;
  result = ParseBody(response_body, &activation);
  LOG(INFO) << "runtime activation status: " << activation;
  if (!result) {
    std::move(callback).Run(result);
    return;
  }

  std::move(callback).Run(true);
}

void CyfsRuntimeInitService::OnRuntimeProxyResponse(
    OnGetStatus callback,
    int response_code,
    const std::string& response_body,
    const base::flat_map<std::string, std::string>& response_headers) {
  bool result = CheckStatusCode(response_code);
  if (!result) {
    std::move(callback).Run(result);
    return;
  }

  std::move(callback).Run(true);
}

void CyfsRuntimeInitService::RequestRuntimeStatus(OnGetStatus callback) {
  auto api_request_helper_callback =
      base::BindOnce(&CyfsRuntimeInitService::OnRuntimeProcessResponse,
                     weak_ptr_factory_.GetWeakPtr(), std::move(callback));
  api_request_helper_->Request("GET", GURL(check_url), "", "", false,
                               std::move(api_request_helper_callback));
}

void CyfsRuntimeInitService::RequestRuntimeProxyStatus(OnGetStatus callback) {
  LOG(INFO) << "Prefetch runtime sdk javascript file: " << cyfs_js_url;
  auto api_request_helper_callback =
      base::BindOnce(&CyfsRuntimeInitService::OnRuntimeProxyResponse,
                     weak_ptr_factory_.GetWeakPtr(), std::move(callback));
  api_request_helper_->Request("GET", GURL(cyfs_js_url), "", "", false,
                               std::move(api_request_helper_callback));
}

bool CyfsRuntimeInitService::CheckStatusCode(int status_code) {
  if (status_code == net::HTTP_NOT_FOUND) {
    VLOG(1) << "No captcha scheduled for given payment id";
    return false;
  }

  if (status_code == net::HTTP_INTERNAL_SERVER_ERROR) {
    LOG(ERROR) << "Failed to retrieve the captcha";
    return false;
  }

  if (status_code != net::HTTP_OK) {
    LOG(ERROR) << "Unexpected HTTP status: " << status_code;
    return false;
  }

  return true;
}

bool CyfsRuntimeInitService::ParseBody(const std::string& body,
                                       std::string* activation) {
  absl::optional<base::Value> value = base::JSONReader::Read(body);
  if (!value || !value->is_dict()) {
    LOG(ERROR) << "Invalid JSON";
    return false;
  }

  base::DictionaryValue* dictionary = nullptr;
  if (!value->GetAsDictionary(&dictionary)) {
    LOG(ERROR) << "Invalid JSON";
    return false;
  }
  absl::optional<bool> activation_ = dictionary->FindBoolKey("activation");
  if (activation_) {
    *activation = (*activation_ ? "true" : "false");
  }

  return true;
}
