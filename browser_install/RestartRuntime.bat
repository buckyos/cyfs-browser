@echo off
setlocal enabledelayedexpansion

set desc_file=%appdata%\\cyfs\\etc\\desc\\device.desc
set sec_file=%appdata%\\cyfs\\etc\\desc\\device.sec

@echo off
if "%1" == "h" goto begin
mshta vbscript:createobject("wscript.shell").run("""%~nx0"" h",0)(window.close)&&exit
:begin

set Vbscript=Msgbox("Are you sure restart CYFS Runtime process��",1,"CYFS Runtime")
for /f "Delims=" %%a in ('MsHta VBScript:Execute("CreateObject(""Scripting.Filesystemobject"").GetStandardStream(1).Write(%Vbscript:"=""%)"^)(Close^)') do Set "MsHtaReturnValue=%%a"
@REM set ReturnValue1=ȷ��
@REM set ReturnValue2=ȡ����رմ���
rem echo ������!ReturnValue%MsHtaReturnValue%!
if %MsHtaReturnValue% == 1 goto restart
if %MsHtaReturnValue% != 1 goto end

:restart
echo kill runtime process
taskkill /f /t /im cyfs-runtime.exe

echo load runtime process
if exist %desc_file% (
    if exist %sec_file% (
        "%appdata%\\cyfs\\services\\runtime\\cyfs-runtime.exe" "--proxy-port=38090"
        echo "%appdata%\\cyfs\\services\\runtime\\cyfs-runtime.exe --proxy-port=38090"
        goto end
    )
)
"%appdata%\\cyfs\\services\\runtime\\cyfs-runtime.exe" "--anonymous" "--proxy-port=38090"
goto end

:end
exit