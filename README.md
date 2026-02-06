# PyCOM

<div align="center">

![Version](https://img.shields.io/badge/version-1.3.2-blue)
![Python](https://img.shields.io/badge/python-3.14+-green)
![License](https://img.shields.io/badge/license-MIT-orange)

**一个功能强大的串口通信工具，基于 Python 和 PySide6 开发**

[English](#) | [简体中文](#)

</div>

---

## 📋 目录

- [功能特性](#-功能特性)
- [系统要求](#-系统要求)
- [快速开始](#-快速开始)
- [安装指南](#-安装指南)
- [使用说明](#-使用说明)
- [JSON 文件格式](#-json-文件格式)
- [打包发布](#-打包发布)
- [项目结构](#-项目结构)
- [技术栈](#-技术栈)
- [版本历史](#-版本历史)
- [常见问题](#-常见问题)
- [贡献指南](#-贡献指南)
- [许可证](#-许可证)
- [联系方式](#-联系方式)

---

## ✨ 功能特性

### 🔌 串口管理
- ✅ 自动检测和枚举可用串口
- ✅ 支持波特率：300 ~ 3000000 bps
- ✅ 可配置数据位（5-8）、停止位（1-2）、校验位（None/Odd/Even）
- ✅ 优雅的开关按钮设计，一键开启/关闭串口

### 📤 数据发送
- **单次发送**
  - 支持文本和十六进制模式
  - 可选循环发送，自定义发送间隔
  - 可选添加换行符
  
- **多路发送**
  - 6 个独立发送通道
  - 每个通道独立配置数据和发送按钮
  - 支持批量循环发送选中项
  - 文本/十六进制模式切换
  
- **文件发送**
  - 支持 TXT 文本文件直接发送
  - 支持 JSON 配置文件高级发送
  - JSON 模式可自定义发送顺序、间隔和数据格式

### 📥 数据接收
- ✅ 实时显示接收数据
- ✅ 文本/十六进制模式切换
- ✅ 保存接收数据到文件
- ✅ 清空接收缓冲区
- ✅ 发送/接收字节统计

### 🌐 编码支持
- ASCII
- UTF-8
- UTF-16
- UTF-32
- GBK / GB2312（默认）

### 🎨 用户界面
- 现代化的 GUI 界面
- 直观的操作控件
- 实时状态指示
- 内置使用指南

---

## 💻 系统要求

| 项目 | 要求 |
|------|------|
| **操作系统** | Windows 7/8/10/11 |
| **Python 版本** | 3.14 或更高 |
| **包管理器** | UV（推荐）或 pip |
| **硬件** | 支持串口通信的设备 |

---

## 🚀 快速开始

### 方式一：使用 UV（推荐）

```powershell
# 1. 安装 UV 包管理器
irm https://astral.sh/uv/install.ps1 | iex

# 2. 克隆项目
git clone https://github.com/kainan-tek/PyCom.git
cd PyCom

# 3. 同步依赖
uv sync

# 4. 运行程序
uv run python main.py
```

### 方式二：使用 pip

```powershell
# 1. 克隆项目
git clone https://github.com/kainan-tek/PyCom.git
cd PyCom

# 2. 创建虚拟环境（可选）
python -m venv .venv
.\.venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt
# 或手动安装
pip install pyserial pyside6 chardet

# 4. 运行程序
python main.py
```

---

## 📦 安装指南

### 前置条件

确保已安装 Python 3.14 或更高版本：

```powershell
python --version
```

### 依赖包说明

| 包名 | 版本 | 用途 |
|------|------|------|
| **PySide6** | >= 6.10.2 | Qt6 GUI 框架 |
| **pyserial** | >= 3.5 | 串口通信库 |
| **chardet** | >= 5.2.0 | 字符编码检测 |

### 安装步骤

#### 使用 UV（推荐）

UV 是一个快速的 Python 包管理器，比 pip 更快更可靠。

```powershell
# 安装 UV
irm https://astral.sh/uv/install.ps1 | iex

# 进入项目目录
cd PyCom

# 同步依赖（自动创建虚拟环境）
uv sync

# 运行程序
uv run python main.py
```

#### 使用 pip

```powershell
# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
.\.venv\Scripts\activate

# 安装依赖
pip install pyserial pyside6 chardet

# 运行程序
python main.py
```

---

## 📖 使用说明

### 1. 串口配置

#### 步骤：
1. 点击 **"Check"** 按钮扫描可用串口
2. 从下拉菜单选择目标串口
3. 配置串口参数：
   - **波特率**：300 ~ 3000000（默认：115200）
   - **数据位**：5/6/7/8（默认：8）
   - **停止位**：1/2（默认：1）
   - **校验位**：None/Odd/Even（默认：None）
4. 点击开关按钮打开串口

#### 提示：
- 串口打开后，配置选项将被禁用
- 关闭串口后才能重新配置参数

---

### 2. 单次发送

#### 功能说明：
在文本框中输入数据，点击发送按钮即可发送。

#### 选项：
- **Hex Mode**：勾选后以十六进制格式发送数据
  - 输入格式：`48 65 6C 6C 6F` 或 `48656C6C6F`
  - 自动格式化为空格分隔的十六进制
  
- **Cycle**：勾选后启用循环发送
  - 输入框设置发送间隔（毫秒）
  - 范围：1 ~ 99999 ms
  
- **New Line**：勾选后自动添加换行符（\r\n）

#### 操作：
1. 在文本框输入要发送的数据
2. 根据需要勾选选项
3. 点击 **"Send"** 按钮发送
4. 点击 **"Clear"** 按钮清空输入

#### 示例：
```
文本模式：Hello World
十六进制模式：48 65 6C 6C 6F
```

---

### 3. 多路发送

#### 功能说明：
提供 6 个独立的发送通道，每个通道可以独立发送或批量循环发送。

#### 使用方式：

**方式一：独立发送**
1. 在任意输入框中输入数据
2. 点击对应的 **"Send"** 按钮发送该条数据

**方式二：批量循环发送**
1. 在多个输入框中输入数据
2. 勾选需要发送的数据项前的复选框
3. 勾选 **"Cycle"** 并设置发送间隔
4. 程序将按顺序循环发送选中的数据项

#### 选项：
- **Hex Mode**：十六进制模式（应用于所有通道）
- **Cycle**：循环发送模式
- **New Line**：自动添加换行符

#### 提示：
- 单次发送和多路发送的循环模式不能同时启用
- 空白的输入框将被自动跳过

---

### 4. 文件发送

#### 支持的文件类型：

##### 4.1 TXT 文件
直接发送文本文件的全部内容。

**操作步骤：**
1. 点击 **"Select"** 按钮选择 TXT 文件
2. 点击 **"Send"** 按钮发送文件内容

**特点：**
- 自动检测文件编码
- 支持大文件发送
- 保留原始格式（包括换行符）

##### 4.2 JSON 文件
使用 JSON 配置文件进行高级发送控制。

**操作步骤：**
1. 点击 **"Select"** 按钮选择 JSON 文件
2. 点击 **"Send"** 按钮开始发送
3. 程序将根据 JSON 配置自动发送数据

**优势：**
- 可配置发送间隔
- 可选择发送哪些数据项
- 支持文本和十六进制混合发送
- 适合自动化测试场景

详细的 JSON 格式说明请参见 [JSON 文件格式](#-json-文件格式) 章节。

---

### 5. 数据接收

#### 功能：
- **实时显示**：接收到的数据实时显示在接收区域
- **Hex Mode**：勾选后以十六进制格式显示接收数据
- **Save**：保存接收数据到 TXT 文件
- **Clear**：清空接收区域和接收计数

#### 状态栏：
底部状态栏实时显示发送和接收的字节数：
```
Send: 1024  |  Receive: 2048
```

---

### 6. 编码设置

#### 更改编码：
菜单栏 → **Settings** → **Encoding** → 选择编码格式

#### 支持的编码：
- ASCII
- UTF-8
- UTF-16
- UTF-32
- GBK / GB2312（默认）

#### 说明：
- 编码设置影响数据的发送和接收
- 建议根据通信设备的编码格式进行设置
- 默认使用 GBK 编码（适合中文环境）

---

## 📄 JSON 文件格式

### 文件结构

JSON 文件用于配置高级发送功能，包含以下字段：

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

### 字段说明

| 字段 | 类型 | 说明 | 可选值 |
|------|------|------|--------|
| **cycle_ms** | 整数 | 发送间隔（毫秒） | 0 = 立即发送所有<br>≥1 = 循环发送间隔 |
| **hexmode** | 整数 | 数据格式 | 0 = 文本模式<br>1 = 十六进制模式 |
| **datas** | 数组 | 数据项列表 | 包含多个数据对象 |
| **select** | 整数 | 是否发送该项 | 0 = 不发送<br>1 = 发送 |
| **data** | 字符串 | 要发送的数据 | 文本或十六进制字符串 |

### 示例文件

#### 示例 1：文本模式（demo_txt_data.json）

```json
{
    "cycle_ms": 1000,
    "hexmode": 0,
    "datas": [
        {
            "select": 1,
            "data": "test 1\r\n"
        },
        {
            "select": 1,
            "data": "中文 2\r\n"
        },
        {
            "select": 0,
            "data": "test 3\r\n"
        },
        {
            "select": 1,
            "data": "test 4\r\n"
        }
    ]
}
```

**说明：**
- 每隔 1000ms 发送一条数据
- 文本模式发送
- 将发送：test 1 → 中文 2 → test 4（跳过 test 3）

#### 示例 2：十六进制模式（demo_hex_data.json）

```json
{
    "cycle_ms": 1000,
    "hexmode": 1,
    "datas": [
        {
            "select": 1,
            "data": "02 04 1f FF fe"
        },
        {
            "select": 0,
            "data": "02 04 1f FF fe"
        },
        {
            "select": 1,
            "data": "ff fe 3f FF fa 0d 0a"
        }
    ]
}
```

**说明：**
- 每隔 1000ms 发送一条数据
- 十六进制模式发送
- 将发送：02 04 1f FF fe → ff fe 3f FF fa 0d 0a

### 使用场景

- ✅ 自动化测试脚本
- ✅ 批量数据发送
- ✅ 设备调试和配置
- ✅ 协议测试和验证

---

## 📦 打包发布

### 使用 Nuitka 打包

Nuitka 可以将 Python 程序编译为独立的可执行文件。

#### 前置条件

1. **安装 Microsoft Visual C++ 编译器**
   - 下载并安装 [Visual Studio Build Tools](https://visualstudio.microsoft.com/downloads/)
   - 或安装完整的 Visual Studio

2. **安装 Nuitka**
   ```powershell
   uv pip install nuitka
   # 或
   pip install nuitka
   ```

#### 打包命令

```powershell
nuitka --msvc=latest ^
       --standalone ^
       --follow-imports ^
       --windows-console-mode=disable ^
       --show-progress ^
       --show-memory ^
       --enable-plugin=pyside6 ^
       --windows-icon-from-ico=.\resrc\images\pycom.ico ^
       --include-data-dir=.\demo=.\demo ^
       --include-data-files=.\ReleaseNote.txt=ReleaseNote.txt ^
       main.py ^
       -o PyCOM.exe
```

#### 参数说明

| 参数 | 说明 |
|------|------|
| `--msvc=latest` | 使用最新版本的 MSVC 编译器 |
| `--standalone` | 创建独立可执行文件（包含所有依赖） |
| `--follow-imports` | 自动包含所有导入的模块 |
| `--windows-console-mode=disable` | 禁用控制台窗口（GUI 程序） |
| `--show-progress` | 显示编译进度 |
| `--show-memory` | 显示内存使用情况 |
| `--enable-plugin=pyside6` | 启用 PySide6 插件 |
| `--windows-icon-from-ico` | 设置程序图标 |
| `--include-data-dir` | 包含数据目录 |
| `--include-data-files` | 包含额外文件 |
| `-o PyCOM.exe` | 输出文件名 |

#### 打包后的文件

编译完成后，会生成 `main.dist` 目录，包含：
- `PyCOM.exe`：主程序
- 依赖的 DLL 文件
- `demo/` 目录
- `ReleaseNote.txt`

#### 运行打包后的程序

```powershell
cd main.dist
.\PyCOM.exe
```

---

## 📁 项目结构

```
PyCOM/
│
├── main.py                 # 主程序入口
├── about.py                # 关于对话框
├── globalvar.py            # 全局变量和常量
├── jsonparser.py           # JSON 文件解析器
├── logwrapper.py           # 日志封装模块
├── togglebt.py             # 自定义开关按钮组件
│
├── ui/                     # 用户界面
│   ├── mainwindow.ui       # 主窗口 UI 设计文件
│   ├── mainwindow_ui.py    # 主窗口 UI 代码（自动生成）
│   ├── about.ui            # 关于对话框 UI 设计文件
│   └── about_ui.py         # 关于对话框 UI 代码（自动生成）
│
├── resrc/                  # 资源文件
│   ├── images/             # 图标和图片
│   │   ├── pycom.ico       # 应用程序图标
│   │   ├── pycom.png       # 应用程序 Logo
│   │   └── wechat.jpg      # 微信二维码
│   ├── resource.qrc        # Qt 资源配置文件
│   └── resource_rc.py      # Qt 资源代码（自动生成）
│
├── demo/                   # 示例文件
│   ├── demo_txt_data.json  # 文本模式示例
│   └── demo_hex_data.json  # 十六进制模式示例
│
├── .venv/                  # 虚拟环境（自动生成）
├── __pycache__/            # Python 缓存（自动生成）
├── main.build/             # Nuitka 构建目录（自动生成）
├── main.dist/              # Nuitka 输出目录（自动生成）
│
├── pyproject.toml          # 项目配置文件
├── uv.lock                 # UV 依赖锁定文件
├── .gitignore              # Git 忽略规则
├── .python-version         # Python 版本标识
├── LICENSE                 # MIT 许可证
├── README.md               # 项目说明文档
└── ReleaseNote.txt         # 版本更新日志
```

### 核心模块说明

| 模块 | 功能 |
|------|------|
| **main.py** | 主窗口逻辑、串口通信、数据收发 |
| **about.py** | 关于对话框的实现 |
| **globalvar.py** | 全局配置、串口参数、界面文本 |
| **jsonparser.py** | JSON 文件的读取和解析 |
| **logwrapper.py** | 日志记录和管理 |
| **togglebt.py** | 自定义开关按钮控件 |

---

## 🛠️ 技术栈

### 核心技术

| 技术 | 版本 | 用途 |
|------|------|------|
| **Python** | 3.14+ | 编程语言 |
| **PySide6** | 6.10.2+ | GUI 框架（Qt6 for Python） |
| **pyserial** | 3.5+ | 串口通信库 |
| **chardet** | 5.2.0+ | 字符编码检测 |

### 开发工具

- **UV**：快速的 Python 包管理器
- **Nuitka**：Python 到 C/C++ 编译器
- **Git**：版本控制
- **Qt Designer**：UI 设计工具

### 架构特点

- **MVC 架构**：界面与逻辑分离
- **多线程设计**：接收线程独立运行，不阻塞 UI
- **事件驱动**：基于 Qt 信号槽机制
- **模块化设计**：功能模块独立，易于维护

---

## 📝 版本历史

### 最新版本

#### v1.3.2 (2024-12-XX)
- 更新 PySide6 到 v6.10.2
- 优化异常处理，使用更精确的异常类型
- 简化代码，移除冗余注释
- 改进资源清理逻辑

#### v1.3.1 (2024-11-XX)
- 优化串口开关按钮动画效果
- 改进用户交互体验

#### v1.3.0 (2024-10-XX)
- 引入 UV 包管理器
- 使用 Ruff 格式化代码
- 提升代码质量和一致性

### 历史版本

<details>
<summary>点击展开查看完整版本历史</summary>

#### v1.2.9
- 串口关闭时禁用相关按钮
- 更新微信二维码

#### v1.2.8
- 用开关按钮替换开启/关闭按钮
- 更新 Python 到 v3.13.2

#### v1.2.7
- 更新 Python 到 v3.12.4

#### v1.2.6
- 将 pycom.py 重命名为 main.py

#### v1.2.5
- 优化用户界面

#### v1.2.4
- 更新 PySide6 到 v6.6.2

#### v1.2.3
- 将 main.py 重命名为 pycom.py
- 添加 Nuitka 打包命令
- 修复日志打印问题

#### v1.2.2
- 一些小的改进

#### v1.2.1
- 修复 JSON 十六进制内容发送错误
- 一些小的改进

#### v1.2.0
- 一些小的改进

#### v1.1.2
- 为 JSON 文件发送功能添加十六进制模式
- 修复应用关闭问题
- 一些小的改进

#### v1.1.1
- 添加多种编码选项
- 修复文件发送中的换行问题
- 一些小的改进

#### v1.1.0
- 添加多路发送功能
- 添加文件发送功能

#### v1.0.0
- 初始版本
- 使用 PySide6 和 pyserial 实现

</details>

完整的版本历史请查看 [ReleaseNote.txt](ReleaseNote.txt)。

---

## ❓ 常见问题

### Q1: 无法检测到串口设备？

**A:** 请检查：
1. 设备是否正确连接到电脑
2. 设备驱动是否已安装
3. 设备是否被其他程序占用
4. 在设备管理器中查看串口是否正常

### Q2: 打开串口时提示"端口被占用"？

**A:** 可能的原因：
1. 其他程序正在使用该串口（如串口调试助手、Arduino IDE 等）
2. 上次程序异常退出，串口未正常关闭
3. 解决方法：关闭占用串口的程序，或重新插拔设备

### Q3: 接收到的中文显示乱码？

**A:** 编码设置不匹配：
1. 菜单栏 → Settings → Encoding
2. 尝试切换到 UTF-8 或 GBK
3. 根据发送设备的编码格式选择对应编码

### Q4: 十六进制模式下无法输入数据？

**A:** 十六进制模式限制：
1. 只能输入 0-9、A-F、a-f
2. 可以输入空格分隔
3. 如果需要输入其他字符，请取消勾选 Hex Mode

### Q5: 循环发送无法停止？

**A:** 停止循环发送：
1. 取消勾选 Cycle 复选框
2. 或关闭串口

### Q6: JSON 文件发送失败？

**A:** 请检查：
1. JSON 文件格式是否正确
2. 必需字段是否完整（cycle_ms、hexmode、datas）
3. 十六进制模式下，data 字段是否为有效的十六进制字符串
4. 参考 demo 目录下的示例文件

### Q7: 打包后的程序无法运行？

**A:** 可能的原因：
1. 缺少 Visual C++ 运行库，请安装 [VC++ Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe)
2. 打包时未包含必要的资源文件
3. 检查 main.dist 目录是否完整

### Q8: 如何查看程序日志？

**A:** 日志文件位置：
```
C:\Users\<用户名>\log\pycom\pycom.log
```

---

## 🤝 贡献指南

欢迎贡献代码、报告问题或提出建议！

### 如何贡献

1. **Fork 本仓库**
2. **创建特性分支**
   ```bash
   git checkout -b feature/AmazingFeature
   ```
3. **提交更改**
   ```bash
   git commit -m 'Add some AmazingFeature'
   ```
4. **推送到分支**
   ```bash
   git push origin feature/AmazingFeature
   ```
5. **提交 Pull Request**

### 代码规范

- 遵循 PEP 8 代码风格
- 使用类型提示（Type Hints）
- 添加必要的注释和文档字符串
- 确保代码通过测试

### 报告问题

在 [GitHub Issues](https://github.com/kainan-tek/PyCom/issues) 中报告问题时，请提供：
- 操作系统和 Python 版本
- 详细的问题描述
- 复现步骤
- 错误信息或截图

---

## 📜 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

```
MIT License

Copyright (c) 2024 kainan-tek

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 📧 联系方式

### 作者信息

- **作者**：kainan-tek
- **邮箱**：kainanos@outlook.com
- **GitHub**：https://github.com/kainan-tek/PyCom

### 获取帮助

- **问题反馈**：[GitHub Issues](https://github.com/kainan-tek/PyCom/issues)
- **功能建议**：[GitHub Discussions](https://github.com/kainan-tek/PyCom/discussions)
- **邮件支持**：kainanos@outlook.com

### 社区

如果这个项目对你有帮助，请给个 ⭐ Star 支持一下！

---

<div align="center">

**Made with ❤️ by kainan-tek**

[⬆ 回到顶部](#pycom)

</div>
