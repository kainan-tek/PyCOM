# PyCOM

<div align="center">

![Version](https://img.shields.io/badge/version-2.0.0-blue)
![Python](https://img.shields.io/badge/python-3.14+-green)
![License](https://img.shields.io/badge/license-MIT-orange)
![Code Quality](https://img.shields.io/badge/code%20quality-9.4%2F10-brightgreen)

**Powerful Serial Communication Tool | Built with Python and PySide6**

[Features](#features) • [Quick Start](#quick-start) • [Usage Guide](#usage-guide) • [Project Structure](#project-structure)

[中文文档](README.md) | English

</div>

---

## Features

### Serial Port Management
- ✅ Auto-detect available ports
- ✅ Baud rate support: 300 ~ 3000000 bps
- ✅ Configurable data bits, stop bits, parity
- ✅ Elegant toggle button design

### Data Transmission
- **Single Send**: Text/Hex mode with cycle sending
- **Multi Send**: 6 independent channels with batch cycle sending
- **File Send**: Support for TXT and JSON files

### Data Reception
- ✅ Real-time data display
- ✅ Text/Hex mode switching
- ✅ Save received data to file
- ✅ Send/Receive byte statistics

### Encoding Support
ASCII • UTF-8 • UTF-16 • UTF-32 • GBK/GB2312

---

## System Requirements

| Item | Requirement |
|------|-------------|
| OS | Windows 7/8/10/11 |
| Python | 3.14+ |
| Package Manager | UV (recommended) or pip |

---

## Quick Start

### Using UV (Recommended)

```powershell
# Install UV
irm https://astral.sh/uv/install.ps1 | iex

# Clone repository
git clone https://github.com/kainan-tek/PyCom.git
cd PyCom

# Sync dependencies
uv sync

# Run application
uv run python main.py
```

### Using pip

```powershell
# Clone repository
git clone https://github.com/kainan-tek/PyCom.git
cd PyCom

# Create virtual environment
python -m venv .venv
.\.venv\Scripts\activate

# Install dependencies
pip install pyserial pyside6 chardet

# Run application
python main.py
```

---

## Usage Guide

### 1. Serial Port Configuration

1. Click **Check** to scan available ports
2. Select target port
3. Configure parameters (baud rate, data bits, stop bits, parity)
4. Click toggle button to open port

### 2. Single Send

**Basic Operation**:
- Enter data in text box
- Click **Send** to transmit

**Options**:
- **Hex Mode**: Hexadecimal mode (auto-conversion)
- **Cycle**: Cycle sending (set interval in milliseconds)
- **New Line**: Auto-append line break

**Examples**:
```
Text mode: Hello World
Hex mode: 48 65 6C 6C 6F (auto-formatted)
```

### 3. Multi Send

**Individual Send**:
- Enter data in any input box
- Click corresponding **Send** button

**Batch Cycle Send**:
1. Enter data in multiple input boxes
2. Check items to send
3. Check **Cycle** and set interval
4. Send selected items in sequence

**Options**:
- **Hex Mode**: Hexadecimal mode (applies to all channels)
- **Cycle**: Cycle sending
- **New Line**: Auto-append line break

### 4. File Send

**TXT Files**:
- Send entire text file content
- Auto-detect file encoding

**JSON Files**:
- Advanced send control
- Configurable intervals and order
- Support mixed text and hex data

**JSON Format**:
```json
{
    "cycle_ms": 1000,
    "hexmode": 0,
    "datas": [
        {
            "select": 1,
            "data": "Hello World\r\n"
        },
        {
            "select": 1,
            "data": "Test Data"
        }
    ]
}
```

**Field Description**:
- `cycle_ms`: Send interval (0=immediate, ≥1=cycle interval)
- `hexmode`: Data format (0=text, 1=hexadecimal)
- `select`: Whether to send (0=skip, 1=send)
- `data`: Data to send

**Example Files**: See `demo/` directory

### 5. Data Reception

- **Hex Mode**: Display in hexadecimal
- **Save**: Save to file
- **Clear**: Clear receive area

**Status Bar**: Real-time send/receive byte count
```
Send: 1024  |  Receive: 2048
```

### 6. Encoding Settings

Menu Bar → **Settings** → **Encoding** → Select encoding

Supported: ASCII, UTF-8, UTF-16, UTF-32, GBK/GB2312

---

## Project Structure

```
PyCOM/
├── main.py                 # Main program (UI control)
├── serial_manager.py       # Serial port management
├── data_handler.py         # Data processing module
│   ├── DataConverter       # Data format conversion
│   ├── DataSender          # Data send management
│   └── DataReceiver        # Data receive thread
├── file_handler.py         # File operations
├── globalvar.py            # Global constants
├── logwrapper.py           # Logging wrapper
├── jsonparser.py           # JSON parser
├── togglebt.py             # Custom toggle button
├── about.py                # About dialog
│
├── ui/                     # User interface
│   ├── mainwindow.ui       # Main window design
│   ├── mainwindow_ui.py    # Main window code
│   ├── about.ui            # About dialog design
│   └── about_ui.py         # About dialog code
│
├── resrc/                  # Resources
│   ├── images/             # Icons and images
│   ├── resource.qrc        # Qt resource config
│   └── resource_rc.py      # Qt resource code
│
├── demo/                   # Example files
│   ├── demo_txt_data.json  # Text mode example
│   └── demo_hex_data.json  # Hex mode example
│
├── pyproject.toml          # Project configuration
├── uv.lock                 # Dependency lock
├── LICENSE                 # MIT License
└── README.md               # Project documentation
```

### Core Modules

| Module | Responsibility | Lines |
|--------|----------------|-------|
| **main.py** | UI control and event handling | 896 |
| **serial_manager.py** | Serial port management | 150 |
| **data_handler.py** | Data processing (3 classes) | 450 |
| **file_handler.py** | File operations | 150 |

### Architecture Features

- ✅ **Modular Design**: Clear responsibilities, easy maintenance
- ✅ **Single Responsibility**: Each module handles one core function
- ✅ **Low Coupling, High Cohesion**: Modules communicate via interfaces
- ✅ **Dependency Injection**: Improved testability
- ✅ **Multi-threading**: Independent receive thread, non-blocking UI

---

## Tech Stack

| Technology | Version | Purpose |
|------------|---------|---------|
| **Python** | 3.14+ | Programming language |
| **PySide6** | 6.10.2+ | GUI framework |
| **pyserial** | 3.5+ | Serial communication |
| **chardet** | 5.2.0+ | Encoding detection |

**Development Tools**: UV, Nuitka, Git, Qt Designer

---

## Build & Release

### Using Nuitka

```powershell
# Install Nuitka
uv pip install nuitka

# Build command
nuitka --msvc=latest ^
       --standalone ^
       --follow-imports ^
       --windows-console-mode=disable ^
       --show-progress ^
       --enable-plugin=pyside6 ^
       --windows-icon-from-ico=.\resrc\images\pycom.ico ^
       --include-data-dir=.\demo=.\demo ^
       --include-data-files=.\ReleaseNote.txt=ReleaseNote.txt ^
       main.py ^
       -o PyCOM.exe
```

**Output**: `main.dist/PyCOM.exe`

---

## FAQ

### Q: Cannot detect serial ports?
**A**: Check device connection, driver installation, or if port is occupied by another program

### Q: "Port occupied" error when opening?
**A**: Close other serial programs, or reconnect the device

### Q: Chinese characters display as garbled text?
**A**: Menu Bar → Settings → Encoding → Select UTF-8 or GBK

### Q: Cannot input in hex mode?
**A**: Only 0-9, A-F, a-f, and space are allowed

### Q: Cannot stop cycle sending?
**A**: Uncheck Cycle checkbox, or close the port

### Q: JSON file send failed?
**A**: Check JSON format, refer to examples in demo directory

**Log Location**: `C:\Users\<username>\log\pycom\pycom.log`

---

## Version History

### v2.0.0 (2026-02-09) - Refactored Version
- 🎉 **Architecture Refactor**: Modular design, code quality improved to 9.4/10
- ✨ **New Features**: Multi Send Hex Mode auto-conversion and validation
- 🐛 **Bug Fixes**: Encoding sync, resource cleanup, behavior consistency
- 📝 **Code Optimization**: Removed redundant code, improved error handling
- 📊 **Performance**: Added data loss monitoring

### v1.3.2 (2024-12-XX)
- Updated PySide6 to v6.10.2
- Optimized exception handling
- Improved resource cleanup

<details>
<summary>View Full Version History</summary>

### v1.3.1 (2024-11-XX)
- Optimized serial port toggle button animation

### v1.3.0 (2024-10-XX)
- Introduced UV package manager
- Code formatting with Ruff

### v1.2.x
- UI optimization and feature improvements

### v1.1.x
- Added multi-send and file-send features

### v1.0.0
- Initial release

</details>

Full version history: [ReleaseNote.txt](ReleaseNote.txt)

---

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Submit Pull Request

**Code Standards**:
- Follow PEP 8
- Use type hints
- Add docstrings
- Ensure tests pass

**Report Issues**: [GitHub Issues](https://github.com/kainan-tek/PyCom/issues)

---

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details

---

## Contact

- **Author**: kainan-tek
- **Email**: kainanos@outlook.com
- **GitHub**: https://github.com/kainan-tek/PyCom
- **Issue Tracker**: [GitHub Issues](https://github.com/kainan-tek/PyCom/issues)

---

<div align="center">

**If this project helps you, please give it a ⭐ Star!**

Made with ❤️ by kainan-tek

[⬆ Back to Top](#pycom)

</div>
