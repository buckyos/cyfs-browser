; Script generated by the HM NIS Edit Script Wizard.

; HM NIS Edit Wizard helper defines
!define PRODUCT_NAME "CYFS_Browser"
!define BROWSER_DESKTOP_NAME "CYFS Browser"
!define START_RUNTIME_BAT "Restart Runtime"
!define BROWSER_EXE_NAME "${PRODUCT_NAME}.exe"
!define NFT_TOOL_EXE "nft-creator.exe"
!define PRODUCT_RUNTIME_NAME "cyfs-runtime"
!define RUNTIME_EXE_NAME "${PRODUCT_RUNTIME_NAME}.exe"
!define IPFS_PROXY_BIN_NAME "ipfs-proxy.exe"
!define IPFS_RUNTIME_BIN_NAME "ipfs.exe"
!define CYFS_UPLOAD_BIN_NAME "cyfs-file-uploader.exe"
!define ENS_LOOKUP_BIN_NAME "enslookup.exe"
!define RUNTIME_DESKTOP_NAME "Cyfs Runtime"
!define PRODUCT_VERSION "${BrowserVersion}"
!define PRODUCT_CHANNEL "${channel}"
!define RUNTIME_PRODUCT_VERSION "${RuntimeVersion}"
!define PRODUCT_PUBLISHER "CYFS Core Dev Team"
!define PRODUCT_WEB_SITE "https://cyfs.com"
!define PRODUCT_DIR_REGKEY "Software\Microsoft\Windows\CurrentVersion\App Paths\${PRODUCT_NAME}.exe"
!define PRODUCT_UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}"
!define AUTORUN_KEYPATH "Software\Microsoft\Windows\CurrentVersion\Run"
!define PRODUCT_UNINST_ROOT_KEY "HKLM"
!define PRODUCT_INST_ROOT_KEY "HKLM"
!define AUTORUN_ROOT_KEY "HKLM"

!define NFT_TOOL_ROOT_KEY "HKCR"
!define CYFS_SCHEME_REGKEY "cyfs"
!define CYFS_SCHEME_ROOT_KEY "HKCR"

!define VC_COMPONENT_KEY "SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Vc"
!define RELATED_BROWSER_BIN "kalama.exe"

; MUI 1.67 compatible ------
!include "MUI2.nsh"
!include "Sections.nsh"
!include "LogicLib.nsh"
!include "Memento.nsh"
!include "WordFunc.nsh"
!include "Util.nsh"
!include "Integration.nsh"
!include "FileFunc.nsh"
!include "nsDialogs.nsh"
!include "WinMessages.nsh"
!include "WordFunc.nsh"

Unicode True

; ;Head pic
!define MUI_HEADERIMAGE_BITMAP ".\images\header.bmp"
!define MUI_HEADERIMAGE_UNBITMAP ".\images\header.bmp"
!define MUI_ABORTWARNING

; MUI Settings
; install and uninstall applicatiuon icon
!define MUI_ICON ".\images\icon.ico"
!define MUI_UNICON ".\images\icon.ico"

;Left pic
!define MUI_WELCOMEFINISHPAGE_BITMAP ".\images\left.bmp"
!define MUI_UNWELCOMEFINISHPAGE_BITMAP ".\images\left.bmp"

!define MUI_WELCOMEPAGE_TITLE "Welcome to install ${BROWSER_DESKTOP_NAME}"
## $\n == blank line
## $\r$\n == new line
!define MUI_WELCOMEPAGE_TEXT "A truly decentralized browser. Support CYFS link browsing, new web3 product experience.$\r$\n\
$\nLow threshold for use$\r$\n\
The ${BROWSER_DESKTOP_NAME} is based on the secondary development of Chromium, retains the original Chrome UI, and retains your usage habits.$\r$\n\
$\nprivacy protection$\r$\n\
${BROWSER_DESKTOP_NAME} supports anonymous browsing mode to protect your online privacy.$\r$\n\
$\nBrowse Decentralized Data$\r$\n\
The ${BROWSER_DESKTOP_NAME} makes the 404 situation in the centralized network disappear and browses the decentralized data permanently.$\r$\n\
$\nCreate NFTs with ease$\r$\n\
${BROWSER_DESKTOP_NAME} can help you easily create NFT works, and convert any file into NFT in just a few simple steps.$\r$\n\
"

