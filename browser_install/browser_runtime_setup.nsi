; Script generated by the HM NIS Edit Script Wizard.

; HM NIS Edit Wizard helper defines
!define PRODUCT_NAME "Cyfs_Browser"
!define BROWSER_NAME_ALIAS "CYFS Browser"
!define BROWSER_DESKTOP_NAME "CYFS Browser"
!define START_RUNTIME_BAT "Restart Runtime"
!define BROWSER_EXE_NAME "${PRODUCT_NAME}.exe"
!define NFT_TOOL_EXE "nft-creator.exe"
!define PRODUCT_RUNTIME_NAME "cyfs-runtime"
!define RUNTIME_EXE_NAME "${PRODUCT_RUNTIME_NAME}.exe"
!define RUNTIME_DESKTOP_NAME "Cyfs Runtime"
!define PRODUCT_VERSION "${BrowserVersion}"
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
!define OLD_BROWSER_USER_DATA_DIR "Chromium"
!define BROWSER_USER_DATA_DIR "Cyber"

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

!define MUI_WELCOMEPAGE_TITLE "Welcome to install CYFS Browser"
## $\n == blank line
## $\r$\n == new line
!define MUI_WELCOMEPAGE_TEXT "A truly decentralized browser. Support CYFS link browsing, new web3 product experience.$\r$\n\
$\nLow threshold for use$\r$\n\
The CYFS Browser is based on the secondary development of Chromium, retains the original Chrome UI, and retains your usage habits.$\r$\n\
$\nCreate NFTs with ease$\r$\n\
CYFS Browser can help you easily create NFT works, and convert any file into NFT in just a few simple steps.$\r$\n\
$\nBrowse Decentralized Data$\r$\n\
The CYFS Browser makes the 404 situation in the centralized network disappear and browses the decentralized data permanently.$\r$\n\
$\nprivacy protection$\r$\n\
CYFS Browser supports anonymous browsing mode to protect your online privacy.$\r$\n\
"

!define MUI_LICENSEPAGE_TEXT_TOP "Press Page Down to see the terms of the agreement."
!define MUI_LICENSEPAGE_TEXT_BOTTOM "If you accept the terms of the agreement, click I Agree to continue."
!define MUI_INSTFILESPAGE_FINISHHEADER_TEXT "Please wait while CYFS Browser (V ${BrowserVersion}) is being installed"
; !define MUI_INSTFILESPAGE_FINISHHEADER_SUBTEXT


!define MUI_FINISHPAGE_TITLE "CYFS Browser install complete"
!define MUI_FINISHPAGE_TEXT "CYFS Browser (V ${BrowserVersion}) has been installed on your computer.$\r$\n\
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

!define MUI_FINISHPAGE_NOREBOOTSUPPORT
!insertmacro MUI_PAGE_FINISH

; Uninstaller pages
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

; Language files
!insertmacro MUI_LANGUAGE "English"


Name "${BROWSER_NAME_ALIAS} ${PRODUCT_VERSION}"
; Name "${BROWSER_NAME_ALIAS}"
OutFile "${PRODUCT_NAME}_${PRODUCT_VERSION}.exe"
Caption "${BROWSER_NAME_ALIAS} Install (V ${BrowserVersion})"

;ShowInstDetails nevershow
;ShowUnInstDetails nevershow

BrandingText "CYFS Core Dev Team"

; set browser install path
InstallDir "$APPDATA\${PRODUCT_NAME}"

; install need admin rights
RequestExecutionLevel admin

InstallDirRegKey ${PRODUCT_INST_ROOT_KEY} "${PRODUCT_DIR_REGKEY}" ""
; InstallDirRegKey ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" ""

Function KillProc
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

!macro ForceKillProcess EXEName
	push ${EXEName}
	Call KillProc
!macroend

Function .onInit
  !insertmacro MUI_LANGDLL_DISPLAY
  !insertmacro ForceKillProcess ${RUNTIME_EXE_NAME}
  !insertmacro ForceKillProcess ${BROWSER_EXE_NAME}
  !insertmacro ForceKillProcess ${NFT_TOOL_EXE}
FunctionEnd

Function AutoBoot
  WriteRegStr ${AUTORUN_ROOT_KEY} "${AUTORUN_KEYPATH}" "${PRODUCT_NAME}" "$INSTDIR\${PRODUCT_NAME}\${PRODUCT_NAME}.exe"
FunctionEnd

Function LaunchLink
  ExecShell "" "$INSTDIR\${PRODUCT_NAME}\${PRODUCT_NAME}.exe"
FunctionEnd

Function LaunchCyfsRuntime
  ExecShell "" "$APPDATA\cyfs\services\runtime\${RUNTIME_EXE_NAME}"
FunctionEnd

Function InstallVC
  Push $R0
  ClearErrors
  ReadRegStr $R0 ${PRODUCT_INST_ROOT_KEY} ${VC_COMPONENT_KEY} "install_vc"

  IfErrors 0 VSRedistInstalled
  LogText "install vc runtime"
  Exec "$INSTDIR\VC_redist.x64.exe /q /norestart"
  WriteRegStr ${PRODUCT_INST_ROOT_KEY} "${VC_COMPONENT_KEY}" "install_vc" "1"
  StrCpy $R0 "-1"

