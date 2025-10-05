@echo off
SETLOCAL ENABLEDELAYEDEXPANSION
set PROJECT_DIR=%~dp0
set VENV_NAME=.venv

echo Checking for virtual environment...
if exist "%VENV_NAME%\" (
    echo Virtual environment found. Activating...
    call "%PROJECT_DIR%%VENV_NAME%\Scripts\activate.bat"
    
) else (
    echo No virtual environment found. Creating...
    C:\Python311\python.exe -m venv "%PROJECT_DIR%%VENV_NAME%"
    call "%PROJECT_DIR%%VENV_NAME%\Scripts\activate.bat"
)

echo Updating pip...
python -m pip install --upgrade pip | FINDSTR /V /C:"Requirement already satisfied"

echo Checking CUDA version...
for /F "delims=" %%A in ('nvcc --version ^| FINDSTR /R "[0-9][0-9]\.[0-9]"') do (
    set "line=%%A"
    set "line=!line:,=!"

    for %%B in (!line!) do (

        >__tmp.txt echo %%B

        for /F %%C in ('FINDSTR /R "^[0-9][0-9]\.[0-9]$" __tmp.txt') DO (
            set "match=%%C"
            set "nodot=!match:.=!"
            del __tmp.txt
            goto :versionfound
        )
    )
)

if exist __tmp.txt del __txt.tmp

echo No CUDA version found. Will proceed using CPU torch.
goto :update


:versionfound
echo CUDA version %match% found. Checking install of pytorch version.
pip install torch==2.5.1 torchvision==0.20.1 torchaudio==2.5.1 --index-url https://download.pytorch.org/whl/cu%nodot% | FINDSTR /V /C:"Requirement already satisfied"
goto :update


:update
echo Checking remaining requirements...
pip install -r "%PROJECT_DIR%requirements.txt" | FINDSTR /V /C:"Requirement already satisfied"
echo Requirements up-to-date.

echo Installing frontend requirements...
call npm --prefix src/frontend install --silent

echo Launching frontend...
start "Frontend" cmd /c "npm --prefix src/frontend start"

echo Launching backend...
python src/api.py