!define MUI_LICENSEPAGE_TEXT_TOP "Press Page Down to see the terms of the agreement."
!define MUI_LICENSEPAGE_TEXT_BOTTOM "If you accept the terms of the agreement, click I Agree to continue."
!define MUI_INSTFILESPAGE_FINISHHEADER_TEXT "Please wait while ${BROWSER_DESKTOP_NAME} (V ${BrowserVersion} ${channel}) is being installed"
; !define MUI_INSTFILESPAGE_FINISHHEADER_SUBTEXT


!define MUI_FINISHPAGE_TITLE "${BROWSER_DESKTOP_NAME} install complete"
!define MUI_FINISHPAGE_TEXT "${BROWSER_DESKTOP_NAME} (V ${BrowserVersion} ${channel}) has been installed on your computer.$\r$\n\
$\nClick finish to close Setup."

; !define MUI_TEXTCOLOR "000000"
; !define MUI_BGCOLOR "339EBC"

; Welcome page
!insertmacro MUI_PAGE_WELCOME
; custom page
; License page
!insertmacro MUI_PAGE_LICENSE "license.txt"
; Directory page
;!insertmacro MUI_PAGE_DIRECTORY
; Instfiles page
!insertmacro MUI_PAGE_INSTFILES

UninstPage custom un.nsDialogsPage
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

!define MUI_FINISHPAGE_NOREBOOTSUPPORT
!define MUI_FINISHPAGE_RUN
!define MUI_FINISHPAGE_RUN_TEXT "Launch CYFS Browser"
!define MUI_FINISHPAGE_RUN_FUNCTION startApp
!insertmacro MUI_PAGE_FINISH

; Language files
!insertmacro MUI_LANGUAGE "English"


Name "${BROWSER_DESKTOP_NAME} ${PRODUCT_VERSION} ${channel}"
OutFile "${PRODUCT_NAME}_${PRODUCT_VERSION}-${PRODUCT_CHANNEL}.exe"
Caption "${BROWSER_DESKTOP_NAME} Install (V ${BrowserVersion} ${channel})"

;ShowInstDetails nevershow
;ShowUnInstDetails nevershow

BrandingText "CYFS Core Dev Team"

; set browser install path
InstallDir "$LOCALAPPDATA\${PRODUCT_NAME}"

; install need admin rights
; RequestExecutionLevel admin


Var /GLOBAL DeleteUserData

Var /GLOBAL Dialog_1
Var /GLOBAL Label_1
Var /GLOBAL Label_2
Var /GLOBAL Label_3
Var /GLOBAL CheckBox_1

Function startApp
Exec `"$LOCALAPPDATA\${PRODUCT_NAME}\Application\${PRODUCT_NAME}.exe"`
FunctionEnd


# Install webview2 by launching the bootstrapper
# See https://docs.microsoft.com/en-us/microsoft-edge/webview2/concepts/distribution#online-only-deployment
Function installWebView2
	# If this key exists and is not empty then webview2 is already installed
  SetOutPath "$INSTDIR"
  DetailPrint "Check Installing WebView2 Runtime"
	ReadRegStr $0 HKLM "SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}" "pv"

	${If} ${Errors} 
	${OrIf} $0 == ""
		DetailPrint "Installing: WebView2 Runtime"
    File "MicrosoftEdgeWebview2Setup.exe"
		ExecWait '"$INSTDIR\MicrosoftEdgeWebview2Setup.exe" /silent /install'
	${EndIf}
