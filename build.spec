# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path

block_cipher = None

project_root = Path(SPECFILE).parent if SPECFILE else Path('.')
dist_dir = project_root / 'build'

pyside6_path = None
for p in sys.path:
    if 'PySide6' in p:
        pyside6_path = Path(p).parent
        break

hidden_imports = [
    'pypdf',
    'pikepdf',
    'PyMuPDF',
    'PIL',
    'PySide6',
    'PySide6.QtCore',
    'PySide6.QtGui',
    'PySide6.QtWidgets',
    'PySide6.scripts',
    'shiboken6',
]

excludes = [
    'tkinter',
    'test',
    'unittest',
    'pytest',
    'numpy',
    'pandas',
    'matplotlib',
    'scipy',
    'IPython',
    'notebook',
    'jupyter',
]

a = Analysis(
    ['main.py'],
    pathex=[str(project_root)],
    binaries=[],
    datas=[
        (str(project_root / 'assets'), 'assets'),
    ],
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='PDFTool',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(project_root / 'assets' / 'app_icon.ico') if (project_root / 'assets' / 'app_icon.ico').exists() else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='PDFTool',
)

app = BUNDLE(
    coll,
    name='PDFTool.app',
    icon=str(project_root / 'assets' / 'app_icon.ico') if (project_root / 'assets' / 'app_icon.ico').exists() else None,
    bundle_identifier='com.pdftool.app',
    info_plist={
        'CFBundleDisplayName': 'PDF Tool',
        'CFBundleName': 'PDFTool',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'LSMinimumSystemVersion': '10.15',
    },
    console=False,
)
