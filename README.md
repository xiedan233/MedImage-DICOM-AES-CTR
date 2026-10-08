# 医学影像数据安全传输工具（基于 AES-CTR 模式）

Secure Transmission Tool for Medical Image Data Based on AES Algorithm in CTR Mode

本项目实现了一套面向 DICOM 医学影像的**加密传输**与**可视化**工具。核心采用 **AES 算法 CTR 模式**对医学影像数据进行加密，并结合 **Diffie-Hellman 密钥交换**完成安全信道建立。

## 功能特性

- 医学影像（DICOM）加密传输：客户端—服务器架构，传输内容经 AES-CTR 加密。
- 安全密钥协商：通过 Diffie-Hellman 密钥交换动态生成会话密钥。
- 图形化操作界面：基于 PyQt5 的客户端 GUI，可选择 DICOM 文件并发送。
- DICOM 影像查看：基于 Qt 的桌面查看器，支持 DICOM 文件读取与显示。

## 目录结构

```
.
├── 代码/                    # Python 实现：加密传输客户端 / 服务器
│   ├── main.py              # 入口：启动 client / server / GUI
│   ├── config.py            # 配置
│   ├── requirements.txt     # Python 依赖
│   ├── client/              # 客户端（GUI、加密、DICOM 处理、网络）
│   ├── server/              # 服务器端（加密、DICOM 处理、网络）
│   ├── security/            # DH 密钥交换
│   └── utils/               # 日志等工具
└── 医疗DICOM数据处理软件DCMV/ # C++ / Qt 实现的 DICOM 查看器
│   ├── main.cpp
│   ├── DicomViewer.cpp / .h
│   ├── DicomHelper.cpp / .h
│   └── DicomViewer.ui
```


## 技术栈

- 加密：Python `pycryptodome` / `cryptography`，AES-CTR 模式，Diffie-Hellman 密钥交换
- 影像处理：`pydicom`、`gdcm`、`pylibjpeg`、`numpy`、`matplotlib`
- 界面：PyQt5（Python 端）、Qt（C++ 端）
- 通信：基于 socket 的客户端 / 服务器网络模块

## 快速开始（Python 端）

```bash
cd 代码
pip install -r requirements.txt

# 启动服务器
python main.py server

# 启动客户端（图形界面）
python main.py client --gui

# 或命令行直接发送某个 DICOM 文件
python main.py client path/to/file.dcm
```

## C++ DICOM 查看器

使用 Qt 构建 `医疗DICOM数据处理软件DCMV` 工程，编译后运行 `DicomViewer` 即可查看 DICOM 影像。

## 安全说明

- 数据在传输前经 AES-CTR 加密，密钥通过 Diffie-Hellman 协商，降低密钥泄露风险。
- 本仓库代码仅用于学习与工程实践，请勿直接用于生产环境而不做进一步安全评估。

## 许可证

本项目仅供学习与研究使用。