FunctionEnd

Function InstallVC
  SetOutPath "$INSTDIR"
  DetailPrint "Check Installing Visual C++ Runtime"
  Push $R0
  ClearErrors
  ReadRegStr $R0 ${PRODUCT_INST_ROOT_KEY} ${VC_COMPONENT_KEY} "install_vc"

  IfErrors 0 VSRedistInstalled
  LogText "install vc runtime"
  File "VC_redist.x64.exe"
  Exec "$INSTDIR\VC_redist.x64.exe /q /norestart"
  WriteRegStr ${PRODUCT_INST_ROOT_KEY} "${VC_COMPONENT_KEY}" "install_vc" "1"
  StrCpy $R0 "-1"

VSRedistInstalled:
  Exch $R0
FunctionEnd

Function ForceKillProcess
  Pop $1 ; exe name
  LogText "check $1 is or not running, if yes need kill this process"
	nsProcess::_FindProcess $1
	Pop $R0

	${If} $R0 == 0
		LogText "$1 is exits, need kill this process"
		nsProcess::_KillProcess  $1
   		${For} $R1 0 10
      	Sleep 1000
			  nsProcess::_FindProcess $1
			  Pop $R0
			  ${If} $R0 != 0
          LogText "kill $1 process success"
				  goto KillProcEnd
			  ${EndIf}
			  LogText "kill $1 failed, so retry to kill process $1"
		  ${Next}
	KillProcEnd:
    LogText "after nsProcess::_KillProcess,  $1 is not running"
  ${Else}
    LogText "$1 is not running"
  ${EndIf}
FunctionEnd

Function checkNeedUpgrade
  SetOutPath "$INSTDIR"
  DetailPrint "Check version for upgrade"
	ReadRegStr $0 HKCU "SOFTWARE\CYFS_Browser" "pv"
  LogText " old browser version $0 , curent version ${PRODUCT_VERSION}"

  ${VersionCompare} $0 ${PRODUCT_VERSION} $R0
  ${if} $R0 == 1
    LogText " cannot downgrade install browser"
    ; MessageBox MB_ICONSTOP " Unable to install.  A newer version of CYFS Browser is already installed."
    MessageBox MB_ICONSTOP " Unable to install.  A newer version ($0) of CYFS Browser is already installed."
    Quit
  ${EndIf}
FunctionEnd

Function checkOtherBrowserRunning
  nsProcess::_FindProcess ${RELATED_BROWSER_BIN}
  Pop $R0
  ${If} $R0 == 0
    LogText "${RELATED_BROWSER_BIN} is exits, need kill this process"
    MessageBox MB_ICONSTOP "It seems that you have already installed Kalama, if you want to continue to install CYFS Browser, please uninstall Kalama first, otherwise there may be inconsistent data."
    Quit
  ${EndIf}
FunctionEnd

Function killBrowserComponmentProcess
  Push ${RUNTIME_EXE_NAME}
  Call ForceKillProcess
  Push ${ENS_LOOKUP_BIN_NAME}
  Call ForceKillProcess
  Push ${BROWSER_EXE_NAME}
  Call ForceKillProcess
  Push ${NFT_TOOL_EXE}
  Call ForceKillProcess
  Push ${IPFS_PROXY_BIN_NAME}
  Call ForceKillProcess
  Push ${CYFS_UPLOAD_BIN_NAME}
  Call ForceKillProcess
  Sleep 1000
  Push ${IPFS_RUNTIME_BIN_NAME}
  Call ForceKillProcess
FunctionEnd


Section "-LogSetOn"
  LogSet on
SectionEnd


Function deleteOldBrowserFiles
  RMDir /r "$LOCALAPPDATA\${PRODUCT_NAME}\User Data\Default/cyfs_extensions"

  IfFileExists "$APPDATA\${PRODUCT_NAME}\*.*" old_browser_exist old_browser_not_exist
