// Copyright 2013 The Chromium Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

#ifndef CHROME_BROWSER_CYFS_RUNTIME_INIT_SERVICE_FACTORY_H_
#define CHROME_BROWSER_CYFS_RUNTIME_INIT_SERVICE_FACTORY_H_

#include "base/memory/singleton.h"
#include "components/keyed_service/content/browser_context_keyed_service_factory.h"

class CyfsRuntimeInitService;
class Profile;

class CyfsRuntimeInitServiceFactory : public BrowserContextKeyedServiceFactory {
 public:
  static CyfsRuntimeInitService* GetForProfile(Profile* profile);

  static CyfsRuntimeInitService* GetForProfileIfExists(Profile* profile);

  static CyfsRuntimeInitServiceFactory* GetInstance();

 private:
  friend struct base::DefaultSingletonTraits<CyfsRuntimeInitServiceFactory>;

  CyfsRuntimeInitServiceFactory();
  ~CyfsRuntimeInitServiceFactory() override;

  // BrowserContextKeyedServiceFactory:
  KeyedService* BuildServiceInstanceFor(
      content::BrowserContext* context) const override;

  void RegisterProfilePrefs(
      user_prefs::PrefRegistrySyncable* registry) override;

  content::BrowserContext* GetBrowserContextToUse(
      content::BrowserContext* context) const override;

};

#endif  // CHROME_BROWSER_CYFS_RUNTIME_INIT_SERVICE_FACTORY_H_
