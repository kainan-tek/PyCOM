# PyCOM
***A serial communication tool written with python***   

## Steps to run the tool
```C
// install uv tool in windows powershell:
irm https://astral.sh/uv/install.ps1 | iex
// set up environment with below cmd on PyCOM path:
uv sync
// run the python file
uv run python main.py
```

## Package into PyCOM.exe with nuitka
```C
// install nuitka  
uv pip install nuitka
// generate exe
nuitka --msvc=latest --standalone --follow-imports --windows-console-mode=disable --show-progress --show-memory --enable-plugin=pyside6 --windows-icon-from-ico=.\resrc\images\pycom.ico --include-data-dir=.\demo=.\demo --include-data-files=.\ReleaseNote.txt=ReleaseNote.txt main.py -o PyCOM.exe
// run the executable file: PyCOM.exe
```