old_browser_exist:
  Delete "$DESKTOP\${BROWSER_DESKTOP_NAME}.lnk"
  Delete "$SMPROGRAMS\${BROWSER_DESKTOP_NAME}.lnk"
  RMDir /r "$SMPROGRAMS\${PRODUCT_NAME}"
  DeleteRegValue ${AUTORUN_ROOT_KEY} "${AUTORUN_KEYPATH}" "${PRODUCT_NAME}"
    DeleteRegValue ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "${PRODUCT_NAME}"
    DeleteRegValue ${PRODUCT_INST_ROOT_KEY} "${PRODUCT_DIR_REGKEY}" "BrowserInstallDir"
  SetOutPath $APPDATA
    RMDir /r  "$APPDATA\${PRODUCT_NAME}"
  RMDir /r  $INSTDIR
    RMDir /r "$LOCALAPPDATA\${PRODUCT_NAME}\User Data\Extensions"

    DeleteRegKey ${NFT_TOOL_ROOT_KEY} "*\shell\Create NFT by cyfs link"
    DeleteRegKey ${NFT_TOOL_ROOT_KEY} "*\shell\Create NFT by cyfs link\command"
old_browser_not_exist:
FunctionEnd

Section "preparation" 1
  Call checkNeedUpgrade

  Call checkOtherBrowserRunning
  Call killBrowserComponmentProcess
  Call deleteOldBrowserFiles
SectionEnd

Section "main" 2
  SetOutPath "$INSTDIR"

  WriteUninstaller "$INSTDIR\${PRODUCT_NAME}_uninstaller.exe"

  File "mini_installer.exe"
  Exec `"$INSTDIR\mini_installer.exe"`

  ; Call checkNeedUpgrade

  Call killBrowserComponmentProcess

  Call InstallVC
  Call installWebView2
SectionEnd

Section "install_component" 3
  SetOutPath $APPDATA
  RMDir /r  "$APPDATA\cyfs\services\runtime"

  SetOutPath "$APPDATA\cyfs\services\runtime"
  SetOverwrite on
  File /r /x  "runtime\acl.toml" /x  "runtime\runtime.toml" /x "runtime\tools\*.*" "runtime\*.*"
  ; File "restart_runtime.ico" "RestartRuntime.bat"


  IfFileExists "$APPDATA\cyfs\etc\runtime" exists not_exists
  not_exists:
    CreateDirectory "$APPDATA\cyfs\etc\runtime"
  exists:
    LogText "$APPDATA\cyfs\etc\runtime is exists"
  SetOutPath "$APPDATA\cyfs\etc\runtime"
  File "runtime\runtime.toml"


  SetOutPath "$APPDATA\cyfs\services\runtime\tools"
  File /r "runtime\tools\*.*"

  SetOutPath "$APPDATA\cyfs\etc\acl"
  File "runtime\acl.toml"

  SetOutPath "$APPDATA\cyfs\services\runtime"
  Delete "$APPDATA\cyfs\services\runtime\runtime.toml"
SectionEnd

Section "browser_regedit" 4
  WriteRegStr ${CYFS_SCHEME_ROOT_KEY} "${CYFS_SCHEME_REGKEY}" "" "URL:cyfs Protocol"
  WriteRegStr ${CYFS_SCHEME_ROOT_KEY} "${CYFS_SCHEME_REGKEY}" "URL Protocol" ""
  WriteRegStr ${CYFS_SCHEME_ROOT_KEY} "${CYFS_SCHEME_REGKEY}\shell\open\command" "" '"$LOCALAPPDATA\${PRODUCT_NAME}\Application\${PRODUCT_NAME}.exe" "%1"'
SectionEnd

Section "copy_extensions" 5
  SetOutPath "$LOCALAPPDATA\${PRODUCT_NAME}\Application"
  RMDir /r "$LOCALAPPDATA\${PRODUCT_NAME}\Application\Extensions"
  File /r "Extensions"
