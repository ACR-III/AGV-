pause
pause
pause

for /r . %%a in (.) do @if exist "%%a\.git" rd /s /q "%%a\.git"
