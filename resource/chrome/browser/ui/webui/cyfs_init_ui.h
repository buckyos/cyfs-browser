#ifndef CHROME_BROWSER_UI_WEBUI_CYFS_INIT__UI_H_
#define CHROME_BROWSER_UI_WEBUI_CYFS_INIT__UI_H_
#pragma once

#include "content/public/browser/web_ui_controller.h"

namespace user_prefs {
class PrefRegistrySyncable;
}

// The WebUI for chrome://hello-world
class CyfsInitUI : public content::WebUIController {
public:
  explicit CyfsInitUI(content::WebUI* web_ui);
  ~CyfsInitUI() override;
  static void RegisterProfilePrefs(user_prefs::PrefRegistrySyncable* registry);
};

#endif  // CHROME_BROWSER_UI_WEBUI_CYFS_INIT__UI_H_