SectionEnd

Section "end" 6
  SetOutPath "$LOCALAPPDATA\${PRODUCT_NAME}"
  Delete "$LOCALAPPDATA\${PRODUCT_NAME}\mini_installer.exe"

  SetOutPath "$LOCALAPPDATA\${PRODUCT_NAME}"
  RMDir /r "$LOCALAPPDATA\${PRODUCT_NAME}\User Data\Default\cyfs_extensions"

  ReadRegStr $R0 "HKCU" "Software\${PRODUCT_NAME}" "UninstallString"
  LogText "current application uninstall bin = $R0"

SectionEnd



####### uninstall #######
Function un.onUninstSuccess
  HideWindow
  MessageBox MB_ICONINFORMATION|MB_OK "$(^Name) Has been successfully removed from your computer"
  Delete "$LOCALAPPDATA\${PRODUCT_NAME}\mini_installer.exe"
FunctionEnd

Function un.checkOtherBrowserRunning
  nsProcess::_FindProcess ${RELATED_BROWSER_BIN}
  Pop $R0
  ${If} $R0 == 0
    LogText "$1 is exits, need kill this process"
    MessageBox MB_ICONSTOP "${RELATED_BROWSER_BIN} is Running, Please exit ${RELATED_BROWSER_BIN} Application"
    Quit
  ${EndIf}
FunctionEnd


Function un.killRuntimeProcess
  LogText "kill ${CYFS_UPLOAD_BIN_NAME} process"
  Exec '"taskkill" /F /IM ${CYFS_UPLOAD_BIN_NAME} /T'
  Sleep 2000
FunctionEnd

Function un.deleteOldRegAndShortcut
  DeleteRegKey ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}"
  DeleteRegKey ${PRODUCT_INST_ROOT_KEY} "${PRODUCT_DIR_REGKEY}"
  DeleteRegKey ${CYFS_SCHEME_ROOT_KEY} "${CYFS_SCHEME_REGKEY}"

  DeleteRegKey ${NFT_TOOL_ROOT_KEY} "*\shell\Create NFT by cyfs link"
  DeleteRegKey ${NFT_TOOL_ROOT_KEY} "*\shell\Create NFT by cyfs link\command"

  Delete "$DESKTOP\${BROWSER_DESKTOP_NAME}.lnk"
  Delete "$DESKTOP\${RUNTIME_DESKTOP_NAME}.lnk"
  Delete "$DESKTOP\${START_RUNTIME_BAT}.lnk"
  Delete "$SMPROGRAMS\${BROWSER_DESKTOP_NAME}.lnk"
  Delete "$SMPROGRAMS\${RUNTIME_DESKTOP_NAME}.lnk"

  RMDir /r "$SMPROGRAMS\${PRODUCT_NAME}"
  RMDir /r "$SMPROGRAMS\${PRODUCT_RUNTIME_NAME}"
  DeleteRegValue ${AUTORUN_ROOT_KEY} "${AUTORUN_KEYPATH}" "${PRODUCT_NAME}"
FunctionEnd

Function un.killIpfsProcess
  Pop $1 ; exe name
  LogText "check $1 is or not running, if yes need kill this process"
	nsProcess::_FindProcess $1
	Pop $R0

	${If} $R0 == 0
		LogText "$1 is exits, need kill this process"
    DetailPrint "$1 is exits, need kill this process"
		nsProcess::_KillProcess  $1
   		${For} $R1 0 10
      	Sleep 1000
			  nsProcess::_FindProcess $1
			  Pop $R0
			  ${If} $R0 != 0
          LogText "kill $1 process success"
          DetailPrint "kill $1 process success"
				  goto KillProcEnd
			  ${EndIf}
			  LogText "kill $1 failed, so retry to kill process $1"
        DetailPrint "kill $1 failed, so retry to kill process $1"
		  ${Next}
	KillProcEnd:
    LogText "after nsProcess::_KillProcess,  $1 is not running"
    DetailPrint "after nsProcess::_KillProcess,  $1 is not running"
  ${Else}
    LogText "$1 is not running"
    DetailPrint "$1 is not running"
  ${EndIf}
