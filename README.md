# PDF 工具箱

基于 PySide6 的 PDF 处理工具，支持 PDF 拆分、合并、压缩以及多种扩展功能。提供三主题一键切换的现代化界面，全部 UI 元素采用 QPainter 自绘 + Unicode，零外部图标纹理资源。

## 功能特点

### 核心功能

#### PDF 拆分

支持两种拆分模式：

- **按页码范围拆分**：用户可以指定页码范围列表，例如输入 `1-3,5,7-9` 会将 PDF 拆分为包含第1-3页、第5页、第7-9页的多个文件
- **按固定页数拆分**：用户可以指定每 N 页拆分为一个文件，例如每 10 页拆分为一个独立的 PDF 文件

拆分后的文件命名格式为 `{原文件名}_part1.pdf`、`{原文件名}_part2.pdf` 或 `{原文件名}_p1_to_p10.pdf` 等。

#### PDF 合并

- 支持同时合并多个 PDF 文件为一个文件
- 支持在合并时指定每个文件的页面范围，页码规格格式为 `1-3,5,7-9`
- 支持调整文件合并顺序，拖拽调整优先级
- 输出文件名称可自定义

#### PDF 压缩

提供三档压缩级别：

- **低压缩**：保持较高的图片质量，适合需要保持可读性的文档
- **中压缩**：平衡文件大小和质量，适合一般办公文档
- **高压缩**：最大程度减小文件大小，可能会明显降低图片清晰度

压缩会处理 PDF 中的图片和流数据，可有效减小文件体积。

### 扩展功能

#### 页面编辑

- **页面旋转**：支持 90° / 180° / 270° 三个角度旋转，可选顺/逆时针方向
- **删除页面**：支持页码范围语法删除指定页面，删除前有确认提示
- 输出文件命名：`{原文件名}_rotated.pdf` / `{原文件名}_trimmed.pdf`

#### PDF 转图片

- 支持输出格式：PNG（透明背景）/ JPG（白底）
- 可选 DPI：72（屏幕）/ 150（标准）/ 300（高清）/ 600（打印）
- 支持指定页码范围转换
- 输出命名：`{原文件名}_page_1.png`

#### 转为 PDF

支持多种格式转换为 PDF：

| 源格式                        | 说明                                      |
| -------------------------- | --------------------------------------- |
| 图片 (PNG/JPG/BMP/TIFF/WebP) | 多图可合并为一个 PDF，支持拖拽调整顺序                   |
| Word (.docx/.doc)          | 需要 Microsoft Office / WPS / LibreOffice |
| PowerPoint (.pptx/.ppt)    | 需要 Microsoft Office / WPS / LibreOffice |

### 界面功能

- **三主题切换**：简约风 / 水墨风 / 科幻风，一键切换，全部自绘
- **无边框窗口**：自定义标题栏，支持拖拽移动
- **侧边栏导航**：220px 宽，支持折叠为 56px 图标模式（窗口<1100px 自动折叠）
- **拖拽操作**：支持直接将文件拖拽到窗口中进行处理
- **进度显示**：处理过程中显示实时进度条（三主题不同风格）
- **文件预览**：支持预览 PDF 页面内容
- **Toast 反馈**：操作结果即时提示，三主题各自风格

## 三主题视觉系统

| 特性 | 简约风 | 水墨风 | 科幻风 |
|------|--------|--------|--------|
| 主背景 | `#FAFAFA` | `#F4EEDF` | `#0A0E14` |
| 卡片 | `#FFFFFF` 圆角10px | `#FBF6E9` 圆角4px+墨晕 | `#111826` 圆角2px+网格 |
| 侧边栏 | `#F2F2F4` | `#EBE3CF` | `#0D131D` |
| 强调色 | `#2E6BE6` | `#8B2B2B` | `#00E5FF` |
| 字体 | Inter/PingFang SC | 霞鹜文楷/Noto Serif | Orbitron/Rajdhani |
| 按钮 | 蓝填充圆角6px | 朱砂印章块 | 切角矩形+发光 |
| 纹理 | 无 | 宣纸噪点+纤维线 | 40px网格+暗角+扫描条 |
| 图标风格 | 线稿1.5px RoundCap | 飞白描边FlatCap | 青蓝SquareCap+外发光 |

### 自绘图标系统

14+ 枚图标统一 `IconWidget(name, size, theme)`：
- 简约：线稿 1.5px RoundCap，随 palette 着色
- 水墨：同路径但描边 1.2–2.2 非均匀分段（FlatCap+透明度梯度模拟飞白）
- 科幻：路径外六边形框，青蓝 `#00E5FF` 1.2px SquareCap，可选外发光

### 背景纹理（纯代码生成）

