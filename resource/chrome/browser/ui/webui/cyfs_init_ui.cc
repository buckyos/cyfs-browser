
#include "chrome/browser/ui/webui/cyfs_init_ui.h"

#include <memory>
#include <string>

#include "base/bind.h"
#include "base/callback_helpers.h"
#include "base/values.h"

#include "ui/base/webui/web_ui_util.h"

#include "chrome/browser/cyfs_init/cyfs_init_service_factory.h"
#include "chrome/browser/profiles/profile.h"
#include "chrome/browser/ui/webui/webui_util.h"
#include "chrome/common/pref_names.h"
#include "chrome/common/url_constants.h"
#include "chrome/common/webui_url_constants.h"
#include "chrome/grit/browser_resources.h"
#include "chrome/grit/dev_ui_browser_resources.h"
#include "chrome/grit/generated_resources.h"

#include "content/public/browser/web_contents.h"
#include "content/public/browser/web_ui.h"
#include "content/public/browser/web_ui_data_source.h"
#include "content/public/browser/web_ui_message_handler.h"

#include "components/cyfs_init/cyfs_runtime_init_service.h"
#include "components/pref_registry/pref_registry_syncable.h"
#include "components/prefs/pref_service.h"
#include "services/network/public/cpp/shared_url_loader_factory.h"

class CyfsInitMessageHandler : public content::WebUIMessageHandler {
 public:
  CyfsInitMessageHandler() {}
  ~CyfsInitMessageHandler() override {}

  // WebUIMessageHandler implementation.
  void RegisterMessages() override {
    web_ui()->RegisterMessageCallback(
        "getRuntimeProcessStatus",
        base::BindRepeating(&CyfsInitMessageHandler::GetRuntimeProcessStatus,
                            base::Unretained(this)));
    web_ui()->RegisterMessageCallback(
        "getRuntimeProxystatus",
        base::BindRepeating(&CyfsInitMessageHandler::GetRuntimeProxyStatus,
                            base::Unretained(this)));
    web_ui()->RegisterMessageCallback(
        "restartRuntime",
        base::BindRepeating(&CyfsInitMessageHandler::RestartRuntime,
                            base::Unretained(this)));
    web_ui()->RegisterMessageCallback(
        "getRuntimeFirstRunningStatus",
        base::BindRepeating(&CyfsInitMessageHandler::GetFirstRunningStatus,
                            base::Unretained(this)));
    web_ui()->RegisterMessageCallback(
        "getRuntimeBindStatus",
        base::BindRepeating(&CyfsInitMessageHandler::GetRuntimeBindStatus,
                            base::Unretained(this)));
    web_ui()->RegisterMessageCallback(
        "getRuntimeBindStatusFromProfile",
        base::BindRepeating(
            &CyfsInitMessageHandler::GetRuntimeBindStatusFromProfile,
            base::Unretained(this)));
  }

  static void RegisterProfilePrefs(user_prefs::PrefRegistrySyncable* registry);

 private:
  void GetRuntimeProcessStatus(const base::Value::List& value) {
    VLOG(1) << "Get Runtime Process Status";
    AllowJavascript();

    CyfsRuntimeInitService* runtime_service =
        CyfsRuntimeInitServiceFactory::GetForProfile(
            Profile::FromWebUI(web_ui()));
    runtime_service->RequestRuntimeStatus(base::BindOnce(
        &CyfsInitMessageHandler::DidGetRuntimeProcessStatus,
        weak_ptr_factory_.GetWeakPtr(), value[0].GetString()));
  }

    void GetRuntimeProxyStatus(const base::Value::List& value) {
    VLOG(1) << "Get Runtime proxy Status";
    AllowJavascript();

    CyfsRuntimeInitService* runtime_service =
        CyfsRuntimeInitServiceFactory::GetForProfile(
            Profile::FromWebUI(web_ui()));
    runtime_service->RequestRuntimeProxyStatus(base::BindOnce(
        &CyfsInitMessageHandler::DidGetRuntimeProcessStatus,
        weak_ptr_factory_.GetWeakPtr(), value[0].GetString()));
  }

  void RestartRuntime(const base::Value::List&value) const {}

  void GetRuntimeBindStatus(const base::Value::List& value) {
    VLOG(1) << "Get Runtime Bind status";
    AllowJavascript();
    CyfsRuntimeInitService* runtime_service =
        CyfsRuntimeInitServiceFactory::GetForProfile(
            Profile::FromWebUI(web_ui()));
    runtime_service->RequestRuntimeBindStatus(base::BindOnce(
        &CyfsInitMessageHandler::DidGetRuntimeBindStatus,
        weak_ptr_factory_.GetWeakPtr(), value[0].GetString()));
  }

