// Copyright 2013 The Chromium Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

#include "chrome/browser/cyfs_init/cyfs_init_service_factory.h"

#include "chrome/browser/profiles/profile.h"
#include "components/keyed_service/content/browser_context_dependency_manager.h"
#include "components/cyfs_init/cyfs_runtime_init_service.h"
#include "chrome/browser/profiles/incognito_helpers.h"

#include "base/memory/raw_ptr.h"
#include "components/user_prefs/user_prefs.h"
#include "content/public/browser/storage_partition.h"
#include "services/network/public/cpp/shared_url_loader_factory.h"


// static
CyfsRuntimeInitService* CyfsRuntimeInitServiceFactory::GetForProfile(
    Profile* profile) {
  return static_cast<CyfsRuntimeInitService*>(
      GetInstance()->GetServiceForBrowserContext(profile, true));
}

// static
CyfsRuntimeInitService* CyfsRuntimeInitServiceFactory::GetForProfileIfExists(
    Profile* profile) {
  return static_cast<CyfsRuntimeInitService*>(
      GetInstance()->GetServiceForBrowserContext(profile, false));
}

// static
CyfsRuntimeInitServiceFactory* CyfsRuntimeInitServiceFactory::GetInstance() {
  return base::Singleton<CyfsRuntimeInitServiceFactory>::get();
}

CyfsRuntimeInitServiceFactory::CyfsRuntimeInitServiceFactory()
    : BrowserContextKeyedServiceFactory(
        "CyfsRuntimeInitService",
        BrowserContextDependencyManager::GetInstance()) {
}

CyfsRuntimeInitServiceFactory::~CyfsRuntimeInitServiceFactory() {
}

KeyedService* CyfsRuntimeInitServiceFactory::BuildServiceInstanceFor(
    content::BrowserContext* context) const {
  auto url_loader_factory = context->GetDefaultStoragePartition()
                                ->GetURLLoaderFactoryForBrowserProcess();
  return new CyfsRuntimeInitService(user_prefs::UserPrefs::Get(context), std::move(url_loader_factory));

}

void CyfsRuntimeInitServiceFactory::RegisterProfilePrefs(
    user_prefs::PrefRegistrySyncable* registry) {

}

content::BrowserContext* CyfsRuntimeInitServiceFactory::GetBrowserContextToUse(
    content::BrowserContext* context) const {
  return chrome::GetBrowserContextRedirectedInIncognito(context);
}