- **水墨宣纸**：固定种子撒 800–1200 个 1–2px 噪点 + 2–3 条淡贝塞尔纤维线
- **科幻网格**：40px 步长青蓝细线 + 径向暗角；扫描条 4px QPropertyAnimation y 轴循环
- **简约**：纯色面

## 技术栈

| 类别     | 技术                      | 说明                 |
| ------ | ----------------------- | ------------------ |
| GUI 框架 | PySide6 (Qt for Python) | 跨平台桌面应用开发框架        |
| PDF 处理 | pypdf                   | PDF 读取和写入          |
| PDF 处理 | pikepdf                 | PDF 底层操作和压缩        |
| 图片处理   | Pillow (PIL)            | PDF 内嵌图片处理、图片转 PDF |
| PDF 渲染 | fitz (PyMuPDF)          | PDF 页面渲染、PDF 转图片   |

## 项目结构

```
pdf_tool/
├── core/                    # 核心 PDF 操作模块
│   ├── split.py             # PDF 拆分功能实现
│   ├── merge.py             # PDF 合并功能实现
│   ├── compress.py          # PDF 压缩功能实现
│   ├── page_editor.py       # 页面旋转与删除
│   ├── pdf_to_image.py      # PDF 转图片
│   ├── to_pdf.py            # 多格式转 PDF
│   ├── plugins.py           # 扩展功能插件系统
│   └── __init__.py          # 模块初始化，包含基类定义
├── ui/                      # 用户界面模块
│   ├── main_window.py       # 主窗口（标题栏+侧边栏+内容区+状态栏）
│   ├── home_page.py         # 主页/导航页面（旧版兼容）
│   ├── split_page.py        # 拆分功能页面
│   ├── merge_page.py        # 合并功能页面
│   ├── compress_page.py     # 压缩功能页面
│   ├── preview_widget.py    # PDF 预览组件
│   ├── dialogs.py           # 对话框组件（旧版兼容）
│   ├── drag_drop_mixin.py   # 拖拽功能混入类
│   ├── pages/               # 新页面目录
│   │   └── home_page.py     # 三主题适配主页
│   ├── widgets/             # 自绘控件目录
│   │   ├── icon.py          # 自绘图标系统（14+ 图标）
│   │   ├── painters.py      # InkLine/CinnabarSeal/ChamferedButton/CornerMarks/BrushArrow/NeonProgressBar
│   │   ├── textures.py      # RicePaperTexture/SciFiGridTexture/MinimalTexture
│   │   └── toast.py         # 三主题 Toast 组件
│   ├── styles/              # 主题 QSS 目录
│   │   ├── minimal.py       # 简约风 QSS
│   │   ├── ink.py           # 水墨风 QSS
│   │   └── scifi.py         # 科幻风 QSS
│   ├── dialogs/             # 新对话框目录
│   │   ├── drop_dialog.py   # 拖放选择对话框
│   │   └── settings_dialog.py # 设置浮层+主题预览
│   └── plugins/             # 扩展功能页面
│       ├── page_editor_page.py
│       ├── pdf_to_image_page.py
│       └── to_pdf_page.py
├── workers/                 # 后台工作线程
│   ├── split_worker.py
│   ├── merge_worker.py
│   ├── compress_worker.py
│   ├── page_editor_worker.py
│   ├── pdf_to_image_worker.py
│   └── to_pdf_worker.py
├── utils/                   # 工具模块
│   ├── theme_manager.py     # 主题管理器（三主题切换+持久化）
│   └── config_manager.py    # 配置管理（导出路径等）
├── assets/                  # 资源文件
│   └── styles/              # 旧版 QSS 样式表（兼容）
│       ├── dark_theme.qss
│       └── light_theme.qss
├── main.py                  # 应用入口文件
└── build.spec               # PyInstaller 打包配置
```

## 环境要求

- Python 3.10+
- Windows/Linux/macOS 操作系统

### 可选依赖

Word 和 PPT 转换功能需要以下环境之一：

- Microsoft Office (Windows/Mac)
- WPS Office (Windows/Mac)
- LibreOffice (Linux/Windows/Mac)

## 安装依赖

```bash
pip install -r requirements.txt
```

可选依赖（用于 Word/PPT 转 PDF）：

```bash
pip install docx2pdf comtypes  # Windows
pip install docx2pdf            # Mac
```

## 运行方式

```bash
python main.py
```

## 打包发布

使用 PyInstaller 打包为可执行文件：

```bash
pyinstaller build.spec
```

打包完成后，可执行文件位于 `dist/` 目录下，可以独立运行无需安装 Python 环境。

## 使用说明

### 主题切换

点击标题栏右侧的主题切换按钮（简约=方块/水墨=墨点/科幻=六边形），即可在三主题间循环切换。主题选择会自动保存，下次启动时恢复。

### 导出位置配置