  void GetRuntimeBindStatusFromProfile(const base::Value::List&value) {
    AllowJavascript();
    const std::string& callback_id = value[0].GetString();
    PrefService* prefs = Profile::FromWebUI(web_ui())->GetPrefs();
    bool bindStatus = prefs->GetBoolean(prefs::kCyfsRuntimeBindingStatus);
    ResolveJavascriptCallback(base::Value(callback_id),
                              base::Value(bindStatus));
  }

  void GetFirstRunningStatus(const base::Value::List& value) {
    VLOG(1) << "Get Current Runtime First Run status";
    AllowJavascript();
    const std::string& callback_id = value[0].GetString();
    // CyfsRuntimeInitService* runtime_service =
    //     CyfsRuntimeInitServiceFactory::GetForProfile(Profile::FromWebUI(web_ui()));
    // auto isFirst = runtime_service->IsFirstRunning();
    PrefService* prefs = Profile::FromWebUI(web_ui())->GetPrefs();
    bool isFirst = prefs->GetBoolean(prefs::kCyfsRuntimeFirstRun);
    VLOG(1) << "Current User runtime is " << (isFirst ? "" : "not")
            << " First Run";
    if (isFirst) {
      LOG(INFO) << "Set " << prefs::kCyfsRuntimeFirstRun << " to false";
      prefs->SetBoolean(prefs::kCyfsRuntimeFirstRun, false);
    }
    base::Value data(isFirst);
    ResolveJavascriptCallback(base::Value(callback_id), data);
  }

  void DidGetRuntimeProcessStatus(std::string callback_id, bool value) {
    AllowJavascript();
    VLOG(1) << "Get Runtime process(proxy) Status "
            << (value ? "running" : "not running");
    base::Value data(value);
    ResolveJavascriptCallback(base::Value(callback_id), data);
  }

  void DidGetRuntimeBindStatus(std::string callback_id, bool value) {
    AllowJavascript();
    VLOG(1) << "Current User Runtime Bind Status : "
            << (value ? "binding" : "not binding");
    if (value) {
      LOG(INFO) << "Update Runtime Bind status to Binding";
      PrefService* prefs = Profile::FromWebUI(web_ui())->GetPrefs();
      prefs->SetBoolean(prefs::kCyfsRuntimeBindingStatus, true);
    }
    base::Value data(value);
    ResolveJavascriptCallback(base::Value(callback_id), data);
  }

 private:
  base::WeakPtrFactory<CyfsInitMessageHandler> weak_ptr_factory_{this};
};

// static
void CyfsInitMessageHandler::RegisterProfilePrefs(
    user_prefs::PrefRegistrySyncable* registry) {
  registry->RegisterBooleanPref(
      prefs::kCyfsRuntimeBindingStatus, false,
      user_prefs::PrefRegistrySyncable::SYNCABLE_PREF);
  registry->RegisterBooleanPref(
      prefs::kCyfsRuntimeFirstRun, true,
      user_prefs::PrefRegistrySyncable::SYNCABLE_PREF);
}

// static
void CyfsInitUI::RegisterProfilePrefs(
    user_prefs::PrefRegistrySyncable* registry) {
  CyfsInitMessageHandler::RegisterProfilePrefs(registry);
}

CyfsInitUI::CyfsInitUI(content::WebUI* web_ui)
    : content::WebUIController(web_ui) {
  web_ui->AddMessageHandler(std::make_unique<CyfsInitMessageHandler>());
  // Set up the chrome://cyfs-init source.
  content::WebUIDataSource* html_source =
      content::WebUIDataSource::Create(chrome::kChromeUICyfsInitHost);

  html_source->OverrideContentSecurityPolicy(
      network::mojom::CSPDirectiveName::ScriptSrc,
      "script-src chrome://resources 'self' 'unsafe-eval';");
  html_source->OverrideContentSecurityPolicy(
      network::mojom::CSPDirectiveName::TrustedTypes,
      "trusted-types jstemplate;");

  // Localized strings.
  // static constexpr webui::LocalizedString kStrings[] = {};
  // html_source->AddLocalizedStrings(kStrings);

  html_source->AddString("welcomeMessage", "Welcome to this cyfs page");
  html_source->AddString("browser_url", chrome::kCyfsBrowserURL);
  html_source->AddString("guide_url", chrome::kCyfsBrowserGuideURL);
  html_source->UseStringsJs();

  // Add required resources.
  html_source->AddResourcePath("cyfs_init.css", IDR_CYFS_INIT_UI_CSS);
  html_source->AddResourcePath("cyfs_init.js", IDR_CYFS_INIT_UI_JS);
  html_source->AddResourcePath("starting.png", IDR_CYFS_STARTING_H);

  html_source->SetDefaultResource(IDR_CYFS_INIT_UI_HTML);

  content::WebUIDataSource::Add(web_ui->GetWebContents()->GetBrowserContext(),
                                html_source);
}

CyfsInitUI::~CyfsInitUI() {}