FunctionEnd

Function un.nsDialogsPage
  SetOutPath $LOCALAPPDATA

	nsDialogs::Create 1018
	Pop $Dialog_1
	${If} $Dialog_1 == error
		Abort
	${EndIf}
	${NSD_CreateLabel} 0 0 100% 30u "${BROWSER_DESKTOP_NAME} ${BrowserVersion} ${channel} will be uninstalled from the following folder. Click Uninstall to start the uninstallation."
	Pop $Label_1

  ; ${NSD_CreateGroupBox} 0 30u 100% 25u ""
  ; Pop $0
	${NSD_CreateLabel} 0 35u 50u 15u "Uninstall from:"
	Pop $Label_2
  ${NSD_CreateText} 50u 35u 180u 15u "$LOCALAPPDATA\${PRODUCT_NAME}"
	Pop $Label_3

	${NSD_CreateCheckbox} 0 85u 100% 10u "Also delete user data (Make sure you have backed up DID)"
	Pop $CheckBox_1
  ${NSD_OnClick} $CheckBox_1 un.DeleteUserData
	nsDialogs::Show
FunctionEnd

Function un.DeleteUserData
  Pop $0
  ${NSD_GetState} $CheckBox_1 $0
  ${If} $0 = ${BST_CHECKED}
    StrCpy $DeleteUserData 1
  ${Else}
    StrCpy $DeleteUserData 0
  ${EndIF}
FunctionEnd

Section Uninstall
  SetOutPath $LOCALAPPDATA

  Call un.checkOtherBrowserRunning

  Call un.killRuntimeProcess

  Exec '"taskkill" /F /IM ${BROWSER_EXE_NAME} /T'

  Sleep 2000

  ReadRegStr $R0 "HKCU" "Software\${PRODUCT_NAME}" "UninstallString"
  LogText "current application uninstall bin = $R0"

  ${if} $DeleteUserData == 1
    ExecWait '"$R0" --uninstall --delete-profile'
  ${Else}
    ExecWait '"$R0" --uninstall'
  ${EndIf}

  Sleep 2000

  DetailPrint "kill ${IPFS_PROXY_BIN_NAME}"
  Push ${IPFS_PROXY_BIN_NAME}
  Call un.killIpfsProcess
  LogText "kill ${IPFS_PROXY_BIN_NAME}"


  DetailPrint "kill ${IPFS_RUNTIME_BIN_NAME}"
  Push ${IPFS_RUNTIME_BIN_NAME}
  Call un.killIpfsProcess
  LogText "kill ${IPFS_RUNTIME_BIN_NAME}"

  DetailPrint "kill ${IPFS_PROXY_BIN_NAME}"
  Push ${IPFS_PROXY_BIN_NAME}
  Call un.killIpfsProcess
  LogText "kill ${IPFS_PROXY_BIN_NAME}"


  ${RefreshShellIcons}

  ${if} $DeleteUserData == 1
    RMDir /r "$APPDATA\cyfs"
  ${EndIf}

  SetOutPath "$LOCALAPPDATA\${PRODUCT_NAME}"
  RMDir /r "$LOCALAPPDATA\${PRODUCT_NAME}\Application"
  Delete "$LOCALAPPDATA\${PRODUCT_NAME}\install.log"
  Delete "$LOCALAPPDATA\${PRODUCT_NAME}\${PRODUCT_NAME}_uninstaller.exe"
  Delete "$LOCALAPPDATA\${PRODUCT_NAME}\mini_installer.exe"


  Sleep 4000
  SetAutoClose true
SectionEnd