每个功能页面（拆分/合并/压缩/页面编辑等）都支持两种导出位置模式：

- **使用默认位置**：文件将直接导出到预设的默认路径（无需弹窗）
- **每次询问**：功能执行时弹出文件保存对话框，让用户手动指定导出位置

#### 设置默认导出路径

在功能页面中，点击「导出位置」分组下的「设置...」按钮。

默认导出路径初始值为 `~/Documents/PDFTool_Output`（可根据实际需求修改）。

### 拆分 PDF

1. 启动应用后，选择「拆分 PDF」功能
2. 点击「浏览...」或直接拖拽 PDF 文件到窗口
3. 选择拆分模式（按范围或按固定页数）
4. 设置拆分参数
5. 在「导出位置」中选择导出模式（默认位置/每次询问）
6. 点击「开始拆分」按钮

### 合并 PDF

1. 选择「合并 PDF」功能
2. 点击「添加文件」或拖拽多个 PDF 文件
3. 如需指定页面范围，点击文件后的编辑按钮
4. 拖拽调整文件顺序
5. 在「导出位置」中选择导出模式（默认位置/每次询问）
6. 点击「开始合并」按钮

### 压缩 PDF

1. 选择「压缩 PDF」功能
2. 添加 PDF 文件
3. 选择压缩级别（低/中/高）
4. 在「导出位置」中选择导出模式（默认位置/每次询问）
5. 点击「开始压缩」按钮

### 页面编辑

1. 选择「页面编辑」功能
2. 添加 PDF 文件
3. 在左侧设置旋转角度和方向，或输入要删除的页码
4. 可勾选缩略图中的页面来自动填充页码
5. 点击「旋转页面」或「删除页面」按钮

### PDF 转图片

1. 选择「PDF 转图片」功能
2. 添加 PDF 文件
3. 选择输出格式（PNG/JPG）和 DPI
4. 可选择指定页面范围或全部转换
5. 点击「开始转换」按钮

### 转为 PDF

1. 选择「转为 PDF」功能
2. 添加图片/Word/PPT 文件
3. 如为多图，可拖拽调整合并顺序
4. 设置输出文件名
5. 点击「开始转换」按钮

## 设计规范

### 视觉参数

- 窗口尺寸：1440×860（最小 1100×700）
- 侧边栏：220px（折叠时 56px）
- 标题栏：44px
- 状态栏：28px
- 栅格间距：8px
- 字号：20/15/13/12/13px

### 主题切换机制

`ThemeManager.apply(name)`：
1. 加载 QSS 字符串
2. `setStyleSheet` 应用样式
3. 广播 `themeChanged` 信号
4. 所有自绘组件 `update()` 重绘
5. `MainWindow` 重绘纹理
6. `QSettings` 持久化保存

### 图标升级路径

后续接入正式 SVG 资源，仅需为 `IconWidget` 增加「优先外部 SVG，失败回退自绘」分支，其余架构完全复用。

## 注意事项

- 压缩功能会处理 PDF 中的图片，处理大型文件可能需要较长时间
- 合并时支持页码规格语法：
  - 单页：`5` 表示第5页
  - 连续页：`1-3` 表示第1到第3页
  - 混合：`1-3,5,7-9` 表示第1-3页、第5页、第7-9页
- 拆分时的页码范围使用 1-based 索引（从1开始计数）
- Word/PPT 转换需要系统安装 Microsoft Office、WPS 或 LibreOffice

## 已知限制

- 处理非常大的 PDF 文件可能会消耗较多内存
- 某些加密 PDF 文件可能无法处理
- 图片转 PDF 功能仅支持常见图片格式（PNG、JPG、BMP、TIFF、WebP）
- Word/PPT 转换在无 Office 环境的 Linux 服务器上不可用

## 故障排除

### 常见问题

1. **应用无法启动**
   - 检查是否安装了所有必要的依赖项
   - 确保 Python 版本为 3.10 或更高

2. **PDF 处理失败**
   - 检查 PDF 文件是否损坏
   - 对于加密 PDF，确保有正确的密码
   - 对于大文件，确保有足够的内存

3. **导出路径问题**
   - 确保指定的导出路径存在且有写入权限
   - 检查默认导出路径设置是否正确

4. **Word/PPT 转换失败**
   - 确保系统已安装 Microsoft Office、WPS 或 LibreOffice
   - 尝试以管理员权限运行应用

### 错误信息

- **"文件不是有效的 PDF"**：检查文件格式是否正确，确保是标准 PDF 文件
- **"权限错误"**：确保有足够的权限读取输入文件和写入输出文件
- **"内存不足"**：尝试处理较小的文件或增加系统内存
- **"Word/PPT 转换需要..."**：检查 Office 软件是否正确安装

## 联系方式

如有问题或建议，请通过项目仓库提交 Issue 或 Pull Request。