VSRedistInstalled:
  Exch $R0
FunctionEnd

Section "-LogSetOn"
  LogSet on
SectionEnd

Section "delete_browser_old_files" 1
  ReadRegStr $0 ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayVersion"
  LogText "current application version = $0"

  ReadRegStr $1 ${PRODUCT_INST_ROOT_KEY} "${PRODUCT_DIR_REGKEY}" "BrowserInstallDir"
  LogText "current install path = $1"

  UserInfo::GetAccountType
  Pop $R0
  LogText "current user = $R0"

  !insertmacro ForceKillProcess ${BROWSER_EXE_NAME}
  !insertmacro ForceKillProcess ${RUNTIME_EXE_NAME}
  !insertmacro ForceKillProcess ${NFT_TOOL_EXE}
  Delete "$DESKTOP\${BROWSER_DESKTOP_NAME}.lnk"
  Delete "$SMPROGRAMS\${BROWSER_DESKTOP_NAME}.lnk"
  ;delete old version shortcut dir
  RMDir /r "$SMPROGRAMS\${PRODUCT_NAME}"
  DeleteRegValue ${AUTORUN_ROOT_KEY} "${AUTORUN_KEYPATH}" "${PRODUCT_NAME}"
  ;return up-level directory and delete all files
  SetOutPath $APPDATA
  RMDir /r  $INSTDIR
SectionEnd

Section "regedit_browser_info" 2
  SetOutPath "$INSTDIR"
  ; if old same name file is exists, directly overwrite
  SetOverwrite on
  ;File /r /x *.nsi /x ${OutFile} /x .git /x "\cyfs-runtime-pack\*.*"  *.*
  SetOutPath "$INSTDIR\Cyfs_Browser"
  File /r "Cyfs_Browser\*.*"
  SetOutPath "$INSTDIR"
  File browser.ico license.txt VC_redist.x64.exe

  WriteUninstaller "$INSTDIR\uninst.exe"

  WriteRegStr ${PRODUCT_INST_ROOT_KEY} "${PRODUCT_DIR_REGKEY}" "BrowserInstallDir" "$INSTDIR"

  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayName" "$(^Name)"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "Publisher" "${PRODUCT_PUBLISHER}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "UninstallString" "$INSTDIR\uninst.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayIcon" "$INSTDIR\${PRODUCT_NAME}\${PRODUCT_NAME}.exe,0"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayVersion" "${PRODUCT_VERSION}"

  WriteRegStr ${CYFS_SCHEME_ROOT_KEY} "${CYFS_SCHEME_REGKEY}" "" "URL:cyfs Protocol"
  WriteRegStr ${CYFS_SCHEME_ROOT_KEY} "${CYFS_SCHEME_REGKEY}" "URL Protocol" ""
  WriteRegStr ${CYFS_SCHEME_ROOT_KEY} "${CYFS_SCHEME_REGKEY}\shell\open\command" "" '"$APPDATA\\Cyfs_Browser\\Cyfs_Browser\\Cyfs_Browser.exe" "%1"'

  Call InstallVC
SectionEnd

Section "create_browser_shortcuts" 3
  ${RefreshShellIcons}
  SetOutPath "$INSTDIR"
  CreateShortCut "$SMPROGRAMS\${BROWSER_DESKTOP_NAME}.lnk" "$INSTDIR\${PRODUCT_NAME}\${PRODUCT_NAME}.exe" "" "$INSTDIR\browser.ico"
  CreateShortCut "$DESKTOP\${BROWSER_DESKTOP_NAME}.lnk" "$INSTDIR\${PRODUCT_NAME}\${BROWSER_EXE_NAME}" "" "$INSTDIR\browser.ico"
SectionEnd

Section "delete_runtime_old_files" 4
  Delete "$DESKTOP\${RUNTIME_DESKTOP_NAME}.lnk"
  Delete "$DESKTOP\${START_RUNTIME_BAT}.lnk"
  Delete "$SMPROGRAMS\${RUNTIME_DESKTOP_NAME}.lnk"
  ;delete old version shortcut dir
  RMDir /r "$SMPROGRAMS\${RUNTIME_DESKTOP_NAME}"
  ;return up-level directory and delete all files
  SetOutPath $APPDATA
  RMDir /r  "$APPDATA\cyfs\services\runtime"
SectionEnd

