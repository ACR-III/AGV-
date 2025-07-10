:: 执行下句开启pause。如果取消pause，注释掉下一句
:: set DebugFlag=Defined
:: @if defined DebugFlag (@pause)

:: 如果命令行带有debug，则启动pause测试
if "%1"=="debug" (set DebugFlag=Defined)
if "%1"=="d" (set DebugFlag=Defined)

:: ------------------------------
set UWISToolsLib="c:\uwistoolslib"
:: ------------------------------

rm -r -f dist
rm -r -f build

:: 编译每一个py文件s
pyinstaller3 -F --distpath .\ main.py
copy /Y main.exe agvemulator.exe

@if defined DebugFlag (@pause)

git log --pretty=format:"%%h" | awk "NR==1{print $1}" > commitid.txt

set /P commitid=<commitid.txt
echo commitid=%commitid%
set MyVersionNumber=%commitid%

:: 删除过程文件

@if defined DebugFlag (@pause)

rm -r -f dist
rm -r -f build

@if defined DebugFlag (@pause)
