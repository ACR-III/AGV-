:: ִ���¾俪��pause�����ȡ��pause��ע�͵���һ��
:: set DebugFlag=Defined
:: @if defined DebugFlag (@pause)

:: ��������д���debug��������pause����
if "%1"=="debug" (set DebugFlag=Defined)
if "%1"=="d" (set DebugFlag=Defined)

:: ------------------------------
set UWISToolsLib="c:\uwistoolslib"
:: ------------------------------

rm -r -f dist
rm -r -f build

:: ����ÿһ��py�ļ�s
pyinstaller3 -F --distpath .\ main.py
copy /Y main.exe agvemulator.exe

@if defined DebugFlag (@pause)

git log --pretty=format:"%%h" | awk "NR==1{print $1}" > commitid.txt

set /P commitid=<commitid.txt
echo commitid=%commitid%
set MyVersionNumber=%commitid%

:: ɾ�������ļ�

@if defined DebugFlag (@pause)

rm -r -f dist
rm -r -f build

@if defined DebugFlag (@pause)