Section "copy_runtime_file" 5
  SetOutPath "$APPDATA\cyfs\services\runtime"
  ; if old same name file is exists, directly overwrite
  SetOverwrite on
  File /r /x  "cyfs-runtime-pack\acl.toml" /x  "cyfs-runtime-pack\runtime.toml" /x "cyfs-runtime-pack\tools\*.*" "cyfs-runtime-pack\*.*"
  File "restart_runtime.ico" "RestartRuntime.bat"

  SetOutPath "$APPDATA\cyfs\etc\acl"
  File "cyfs-runtime-pack\acl.toml"

  IfFileExists "$APPDATA\cyfs\etc\runtime" exists not_exists
  not_exists:
    CreateDirectory "$APPDATA\cyfs\etc\runtime"
  exists:
    LogText "$APPDATA\cyfs\etc\runtime is exists"
  SetOutPath "$APPDATA\cyfs\etc\runtime"
  File "cyfs-runtime-pack\runtime.toml"

  SetOutPath "$APPDATA\cyfs\services\runtime\tools"
  File /r "cyfs-runtime-pack\tools\*.*"

  SetOutPath "$APPDATA\cyfs\services\runtime"
  Delete "$APPDATA\cyfs\services\runtime\runtime.toml"
SectionEnd

; Section "create_runtime_shortcuts" 6
;   ${RefreshShellIcons}
;   SetOutPath "$APPDATA\cyfs\services\runtime"
;   CreateShortCut "$SMPROGRAMS\${RUNTIME_DESKTOP_NAME}.lnk" "$APPDATA\cyfs\services\runtime\${PRODUCT_RUNTIME_NAME}.exe" "" "$APPDATA\cyfs\services\runtime\runtime.ico"
;   CreateShortCut "$DESKTOP\${RUNTIME_DESKTOP_NAME}.lnk" "$APPDATA\cyfs\services\runtime\${PRODUCT_RUNTIME_NAME}.exe" "" "$APPDATA\cyfs\services\runtime\runtime.ico"
;   CreateShortCut "$DESKTOP\${START_RUNTIME_BAT}.lnk" "$APPDATA\cyfs\services\runtime\RestartRuntime.bat" "" "$APPDATA\cyfs\services\runtime\restart_runtime.ico"
;   ; Call LaunchCyfsRuntime
; SectionEnd

Section "regedit_nft_tool_info" 7
  WriteRegStr ${NFT_TOOL_ROOT_KEY} "*\shell\Create NFT by cyfs link" "Icon" "$APPDATA\\Cyfs_Browser\\Cyfs_Browser\\nft-creator.exe,0"
  WriteRegStr ${NFT_TOOL_ROOT_KEY} "*\shell\Create NFT by cyfs link\command" "" '"$APPDATA\\Cyfs_Browser\\Cyfs_Browser\\nft-creator.exe" "%1"'

  WriteRegStr ${NFT_TOOL_ROOT_KEY} "Directory\shell\Create NFT by cyfs link" "Icon" "$APPDATA\\Cyfs_Browser\\Cyfs_Browser\\nft-creator.exe,0"
  WriteRegStr ${NFT_TOOL_ROOT_KEY} "Directory\shell\Create NFT by cyfs link\command" "" '"$APPDATA\\Cyfs_Browser\\Cyfs_Browser\\nft-creator.exe" "%1"'
SectionEnd

Function .onInstSuccess
  ;ExecShell "open" "$INSTDIR\${BROWSER_NAME_ALIAS}\${BROWSER_EXE_NAME}"
FunctionEnd

Function un.onInit
  MessageBox MB_ICONQUESTION|MB_YESNO|MB_DEFBUTTON2 "Are you sure to remove $(^Name) and its all components completely?" IDYES +2
  Abort
  Exec '"taskkill" /F /IM ${BROWSER_EXE_NAME} /T'
FunctionEnd

Function un.onUninstSuccess
  HideWindow
  MessageBox MB_ICONINFORMATION|MB_OK "$(^Name) Has been successfully removed from your computer"
FunctionEnd

Function un.deleteUserData
  MessageBox MB_OKCANCEL "Do you want to delete user data" /SD IDOK IDOK label_ok IDCANCEL label_cancel
label_ok:
  SetOutPath $APPDATA
  LogText "delete runtime data $APPDATA\cyfs"
  DetailPrint "delete runtime data $APPDATA\cyfs"
  RMDir /r  "$APPDATA\cyfs"
  LogText "delete browser user data"
  RMDir /r "$LOCALAPPDATA\${BROWSER_USER_DATA_DIR}"
  RMDir /r "$LOCALAPPDATA\${OLD_BROWSER_USER_DATA_DIR}"
  Goto end
label_cancel:
  LogText "cancel delete user data"
  Goto end
end:
FunctionEnd

Function un.killRuntimeProcess
  DetailPrint "kill runtime process"
  MessageBox MB_OKCANCEL "Do you want to uninstall ${RUNTIME_EXE_NAME} component , MAY cause other applications unavailable" /SD IDOK IDOK label_ok IDCANCEL label_cancel
label_ok:
  LogText "start kill runtime process"
  Exec '"taskkill" /F /IM ${RUNTIME_EXE_NAME} /T'
  Sleep 1000
  RMDir /r "$APPDATA\cyfs\services\runtime"
label_cancel:
  Goto end
end:
FunctionEnd

Section Uninstall
  SetOutPath $APPDATA

  RMDir /r "$INSTDIR"
  RMDir /r "$APPDATA\${PRODUCT_NAME}"

  Call un.killRuntimeProcess
  Call un.deleteUserData

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
  ${RefreshShellIcons}
  SetAutoClose true
SectionEnd

