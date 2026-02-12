# PyCOM

<div align="center">

![Version](https://img.shields.io/badge/version-2.0.0-blue)
![Python](https://img.shields.io/badge/python-3.14+-green)
![License](https://img.shields.io/badge/license-MIT-orange)
![Code Quality](https://img.shields.io/badge/code%20quality-9.4%2F10-brightgreen)

**功能强大的串口通信工具 | 基于 Python 和 PySide6**

[功能特性](#功能特性) • [快速开始](#快速开始) • [使用说明](#使用说明) • [项目结构](#项目结构)

中文 | [English](README_EN.md)

</div>

---

## 功能特性

### 串口管理
- ✅ 自动检测可用串口
- ✅ 支持波特率 300 ~ 3000000 bps
- ✅ 可配置数据位、停止位、校验位
- ✅ 优雅的开关按钮设计

### 数据发送
- **单次发送**: 文本/十六进制模式，支持循环发送
- **多路发送**: 6 个独立通道，批量循环发送
- **文件发送**: 支持 TXT 和 JSON 文件

### 数据接收
- ✅ 实时显示接收数据
- ✅ 文本/十六进制模式切换
- ✅ 保存接收数据到文件
- ✅ 发送/接收字节统计

### 编码支持
ASCII • UTF-8 • UTF-16 • UTF-32 • GBK/GB2312

---

## 系统要求

| 项目 | 要求 |
|------|------|
| 操作系统 | Windows 7/8/10/11 |
| Python | 3.14+ |
| 包管理器 | UV（推荐）或 pip |

---

## 快速开始

### 使用 UV（推荐）

```powershell
# 安装 UV
irm https://astral.sh/uv/install.ps1 | iex

# 克隆项目
git clone https://github.com/kainan-tek/PyCom.git
cd PyCom

# 同步依赖
uv sync

# 运行程序
uv run python main.py
```

### 使用 pip

```powershell
# 克隆项目
git clone https://github.com/kainan-tek/PyCom.git
cd PyCom

# 创建虚拟环境
python -m venv .venv
.\.venv\Scripts\activate

# 安装依赖
pip install pyserial pyside6 chardet

# 运行程序
python main.py
```

---

## 使用说明

### 1. 串口配置

1. 点击 **Check** 扫描可用串口
2. 选择目标串口
3. 配置参数（波特率、数据位、停止位、校验位）
4. 点击开关按钮打开串口

### 2. 单次发送

**基本操作**:
- 在文本框输入数据
- 点击 **Send** 发送

**选项**:
- **Hex Mode**: 十六进制模式（自动转换）
- **Cycle**: 循环发送（设置间隔毫秒）
- **New Line**: 自动添加换行符

**示例**:
```
文本模式: Hello World
十六进制模式: 48 65 6C 6C 6F (自动格式化)
```

### 3. 多路发送

**独立发送**:
- 在任意输入框输入数据
- 点击对应的 **Send** 按钮

**批量循环发送**:
1. 在多个输入框输入数据
2. 勾选需要发送的数据项
3. 勾选 **Cycle** 并设置间隔
4. 按顺序循环发送选中项

**选项**:
- **Hex Mode**: 十六进制模式（应用于所有通道）
- **Cycle**: 循环发送
- **New Line**: 自动添加换行符

### 4. 文件发送

**TXT 文件**:
- 直接发送文本文件全部内容
- 自动检测文件编码

**JSON 文件**:
- 高级发送控制
- 可配置发送间隔和顺序
- 支持文本和十六进制混合

**JSON 格式**:
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

**字段说明**:
- `cycle_ms`: 发送间隔（0=立即发送，≥1=循环间隔）
- `hexmode`: 数据格式（0=文本，1=十六进制）
- `select`: 是否发送（0=跳过，1=发送）
- `data`: 要发送的数据

**示例文件**: 参见 `demo/` 目录

### 5. 数据接收

- **Hex Mode**: 十六进制显示
- **Save**: 保存到文件
- **Clear**: 清空接收区域

**状态栏**: 实时显示发送/接收字节数
```
Send: 1024  |  Receive: 2048
```

### 6. 编码设置

菜单栏 → **Settings** → **Encoding** → 选择编码

支持: ASCII、UTF-8、UTF-16、UTF-32、GBK/GB2312

---

## 项目结构

```
PyCOM/
├── main.py                 # 主程序（UI 控制）
├── serial_manager.py       # 串口管理模块
├── data_handler.py         # 数据处理模块
│   ├── DataConverter       # 数据格式转换
│   ├── DataSender          # 数据发送管理
│   └── DataReceiver        # 数据接收线程
├── file_handler.py         # 文件操作模块
├── globalvar.py            # 全局常量配置
├── logwrapper.py           # 日志封装
├── jsonparser.py           # JSON 解析器
├── togglebt.py             # 自定义开关按钮
├── about.py                # 关于对话框
│
├── ui/                     # 用户界面
│   ├── mainwindow.ui       # 主窗口设计
│   ├── mainwindow_ui.py    # 主窗口代码
│   ├── about.ui            # 关于对话框设计
│   └── about_ui.py         # 关于对话框代码
│
├── resrc/                  # 资源文件
│   ├── images/             # 图标和图片
│   ├── resource.qrc        # Qt 资源配置
│   └── resource_rc.py      # Qt 资源代码
│
├── demo/                   # 示例文件
│   ├── demo_txt_data.json  # 文本模式示例
│   └── demo_hex_data.json  # 十六进制示例
│
├── pyproject.toml          # 项目配置
├── uv.lock                 # 依赖锁定
├── LICENSE                 # MIT 许可证
└── README.md               # 项目文档
```

### 核心模块

| 模块 | 职责 | 行数 |
|------|------|------|
| **main.py** | UI 控制和事件处理 | 896 |
| **serial_manager.py** | 串口管理 | 150 |
| **data_handler.py** | 数据处理（3个类） | 450 |
| **file_handler.py** | 文件操作 | 150 |

### 架构特点

- ✅ **模块化设计**: 职责清晰，易于维护
- ✅ **单一职责**: 每个模块只负责一个核心功能
- ✅ **低耦合高内聚**: 模块间通过接口通信
- ✅ **依赖注入**: 提高可测试性
- ✅ **多线程**: 接收线程独立运行，不阻塞 UI

---

## 技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| **Python** | 3.14+ | 编程语言 |
| **PySide6** | 6.10.2+ | GUI 框架 |
| **pyserial** | 3.5+ | 串口通信 |
| **chardet** | 5.2.0+ | 编码检测 |

**开发工具**: UV、Nuitka、Git、Qt Designer

---

## 打包发布

### 使用 Nuitka

```powershell
# 安装 Nuitka
uv pip install nuitka

# 打包命令
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

**输出**: `main.dist/PyCOM.exe`

---

## 常见问题

### Q: 无法检测到串口？
**A**: 检查设备连接、驱动安装、是否被其他程序占用

### Q: 打开串口提示"端口被占用"？
**A**: 关闭其他串口程序，或重新插拔设备

### Q: 中文显示乱码？
**A**: 菜单栏 → Settings → Encoding → 选择 UTF-8 或 GBK

### Q: 十六进制模式无法输入？
**A**: 只能输入 0-9、A-F、a-f 和空格

### Q: 循环发送无法停止？
**A**: 取消勾选 Cycle 复选框，或关闭串口

### Q: JSON 文件发送失败？
**A**: 检查 JSON 格式，参考 demo 目录示例

**日志位置**: `C:\Users\<用户名>\log\pycom\pycom.log`

---

## 版本历史

### v2.0.0 (2026-02-09) - 重构版本
- 🎉 **架构重构**: 模块化设计，代码质量提升至 9.4/10
- ✨ **新增功能**: Multi Send Hex Mode 自动转换和验证
- 🐛 **修复问题**: 编码同步、资源清理、行为一致性
- 📝 **代码优化**: 删除冗余代码，改进错误处理
- 📊 **性能提升**: 添加数据丢失监控

### v1.3.2 (2024-12-XX)
- 更新 PySide6 到 v6.10.2
- 优化异常处理
- 改进资源清理

<details>
<summary>查看完整版本历史</summary>

### v1.3.1 (2024-11-XX)
- 优化串口开关按钮动画

### v1.3.0 (2024-10-XX)
- 引入 UV 包管理器
- 使用 Ruff 格式化代码

### v1.2.x
- 界面优化和功能改进

### v1.1.x
- 添加多路发送和文件发送功能

### v1.0.0
- 初始版本

</details>

完整版本历史: [ReleaseNote.txt](ReleaseNote.txt)

---

## 贡献指南

欢迎贡献！请遵循以下步骤：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交 Pull Request

**代码规范**:
- 遵循 PEP 8
- 使用类型提示
- 添加文档字符串
- 确保通过测试

**报告问题**: [GitHub Issues](https://github.com/kainan-tek/PyCom/issues)

---

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

---

## 联系方式

- **作者**: kainan-tek
- **邮箱**: kainanos@outlook.com
- **GitHub**: https://github.com/kainan-tek/PyCom
- **问题反馈**: [GitHub Issues](https://github.com/kainan-tek/PyCom/issues)

---

<div align="center">

**如果这个项目对你有帮助，请给个 ⭐ Star！**

Made with ❤️ by kainan-tek

[⬆ 回到顶部](#pycom)

</div>
