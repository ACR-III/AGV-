:: ִ���¾俪��pause�����ȡ��pause��ע�͵���һ��
:: set DebugFlag=Defined
:: @if defined DebugFlag (@pause)

:: ��������д���debug��������pause����
if "%1"=="debug" (set DebugFlag=Defined)
if "%1"=="d" (set DebugFlag=Defined)

rem ��װPython3.7/3.8����ı�Ҫ����չ��
rem --timeout 6000 ������Ϊ�˷�ֹpip��װ��ʱ��ʱ����

set Python37_Path=C:\Users\Administrator\AppData\Local\Programs\Python\Python37
set Python38_Path=C:\Users\Administrator\AppData\Local\Programs\Python\Python38

if exist %Python37_Path% (
  cd /d %Python37_Path%
)
if exist %Python38_Path% (
  cd /d %Python38_Path%
)

cp -f python.exe python3.exe
cd Scripts
cp -f easy_install.exe easy_install3.exe
cp -f pip.exe pip3.exe
cp -f pyinstaller.exe pyinstaller3.exe

@if defined DebugFlag (@pause)

rem ��ʼ��װģ��
python3.exe -m pip install --upgrade pip --force-reinstall --timeout 6000 -i https://pypi.tuna.tsinghua.edu.cn/simple/

@if defined DebugFlag (@pause)

pip3 uninstall -y pymysql
pip3 uninstall -y pyinstaller
pip3 uninstall -y pytest

pip3 install pymysql -i https://pypi.tuna.tsinghua.edu.cn/simple/
pip3 install pyinstaller -i https://pypi.tuna.tsinghua.edu.cn/simple/
pip3 install pytest -i https://pypi.tuna.tsinghua.edu.cn/simple/
pip3 install paramiko qiniu pypandoc -i https://pypi.tuna.tsinghua.edu.cn/simple/
pip3 install pyttsx3 thready -i https://pypi.tuna.tsinghua.edu.cn/simple/
pip3 install pipenv -i https://pypi.tuna.tsinghua.edu.cn/simple/
pip3 install PyQt5 -i https://pypi.tuna.tsinghua.edu.cn/simple/
pip3 install qtawesome -i https://pypi.tuna.tsinghua.edu.cn/simple/
pip3 install pycommands -i https://pypi.tuna.tsinghua.edu.cn/simple/


cd C:\Users\Administrator\AppData\Local\Programs\Python\Python38\Scripts
cp -f pyinstaller.exe pyinstaller3.exe

@if defined DebugFlag (@pause)
