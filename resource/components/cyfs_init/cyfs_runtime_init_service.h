// Copyright 2013 The Chromium Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

#ifndef COMPONENTS_CYFS_RUNTIME_INIT_SERVICE_H_
#define COMPONENTS_CYFS_RUNTIME_INIT_SERVICE_H_

#include <memory>
#include <string>

#include "base/bind.h"
#include "base/callback.h"
#include "base/containers/flat_map.h"
#include "base/sequence_checker.h"

#include "base/files/file_util.h"
#include "base/files/file_path.h"
#include "base/path_service.h"

#include "base/memory/raw_ptr.h"
#include "chrome/common/chrome_constants.h"
#include "chrome/common/chrome_paths.h"
#include "components/api_request_helper/api_request_helper.h"
#include "components/keyed_service/core/keyed_service.h"

namespace network {
class SharedURLLoaderFactory;
}  // namespace network

class PrefRegistrySimple;
class PrefService;

using OnGetStatus = base::OnceCallback<void(bool value)>;
// CyfsRuntimeInitService
// --------------------------------------------------------

// CyfsRuntimeInitService is owned by the profile, and is responsible for
// observing BookmarkModel changes in order to provide an undo for those
// changes.
class CyfsRuntimeInitService : public KeyedService {
 public:
  CyfsRuntimeInitService(
      PrefService* prefs,
      scoped_refptr<network::SharedURLLoaderFactory> url_loader_factory);
  ~CyfsRuntimeInitService() override;

  void Start();
  void Shutdown() override;

  void RequestRuntimeStatus(OnGetStatus callback);
  void RequestRuntimeProxyStatus(OnGetStatus callback);

  bool IsFirstRunning();

  void RequestRuntimeBindStatus(OnGetStatus callback);
  void OnGetRuntimeBindStatus(OnGetStatus callback, bool result);

 private:
  bool CheckStatusCode(int status_code);
  void OnRuntimeProcessResponse(
      OnGetStatus callback,
      int response_code,
      const std::string& response_body,
      const base::flat_map<std::string, std::string>& response_headers);
  bool ParseBody(const std::string& body, std::string* activation);

  void OnRuntimeProxyResponse(
      OnGetStatus callback,
      int response_code,
      const std::string& response_body,
      const base::flat_map<std::string, std::string>& response_headers);

 private:
  raw_ptr<PrefService> prefs_ = nullptr;
  const scoped_refptr<base::SequencedTaskRunner> file_task_runner_;
  std::unique_ptr<api_request_helper::APIRequestHelper> api_request_helper_;
  base::WeakPtrFactory<CyfsRuntimeInitService> weak_ptr_factory_;

};

#endif  // COMPONENTS_CYFS_RUNTIME_INIT_SERVICE_H_
