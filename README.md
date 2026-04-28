# PDF Tool - 多功能 PDF 处理工具箱

一款跨平台的桌面 PDF 处理工具，提供拆分、合并、压缩、页面编辑、格式转换等一站式解决方案。

---

## 这是什么

PDF Tool 是一个基于 Python + Qt 开发的桌面应用程序，帮助用户无需安装 Adobe Acrobat 等专业软件，即可完成日常 PDF 处理任务。支持 Windows、macOS 和 Linux 系统。

---

## 核心功能

- **PDF 拆分**：按页码范围或固定页数将 PDF 拆分为多个文件
- **PDF 合并**：将多个 PDF 文件合并为一个，支持指定页码范围
- **PDF 压缩**：提供低/中/高三档压缩，有效减小文件体积
- **页面编辑**：旋转、删除指定页面，支持批量操作
- **PDF 转图片**：将 PDF 页面导出为 PNG/JPG 格式，支持自定义 DPI
- **转为 PDF**：图片、Word、PPT 文件一键转换为 PDF

---

## 技术栈

| 类别 | 技术 |
|------|------|
| 编程语言 | Python 3.9+ |
| GUI 框架 | PySide6 (Qt6) |
| PDF 处理 | pypdf, pikepdf, PyMuPDF |
| 图片处理 | Pillow |
| Office 转换 | pywin32 (Windows) / LibreOffice |
| 主题系统 | 自定义 QSS + 动态切换 |

---

## 快速开始

### 环境要求

- Python 3.9 或更高版本
- Windows 10+/macOS 10.15+/Linux

### 安装依赖

```bash
# 克隆仓库
git clone <repository-url>
cd pdf_tool

# 创建虚拟环境（推荐）
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 运行程序

```bash
python main.py
```

---

## 贡献指南

### 提交 Issue

- 使用清晰的标题描述问题
- 提供复现步骤和系统环境信息
- 如有错误日志，请一并附上

### 提交 Pull Request

1. Fork 本仓库
2. 创建功能分支：`git checkout -b feature/your-feature`
3. 提交更改：`git commit -m "feat: add some feature"`
4. 推送分支：`git push origin feature/your-feature`
5. 创建 Pull Request

### 代码规范

- 遵循 PEP 8 代码风格
- 新功能需添加适当的日志记录
- 保持与现有代码风格一致

---

## 许可证

MIT License
