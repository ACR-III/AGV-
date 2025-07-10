
:: 删除所有的exe文件（唯一留下pandoc.exe）

for %%i in (*.exe) do (
  if "%%i" NEQ "pandoc.exe" (del /f /q "%%i")
)

del /q /f *.bak

rd /s /q __pycache__

rd /s /q venv 

pause
